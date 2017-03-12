import random

from flask import Flask, request

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

app = Flask(__name__)


@app.route('/', methods=['GET'])
def quiz():
    quiz_ast = gift_parse(QUIZ_LINES)
    ast = html_escape_node_body_strs(quiz_ast)
    answer_table = build_quiz_answer(quiz_ast)
    html = build_form_content(ast, length_hint=answer_table)
    return HEAD + """<form action="/submit_answer" method="post">""" + html + \
           """<br /><button class="submit" type=submit">Send</button></form>""" + FOOT


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    quiz_ast = gift_parse(QUIZ_LINES)
    ast = html_escape_node_body_strs(quiz_ast)
    answer_table = build_quiz_answer(ast)

    fc = parse_form_content(request.form)
    score_table = score_submission(fc, answer_table)

    correct_count = 0
    miss_count = 0
    for k in answer_table.keys():
        if score_table.get(k):
            correct_count += 1
        else:
            miss_count += 1
    c = correct_count + miss_count
    s = correct_count * 1.0 / c
    return HEAD + """Result: %dpts (%d out of %d).""" % (int(s * 100), correct_count, c) + FOOT


app.run(debug=True)
