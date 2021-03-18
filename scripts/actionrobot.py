import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape


@eel.expose
def actionrobotload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/posible_action_robot.html')

    rendered_page = template.render()

    with open('static/posible_action_robot.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
