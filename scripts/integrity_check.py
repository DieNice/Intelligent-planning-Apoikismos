import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models.models import *
from typing import List
from .action_robot import get_possible_actions_all, squeeze
from .simple_actions import get_all, types


@eel.expose
def global_skip() -> None:
    GLOBAL_CHECK.GLOBAL_CHECK = "Не пройдена"


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


def check_actions() -> List[str]:
    data = get_possible_actions_all()
    precond_data = squeeze(data[0])
    result_data = squeeze(data[1])
    conflicts = []
    index = 1
    for i in precond_data:
        sub_index = 0
        for j in i:
            if isinstance(j[1], MaterialPrecondition):
                if j[1].count <= 0:
                    conflicts.append(
                        index + "-я строка Число материалов(ресурсов) в предусловии не может быть отрицательно!")
            if isinstance(j[1], BuildingPrecondition):
                if result_data[index - 1][sub_index][1].building_id == 10:
                    conflicts.append(str(index) + "-я строка Результатом не может быть пустая постройка!")
                elif j[1].building_id == result_data[index - 1][sub_index][1].building_id:
                    conflicts.append(
                        str(index) + "-я строка Постройка в предусловии и результате совпадают!!")

            sub_index += 1
        index += 1

    if len(conflicts) == 0:
        conflicts.append("Успешно пройдено!")
    return conflicts
