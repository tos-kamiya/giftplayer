import os.path as path
import random
import sys

from flask import Flask, request

from .html import DEFAULT_SEND_BUTTON, DEFAULT_CSS, JQUERY_LOCAL_JS
from .gift_ast import gift_parse
from .html_form_builder import html_escape_node_body_strs, build_form_content
from .answer_scorer import build_quiz_answer, parse_form_content, score_submission


CSS = """
""" + DEFAULT_CSS + """
<style type="text/css">
table.score {
  border-collapse: collapse;
  border: 2px solid #333;
}
table.score td, table.score th {
  border-collapse: collapse;
  border: 1px solid #333;
}
</style>
"""

HEAD = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
%s
%s
</head>
<body>
<form action="/submit_answer" method="post">
""" % (CSS, JQUERY_LOCAL_JS)

FOOT = """
<br />
<br />
%s
</form>
</body>
</html>
""" % DEFAULT_SEND_BUTTON

HEAD_ANS = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
%s
</head>
""" % CSS

FOOT_ANS = """
<br />
<a href="/">
<div>Back to questions</div>
</a>
</body>
</html>
"""

# constant values, page contents (assigned before flask app instance is created)
GIFT_SCRIPT = [None]
GIFT_SCRIPT_CACHE = [None]
SHUFFLE_FUNC = [None]

app = Flask(__name__)


def _read_quiz_script():
    gift_script = GIFT_SCRIPT[0]
    if gift_script == '-':
        if GIFT_SCRIPT_CACHE[0] is not None:
            lines = GIFT_SCRIPT_CACHE[0]
        else:
            lines = GIFT_SCRIPT_CACHE[0] = sys.stdin.readlines()
    else:
        with open(gift_script, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    ast = gift_parse(lines, merge_empty_line=False)
    # print(ast)

    return ast


def _quiz():
    ast = _read_quiz_script()
    ast = html_escape_node_body_strs(ast)
    answer_table = build_quiz_answer(ast)
    html = build_form_content(ast, shuffle_func=SHUFFLE_FUNC[0], length_hint=answer_table)
    html = HEAD + html + FOOT
    return html

@app.route('/', methods=['GET'])
def quiz():
    return _quiz()


@app.route('/<foobar>', methods=['GET'])
def quiz_foobar(foobar):
    return _quiz()


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    # return '<br>'.join(request.form.keys())

    ast = _read_quiz_script()
    ast = html_escape_node_body_strs(ast)
    answer_table = build_quiz_answer(ast)

    quiz_keys = list(answer_table.keys())
    quiz_keys.sort()

    fc = parse_form_content(request.form)
    score_table = score_submission(fc, answer_table)

    buf = ['<table class="score">', '<tr><th>question</th><th>submitted</th><th>result</th></tr>']
    for k in quiz_keys:
        submitted = fc.get(k, '')
        score = score_table.get(k)
        buf.append('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (k, submitted, repr(score)))
    buf.append('</table>')

    return '\n'.join([HEAD_ANS] + buf + [FOOT_ANS])


def entrypoint(gift_script, shuffle, port=5000):
    GIFT_SCRIPT[0] = gift_script
    if not path.isfile(gift_script):
        sys.exit("file not found: %s" % repr(gift_script))

    if shuffle >= 0:
        random.seed(shuffle)
        shuffle_func = random.shuffle
    else:
        shuffle_func = lambda lst: None
    SHUFFLE_FUNC[0] = shuffle_func

    app.run(debug=True, port=port, use_reloader=False)
