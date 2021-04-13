import eel
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.models import *

from scripts.simple_actions import *
from scripts.action_robot import *
from scripts.integrity_check import *
from scripts.resolver import *

if __name__ == '__main__':
    eel.init('static', allowed_extensions=['.js', '.html'])
    eel.start('index.html', jinja_templates='templates', port=8080)
