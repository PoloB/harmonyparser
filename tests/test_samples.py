from types import GeneratorType
from xml.etree import cElementTree

from src.harmonyparser.parser import HColumn, HElement


def test_sample_scene(sample_scene):
    assert isinstance(sample_scene.id, str)
    assert isinstance(sample_scene.start_frame, int)
    assert isinstance(sample_scene.end_frame, int)
    assert isinstance(sample_scene.xml_node, cElementTree.Element)
    gen_columns = sample_scene.iter_columns()
    assert isinstance(gen_columns, GeneratorType)


def test_sample_column(sample_column):
    assert isinstance(sample_column, HColumn)
    assert isinstance(sample_column.name, str)
    assert isinstance(sample_column.type, int)
    element = sample_column.get_element()
    assert isinstance(element, HElement)
