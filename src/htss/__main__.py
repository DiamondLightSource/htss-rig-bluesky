import importlib

import click
import IPython
from traitlets.config import get_config

from htss import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="htss")
@click.pass_context
def main(ctx):
    # if no command is supplied, run with the options passed
    if ctx.invoked_subcommand is None:
        mod = importlib.import_module("htss.startup")
        globals().update(mod)

        conf = get_config()
        conf.InteractiveShellEmbed.colors = "Linux"
        IPython.embed(config=conf)


if __name__ == "__main__":
    main()
