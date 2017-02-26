import html
import os.path as path
import sys
import random

from .ast import gift_parse, Node, GiftSyntaxError
from .html_form_answer import gift_build_quiz_answer


SCRIPTDIR = path.dirname(path.realpath(__file__))
SAMPLE_GIFT_FILE = "sample.gift"

CSS = """
<style type="text/css">
* {
  font-family: sans-serif;
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
<form>
""" % (CSS, JS)

FOOT = """
</form>
</body>
</html>
"""

with open(path.join(SCRIPTDIR, "match_question.js"), 'r') as _f:
    SELECT_JS_TEMPLATE = "<script>\n" + _f.read() + "</script>\n"


def select_js(quiz_num):
    return SELECT_JS_TEMPLATE.format(quiz_num=quiz_num)


def gift_build_html_i_quiz_node(node, quiz_num, shuffle_func=None, length_hint=None):
    if shuffle_func is None:
        shuffle_func = lambda lst: None
    buf = []
    if node.mark == '{~}':
        buf.append('<select name="quiz%d">' % quiz_num)
        choices = []
        for cn in node.body:
            if cn.mark in ('=', '~'):
                choices.append(cn.body[0])
            elif cn.mark == '#':
                pass
            else:
                raise GiftSyntaxError("invalid node mark: %s" % cn.mark)
        shuffle_func(choices)
        buf.append('<option value="">- select one -</option>')
        for c in choices:
            buf.append('<option value="%s">' % c)
            buf.append(c)
            buf.append('</option>')
        buf.append('</select>')
    elif node.mark == '{%}':
        buf.append('<span style="border: 1px solid #888">')
        choices = []
        for cn in node.body:
            if cn.mark in ('%+', '%-'):
                choices.append(cn.body[0])
            else:
                raise GiftSyntaxError("invalid node mark: %s" % cn.mark)
        shuffle_func(choices)
        for ci, c in enumerate(choices):
            buf.append('<label><input type="checkbox" name="quiz%d_check%d" value="%s"/>' % (quiz_num, ci + 1, c))
            buf.append(c)
            buf.append('</label>')
        buf.append('</span>')
    elif node.mark == '{}':
        buf.append('<br /><textarea name="quiz%d" cols="40" rows="5"></textarea>' % quiz_num)
    elif node.mark in ('{=}', '{#}'):
        if length_hint:
            expected_length = int((len(length_hint.body[0]) + 1) * 1.5)
        else:
            expected_length = 20
        buf.append('<input name="quiz%d" type="text" size="%d" />' % (quiz_num, expected_length))
    elif node.mark == '{T}':
        buf.append('<select name="quiz%d">' % quiz_num)
        buf.append('<option value="">- select one -</option>')
        buf.append('<option value="false">False</option>')
        buf.append('<option value="true">True</option>')
        buf.append('</select>')
    elif node.mark == '{->}':
        left_choices = []
        right_choices = []
        for cn in node.body:
            if cn.mark == '=':
                left_choices.append(cn.body[0])
            elif cn.mark == '->':
                right_choices.append(cn.body[0])
        assert len(left_choices) == len(right_choices)
        shuffle_func(left_choices)
        shuffle_func(right_choices)
        buf.append('<br />')
        for lci, lc in enumerate(left_choices):
            buf.append('<input type="hidden" name="quiz%d_left%d" value="%s" />' % (quiz_num, lci + 1, lc))
        for lci, lc in enumerate(left_choices):
            buf.append(lc)
            buf.append('<select name="quiz%d_right%d" class="match%d">' % (quiz_num, lci + 1, quiz_num))
            buf.append('<option value="">- select one -</option>')
            for rci, rc in enumerate(right_choices):
                buf.append('<option value="%s">%s</option>' % (rc, rc))
            buf.append('</select>')
            buf.append('<br />')
        buf.append('<div class="match%d" style="color:red;"></div>' % quiz_num)
        buf.append(select_js(quiz_num))
    else:
        assert False
    return buf


def gift_build_form_content(ast, shuffle_func=None, length_hint=None):
    buf = []
    quiz_num = 0
    assert isinstance(ast, Node)
    for cn in ast.body:
        if isinstance(cn, str):
            buf.append(cn)
        elif cn.mark == '**':
            buf.append('<b>' + cn.body[0] + '</b>')
        elif cn.mark == '::':
            buf.append('<h2>' + cn.body[0] + '</h2>')
        elif cn.mark.startswith('{'):
            quiz_num += 1
            lh = length_hint.get(quiz_num) if length_hint else None
            buf.extend(gift_build_html_i_quiz_node(cn, quiz_num, shuffle_func=shuffle_func, length_hint=lh))
        else:
            raise GiftSyntaxError("invalid node mark: %s" % cn.mark)
    return '\n'.join(buf)


def html_escape_node_body_strs(node):
    if isinstance(node, Node):
        assert isinstance(node.body, list)
        n = Node(node.mark, [])
        for cn in node.body:
            n.body.append(html_escape_node_body_strs(cn))
        return n
    elif isinstance(node, str):
        s = node.strip()
        if s == '':
            return '<br />'
        return html.escape(s)
    else:
        assert False


def entrypoint(gift_script, answer, shuffle, debug_wo_hint):
    if shuffle >= 0:
        random.seed(shuffle)
        shuffle_func = random.shuffle
    else:
        shuffle_func = lambda lst: None
    if not gift_script:
        sys.stderr.write("> No gift_script is given. Use %s.\n" % SAMPLE_GIFT_FILE)
        gift_script = path.join(SCRIPTDIR, SAMPLE_GIFT_FILE)

    if gift_script == '-':
        lines = sys.stdin.readlines()
    else:
        with open(gift_script, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    # for token, linenum in gift_split(lines):
    #     print("%d: %s" % (linenum, token))

    ast = gift_parse(lines, merge_empty_line=False)
    ast = html_escape_node_body_strs(ast)
    # print(ast)

    if answer:
        answer = gift_build_quiz_answer(ast)
        print(answer)
    else:
        if debug_wo_hint:
            html = gift_build_form_content(ast, shuffle_func)
        else:
            answer_table = gift_build_quiz_answer(ast)
            html = gift_build_form_content(ast, shuffle_func, length_hint=answer_table)
        html = HEAD + html + FOOT
        print(html)
