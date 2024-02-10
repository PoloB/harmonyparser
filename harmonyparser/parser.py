"""
Parser for Harmony .xstage xml file.
The HProject.from_file class will let you build a hierarchy of objects from the
given xstage file.
"""
from __future__ import annotations
from __future__ import unicode_literals
import abc
from typing import Self, Optional, Iterator
from xml.etree import cElementTree

from harmonyparser import error


class HNode:
    """Abstract class for all Harmony objects."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, xml_node: cElementTree.Element):
        self.__xml_node: cElementTree.Element = xml_node

    @property
    def xml_node(self) -> cElementTree.Element:
        """Returns the root xml node for this given object."""
        return self.__xml_node


class HScene(HNode):
    """Root object of Harmony project."""

    @classmethod
    def from_file(cls, xstage_path: str) -> Self:
        """Build the scene object from the given xstage path"""
        return cls(cElementTree.parse(xstage_path).getroot())

    def _get_scene_root(self) -> cElementTree.Element:
        return self.xml_node.find("./scenes/scene[@name='Top']")

    def get_graph(self):
        root = self._get_scene_root().find("./rootgroup")
        return HGraphNode(root)

    def iter_columns(self) -> Iterator[HColumn]:
        """Returns a generator of columns in the scene."""
        for xml_column in self._get_scene_root().find("/columns/column"):
            yield HColumn(xml_column, self)

    def iter_elements(self) -> Iterator[HElement]:
        """Returns a generator of elements in the scene."""
        for xml_element in self.xml_node.findall("./elements/element"):
            yield HElement(xml_element)

    def get_element_from_id(self, element_id) -> HElement:
        """Return an element from its id."""
        xml_path = f"./elements/element[@id='{element_id}']"
        xml_element = self.xml_node.find(xml_path)
        if not xml_element:
            raise error.NoElementError(f"No element with id '{element_id}' found")
        return HElement(xml_element)

    def get_element_from_name(self, element_name) -> HElement:
        """Return an element from its name."""
        xml_path = f"./elements/element[@elementName='{element_name}']"
        xml_element = self.xml_node.find(xml_path)
        if not xml_element:
            raise error.NoElementError(f"No element with name '{element_name}' found")
        return HElement(xml_element)

    @property
    def id(self) -> str:
        """Return the id of the scene."""
        return self._get_scene_root().attrib["id"]

    @property
    def start_frame(self) -> int:
        """Return the start frame of the project"""
        return int(self._get_scene_root().attrib["startFrame"])

    @property
    def end_frame(self) -> int:
        """Return the end frame of the project"""
        return int(self._get_scene_root().attrib["stopFrame"])


class HElement(HNode):
    """A Harmony element."""

    @property
    def id(self) -> str:
        """Return the id of the element."""
        return self.xml_node.attrib["id"]

    @property
    def folder(self) -> str:
        """Return the folder of the element."""
        return self.xml_node.attrib["elementFolder"]


class HColumn(HNode):
    """A column in the project."""

    def __init__(self, xml_node: cElementTree.Element, scene: HScene):
        super().__init__(xml_node)
        self.__scene = scene

    @property
    def name(self) -> str:
        """Returns the name of the column."""
        return self.xml_node.attrib["name"]

    @property
    def type(self) -> int:
        """Returns the type of the column."""
        return int(self.xml_node.attrib["type"])

    @property
    def color(self) -> str:
        """Return the color of the column in hexadecimal format."""
        return self.xml_node.attrib["color"]

    def get_element(self) -> HElement:
        """Return the associated element."""
        element_id = self.xml_node.attrib["id"]
        return self.__scene.get_element_from_id(element_id)


class HGraphNode(HNode):
    """A node a graph."""

    def __init__(self, xml_node: cElementTree.Element, parent: Optional[Self] = None):
        super().__init__(xml_node)
        self.__parent = parent

    def __repr__(self):
        return f"{self.type}('{self.get_path()}')"

    @property
    def name(self) -> str:
        """Returns the name of the node."""
        return self.xml_node.attrib["name"]

    @property
    def parent(self) -> Self:
        """Return the parent node of the graph."""
        return self.__parent

    @property
    def type(self) -> str:
        """Returns the type of the node."""
        return "ROOT" if not self.__parent else self.xml_node.attrib["type"]

    def is_root(self) -> bool:
        """Return True if the node is the root of the graph."""
        return self.__parent is None

    def get_path(self) -> str:
        """Return the path of the node.
        Each node is separated by a "/" character."""
        if not self.__parent:  # root node case
            return self.name
        return f"{self.parent.get_path()}/{self.name}"

    def children(self, recursive=True) -> Iterator[Self]:
        """Returns a generator of children nodes."""
        for xml_child in self.xml_node.findall("./nodeslist/*"):
            child_node = HGraphNode(xml_child, self)
            yield child_node
            if recursive:
                yield from child_node.children(recursive=recursive)

    def get_child(self, child_name: str) -> Self:
        """Returns the child from its name."""
        current_node = self.xml_node
        current_node = current_node.find(f".//*[@name='{child_name}']")
        if not current_node:
            raise error.NoChildNodeError(
                f"Node '{self.get_path()}' has no child named '{child_name}'"
            )
        return self.__class__(current_node, self)

    def get_child_at_path(self, child_path: str) -> Self:
        """Return the child from its path relative to this node."""
        current_node = self
        for child in child_path.split("/"):
            current_node = current_node.get_child(child)
        return current_node

    def input_nodes(self) -> Iterator[Self]:
        """Iterates over the input nodes of the current node."""
        xml_nodes = self.parent.xml_node.findall(f"./linkedlist//*[@in='{self.name}']")
        names = (xml_node.attrib["out"] for xml_node in xml_nodes)
        for name in names:
            yield self.parent.get_child(name)

    def output_nodes(self) -> Iterator[Self]:
        """Iterates over the input nodes of the current node."""
        xml_nodes = self.parent.xml_node.findall(f"./linkedlist//*[@out='{self.name}']")
        names = (xml_node.attrib["in"] for xml_node in xml_nodes)
        for name in names:
            yield self.parent.get_child(name)
