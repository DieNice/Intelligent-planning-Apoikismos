import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from models.models import *


@eel.expose
def action_robot_load():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/posible_action_robot.html')
    getted_data = get_possible_actions_all()
    data = list()
    set_added = set()
    l_getted_data = len(getted_data)
    for i in range(l_getted_data):
        if getted_data[i][0] not in set_added:
            subdata = []
            subdata.append(getted_data[i])
            for j in range(i + 1, l_getted_data):
                if getted_data[j][0] == getted_data[i][0]:
                    subdata.append(getted_data[j])
            set_added.add(getted_data[i])
            data.append(subdata)

    rendered_page = template.render(action_list=data)

    with open('./static/temp/posible_action_robot.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def get_possible_actions_all():
    se1 = aliased(SimpleEntity)
    se2 = aliased(SimpleEntity)
    se3 = aliased(SimpleEntity)
    _se1 = aliased(SimpleEntity)
    _se2 = aliased(SimpleEntity)
    _se3 = aliased(SimpleEntity)
    query = session.query(PossibleAction, se1.name, se1.description, Precondition.count_material, se2.name,
                          se2.description, se3.name, se3.description,
                          _se1.name, _se1.description, Result.count_material,
                          _se2.name, _se2.description, _se3.name, _se3.description)
    query = query.join(se1, se1.id == Precondition.material_id)
    query = query.join(se2, se2.id == Precondition.instrument_id)
    query = query.join(se3, se3.id == Precondition.building_id)
    query = query.join(_se1, _se1.id == Result.material_id)
    query = query.join(_se2, _se2.id == Result.instrument_id)
    query = query.join(_se3, _se3.id == Result.building_id)
    query = query.order_by(PossibleAction.name)
    found_records = query.cte()
    records = session.query(found_records).all()
    return records
