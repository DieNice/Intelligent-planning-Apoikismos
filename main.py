import eel
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
# from scripts.materials import materialsload


@eel.expose
def materialsload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/materials.html')

    rendered_page = template.render()

    with open('static/materials.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    eel.init('static', allowed_extensions=['.js', '.html'])
    eel.start('index.html', jinja_templates='templates', port=8080)
