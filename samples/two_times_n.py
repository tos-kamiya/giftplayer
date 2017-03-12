#!/usr/bin/env python3

import random

from flask import Flask, request

from giftplayer import Node, build_html_with_answer_render
from giftplayer import gift_parse, build_form_content, html_escape_node_body_strs
from giftplayer import build_quiz_answer, parse_form_content, score_submission


HEAD = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="http://code.jquery.com/jquery-3.1.1.min.js"></script>
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
</style>
</head>
"""

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
random.shuffle(QUIZ_LINES)
QUIZ_LINES = '\n'.join(QUIZ_LINES).replace('\n', '\n\n').split('\n')

QUIZ_AST = html_escape_node_body_strs(gift_parse(QUIZ_LINES))
ANSWER_TABLE = build_quiz_answer(QUIZ_AST)

app = Flask(__name__)


@app.route('/', methods=['GET'])
def quiz():
    html = build_form_content(QUIZ_AST, length_hint=ANSWER_TABLE)
    return HEAD + """<form action="/submit_answer" method="post">""" + html + \
           """<br /><button class="submit" type=submit">Send</button></form>""" + FOOT


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    fc = parse_form_content(request.form)
    score_table = score_submission(fc, ANSWER_TABLE)

    oks = [k for k in ANSWER_TABLE.keys() if score_table.get(k)]
    points = len(oks) * 100 / len(ANSWER_TABLE)

    buf = []
    buf.append('Overall result:')
    buf.append('<span style="font-weight: bold;">%d points</span> (%d out of %d).' % (points, len(oks), len(ANSWER_TABLE)))
    buf.append('')

    ngstr = ' <span style="color: red; font-weight: bold;">-&gt;WRONG</span>'
    okstr = ' -&gt;OK'
    def render_func(quiz_num):
        v = fc.get(quiz_num, "*")
        return v + (okstr if quiz_num in oks else ngstr)
    buf.append("Result for each quiz:")
    buf.append(build_html_with_answer_render(QUIZ_AST, render_func))

    return '<br />'.join(buf)


app.run(debug=True)
