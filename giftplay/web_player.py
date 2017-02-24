import os.path as path
import random
import re

from flask import Flask, request

from .ast import gift_parse
from .html_form import html_escape_node_body_strs, gift_build_form_content
from .html_form_answer import gift_build_quiz_answer

SCRIPTDIR = path.dirname(path.realpath(__file__))

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
<html lang="ja">
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
<html lang="ja">
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
QUIZ_PAGE_HTML = []
ANSWER_TABLE = []


app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return QUIZ_PAGE_HTML[0]


def parse_form_content(form_content):
    def extend_if_needed(lst, idx):
        while idx >= len(lst):
            lst.append(('', ''))

    pat_quiz = re.compile(r'quiz(\d+)')
    pat_match_left = re.compile(r'quiz(\d+)_left(\d+)')
    pat_match_right = re.compile(r'quiz(\d+)_right(\d+)')
    pat_multiple_choice = re.compile(r'quiz(\d+)_check(\d+)')
    answer_tbl = {}  # 'quiz%d' -> str or [(left, right)] or [str]
    keys = form_content.keys()
    for k in keys:
        m = pat_match_left.match(k) or pat_match_right.match(k) or \
                pat_multiple_choice.match(k) or pat_quiz.match(k)
        if m.re is pat_match_left:
            key = int(m.group(1))
            lst = answer_tbl.setdefault(key, [])
            idx = int(m.group(2)) - 1
            assert 0 <= idx < 999
            extend_if_needed(lst, idx)
            item = lst[idx]
            lst[idx] = (form_content.get(k), item[1])
        elif m.re is pat_match_right:
            key = int(m.group(1))
            lst = answer_tbl.setdefault(key, [])
            idx = int(m.group(2)) - 1
            assert 0 <= idx < 999
            extend_if_needed(lst, idx)
            item = lst[idx]
            lst[idx] = (item[0], form_content.get(k))
        elif m.re is pat_multiple_choice:
            key = int(m.group(1))
            lst = answer_tbl.setdefault(key, [])
            lst.append(form_content.get(k))
        elif m.re is pat_quiz:
            key = int(m.group(1))
            answer_tbl[key] = form_content.get(k)
    return answer_tbl


def score_submission(submission, anwser_table):
    pat_math_ans_wo_error = re.compile(r'^(\d+([.]\d+)?)$')
    pat_math_ans_with_error = re.compile(r'^(\d+([.]\d+)?):(\d+([.]\d+)?)$')
    pat_math_ans_range = re.compile(r'^(\d+([.]\d+)?)..(\d+([.]\d+)?)$')
    score_table = {}
    for k, an in sorted(anwser_table.items()):
        s = submission.get(k)
        if not s:
            score_table[k] = None
        else:
            if an.mark == '{}':
                score_table[k] = 'filled'
            elif an.mark in ('{T}', '{~}'):
                score_table[k] = s == an.body[0]
            elif an.mark == '{=}':
                s = s.strip()
                score_table[k] = any(s == correct_str.strip() for correct_str in an.body)
            elif an.mark == '{%}':
                score_table[k] = set(s) == set(an.body)
            elif an.mark == '{->}':
                score_table[k] = set(s) == set(an.body)
            elif an.mark == '{#}':
                try:
                    submitted_value = float(s)
                    correct_str = an.body[0]
                    m = pat_math_ans_range.match(correct_str) or pat_math_ans_wo_error.match(correct_str) or \
                            pat_math_ans_with_error.match(correct_str)
                    if m.re is pat_math_ans_range:
                        range_min, range_max = float(m.group(1)), float(m.group(3))
                        score_table[k] = range_min <= submitted_value <= range_max
                    elif m.re is pat_math_ans_wo_error:
                        val = float(m.group(1))
                        score_table[k] = submitted_value == val
                    elif m.re is pat_math_ans_with_error:
                        val, err = float(m.group(1)), float(m.group(3))
                        score_table[k] = val - err <= submitted_value <= val + err
                    else:
                        assert False
                except ValueError:
                    score_table[k] = 'invalid as number'

    return score_table


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    # return '<br>'.join(request.form.keys())
    answer_table = ANSWER_TABLE[0]
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


def entrypoint(gift_script, shuffle):
    if shuffle >= 0:
        random.seed(shuffle)
        shuffle_func = random.shuffle
    else:
        shuffle_func = lambda lst: None

    lines = None
    if gift_script:
        with open(gift_script, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    if not lines:
        lines = SAMPLE_GIFT_SCRIPT.split('\n')

    # for token, linenum in gift_split(lines):
    #     print("%d: %s" % (linenum, token))

    ast = gift_parse(lines)
    ast = html_escape_node_body_strs(ast)
    # print(ast)

    html = gift_build_form_content(ast, shuffle_func)
    html = HEAD + html + FOOT
    QUIZ_PAGE_HTML.append(html)

    answer = gift_build_quiz_answer(ast)
    ANSWER_TABLE.append(answer)

    app.run(debug=True)
