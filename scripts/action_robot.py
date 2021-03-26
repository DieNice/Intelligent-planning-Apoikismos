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
    m1 = aliased(Material)
    m2 = aliased(Material)
    i1 = aliased(Instrument)
    i2 = aliased(Instrument)
    b1 = aliased(Building)
    b2 = aliased(Building)

    query = session.query(PossibleAction, m1, MaterialPrecondition.count, i1, b1, m2, MaterialResult.count, i2, b2)
    query = query.join(MaterialPrecondition, MaterialPrecondition.action_id == PossibleAction.id)
    query = query.join(m1, m1.id == MaterialPrecondition.material_id)
    query = query.join(InstrumentPrecondition, InstrumentPrecondition.action_id == PossibleAction.id)
    query = query.join(i1, i1.id == InstrumentPrecondition.instrument_id)
    query = query.join(BuildingPrecondition, BuildingPrecondition.action_id == PossibleAction.id)
    query = query.join(b1, b1.id == BuildingPrecondition.building_id)

    query = query.join(MaterialResult, MaterialResult.action_id == PossibleAction.id)
    query = query.join(m2, m2.id == MaterialResult.material_id)
    query = query.join(InstrumentResult, InstrumentResult.action_id == PossibleAction.id)
    query = query.join(i2, i2.id == InstrumentResult.instrument_id)
    query = query.join(BuildingResult, BuildingResult.action_id == PossibleAction.id)
    query = query.join(b2, b2.id == BuildingResult.building_id)

    query = query.order_by(PossibleAction.name)
    found_records = query.cte()
    records = session.query(found_records).all()
    return records
