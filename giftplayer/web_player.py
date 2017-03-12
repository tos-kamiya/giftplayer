import os.path as path
import random
import re
import sys

from flask import Flask, request

from .gift_ast import gift_parse
from .html_form_builder import html_escape_node_body_strs, build_form_content
from .answer_scorer import build_quiz_answer, parse_form_content, score_submission


SCRIPTDIR = path.dirname(path.realpath(__file__))
SAMPLE_GIFT_FILE = "sample.gift"

with open(path.join(SCRIPTDIR, "sample.gift"), 'r', encoding='utf-8') as _f:
    SAMPLE_GIFT_SCRIPT = _f.read()

CSS = """
<style type="text/css">
* {
  font-family: sans-serif;
}
button.submit {
  padding: 5px 20px;
  background-color: #248;
  color: #fff;
  border-style: none;
}
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

with open(path.join(SCRIPTDIR, "jquery-3.1.1.min.js"), 'r') as _f:
    JS = """
<script>""" + _f.read() + """
</script>
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
""" % (CSS, JS)

FOOT = """
<br />
<br />
<button class="submit" type=submit">Send</button>
</form>
</body>
</html>
"""

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


@app.route('/', methods=['GET'])
def quiz():
    ast = _read_quiz_script()
    ast = html_escape_node_body_strs(ast)
    answer_table = build_quiz_answer(ast)
    html = build_form_content(ast, shuffle_func=SHUFFLE_FUNC[0], length_hint=answer_table)
    html = HEAD + html + FOOT
    return html


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
    if not gift_script:
        sys.stderr.write("> No gift_script is given. Use %s.\n" % SAMPLE_GIFT_FILE)
        gift_script = path.join(SCRIPTDIR, SAMPLE_GIFT_FILE)
    GIFT_SCRIPT[0] = gift_script

    if shuffle >= 0:
        random.seed(shuffle)
        shuffle_func = random.shuffle
    else:
        shuffle_func = lambda lst: None
    SHUFFLE_FUNC[0] = shuffle_func

    app.run(debug=True, port=port, use_reloader=False)
