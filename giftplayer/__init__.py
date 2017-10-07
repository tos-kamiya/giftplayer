from .gift_ast import Node, gift_parse
from .html_form_builder import html_escape_node_body_strs, build_form_content, build_html_with_answer_render
from .answer_scorer import build_quiz_answer, str_normalize, parse_form_content, score_submission
import html


__version__ = '0.1.8'


__doc__ = """Render/serve given GIFT script as HTML.

Usage:
  giftplayer cat [options] <giftscript>
  giftplayer web [options] <giftscript>
  giftplayer (--help|--version)

Options:
  -s <seed> --shuffle=<seed>  Seed of shuffling choices of each question.
  -p <port> --port=<PORT>     Port number of web app', [default: 5000].
  --debug-wo-hint             Debug option. Generate HTML w/o parsing answer.
"""

def main():
    import sys
    from docopt import docopt
    from . import web_player
    from . import html_form_builder

    args = docopt(__doc__, version=__version__)
    gift_script = args['<giftscript>']
    shuffle_seed = int(args['--shuffle'] or "-1")
    web_server = args['web'] or False
    port = int(args['--port'])
    debug_wo_hint = args['--debug-wo-hint'] or None

    if web_server:
        if not sys.stdout.isatty():
            sys.stdout.write("""<!DOCTYPE HTML><html><body>Go to <a href="http://127.0.0.1:5000">giftplay server</a></body></html>\n""")
            sys.stdout.flush()
        web_player.entrypoint(gift_script, shuffle_seed, port)
    else:
        html_form_builder.entrypoint(gift_script, False, shuffle_seed, debug_wo_hint)
