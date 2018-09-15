truth_table_dict = {
    "BUF" : {(0,) : 0, (1,) : 1},
    "INV" : {(0,) : 1, (1,) : 0},
    "AND" : {(0, 0) : 0, (0, 1): 0, (1, 0): 0, (1, 1): 1},
    "OR" : {(0, 0) : 0, (0, 1): 1, (1, 0): 1, (1, 1): 1},
    "NAND" : {(0, 0) : 1, (0, 1): 1, (1, 0): 1, (1, 1): 0},
    "NOR" : {(0, 0) : 1, (0, 1): 0, (1, 0): 0, (1, 1): 0},
}

class Node:
    def addDriven(self, node):
        self.driven.append(node)

    def addDriving(self, node):
        self.driving.append(node)

    def getValue(self):
        raise NotImplementedError

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
        unknown_list = []
        for wire in self.driven:
            if wire.getValue() == -1:
                unknown_list.append(wire)
            else:
                value_list.append(wire.getValue())
        if unknown_list:
            return(-1, unknown_list)
        else:
            value_tuple = tuple(value_list)
            output_value = self.truth_table[value_tuple]
            return(output_value, unknown_list)
        
class Wire(Node):
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.value = -1
    
    def __str__(self):
        return("Node " + self.index + ", " + super(Wire, self).__str__())
    
    def getValue(self):
        return(self.value)

    def setValue(self, value):
        self.value = value

class Circuit:
    def getWire(self, index):
        if index in self.wire_dict:
            return(self.wire_dict[index])
        else:
            wire = Wire(index)
            self.wire_dict[index] = wire
            return(wire)

    def __init__(self, cir_path):
        self.wire_dict = {}
        self.gate_dict = {}
        self.input_list = []
        self.output_list = []

        fp = open(cir_path, "r")
        cir_lines = fp.readlines()

        for line in cir_lines:
            if line[-1] == '\n':
                line = line[:-1]
            words = line.split(" ")
            words = list(filter(None, words))

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
            wire.setValue(-1)
        for i in range(len(inputs)):
            self.input_list[i].setValue(inputs[i])

    def getOutputs(self, inputs):
        self.initWire(inputs)
        wire_stack = []
        output_list = []
        for output_wire in self.output_list:
            wire_stack.append(output_wire)
            output_value = -1
            while (wire_stack):
                wire = wire_stack.pop()
                if wire.getValue() == -1:
                    gate = wire.driven[0]
                    output_value, unknown_list = gate.getValue()
                    if output_value == -1:
                        wire_stack.append(wire)
                        wire_stack = wire_stack + unknown_list
                    else:
                        wire.setValue(output_value)
                else:
                    output_value = wire.getValue()

            output_list.append(output_value)
            print(str(output_value) + " ")
        
        
            
                
if __name__ == "__main__":
    cir1 = Circuit("C:/Users/zlj52/OneDrive - Georgia Institute of Technology\Academic\Digital Systems Testing/Projects/Logic simulator/logic_simulator/inputs/and_or.txt")
    print(cir1.wire_dict)
    print(cir1)
    cir1.getOutputs([0, 0, 0])
    cir1.getOutputs([0, 0, 1])
    cir1.getOutputs([0, 1, 0])
    cir1.getOutputs([0, 1, 1])
    cir1.getOutputs([1, 0, 0])
    cir1.getOutputs([1, 0, 1])
    cir1.getOutputs([1, 1, 0])
    cir1.getOutputs([1, 1, 1])

    cir2 = Circuit("C:/Users/zlj52/OneDrive - Georgia Institute of Technology\Academic\Digital Systems Testing/Projects/Logic simulator/logic_simulator/inputs/s27.txt")
    cir2.getOutputs([1,1,1,0,1,0,1])


    