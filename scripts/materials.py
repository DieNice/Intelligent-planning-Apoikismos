import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape


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