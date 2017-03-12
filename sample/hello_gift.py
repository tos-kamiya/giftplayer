from flask import Flask, request


from giftplayer import gift_parse, gift_build_form_content, html_escape_node_body_strs


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
Name: {}

Are you human? {=Yes ~No}
""".split('\n')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def quiz():
    quiz_ast = gift_parse(QUIZ_LINES)
    ast = html_escape_node_body_strs(quiz_ast)
    html = gift_build_form_content(ast)
    return HEAD + """<form action="/submit_answer" method="post">""" + html + \
           """<br /><button class="submit" type=submit">Send</button></form>""" + FOOT


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    ans1 = request.form.get("quiz1")
    ans2 = request.form.get("quiz2")
    if ans2 == "Yes":
        return HEAD + ("Hello, %s!<br />" % ans1) + "Welcome to the site." + FOOT
    else:
        return HEAD + "No BOTS allowed.<br />" + FOOT


app.run(debug=True)
