truth_table_dict = {
    "AND" : {(0, 0) : 0, (0, 1): 0, (1, 0): 0, (1, 1): 1},
    "OR" : {(0, 0) : 0, (0, 1): 1, (1, 0): 1, (1, 1): 1}
}

class Node:
    driven = []
    driving = []
    
class Gate(Node):
    logic = ""
    truth_table = {}

    def __init__(self, gate_logic, driven, driving):
        self.logic = gate_logic
        self.truth_table = truth_table_dict[gate_logic]
        self.driven = driven
        self.driving = driving
        
class Wire(Node):
    index = ""
    value = -1

    def __init__(self, index):
        self.index = index

class Circuit:
    wire_list = []
    input_list = []
    output_list = []

    def __init__(self, cir_name):
        fp = open("C:/Users/lzhu308/OneDrive - Georgia Institute of Technology\Academic\Digital Systems Testing/Projects/Logic simulator/logic_simulator/inputs/and_or.txt", "r")
        cir_lines = fp.readlines()

        for line in cir_lines:
            words = line.split(" ")
            if words[0] == "INPUT":
                input_list = words[1 : -1]
            elif words[0] == "OUTPUT":
                output_list = words[1 : -1]
            else:
                gate_logic = words[0]
            
                
if __name__ == "__main__":
    cir1 = Circuit("and_or")


    