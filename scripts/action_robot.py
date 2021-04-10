import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from models.models import *
from scripts.simple_actions import get_all, types
from typing import List, Tuple


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


@eel.expose
def load_creation_action(headername: str, titlename: str):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/edit_create_actions_robot.html')

    m = get_all(types["Materials"], False)
    i = get_all(types["Instruments"], False)
    b = get_all(types["Buildings"], False)

    rendered_page = template.render(materials=m, instruments=i, buildings=b, headername=headername, titlename=titlename)

    with open('./static/temp/edit_create_actions_robot.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


@eel.expose
def createactionrobot(action_name: str, materials: List[Tuple[str, str, int]], instruments: List[Tuple[str, str]],
                      buildings: List[Tuple[str, str]],
                      res_buildings: List[Tuple[str, str]]):
    new_action = PossibleAction(action_name)
    query = session.query(PossibleAction).filter_by(name=action_name).first()
    if query is not None:
        print("Действие с таким названием уже существует!")
    else:
        session.add(new_action)
        session.commit()
        new_action_id = session.query(PossibleAction).filter_by(name=action_name).first()
        print(new_action.id)
        for i in materials:
            query = session.query(Material).filter_by(name=i[0], description=i[1]).first()
            new_material_precond = MaterialPrecondition(new_action_id.id, query.id, i[2])
            session.add(new_material_precond)
            session.commit()
        for i in instruments:
            query = session.query(Instrument).filter_by(name=i[0], description=i[1]).first()
            new_instruments_precond = InstrumentPrecondition(new_action_id.id, query.id)
            session.add(new_instruments_precond)
            session.commit()
        for i in buildings:
            query = session.query(Building).filter_by(name=i[0], description=i[1]).first()
            new_buildings_precond = BuildingPrecondition(new_action_id.id, query.id)
            session.add(new_buildings_precond)
            session.commit()
        # Postconditions (results)
        for i in materials:
            query = session.query(Material).filter_by(name=i[0], description=i[1]).first()
            new_material_res = MaterialResult(new_action_id.id, query.id, i[2] * -1)
            session.add(new_material_res)
            session.commit()
        none_instrument = session.query(Instrument).filter_by(name="Нет").first()
        for _ in instruments:
            new_instruments_res = InstrumentResult(new_action_id.id, none_instrument.id)
            session.add(new_instruments_res)
            session.commit()
        for i in res_buildings:
            query = session.query(Building).filter_by(name=i[0], description=i[1]).first()
            new_buildings_res = BuildingResult(new_action_id.id, query.id)
            session.add(new_buildings_res)
            session.commit()
        print("Успешно добавлено!")
