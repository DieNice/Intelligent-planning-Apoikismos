import eel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from models.models import *
from scripts.simple_actions import get_all, types
from scripts.action_robot import get_possible_actions_all, squeeze
from typing import List, Tuple


@eel.expose
def resolve(materials, instrumetns, buildings, res_buildings):
    initial_state = State(materials, instrumetns, buildings)
    goals = initial_goals(res_buildings)
    resolver = NlpResolver()
    resolver.nlp(initial_state, goals)


class State():
    def __init__(self, materials: List, instruments: List, buildings: List) -> None:
        self.__materials: List[Tuple[str, int]] = []
        self.__instruments: List[str] = []
        self.__buildings: List[str] = []
        for i in materials:
            self.__materials.append((i[0], i[2]))
        for i in instruments:
            self.__instruments.append(i[0])
        for i in buildings:
            self.__buildings.append(i[0])

    def __eq__(self, other):
        pass


def initial_goals(buildings):
    materials = []
    instruments = []
    result_goals = []
    for building in buildings:
        new_goal = State(materials, instruments, [building])
        result_goals.append(new_goal)
    return result_goals


class Operation():
    def __init__(self, precond: List, postcond: List) -> None:
        self.__precond_materials: List[Tuple[str, int]] = []
        self.__precond_instruments: List[str] = []
        self.__precond_buildings: List[str] = []
        self.__postcond_materials: List[Tuple[str, int]] = []
        self.__postcond_buildings: List[str] = []
        self.__postcond_instruments: List[str] = []
        self.__name = precond[0][0].name
        l_parts = len(precond)
        for i in range(l_parts):
            if isinstance(precond[i][2], Material):
                self.__precond_materials.append((precond[i][2].name, precond[i][1].count))
                self.__postcond_materials.append((precond[i][2].name, postcond[i][1].count))
            elif isinstance(precond[i][2], Instrument):
                self.__precond_instruments.append(precond[i][2].name)
                self.__postcond_instruments.append(postcond[i][2].name)
            elif isinstance(precond[i][2], Building):
                self.__precond_buildings.append(precond[i][2].name)
                self.__postcond_buildings.append(postcond[i][2].name)

    def __repr__(self):
        res_str = "\"{}\" Preconditions{{Materials:".format(self.__name)
        for i in self.__precond_materials:
            res_str += str(i) + ';'
        res_str += " Instruments:"
        for i in self.__precond_instruments:
            res_str += i + ';'
        res_str += " Buildings:"
        for i in self.__precond_buildings:
            res_str += i + ';'
        res_str += "} Postcondition{Materials:"
        for i in self.__postcond_materials:
            res_str += str(i) + ';'
        res_str += " Buildings:"
        for i in self.__postcond_buildings:
            res_str += i + ';'
        res_str += "}"
        return res_str

    def __str__(self):
        return self.__repr__()

    def use_operation(self, state: State) -> State:
        pass


class NlpResolver():
    __operations = []
    __initial_state = None

    def __init__(self):
        self.__operations = self.__init_operations()

    def __init_operations(self) -> List[Operation]:
        getted_data = get_possible_actions_all()
        precondition_data = squeeze(getted_data[0])
        postcondition_data = squeeze(getted_data[1])
        l_op = len(precondition_data)
        operations: List[Operation] = []
        for i in range(l_op):
            new_op = Operation(precondition_data[i], postcondition_data[i])
            operations.append(new_op)
            print(new_op)
        return Operation

    def nlp(self, initial_state, goals):
        pass
