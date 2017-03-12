import re
import unicodedata


from .gift_ast import Node


def str_normalize(s):
    if s is None:
        return None
    return unicodedata.normalize('NFKC', s.strip())


def gift_build_quiz_answer_i_quiz_node(node, quiz_num):
    if node.mark == '{~}':
        r = Node(node.mark, [])
        for cn in node.body:
            if cn.mark == '=':
                r.body.append(str_normalize(cn.body[0]))
        return r
    elif node.mark == '{%}':
        r = Node(node.mark, [])
        for cn in node.body:
            if cn.mark == '%+':
                r.body.append(str_normalize(cn.body[0]))
        return r
    elif node.mark == '{}':
        r = Node(node.mark, [])
        return r
    elif node.mark == '{=}':
        r = Node(node.mark, [])
        for cn in node.body:
            if cn.mark == '=':
                r.body.append(str_normalize(cn.body[0]))
        return r
    elif node.mark == '{#}':
        assert len(node.body) == 1 and isinstance(node.body[0], str)
        r = Node(node.mark, [str_normalize(node.body[0])])
        return r
    elif node.mark == '{T}':
        assert len(node.body) == 1 and node.body[0] in ('true', 'false')
        r = Node(node.mark, [node.body[0]])
        return r
    elif node.mark == '{->}':
        r = Node(node.mark, [])
        for cn in node.body:
            if cn.mark == '=':
                r.body.append((str_normalize(cn.body[0]), None))
            elif cn.mark == '->':
                assert r.body and r.body[-1][1] is None
                r.body[-1] = (r.body[-1][0], str_normalize(cn.body[0]))
        return r
    else:
        assert False


def build_quiz_answer(ast):
    qa = {}
    quiz_num = 0
    assert isinstance(ast, Node)
    for cn in ast.body:
        if isinstance(cn, str):
            pass
        elif cn.mark.startswith('{'):
            quiz_num += 1
            qa[quiz_num] = gift_build_quiz_answer_i_quiz_node(cn, quiz_num)
    return qa


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
            lst[idx] = (str_normalize(form_content.get(k)), str_normalize(item[1]))
        elif m.re is pat_match_right:
            key = int(m.group(1))
            lst = answer_tbl.setdefault(key, [])
            idx = int(m.group(2)) - 1
            assert 0 <= idx < 999
            extend_if_needed(lst, idx)
            item = lst[idx]
            lst[idx] = (str_normalize(item[0]), str_normalize(form_content.get(k)))
        elif m.re is pat_multiple_choice:
            key = int(m.group(1))
            lst = answer_tbl.setdefault(key, [])
            lst.append(str_normalize(form_content.get(k)))
        elif m.re is pat_quiz:
            key = int(m.group(1))
            answer_tbl[key] = str_normalize(form_content.get(k))
    return answer_tbl


def score_submission(submission, answer_table):
    pat_math_ans_wo_error = re.compile(r'^(\d+([.]\d+)?)$')
    pat_math_ans_with_error = re.compile(r'^(\d+([.]\d+)?):(\d+([.]\d+)?)$')
    pat_math_ans_range = re.compile(r'^(\d+([.]\d+)?)[.][.](\d+([.]\d+)?)$')
    score_table = {}
    for k, an in sorted(answer_table.items()):
        s = submission.get(k)
        if not s:
            score_table[k] = None
        else:
            if an.mark == '{}':
                score_table[k] = 'filled'
            elif an.mark in ('{T}', '{~}'):
                score_table[k] = s == an.body[0]
            elif an.mark == '{=}':
                score_table[k] = any(s == correct_str for correct_str in an.body)
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
