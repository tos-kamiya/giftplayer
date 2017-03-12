#!/usr/bin/env python3

from flask import Flask, request

from giftplayer.html import *
from giftplayer import *


HEAD = """
<!DOCTYPE html><html>
<head><meta charset="utf-8">%s%s</head>
""" % (DEFAULT_CSS, JQUERY_LOCAL_JS)

FOOT = """
</body>
</html>
"""

QUIZ_LINES = ["2 x 3 = {=6}.", "", "Does Rock win Scissors? {T}"]
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

    buf = []
    quiz_num = 0
    for k in sorted(ANSWER_TABLE.keys()):
        quiz_num += 1
        buf.append("Quiz %d: %s" % (quiz_num, ("OK" if score_table.get(k) else "NG")))

    return HEAD + '<br />'.join(buf) + FOOT


app.run(debug=True)
