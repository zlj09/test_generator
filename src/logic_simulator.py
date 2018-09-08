truth_table_dict = {
    "AND" : {(0, 0) : 0, (0, 1): 0, (1, 0): 0, (1, 1): 1}
}

class Node:
    def __init__(self, driving = [], driven =[]):
        self.driving = driving
        self.driven = driven

class Gate:
    logic = ""
    nets = []
    driven_nets = []
    driving_net = 0
    truth_table = {}

    def __init__(self, gate_logic, gate_nets):
        self.logic = gate_logic
        self.nets = gate_nets
        self.driven_nets = gate_nets[0 : -1]
        self.driving_net = gate_nets[-1]
        self.truth_table = truth_table_dict[gate_logic] 



if __name__ == "__main__":
    print("Hello World!")

    gate0 = Gate("AND", [1, 2, 3])