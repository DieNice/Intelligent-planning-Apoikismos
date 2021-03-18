import eel
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
from scripts.materials import materialsload


if __name__ == '__main__':
    eel.init('static', allowed_extensions=['.js', '.html'])
    eel.start('index.html', jinja_templates='templates', port=8080)
