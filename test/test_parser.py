import glob
import os
from xml.etree import cElementTree

import pytest
import harmonyparser


def _get_sample_files():
    sample_folder = os.environ.get(
        "HARMONY_PARSER_TEST_SAMPLES_FOLDER",
        os.path.join(os.path.dirname(__file__), "samples"),
    )
    return sorted(glob.glob(os.path.join(sample_folder, "*.xstage")))


SAMPLE_FILES = _get_sample_files()


@pytest.fixture(params=SAMPLE_FILES)
def scene():
    return harmonyparser.parse(
        os.path.join(os.path.dirname(__file__), "samples", "sample1.xstage")
    )


def test_scene_attributes(scene):
    assert isinstance(scene.id, str)
    assert isinstance(scene.start_frame, int)
    assert isinstance(scene.end_frame, int)
    assert isinstance(scene.xml_node, cElementTree.Element)
