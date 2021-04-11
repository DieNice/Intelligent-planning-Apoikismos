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
    precondition_data = squeeze(getted_data[0])
    result_data = squeeze(getted_data[1])
    rendered_page = template.render(precondition_data=precondition_data, result_data=result_data)

    with open('./static/temp/posible_action_robot.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def squeeze(data):
    added = set()
    res_data = []
    l_data = len(data)
    for i in range(l_data):
        if data[i][0].id not in added:
            subdata = []
            added.add(data[i][0].id)
            subdata.append(data[i])
            for j in range(i + 1, l_data):
                if data[j][0] == data[i][0]:
                    subdata.append(data[j])
            res_data.append(subdata)
    return res_data


def get_possible_actions_all():
    precondition_records = []
    query = session.query(PossibleAction, MaterialPrecondition, Material)
    query = query.join(MaterialPrecondition, MaterialPrecondition.action_id == PossibleAction.id)
    query = query.join(Material, Material.id == MaterialPrecondition.material_id)
    records = query.all()
    precondition_records.extend(records)
    query = session.query(PossibleAction, InstrumentPrecondition, Instrument)
    query = query.join(InstrumentPrecondition, InstrumentPrecondition.action_id == PossibleAction.id)
    query = query.join(Instrument, Instrument.id == InstrumentPrecondition.instrument_id)
    records = query.all()
    precondition_records.extend(records)
    query = session.query(PossibleAction, BuildingPrecondition, Building)
    query = query.join(BuildingPrecondition, BuildingPrecondition.action_id == PossibleAction.id)
    query = query.join(Building, Building.id == BuildingPrecondition.building_id)
    records = query.all()
    precondition_records.extend(records)
    result_records = []
    query = session.query(PossibleAction, MaterialResult, Material)
    query = query.join(MaterialResult, MaterialResult.action_id == PossibleAction.id)
    query = query.join(Material, Material.id == MaterialResult.material_id)
    records = query.all()
    result_records.extend(records)
    query = session.query(PossibleAction, InstrumentResult, Instrument)
    query = query.join(InstrumentResult, InstrumentResult.action_id == PossibleAction.id)
    query = query.join(Instrument, Instrument.id == InstrumentResult.instrument_id)
    records = query.all()
    result_records.extend(records)
    query = session.query(PossibleAction, BuildingResult, Building)
    query = query.join(BuildingResult, BuildingResult.action_id == PossibleAction.id)
    query = query.join(Building, Building.id == BuildingResult.building_id)
    records = query.all()
    result_records.extend(records)
    return (precondition_records, result_records)


@eel.expose
def load_creation_action(headername: str, titlename: str):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/create_actions_robot.html')

    m = get_all(types["Materials"], False)
    i = get_all(types["Instruments"], False)
    b = get_all(types["Buildings"], False)

    rendered_page = template.render(materials=m, instruments=i, buildings=b, headername=headername, titlename=titlename)

    with open('./static/temp/create_actions_robot.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


@eel.expose
def createactionrobot(action_name: str, materials: List[Tuple[str, str, int]], instruments: List[Tuple[str, str]],
                      buildings: List[Tuple[str, str]],
                      res_buildings: List[Tuple[str, str]]):
    new_action = PossibleAction(action_name)
    query = session.query(PossibleAction).filter_by(name=action_name).first()
    if query is not None:
        print("Действие с таким названием уже существует!")
        eel.already_exists()
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
        eel.sucessfull_create()


@eel.expose
def load_edit_action(headername: str, titlename: str, action_name: str):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/edit_actions_robot.html')
    action_name = action_name.strip()
    action_name = action_name.replace('\n', '')
    action_data = load_action(action_name)
    m = get_all(types["Materials"], False)
    m = prepare_data(m, action_data[0], "material")
    i = get_all(types["Instruments"], False)
    i = prepare_data(i, action_data[0], "instrument")
    b = get_all(types["Buildings"], False)
    b_copy = b.copy()
    b = prepare_data(b, action_data[0], "building")

    m_res = prepare_result_data(action_data[0], "material")
    i_res = prepare_result_data(action_data[0], "instrument")
    b_res = prepare_result_data(action_data[0], "building")
    b_target_left = prepare_data(b_copy, action_data[1], "building")
    b_target = prepare_result_data(action_data[1], "building")

    rendered_page = template.render(materials=m, instruments=i, buildings=b, materials_res=m_res, instruments_res=i_res,
                                    buildings_res=b_res, buildings_target_left=b_target_left, buildings_target=b_target,
                                    headername=headername,
                                    titlename=titlename,
                                    actionname=action_name, action_data=action_data)

    with open('./static/temp/edit_actions_robot.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def load_action(action_name: str):
    precondition_records = []
    query = session.query(PossibleAction, MaterialPrecondition, Material).filter_by(name=action_name)
    query = query.join(MaterialPrecondition, MaterialPrecondition.action_id == PossibleAction.id)
    query = query.join(Material, Material.id == MaterialPrecondition.material_id)
    records = query.all()
    precondition_records.extend(records)
    query = session.query(PossibleAction, InstrumentPrecondition, Instrument).filter_by(name=action_name)
    query = query.join(InstrumentPrecondition, InstrumentPrecondition.action_id == PossibleAction.id)
    query = query.join(Instrument, Instrument.id == InstrumentPrecondition.instrument_id)
    records = query.all()
    precondition_records.extend(records)
    query = session.query(PossibleAction, BuildingPrecondition, Building).filter_by(name=action_name)
    query = query.join(BuildingPrecondition, BuildingPrecondition.action_id == PossibleAction.id)
    query = query.join(Building, Building.id == BuildingPrecondition.building_id)
    records = query.all()
    precondition_records.extend(records)
    result_records = []
    query = session.query(PossibleAction, BuildingResult, Building).filter_by(name=action_name)
    query = query.join(BuildingResult, BuildingResult.action_id == PossibleAction.id)
    query = query.join(Building, Building.id == BuildingResult.building_id)
    records = query.all()
    result_records.extend(records)
    return (precondition_records, result_records)


def prepare_data(data, reserved_data, type):
    for i in reserved_data:
        if i[2].type == type:
            for j in data:
                if j.name == i[2].name:
                    data.remove(j)
    return data


def prepare_result_data(reserved_data, type):
    result_data = []
    for i in reserved_data:
        if i[2].type == type:
            if type == "material":
                result_data.append((i[2], i[1].count))
            else:
                result_data.append(i[2])
    return result_data


@eel.expose
def editactionrobot(oldname: str, newname: str, materials: List[Tuple[str, str, int]],
                    instruments: List[Tuple[str, str]],
                    buildings: List[Tuple[str, str]],
                    res_buildings: List[Tuple[str, str]]):
    delete_action(oldname)
    new_action = PossibleAction(newname)
    query = session.query(PossibleAction).filter_by(name=newname).first()
    if query is not None:
        print("Действие с таким названием уже существует!")
    else:
        session.add(new_action)
        session.commit()
        new_action_id = session.query(PossibleAction).filter_by(name=newname).first()
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
        print("Успешно обновлено!")


@eel.expose
def delete_action(action_name):
    action_name = action_name.strip()
    action_name = action_name.replace('\n', '')
    query = session.query(PossibleAction).filter_by(name=action_name).first()
    session.delete(query)
    session.commit()


@eel.expose
def save_action():
    session.commit()
