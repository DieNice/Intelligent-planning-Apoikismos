import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.models import *
from typing import List
from .action_robot import get_possible_actions_all, squeeze
from .simple_actions import get_all, types


@eel.expose
def check_load(check=False) -> None:
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/integrity_check.html')

    if check:
        check_m = check_object('Materials')
        check_i = check_object('Instruments')
        check_b = check_object('Buildings')
        check_a = check_actions()
        rendered_page = template.render(check_materials=check_m, check_instruments=check_i, check_buildings=check_b,
                                        check_actions=check_a)
        with open('./static/temp/integrity_check.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

    else:
        rendered_page = template.render()
        with open('./static/temp/integrity_check.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


@eel.expose
def preload_check() -> bool:
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/templates/integrity_check.html')
    check_m = check_object('Materials')
    check_i = check_object('Instruments')
    check_b = check_object('Buildings')
    check_a = check_actions()
    rendered_page = template.render(check_materials=check_m, check_instruments=check_i, check_buildings=check_b,
                                    check_actions=check_a)
    with open('./static/temp/integrity_check.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    result_flag = check_m[0] == "Проверка пройдена!" and check_i[0] == "Проверка пройдена!" and check_b[
        0] == "Проверка пройдена!" and check_a[0] == "Проверка пройдена!"
    if result_flag:
        eel.get_true()
    else:
        eel.get_false()


def check_object(type: str) -> List[str]:
    data = get_all(types[type])
    conflicts = []
    for i in range(len(data)):
        if data[i].description == '' and data[i].name == '':
            conflicts.append(str(i + 1) + "-я строка - Пустая запись!")
        elif data[i].description == '':
            conflicts.append(str(i + 1) + "-я строка- Отсутствует описание!")
        elif data[i].name == '':
            conflicts.append(str(i + 1) + "-я строка - Отсутствует имя!")

    if len(conflicts) == 0:
        return ["Проверка пройдена!"]
    else:
        return conflicts


def check_empty_condition(possible_action):
    res_logs = []
    count_material = 0
    count_instruments = 0
    count_buildings = 0
    for action in possible_action:
        if isinstance(action[2], Material):
            count_material += 1
        if isinstance(action[2], Instrument):
            count_instruments += 1
        if isinstance(action[2], Building):
            count_buildings += 1
    where = ''
    name = ""
    if len(possible_action) != 0:
        if isinstance(possible_action[0][1], MaterialPrecondition) or isinstance(possible_action[0][1],
                                                                                 InstrumentPrecondition) or isinstance(
            possible_action[0][1], BuildingPrecondition):
            where = "предусловии"
        else:
            where = "постусловии"
        name = possible_action[0][0].name
    if count_material == 0:
        res_logs.append("\"{}\":материалы отсутствуют в {}".format(name, where))
    if count_instruments == 0:
        res_logs.append("\"{}\":инструменты отсутствуют в {}".format(name, where))
    if count_buildings == 0:
        res_logs.append("\"{}\":постройки отсутствуют в {}".format(name, where))
    return res_logs


def count_buildings(action: List[PossibleAction]) -> int:
    count = 0
    for act in action:
        if isinstance(act[1], BuildingPrecondition) or isinstance(act[1], BuildingResult):
            count += 1
    return count


def check_actions() -> List[str]:
    data = get_possible_actions_all()
    precond_data = squeeze(data[0])
    result_data = squeeze(data[1])
    conflicts = []
    index = 0
    for i in precond_data:
        empty_precondition_check = check_empty_condition(i)
        empty_postcondition_check = check_empty_condition(result_data[index])
        if len(empty_precondition_check) != 0 or len(empty_postcondition_check) != 0:
            conflicts.extend(empty_precondition_check)
            conflicts.extend(empty_postcondition_check)
            continue
        sub_index = 0
        for j in i:
            name = j[0].name
            if isinstance(j[1], MaterialPrecondition):
                if j[1].count <= 0:
                    conflicts.append(
                        "\"{}\":Число материалов(ресурсов) в предусловии не может быть отрицательно!".format(
                            name))
            if isinstance(j[1], BuildingPrecondition):
                if result_data[index][sub_index][1].building_id == 10:
                    conflicts.append("\"{}\":Результатом не может быть пустая постройка!".format(name))
                elif j[1].building_id == result_data[index][sub_index][1].building_id:
                    conflicts.append("\"{}\":Постройка в предусловии и результате совпадают!".format(name))

            sub_index += 1
        index += 1
    for action in precond_data:
        if count_buildings(action) > 1:
            conflicts.append(
                f"\"{action[0].name}\":Число построек в предусловии не может быть больше одной для одного действия")
    for action in result_data:
        if count_buildings(action) > 1:
            conflicts.append(
                f"\"{action[0][0].name}\":Число построек в результатах не может быть больше одной для одного действия")

    if len(conflicts) == 0:
        conflicts.append("Проверка пройдена!")
    return conflicts
