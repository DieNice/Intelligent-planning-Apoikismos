import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape


@eel.expose
def buildingsload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/buildings.html')

    rendered_page = template.render()

    with open('static/buildings.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)