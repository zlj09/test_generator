import re

truth_table_dict = {
    "AND" : {(0, 0) : 0, (0, 1): 0, (1, 0): 0, (1, 1): 1},
    "OR" : {(0, 0) : 0, (0, 1): 1, (1, 0): 1, (1, 1): 1}
}

class Node:
    def addDriven(self, node):
        self.driven.append(node)

    def addDriving(self, node):
        self.driving.append(node)

    def __init__(self):
        self.driven = []
        self.driving = []

    def __str__(self):
        return("Driven by " + str(len(self.driven)) + " nodes, Driving " + str(len(self.driving)) + " nodes")
    
class Gate(Node):
    def __init__(self, gate_logic):
        super().__init__()
        self.logic = gate_logic
        self.truth_table = truth_table_dict[gate_logic]


    def __str__(self):
        return("Gate " + self.logic + ", " + super(Gate, self).__str__())

    def getValue(self):
        value_list = []
        unknown_list []
        
class Wire(Node):
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.value = -1
    
    def __str__(self):
        return("Node " + self.index + ", " + super(Wire, self).__str__())

class Circuit:
    def getWire(self, index):
        if index in self.wire_dict:
            return(self.wire_dict[index])
        else:
            wire = Wire(index)
            self.wire_dict[index] = wire
            return(wire)

    def __init__(self, cir_name):
        self.wire_dict = {}
        self.gate_dict = {}
        self.input_list = []
        self.output_list = []

        fp = open("C:/Users/lzhu308/OneDrive - Georgia Institute of Technology\Academic\Digital Systems Testing/Projects/Logic simulator/logic_simulator/inputs/and_or.txt", "r")
        cir_lines = fp.readlines()

        for line in cir_lines:
            if line[-1] == '\n':
                line = line[:-1]
            words = re.split(' ',line)

            if words[0] == "INPUT":
                for index in words[1 : -1]:
                    self.input_list.append(self.getWire(index))
            elif words[0] == "OUTPUT":
               for index in words[1 : -1]:
                    self.output_list.append(self.getWire(index))
            else:
                if (words[-1] == "-1"):
                    words = words[:-1]
                gate = Gate(words[0])
                for index in words[1 : -1]:
                    wire = self.getWire(index)
                    gate.addDriven(wire)
                    wire.addDriving(gate)
                index = words[-1]
                wire = self.getWire(index)
                gate.addDriving(wire)
                wire.addDriven(gate)

    def __str__(self):
        cir_str = "Input: \n"
        for wire in self.input_list:
            cir_str = cir_str + str(wire) + "\n"
        cir_str = cir_str + "Output: \n"
        for wire in self.output_list:
            cir_str = cir_str + str(wire) + "\n"
        return(cir_str)

    def initWire(self, inputs):
        for wire in self.wire_dict.values():
            wire.value = -1
        for i in len(inputs):
            self.input_list[i].value = inputs[i]

    def getOutputs(self, inputs):
        self.initWire(inputs)
        wire_stack = []
        for output_wire in self.output_list:
            wire_stack.append(output_wire)
            while (wire_stack):
                wire = wire_stack.pop()
                if (wire.value == -1):
                    gate = wire.driven[0]
                    unknown_cnt = 0
                    tmp_stack = []
                    for driving_wire in gate.driving:
                        if (driving_wire.vaule == -1):
                            unknown_cnt = unknown_cnt + 1
                            tmp_stack.append(driving_wire)
            
                
if __name__ == "__main__":
    cir1 = Circuit("and_or")
    print(cir1.wire_dict)
    print(cir1)


    