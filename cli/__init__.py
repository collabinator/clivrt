from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style

global_styles = Style.from_dict({'error': 'bg:ansired'})
def printf(content):
    print_formatted_text(HTML(content), style=global_styles)