import functools
import glob
import os

import pytest

import harmonyparser

import logging

from harmonyparser import HScene

logger = logging.getLogger("harmonyparser_test_collection")


@functools.cache
def _get_sample_paths(config: pytest.Config):
    paths = config.getoption("scene_path")
    if paths is None:
        sample_folder = os.environ.get(
            "HARMONY_PARSER_TEST_SAMPLES_FOLDER",
            os.path.join(os.path.dirname(__file__), "samples"),
        )
        logger.info(f"Collecting sample xstage files in folder {sample_folder}...")
        paths = sorted(glob.glob(os.path.join(sample_folder, "*.xstage")))
    else:
        paths = [paths]
    logger.info(f"Use {len(paths)} tests files:")
    for sample_path in paths:
        logger.info(f"\t{sample_path}")
    return paths


@functools.cache
def _get_scene_from_path(path):
    return harmonyparser.parse(path)


@functools.cache
def _columns_from_scene(scene: HScene):
    return list(scene.iter_columns())


def pytest_addoption(parser):
    parser.addoption("--scene-path", help="Run tests for the given scene paths")
    parser.addoption("--column", help="Run tests for the columns")


def pytest_generate_tests(metafunc: pytest.Metafunc):
    if "sample_scene" in metafunc.fixturenames:
        paths = _get_sample_paths(metafunc.config)
        scenes = {path: _get_scene_from_path(path) for path in paths}
        metafunc.parametrize("sample_scene", scenes.values(), ids=scenes.keys())
    if "sample_column" in metafunc.fixturenames:
        paths = _get_sample_paths(metafunc.config)
        scenes = {path: _get_scene_from_path(path) for path in paths}
        columns = {
            f"{path}, {column.name}": column
            for path, scene in scenes.items()
            for column in _columns_from_scene(scene)
        }
        metafunc.parametrize("sample_column", columns.values(), ids=columns.keys())
