from .parser import HProject


def parse(filename: str) -> HProject:
    """Parse the given filename and return the corresponding HProject object"""
    return HProject.from_file(filename)
