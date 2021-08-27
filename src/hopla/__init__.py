import logging

import sys

import click
from hopla.subgroups.add import add
from hopla.subgroups.api import api
from hopla.subgroups.set import set
from hopla.subcommands.version import version
from hopla.subcommands.auth import auth
from hopla.subcommands.config import config
from hopla.subcommands.feed import feed
from hopla.subcommands.complete import complete
from hopla.subgroups.buy import buy
from hopla.subgroups.get import get


def setup_logging() -> logging.Logger:
    """Setup python logging for the entire hopla project"""
    # https://docs.python.org/3.8/howto/logging.html#logging-basic-tutorial
    logging.basicConfig(
        format='[%(levelname)s][%(filename)s|%(asctime)s] %(message)s',
        level=logging.DEBUG,
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    return logging.getLogger(__name__)


log = setup_logging()


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def hopla():
    """hopla - a command line interface (CLI) to interact with habitica.com

    \f
    :return:
    """
    pass


def entry_cmd():
    log.info("Thank you for trying out hopla in its early release")
    log.info("Bug reports, pull requests, and feature requests are welcomed over at:  ")
    log.info("  <https://github.com/melvio/hopla>")
    log.debug(f"start application with arguments: {sys.argv}")
    # subgroups
    hopla.add_command(add)
    hopla.add_command(api)
    hopla.add_command(set)
    hopla.add_command(buy)
    hopla.add_command(get)
    # subcommands
    hopla.add_command(config)
    hopla.add_command(complete)
    hopla.add_command(version)
    hopla.add_command(auth)
    hopla.add_command(feed)
    hopla()
