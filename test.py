from pygments import highlight
from pygments.style import Style
from pygments.token import Token
from pygments.lexers import Python3Lexer
from pygments.formatters import TerminalFormatter

from pygments.style import Style
from pygments.token import Token, Comment, Keyword, Name, String, \
     Error, Generic, Number, Operator


class YourStyle(Style):

    styles = {
        Token:                  '',
        Comment:                'italic #888',
        Keyword:                'bold #888',
        Name:                   '#f00',
        Name.Class:             'bold #0f0',
        Name.Function:          '#0f0',
        String:                 '#000'
    }

code = 'print("Hello World")'
result = highlight(code, Python3Lexer(), TerminalFormatter(bg='dark', colorscheme=None, linenos=True))
print(result)
