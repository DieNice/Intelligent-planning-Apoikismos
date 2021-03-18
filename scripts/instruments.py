import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape


@eel.expose
def instrumentsload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/instruments.html')

    rendered_page = template.render()

    with open('static/instruments.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
