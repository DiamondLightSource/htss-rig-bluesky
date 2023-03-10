import IPython
from traitlets.config import get_config

from .startup import *  # noqa: F401, F403

conf = get_config()
conf.InteractiveShellEmbed.colors = "Linux"
IPython.embed(config=conf)
