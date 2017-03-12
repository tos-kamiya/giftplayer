#!/usr/bin/env python3

from flask import Flask, request

from giftplayer.html import DEFAULT_SEND_BUTTON, DEFAULT_CSS, JQUERY_LOCAL_JS
from giftplayer import Node, build_html_with_answer_render
from giftplayer import gift_parse, build_form_content, html_escape_node_body_strs
from giftplayer import build_quiz_answer, parse_form_content, score_submission


HEAD = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
%s
%s
</head>
<body>
""" % (DEFAULT_CSS, JQUERY_LOCAL_JS)

FOOT = """
</body>
</html>
"""

QUIZ_LINES = """
2 x 0 = {=0}.
2 x 1 = {=2}.
2 x 2 = {=4}.
2 x 3 = {=6}.
2 x 4 = {=8}.
2 x 5 = {=10}.
2 x 6 = {=12}.
2 x 7 = {=14}.
2 x 8 = {=16}.
2 x 9 = {=18}.
"""[1:-1].split('\n')
QUIZ_LINES = '\n'.join(QUIZ_LINES).replace('\n', '\n\n').split('\n')

QUIZ_AST = html_escape_node_body_strs(gift_parse(QUIZ_LINES))
ANSWER_TABLE = build_quiz_answer(QUIZ_AST)

app = Flask(__name__)


@app.route('/', methods=['GET'])
def quiz():
    html = build_form_content(QUIZ_AST, length_hint=ANSWER_TABLE)
    return HEAD + """<form action="/submit_answer" method="post">%s<br />%s</form>""" % \
            (html, DEFAULT_SEND_BUTTON) + FOOT


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    fc = parse_form_content(request.form)
    score_table = score_submission(fc, ANSWER_TABLE)

    oks = [k for k in sorted(ANSWER_TABLE.keys()) if score_table.get(k)]
    points = len(oks) * 100 / len(ANSWER_TABLE)

    buf = []
    buf.append('Overall result:')
    buf.append('<span style="font-weight: bold;">%d points</span> (%d out of %d).' % \
            (points, len(oks), len(ANSWER_TABLE)))
    buf.append('')

    NGSTR = ' <span style="color: red; font-weight: bold;">-&gt;WRONG</span>'
    OKSTR = ' -&gt;OK'
    def render_func(quiz_num):
        v = fc.get(quiz_num, "*")
        return v + (OKSTR if quiz_num in oks else NGSTR)
    buf.append("Result for each quiz:")
    buf.append(build_html_with_answer_render(QUIZ_AST, render_func))

    return HEAD + '<br />'.join(buf) + FOOT


app.run(debug=True)
