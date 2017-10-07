import os
import os.path as path
import random
import sys
from urllib.parse import quote, unquote

from flask import Flask, request, redirect, url_for, abort

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

HEAD_QUIZ = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
%s
%s
</head>
<body>
""" % (CSS, JQUERY_LOCAL_JS)

FOOT_QUIZ = """
</body>
</html>
"""

FORM_HEAD = """
<form action="/%s/submit_answer" method="post">
"""

FORM_FOOT = """
<br />
<br />
%s
</form>
""" % DEFAULT_SEND_BUTTON

HEAD_ANS = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
%s
</head>
""" % CSS

FOOT_ANS = FOOT_QUIZ

HEAD_DIR = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
%s
</head>
<body>
""" % CSS

FOOT_DIR = FOOT_QUIZ


# constant values, page contents (assigned before flask app instance is created)
GIFT_SCRIPT_DIR = [None]
GIFT_SCRIPTS = []
STDIN_CACHE = [None]
SHUFFLE_FUNC = [None]

app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    if len(GIFT_SCRIPTS) == 1:
        return redirect("/" + quote(GIFT_SCRIPTS[0]))

    buf = [HEAD_DIR]
    for s in GIFT_SCRIPTS:
        buf.append("<a href=%s>%s</a><br />" % (quote(s), s))
    buf.append(FOOT_DIR)
    return ''.join(buf)


def _read_quiz_script(giftscript_unquoted):
    gift_script_path = path.join(GIFT_SCRIPT_DIR[0], giftscript_unquoted)
    if gift_script_path == '-':
        if STDIN_CACHE[0] is not None:
            lines = STDIN_CACHE[0]
        else:
            lines = STDIN_CACHE[0] = sys.stdin.readlines()
    else:
        with open(gift_script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    ast = gift_parse(lines, merge_empty_line=False)
    # print(ast)

    return ast


def _quiz(giftscript_unquoted):
    ast = _read_quiz_script(giftscript_unquoted)
    ast = html_escape_node_body_strs(ast)
    answer_table = build_quiz_answer(ast)
    html = build_form_content(ast, shuffle_func=SHUFFLE_FUNC[0], length_hint=answer_table)
    html = FORM_HEAD % quote(giftscript_unquoted) + html + FORM_FOOT
    html = HEAD_QUIZ + html + FOOT_QUIZ
    return html


@app.route('/<giftscript>', methods=['GET'])
def quiz(giftscript):
    giftscript_unquoted = unquote(giftscript)
    if giftscript_unquoted not in GIFT_SCRIPTS:
        abort(404)
    return _quiz(giftscript_unquoted)


@app.route('/<giftscript>/submit_answer', methods=['POST'])
def submit_answer(giftscript):
    giftscript_unquoted = unquote(giftscript)
    ast = _read_quiz_script(giftscript_unquoted)
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
    if path.isfile(gift_script):
        GIFT_SCRIPT_DIR[0] = path.split(gift_script)[0]
        GIFT_SCRIPTS.append(gift_script)
    elif path.isdir(gift_script):
        GIFT_SCRIPT_DIR[0] = gift_script
        GIFT_SCRIPTS.extend(f for f in os.listdir(gift_script) if f.endswith('.gift'))
        if len(GIFT_SCRIPTS) == 0:
            sys.exit("error: no .gift file found in directory: %s" % repr(gift_script))
    else:
        sys.exit("error: no such file/directory found: %s" % repr(gift_script))

    if shuffle >= 0:
        random.seed(shuffle)
        shuffle_func = random.shuffle
    else:
        shuffle_func = lambda lst: None
    SHUFFLE_FUNC[0] = shuffle_func

    app.run(debug=True, port=port, use_reloader=False)
