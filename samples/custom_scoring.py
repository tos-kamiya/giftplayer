#!/usr/bin/env python3

from flask import Flask, request

from giftplayer.html import DEFAULT_SEND_BUTTON, DEFAULT_CSS, JQUERY_LOCAL_JS
from giftplayer import gift_parse, build_form_content, html_escape_node_body_strs


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
Name: {}

Are you human? {=Yes ~No}
""".split('\n')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def quiz():
    quiz_ast = gift_parse(QUIZ_LINES)
    ast = html_escape_node_body_strs(quiz_ast)
    html = build_form_content(ast)
    return HEAD + """<form action="/submit_answer" method="post">""" + html + \
           """<br />%s</form>""" % DEFAULT_SEND_BUTTON + FOOT


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    ans1 = request.form.get("quiz1")
    ans2 = request.form.get("quiz2")
    if ans2 == "Yes":
        return HEAD + ("Hello, %s!<br />" % ans1) + "Welcome to the site." + FOOT
    else:
        return HEAD + "No BOTS allowed.<br />" + FOOT


app.run(debug=True)
