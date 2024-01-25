import os
from types import GeneratorType

import pytest
import harmonyparser
from harmonyparser import parser as hp


@pytest.fixture
def project():
    return harmonyparser.parse(
        os.path.join(os.path.dirname(__file__), "samples", "sample1.xstage")
    )


def test_parser(project):
    assert isinstance(project, harmonyparser.SBoardProject)


def test_scene(project):
    scene_gen = project.scenes
    assert isinstance(scene_gen, GeneratorType)
    for scene in scene_gen:
        assert isinstance(scene, hp.SBoardScene)

