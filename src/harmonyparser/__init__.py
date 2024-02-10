from .parser import HScene


def parse(filename: str) -> HScene:
    """Parse the given filename and return the corresponding HProject object."""
    return HScene.from_file(filename)
