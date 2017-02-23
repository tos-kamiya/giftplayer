import sys

import gift.gift_html_form
import gift.gift_web

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""usage: python3 -m gift [html|web] ...""")
        sys.exit(0)

    cmd = sys.argv[1]
    del sys.argv[1]
    if cmd == 'html':
        gift.gift_html_form.main()
    elif cmd == 'web':
        gift.gift_web.main()
    else:
        sys.exit('error: invalid command')


