import unicodedata
from .ast import Node


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


def gift_build_quiz_answer(ast):
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
