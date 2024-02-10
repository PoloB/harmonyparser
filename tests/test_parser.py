from types import GeneratorType

import pytest

from src import harmonyparser
from src.harmonyparser import HScene, error
from src.harmonyparser.parser import HColumn, HElement, HGraphNode


@pytest.fixture()
def scene_path() -> str:
    return "samples/new_scene_21.xstage"


@pytest.fixture()
def scene(scene_path: str) -> HScene:
    return harmonyparser.parse(scene_path)


@pytest.fixture()
def exp_element(scene: HScene) -> HElement:
    return scene.get_element_from_name("Drawing")


def test_scene(scene: HScene):
    assert scene.id == "0b0e5000b1861eda"
    assert scene.start_frame == 1
    assert scene.end_frame == 60


def test_element_iter(scene: HScene):
    gen_elements = scene.iter_elements()
    assert isinstance(gen_elements, GeneratorType)
    gen_elements = list(gen_elements)
    assert len(gen_elements) == 1


def test_column_iter(scene: HScene):
    gen_columns = scene.iter_columns()
    assert isinstance(gen_columns, GeneratorType)
    gen_columns = list(gen_columns)
    assert len(gen_columns) == 1


@pytest.mark.parametrize(
    "name, exp_id, exp_folder, exp_root_folder", [("Drawing", 1, "Drawing", "elements")]
)
def test_element_name(
    scene: HScene, name: str, exp_id: int, exp_folder: str, exp_root_folder: str
):
    element = scene.get_element_from_name(name)
    assert isinstance(element, HElement)
    assert element.id == exp_id
    assert element.folder == exp_folder
    assert element.root_folder == exp_root_folder


@pytest.mark.parametrize(
    "e_id, exp_name, exp_folder, exp_root_folder",
    [(1, "Drawing", "Drawing", "elements")],
)
def test_element_id(scene: HScene, e_id: int, exp_name: str, exp_folder: str, exp_root_folder: str):
    element = scene.get_element_from_id(e_id)
    assert isinstance(element, HElement)
    assert element.name == exp_name
    assert element.folder == exp_folder
    assert element.root_folder == exp_root_folder


def test_missing_element(scene: HScene):
    with pytest.raises(error.ElementNotFoundError):
        scene.get_element_from_id(42)
    with pytest.raises(error.ElementNotFoundError):
        scene.get_element_from_name("missing")


def _assert_same_element(element: HElement, expected_element: HElement):
    assert element.id == expected_element.id
    assert element.name == expected_element.name
    assert element.folder == expected_element.folder
    assert element.root_folder == expected_element.root_folder


@pytest.mark.parametrize("c_id, exp_name, exp_type", [(1, "Drawing", 0)])
def test_column_id(
    scene: HScene, c_id: int, exp_name: str, exp_type: int, exp_element: HElement
):
    column = scene.get_column_from_id(c_id)
    assert isinstance(column, HColumn)
    assert column.name == exp_name
    assert column.type == exp_type
    _assert_same_element(column.get_element(), exp_element)


@pytest.mark.parametrize("name, exp_id, exp_type", [("Drawing", 1, 0)])
def test_column_name(
    scene: HScene, name: str, exp_id: int, exp_type: int, exp_element: HElement
):
    column = scene.get_column_from_name(name)
    assert isinstance(column, HColumn)
    assert column.id == exp_id
    assert column.type == exp_type
    _assert_same_element(column.get_element(), exp_element)


def test_missing_column(scene: HScene):
    with pytest.raises(error.ColumnNotFoundError):
        scene.get_column_from_id(42)
    with pytest.raises(error.ColumnNotFoundError):
        scene.get_column_from_name("missing")


def test_graph(scene: HScene):
    graph = scene.get_graph()
    assert isinstance(graph, HGraphNode)
    assert graph.name == "Top"
    assert graph.type == "ROOT"
    assert isinstance(repr(graph), str)
    assert graph.parent is None
    assert graph.is_root()
    assert graph.get_path() == "/Top"
    # Connected nodes of root
    gen_input_nodes = graph.iter_input_nodes()
    assert isinstance(gen_input_nodes, GeneratorType)
    input_nodes = list(gen_input_nodes)
    assert len(input_nodes) == 0
    gen_output_nodes = graph.iter_output_nodes()
    assert isinstance(gen_output_nodes, GeneratorType)
    output_nodes = list(gen_output_nodes)
    assert len(output_nodes) == 0
    # Children
    gen_children = graph.iter_children()
    assert isinstance(gen_children, GeneratorType)
    children = list(gen_children)
    assert len(children) == 4
    # Get child by name
    composite_node = graph.get_child("Composite")
    assert isinstance(composite_node, HGraphNode)
    assert composite_node.parent is graph
    assert composite_node.get_path() == "/Top/Composite"
    assert composite_node.type == "COMPOSITE"
    assert composite_node.name == "Composite"
    # Get child by path
    read_node = graph.get_child_at_path("Drawing")
    assert isinstance(read_node, HGraphNode)
    # Check missing child
    with pytest.raises(error.ChildNotFoundError):
        graph.get_child("unknown")
    with pytest.raises(error.ChildNotFoundError):
        graph.get_child_at_path("unknown")
    # Test connections
    input_nodes = list(composite_node.iter_input_nodes())
    assert len(input_nodes) == 1
    assert input_nodes[0].name == read_node.name
    output_nodes = list(read_node.iter_output_nodes())
    assert len(output_nodes) == 1
    assert output_nodes[0].name == composite_node.name
    assert len(list(read_node.iter_input_nodes())) == 0
    write_node = graph.get_child("Write")
    assert len(list(write_node.iter_output_nodes())) == 0
