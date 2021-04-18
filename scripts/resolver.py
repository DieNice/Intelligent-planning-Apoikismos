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
    good_plan, logs = resolver.nlp(initial_state, goals)
    print(good_plan)
    for i in logs:
        print(i)


class State():
    def __init__(self, materials: List, instruments: List, buildings: List, processed_lists=False) -> None:
        self.__materials: List[Tuple[str, int]] = []
        self.__instruments: List[str] = []
        self.__buildings: List[str] = []
        if not processed_lists:
            for i in materials:
                self.__materials.append((i[0], i[2]))
            for i in instruments:
                self.__instruments.append(i[0])
            for i in buildings:
                self.__buildings.append(i[0])
        else:
            self.__materials = materials
            self.__instruments = instruments
            self.__buildings = buildings

    def __eq__(self, other):
        pass

    def get_buildings(self):
        return self.__buildings

    def get_materials(self):
        return self.__materials

    def get_instruments(self):
        return self.__instruments

    def __sub__(self, other):
        len_materials = len(self.__materials)
        if len_materials <= 0:
            raise Exception('Can\'t apply a oparation')
        materials = self.__materials.copy()
        other_materials = other.get_materials()
        len_other_materials = len(other_materials)
        for i in range(len_other_materials):
            for j in range(len_materials):
                materials[j] = list(materials[j])
                if materials[j][0] == other_materials[i][0]:
                    materials[j][1] = materials[j][1] + other_materials[i][1]

        result: State = State(materials, self.__instruments, other.get_buildings(), True)
        return result

    def add_empty_buildings(self) -> None:
        self.__buildings.append('Нет')

    def __str__(self):
        res_str = "State{{Materials:"
        for i in self.__materials:
            res_str += str(i) + ';'
        res_str += " Instruments:"
        for i in self.__instruments:
            res_str += i + ';'
        res_str += " Buildings:"
        for i in self.__buildings:
            res_str += i + ';'
        res_str += "}"
        return res_str

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

    def get_preconditions(self):
        materials = self.__precond_materials
        instruments = self.__precond_instruments
        buildings = self.__precond_buildings
        result_state: State = State(materials, instruments, buildings, True)
        return result_state

    def __str__(self):
        return self.__repr__()

    def use_operation(self, state: State) -> State:
        pass

    def get_precond(self):
        return [self.__precond_materials, self.__precond_instruments, self.__precond_buildings]

    def get_postcond(self):
        return [self.__postcond_materials, self.__postcond_instruments, self.__postcond_buildings]


class NlpResolver():
    __operations = []

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
        return operations

    def __match(self, state: State, goal: State) -> bool:
        flag: bool = False
        state_buildings = state.get_buildings()
        goal_buildings = goal.get_buildings()
        len_goal = len(goal_buildings)
        len_state = len(state_buildings)
        if len_goal > len_state:
            return flag
        if len_state >= len_goal:
            for i in state_buildings:
                if i in goal_buildings:
                    return not flag
        return flag

    def __choose_operator(self, g: State) -> Operation:
        all_op = self.__operations
        for op in all_op:
            postcond = op.get_postcond()
            goal_bildings = g.get_buildings()
            if goal_bildings == postcond[2]:
                return op
        raise Exception("Plan does not exists")

    def __met_in_state(self, o: Operation, state: State) -> bool:
        def met_materials(precond_m, state_m) -> bool:
            flag = False
            for m1 in precond_m:
                for m2 in state_m:
                    if m2[0] == m1[0]:
                        flag = True
                        if m1[1] > m2[1]:
                            return False
                if flag:
                    flag = False
                else:
                    return False
            return True

        precond_m, precond_i, precond_b = o.get_precond()

        state_m = state.get_materials()
        state_i = state.get_instruments()
        state_b = state.get_buildings()
        if not met_materials(precond_m, state_m):
            return False
        for i in precond_i:
            if i == "Нет":
                break
            if i not in state_i:
                return False
        for b in precond_b:
            if b not in state_b:
                return False
        return True

    def __apply(self, o: Operation, state: State) -> State:
        post_m, post_i, post_b = o.get_postcond()
        new_state = State(post_m, post_i, post_b, True)
        result = state - new_state
        return result

    def nlp(self, initial_state, goals) -> Tuple[List[str], List[Operation]]:
        state = initial_state
        logs = []
        logs.append("Initializated state \"{}\"".format(str(state)))
        goalset = goals.copy()
        for goal in goalset:
            logs.append("Added new goal \"{}\"".format(str(goal)))
        opstack = []
        plan = []
        index = 0
        while index < len(goalset) and len(goalset) != 0:
            g = goalset[index]
            logs.append("Selected goal \"{}\"".format(g))
            g_index = goalset.index(g)
            if not self.__match(state, g):
                logs.append("State \"{}\" dont match goal \"{}\"".format(str(state), str(g)))
                o = self.__choose_operator(g)
                logs.append("Choose operator \"{}\"".format(str(o)))
                opstack.append(o)
                goalset.insert(g_index + 1, o.get_preconditions())
                logs.append("Added new goal \"{}\"".format(str(o.get_preconditions())))
                index += 1
            else:
                logs.append("The goal \"{}\" is complete".format(goalset[index]))
                goalset.pop(index)
                state.add_empty_buildings()
            l_op = len(opstack)
            while l_op != 0 and self.__met_in_state(opstack[l_op - 1], state):
                logs.append("Operation \"{}\" met in state \"{}\"".format(str(opstack[l_op - 1]), str(state)))
                o = opstack.pop()
                logs.append("The goal \"{}\"is complete".format(str(goalset[g_index + 1])))
                goalset.pop(g_index + 1)
                index -= 1
                g_index -= 1
                state = self.__apply(o, state)
                logs.append("Applied operation \"{}\" to state \"{}\"".format(str(o), str(state)))
                plan.append(o)
                logs.append("Added oparation \"{}\" to plan".format(str(o)))
                l_op = len(opstack)
        return plan, logs
