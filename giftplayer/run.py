import sys

import click

from . import html_form_builder
from . import web_player


@click.command(help="Render given GIFT script as HTML.")
@click.argument('gift_script', default='')
@click.option('--shuffle', '-s', help='Seed of shuffling choices of each question', default=-1)
@click.option('--web-server', '-w', help='Run as web app', is_flag=True)
@click.option('--port', '-p', help='Port number of web app', default=5000)
@click.option('--debug-wo-hint', help='Debug option. Generate HTML w/o parsing answer', is_flag=True)
def cmd(gift_script, shuffle, web_server, port, debug_wo_hint):
    if web_server:
        if not sys.stdout.isatty():
            sys.stdout.write("""<!DOCTYPE HTML><html><body>Go to <a href="http://127.0.0.1:5000">giftplay server</a></body></html>\n""")
            sys.stdout.flush()
        web_player.entrypoint(gift_script, shuffle, port)
    else:
        html_form_builder.entrypoint(gift_script, False, shuffle, debug_wo_hint)


cmd()
