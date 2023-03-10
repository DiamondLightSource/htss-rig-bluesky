from importlib.metadata import version

__version__ = version("htss-rig-bluesky")
del version

__all__ = ["__version__"]
