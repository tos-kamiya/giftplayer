import os
import os.path as path
import random
import sys
from urllib.parse import unquote
import urllib.parse

from flask import Flask, request, redirect, url_for, abort

from .html import DEFAULT_SEND_BUTTON, DEFAULT_CSS, JQUERY_LOCAL_JS
from .gift_ast import gift_parse
from .html_form_builder import html_escape_node_body_strs, build_form_content
from .answer_scorer import build_quiz_answer, parse_form_content, score_submission


def quote(s):
    return urllib.parse.quote(s, safe='')


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
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Cache-Control" content="no-cache">
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
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Cache-Control" content="no-cache">
%s
</head>
""" % CSS

FOOT_ANS = FOOT_QUIZ

HEAD_DIR = HEAD_ANS
FOOT_DIR = FOOT_ANS


class GiftScriptInfo:
    def __init__(self):
        self.stdin_cache = None
        self.script_file = None
        self.dir = None


# constant values, page contents (assigned before flask app instance is created)
GIFT_SCRIPT_INFO = GiftScriptInfo()
SHUFFLE_FUNC = [None]

app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    if GIFT_SCRIPT_INFO.stdin_cache:
        return redirect("/-")
    elif GIFT_SCRIPT_INFO.script_file:
        fbody = path.split(GIFT_SCRIPT_INFO.script_file)[1]
        return redirect("/" + quote(fbody))
    elif GIFT_SCRIPT_INFO.dir:
        scripts = [f for f in os.listdir(GIFT_SCRIPT_INFO.dir) if f.endswith('.gift')]
        scripts.sort()
        buf = [HEAD_DIR]
        buf.append("<b>directory: %s</b><br />" % quote(GIFT_SCRIPT_INFO.dir))
        buf.append("<table>")
        c = 0
        items_in_row = 5
        for s in scripts:
            if c % items_in_row == 0:
                buf.append("<tr>")
            buf.append("<td><a href=%s>%s</a></td>" % (quote(s), s))
            c += 1
            if c % items_in_row == 0:
                buf.append("</tr>")
        if c % items_in_row != 0:
            buf.append("</tr>")
        buf.append("</table>")
        buf.append(FOOT_DIR)
        return '\n'.join(buf)
    else:
        assert False


def _read_quiz_script(giftscript_unquoted, cache=None):
    if cache:
        lines = cache
    else:
        with open(giftscript_unquoted, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    ast = gift_parse(lines, merge_empty_line=False)
    # print(ast)
    return ast


def _quiz(giftscript_unquoted, cache=None):
    ast = _read_quiz_script(giftscript_unquoted, cache=cache)
    ast = html_escape_node_body_strs(ast)
    answer_table = build_quiz_answer(ast)
    html = build_form_content(ast, shuffle_func=SHUFFLE_FUNC[0], length_hint=answer_table)
    html = FORM_HEAD % quote(giftscript_unquoted) + html + FORM_FOOT
    html = HEAD_QUIZ + html + FOOT_QUIZ
    return html


@app.route('/<giftscript>', methods=['GET'])
def quiz(giftscript):
    if GIFT_SCRIPT_INFO.stdin_cache:
        if giftscript == '-':
            return _quiz(giftscript, cache=GIFT_SCRIPT_INFO.stdin_cache)
    elif GIFT_SCRIPT_INFO.script_file:
        fbody = path.split(GIFT_SCRIPT_INFO.script_file)[1]
        if giftscript == quote(fbody):
            return _quiz(GIFT_SCRIPT_INFO.script_file)
    elif GIFT_SCRIPT_INFO.dir:
        giftscript_unquoted = unquote(giftscript)
        scripts = [f for f in os.listdir(GIFT_SCRIPT_INFO.dir) if f.endswith('.gift')]
        scripts.sort()
        if giftscript_unquoted in scripts:
            return _quiz(path.join(GIFT_SCRIPT_INFO.dir, giftscript_unquoted))
    abort(404)


def _answer_table(giftscript_unquoted, cache=None):
    ast = _read_quiz_script(giftscript_unquoted, cache=cache)
    ast = html_escape_node_body_strs(ast)
    answer_table = build_quiz_answer(ast)
    return answer_table


@app.route('/<giftscript>/submit_answer', methods=['POST'])
def submit_answer(giftscript):
    answer_table = None
    if GIFT_SCRIPT_INFO.stdin_cache:
        if giftscript == '-':
            answer_table = _answer_table(giftscript, cache=GIFT_SCRIPT_INFO.stdin_cache)
    elif GIFT_SCRIPT_INFO.script_file:
        fbody = path.split(GIFT_SCRIPT_INFO.script_file)[1]
        if giftscript == quote(fbody):
            answer_table = _answer_table(GIFT_SCRIPT_INFO.script_file)
    elif GIFT_SCRIPT_INFO.dir:
        giftscript_unquoted = unquote(giftscript)
        scripts = [f for f in os.listdir(GIFT_SCRIPT_INFO.dir) if f.endswith('.gift')]
        scripts.sort()
        if giftscript_unquoted in scripts:
            answer_table = _answer_table(path.join(GIFT_SCRIPT_INFO.dir, giftscript_unquoted))
    if answer_table is None:
        abort(404)

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
    if gift_script == '-':
        GIFT_SCRIPT_INFO.stdin_cache = sys.stdin.readlines()
    elif path.isfile(gift_script):
        GIFT_SCRIPT_INFO.script_file = gift_script
    elif path.isdir(gift_script):
        GIFT_SCRIPT_INFO.dir = gift_script
        scripts = [f for f in os.listdir(gift_script) if f.endswith('.gift')]
        scripts.sort()
        if not scripts:
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
