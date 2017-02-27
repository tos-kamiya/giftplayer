import sys

import click

from giftplay import html_form
from giftplay import web_player


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@cli.command(help='Generate HTML')
@click.argument('gift_script', default='')
@click.option('--shuffle', '-s', help='Seed of shuffling choices of each question', default=-1)
@click.option('--debug-wo-hint', help='Debug option. Generate HTML w/o parsing answer', default=False)
def html(gift_script, shuffle, debug_wo_hint):
    html_form.entrypoint(gift_script, False, shuffle, debug_wo_hint)


@cli.command(help='Run as web app')
@click.argument('gift_script', default='')
@click.option('--shuffle', '-s', help='Seed of shuffling choices of each question', default=-1)
def web(gift_script, shuffle):
    if not sys.stdout.isatty():
        sys.stdout.write("""<!DOCTYPE HTML><html><body>Go to <a href="http://127.0.0.1:5000">giftplay server</a></body></html>\n""")
        sys.stdout.flush()
    web_player.entrypoint(gift_script, shuffle)


if __name__ == '__main__':
    cli()
