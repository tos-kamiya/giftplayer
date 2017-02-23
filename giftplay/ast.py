import re
import sys
from collections import namedtuple


Node = namedtuple('Node', ['mark', 'body'])  # mark is one of the followings
# '', '//', '::', '**', '{}', '{T}', '{~}', '{=}', '{%}', '{#}', '{->}', '=', '~', '#', '->', '%+', '%-'

# node marks
# {} essay
# {T} true/false
# {~} single choice
# {=} fill-in-the-blank
# {%} multiple choice
# {#} math
# {->} match


class GiftSyntaxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def gift_split(lines):
    for li, L in enumerate(lines):
        linenum = li + 1
        L = L.lstrip()
        if re.match(r'^//.*$', L):
            yield L, linenum  # comment line
        else:
            for t in re.split(r'((?<!\\)[(){}~=#])', L):
                t = re.sub(r'\\([(){}~=#])', r'\1', t)
                if t and not re.match(r'^\s+$', t):
                    yield t, linenum


def get_next(gift_split_it):
    try:
        return next(gift_split_it)
    except StopIteration:
        return None, None


def assert_token(cur, line, expected):
    if not (cur is not None and cur == expected):
        raise GiftSyntaxError("line %d: expected '%s', but appeared '%s'" % (line, expected, cur))


def gift_parse_i_choice(cur, ln, gift_it):
    if cur not in ('=', '~'):
        raise GiftSyntaxError("line %d: expected '=' or '~', but appeared '%s'" % (ln or 0, cur))
    node = Node(cur, [])
    cur, ln = get_next(gift_it)
    if cur in ('(', ')', '{', '}', '~', '=', '#'):
        raise GiftSyntaxError("line %d: unexpected token: %s" % (ln or 0, cur))
    node.body.append(cur)
    cur, ln = get_next(gift_it)
    return node, cur, ln


def gift_parse_i_feedback_text(cur, ln, gift_it):
    assert_token(cur, ln, '#')
    node = Node(cur, [])
    cur, ln = get_next(gift_it)
    if cur in ('(', ')', '{', '}', '~', '=', '#'):
        raise GiftSyntaxError("line %d: unexpected token: %s" % (ln or 0, cur))
    node.body.append(cur)
    cur, ln = get_next(gift_it)
    return node, cur, ln


def convert_to_matching_node(node):
    nn = Node('{->}', [])
    assert node.mark == '{~}'
    for cn in node.body:
        assert cn.mark == '='
        cnb0 = cn.body[0]
        i = cnb0.find('->')
        assert i >= 0
        ncn1 = Node('=', [cnb0[:i]])
        ncn2 = Node('->', [cnb0[i + len('->'):]])
        nn.body.extend([ncn1, ncn2])
    return nn


def convert_to_multiple_choice(node):
    pat = re.compile(r'^%-?\d+%')
    nn = Node('{%}', [])
    assert node.mark == '{~}'
    for cn in node.body:
        assert cn.mark == '~'
        cnb0 = cn.body[0]
        assert pat.match(cnb0)
        if cnb0.startswith('%-'):
            ncn = Node('%-', [pat.sub('', cnb0)])
        else:
            ncn = Node('%+', [pat.sub('', cnb0)])
        nn.body.append(ncn)
    return nn


def convert_to_fill_in_the_blank_node(node):
    nn = Node('{=}', node.body[:])
    return nn


def convert_node_if_needed(node):
    if node.mark == '{~}':
        cn_mark_set = set(cn.mark for cn in node.body)
        if cn_mark_set in ({'='}, {'=', '#'}):
            cn0 = node.body[0]
            if cn0.body[0].find('->') >= 0:
                node = convert_to_matching_node(node)
            else:
                node = convert_to_fill_in_the_blank_node(node)
        elif cn_mark_set in ({'~'}, {'~', '#'}):
            cn0 = node.body[0]
            if cn0.body[0].startswith('%'):
                node = convert_to_multiple_choice(node)
        else:
            assert cn_mark_set in ({'=', '~'}, {'=', '~', '#'})
    return node


def gift_parse_i_block(cur, ln, gift_it):
    assert_token(cur, ln, '{')
    cur, ln = get_next(gift_it)
    if cur == '}':
        node = Node('{}', [])
        cur, ln = get_next(gift_it)
        return node, cur, ln

    if cur in ('T', 'True', 'F', 'False'):
        if cur == 'T':
            cur = 'true'
        elif cur == 'F':
            cur = 'false'
        node = Node('{T}', [cur])
        cur, ln = get_next(gift_it)
        assert_token(cur, ln, '}')
        cur, ln = get_next(gift_it)
        return node, cur, ln

    if cur == '#':
        node = Node('{#}', [])
        cur, ln = get_next(gift_it)
        node.body.append(cur)
        cur, ln = get_next(gift_it)
        if cur != '}':
            raise GiftSyntaxError("line %d: 'multiple numeric answers' not implemented yet" % (ln or 0))
        cur, ln = get_next(gift_it)
        return node, cur, ln

    node = Node('{~}', [])  # tentative
    while cur is not None:
        if cur == '}':
            cur, ln = get_next(gift_it)
            node = convert_node_if_needed(node)
            return node, cur, ln
        elif cur == '=':
            cn, cur, ln = gift_parse_i_choice(cur, ln, gift_it)
            node.body.append(cn)
        elif cur == '~':
            cn, cur, ln = gift_parse_i_choice(cur, ln, gift_it)
            node.body.append(cn)
        elif cur == '#':
            cn, cur, ln = gift_parse_i_feedback_text(cur, ln, gift_it)
            node.body.append(cn)
        else:
            raise GiftSyntaxError("line %d: expected one of '}', '~', '=', '#', but appeared '%s'" % (ln or 0, cur))

    raise GiftSyntaxError("line %d: expected '}', but reached end of file" % ln)


def find_decorated_text(txt):
    buf = []
    while txt:
        m1 = re.match('.*(::).*(::).*', txt)
        m2 = re.match('.*([*][*]).*([*][*]).*', txt)
        m = m1
        if m1 is None:
            m = m2
        elif m2 and m1.start(1) > m2.start(1):
            m = m2
        if not m:
            buf.append(txt)
            txt = ''
        else:
            s1 = txt[:m.start(1)]
            b = txt[m.end(1):m.start(2)]
            txt = txt[m.end(2):]
            buf.extend([s1, Node(m.group(1), [b])])
    return buf


def gift_parse(lines):
    node = Node('', [])
    gift_it = gift_split(lines)
    cur, ln = get_next(gift_it)
    while cur is not None:
        if cur == '{':
            cn, cur, ln = gift_parse_i_block(cur, ln, gift_it)
            node.body.append(cn)
        elif cur.startswith('//'):
            cn = Node('//', [cur])
            node.body.append(cn)
            cur, ln = get_next(gift_it)
        else:
            if node.body and isinstance(node.body[-1], str):
                cur = node.body[-1] + cur
                del node.body[-1]
            b = find_decorated_text(cur)
            node.body.extend(b)
            cur, ln = get_next(gift_it)
    return node


def gift_split_by_title(ast):
    assert isinstance(ast, Node)
    bodies = [[]]
    for item in ast.body:
        if isinstance(item, Node) and item.mark == '::':
            bodies.append([])
        bodies[-1].append(item)
    bodies = [item for item in bodies if len(item) > 0]

    root_nodes = []
    for body in bodies:
        root_nodes.append(Node('', body))

    return root_nodes


def main(argv):
    lines = None
    args = argv[1:]
    if args:
        gift_script = args[0]
        with open(gift_script, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    if not lines:
        lines = """
What two people are entombed in Grant's tomb? {
   ~%-100%No one
   ~%50%Grant
   ~%50%Grant's wife
   ~%-100%Grant's father
} oh.""".split('\n')
        # lines = ['// matching', '::Q4:: Which animal eats which food? {', '  =cat -> cat food', '  =dog -> dog food', '}']

    # print(lines)

    # for token, linenum in gift_split(lines):
    #     print("%d: %s" % (linenum, token))

    node = gift_parse(lines)
    print(node)


if __name__ == '__main__':
    main(sys.argv)
