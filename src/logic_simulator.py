truth_table_dict = {
    "AND" : {(0, 0) : 0, (0, 1): 0, (1, 0): 0, (1, 1): 1},
    "OR" : {(0, 0) : 0, (0, 1): 1, (1, 0): 1, (1, 1): 1}
}

class Node:
    driven = []
    driving = []

    def addDriven(self, node):
        self.driven.append(node)

    def addDriving(self, node):
        self.driving.append(node)
    
class Gate(Node):
    logic = ""
    truth_table = {}

    def __init__(self, gate_logic):
        self.logic = gate_logic
        self.truth_table = truth_table_dict[gate_logic]
        #self.driven = driven
        #self.driving = driving
        
class Wire(Node):
    index = ""
    value = -1

    def __init__(self, index):
        self.index = index

class Circuit:
    wire_dict = {}
    gate_dict = {}
    input_list = []
    output_list = []

    def getWire(self, index):
        if index in self.wire_dict:
            return(self.wire_dict[index])
        else:
            wire = Wire(index)
            self.wire_dict[index] = wire
            return(wire)

    def __init__(self, cir_name):
        fp = open("C:/Users/lzhu308/OneDrive - Georgia Institute of Technology\Academic\Digital Systems Testing/Projects/Logic simulator/logic_simulator/inputs/and_or.txt", "r")
        cir_lines = fp.readlines()

        for line in cir_lines:
            words = line.split(" ")
            if words[0] == "INPUT":
                for index in words[1 : -1]:
                    self.input_list.append(self.wire_dict[index])
            elif words[0] == "OUTPUT":
               for index in words[1 : -1]:
                    self.output_list.append(self.wire_dict[index])
            else:
                gate = Gate(words[0])
                for wire_index in words[1 : -1]:
                    if wire_index in self.wire_dict:
                        wire = self.wire_dict[wire_index]
                        gate.addDriven(wire)
                        wire.addDriving(gate)
                    else:
                        wire = Wire(wire_index)
                        self.wire_dict[wire_index] = wire
                        gate.addDriven(wire)
                        wire.addDriving(gate)
                wire_index = words[-1]


            
                
if __name__ == "__main__":
    cir1 = Circuit("and_or")
    print(cir1.wire_dict["1"].driving[0].driven[0].index)


    