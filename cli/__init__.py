from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from pygments.token import Token

global_styles = Style.from_dict({
    'error': 'bg:ansired',
    'chat': 'bg:ansiblue fg:ansiwhite',
    'info': 'bg:ansiyellow fg:ansiblack'})
def printf(content):
    print_formatted_text(HTML(content), style=global_styles)