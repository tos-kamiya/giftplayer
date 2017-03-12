import os.path as path

SCRIPTDIR = path.dirname(path.realpath(__file__))

DEFAULT_CSS = """
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
"""[1:-1]

DEFAULT_SEND_BUTTON = """
<button class="submit" type=submit">Send</button>
"""[1:-1]

with open(path.join(SCRIPTDIR, "jquery-3.1.1.min.js"), 'r') as _f:
    JQUERY_LOCAL_JS = """<script>""" + _f.read() + """</script>"""

JQUERY_CDN_JS = """<script src="http://code.jquery.com/jquery-3.1.1.min.js"></script>"""


