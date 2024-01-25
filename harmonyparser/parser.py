"""
Parser for Harmony .xstage xml file.
The SBoardScene class will let you build a hierarchy of objects from the
given xstage file.
"""

import abc
import os
from typing import Generator, Self, Optional, Type
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


class HProject(HNode):
    """Root object of Harmony project."""

    @classmethod
    def from_file(cls, sboard_path: str) -> Self:
        """Returns a SBoardProject from the given path.

        Returns:
            SBoardProject
        """
        return cls(cElementTree.parse(sboard_path).getroot())

    @property
    def colums(self, column_filter=None) -> Generator["HColumn", None, None]:
        """Returns a generator of layers in the scene."""
        column_filter = f"[type='{column_filter}']" if column_filter else ""
        path = f"./scenes/scene[@name='Top']/columns/column{column_filter}"
        for xml_column in self.xml_node.findall(path):
            yield HColumn(xml_column)

    def get_graph(self):
        root = self.xml_node.find("./scenes/scene[@name='Top']/rootgroup")
        return HGraphNode(root)


class HColumn(HNode):
    """A column in the project."""

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


class HGraphNode(HNode):
    def __init__(self, xml_node: cElementTree.Element, parent: Optional[Self] = None):
        super().__init__(xml_node)
        self.__parent = parent

    @property
    def name(self) -> str:
        """Returns the name of the node."""
        return self.xml_node.attrib["name"]

    @property
    def parent(self) -> Self:
        """Return the parent node of the graph."""
        return self.__parent

    def get_path(self) -> str:
        """Return the path of the node.
        Each node is separated by a "/" character."""
        if not self.__parent:  # root node case
            return self.name
        return f"{self.parent.get_path()}/{self.name}"

    def children(self, recursive=True) -> Generator[Self, None, None]:
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
