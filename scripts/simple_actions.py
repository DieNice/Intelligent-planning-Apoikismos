import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.models import *

types = {
    'Materials': Material,
    'Instruments': Instrument,
    'Buildings': Building
}


@eel.expose
def object_load(title: str, header: str):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/simple_objects.html')
    data = [i.getstr() for i in get_all(types[title])]
    rendered_page = template.render(objects=data, titlename=title, headername=header)

    with open('./static/temp/simple_objects.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


@eel.expose
def create_object_load(title: str, header: str):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/create_object.html')
    rendered_page = template.render(titlename=title, headername=header)

    with open('./static/temp/create_object.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


@eel.expose
def create_object(type: str, name: str, desc: str) -> None:
    new_material = types[type](name, desc)
    session.add(new_material)
    session.commit()


def get_all(type: SimpleEntity):
    return session.query(type).all()


@eel.expose
def delete_object(type: str, name: str, desc: str):
    name = name.strip()
    name = name.replace('\n', '')
    desc = desc.strip()
    desc = desc.replace('\n', '')
    obj = session.query(types[type]).filter_by(name=name, description=desc).one()
    session.delete(obj)


@eel.expose
def save_changes():
    session.commit()
