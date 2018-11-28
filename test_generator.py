import sys
import random
from enum import Enum

NO_PLOT = False
try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError:
    NO_PLOT = True

###### Definition ######
X = -1
# 0 = 0
# 1 = 1
D = 2
D_bar = 3

truth_table_dict = { \
    "BUF" : {(0,) : 0, (1,) : 1, (X,) : X, (D,) : D, (D_bar,) : D_bar}, \
    "INV" : {(0,) : 1, (1,) : 0, (X,) : X, (D,) : D_bar, (D_bar,) : D}, \
    "AND" : { \
        (0, 0) : 0, (0, 1) : 0, (0, D) : 0, (0, D_bar) : 0, (0, X) : 0, \
        (1, 0) : 0, (1, 1) : 1, (1, D) : D, (1, D_bar) : D_bar, (1, X) : X, \
        (D, 0) : 0, (D, 1) : D, (D, D) : D, (D, D_bar) : 0, (D, X) : X, \
        (D_bar, 0) : 0, (D_bar, 1) : D_bar, (D_bar, D) : 0, (D_bar, D_bar) : D_bar, (D_bar, X) : X, \
        (X, 0) : 0, (X, 1) : X, (X, D) : X, (X, D_bar) : X, (X, X) : X, \
    }, \
    "OR" : { \
        (0, 0) : 0, (0, 1) : 1, (0, D) : D, (0, D_bar) : D_bar, (0, X) : X, \
        (1, 0) : 1, (1, 1) : 1, (1, D) : 1, (1, D_bar) : 1, (1, X) : 1, \
        (D, 0) : D, (D, 1) : 1, (D, D) : D, (D, D_bar) : 1, (D, X) : X, \
        (D_bar, 0) : D_bar, (D_bar, 1) : 1, (D_bar, D) : 1, (D_bar, D_bar) : D_bar, (D_bar, X) : X, \
        (X, 0) : X, (X, 1) : 1, (X, D) : X, (X, D_bar) : X, (X, X) : X, \
    }, \
    "NAND" : { \
        (0, 0) : 1, (0, 1) : 1, (0, D) : 1, (0, D_bar) : 1, (0, X) : 1, \
        (1, 0) : 1, (1, 1) : 0, (1, D) : D_bar, (1, D_bar) : D, (1, X) : X, \
        (D, 0) : 1, (D, 1) : D_bar, (D, D) : D_bar, (D, D_bar) : 1, (D, X) : X, \
        (D_bar, 0) : 1, (D_bar, 1) : D, (D_bar, D) : 1, (D_bar, D_bar) : D, (D_bar, X) : X, \
        (X, 0) : 1, (X, 1) : X, (X, D) : X, (X, D_bar) : X, (X, X) : X, \
    }, \
    "NOR" : { \
        (0, 0) : 1, (0, 1) : 0, (0, D) : D_bar, (0, D_bar) : D, (0, X) : X, \
        (1, 0) : 0, (1, 1) : 0, (1, D) : 0, (1, D_bar) : 0, (1, X) : 0, \
        (D, 0) : D_bar, (D, 1) : 0, (D, D) : D_bar, (D, D_bar) : 0, (D, X) : X, \
        (D_bar, 0) : D, (D_bar, 1) : 0, (D_bar, D) : 0, (D_bar, D_bar) : D, (D_bar, X) : X, \
        (X, 0) : X, (X, 1) : 0, (X, D) : X, (X, D_bar) : X, (X, X) : X, \
    }, \
}

inversion_dict = {
    "BUF" : 0,
    "INV" : 1,
    "AND" : 0,
    "OR" : 0,
    "NAND" : 1,
    "NOR" : 1
}

ctrl_val_dict = {
    "BUF" : 0,
    "INV" : 0,
    "AND" : 0,
    "OR" : 1,
    "NAND" : 0,
    "NOR" : 1
}

def inv(b):
    return(int(not b))

class Fault:
    def __init__(self, wire_index, stuck_val):
        self.wire_index = wire_index
        self.stuck_val = stuck_val
    
    def __str__(self):
        return(str(self.wire_index) + " stuck at " + str(self.stuck_val))

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
        self.inversion = inversion_dict[gate_logic]
        self.ctrl_val = ctrl_val_dict[gate_logic]

    def __str__(self):
        return("Gate " + self.logic + ", " + super(Gate, self).__str__())

    def getValue(self):
        value_list = []
        unknown_list = []
        for wire in self.driven:
            if wire.getValue() == X:
                unknown_list.append(wire)
            else:
                value_list.append(wire.getValue())
        if unknown_list:
            return(X, unknown_list)
        else:
            value_tuple = tuple(value_list)
            output_value = self.truth_table[value_tuple]
            return(output_value, unknown_list)

    def getOutputFaultList(self):
        ctrl_fault_list = set()
        unctrl_fault_list = set()
        ctrl_val_num = 0
        for input_wire in self.driven:
            if (input_wire.getValue() == X):
                print("Error: Wire %s has unknown value\n" %(input_wire.index))
            elif (input_wire.getValue() == self.ctrl_val):
                if (ctrl_val_num):
                    ctrl_fault_list &= input_wire.getFaultList()
                else:
                    ctrl_fault_list |= input_wire.getFaultList()
                ctrl_val_num += 1
            else:
                unctrl_fault_list |= input_wire.getFaultList()
        
        output_wire = self.driving[0]

        if (ctrl_val_num == 0):
            output_fault_list = unctrl_fault_list
            for fault in output_wire.getFaultList():
                if (fault.stuck_val == (self.ctrl_val ^ self.inversion)):
                    output_fault_list.add(fault)
        else:
            output_fault_list = ctrl_fault_list - unctrl_fault_list
            for fault in output_wire.getFaultList():
                if (fault.stuck_val == (self.ctrl_val ^ self.inversion ^ 1)):
                    output_fault_list.add(fault)

        return(output_fault_list)
        
class Wire(Node):
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.value = X
        self.fault_list = set()
    
    def __str__(self):
        return("Node " + self.index + ", " + super(Wire, self).__str__())
    
    def getValue(self):
        return(self.value)

    def setValue(self, value):
        self.value = value

    def addFault(self, fault):
        self.fault_list.add(fault)

    def getFaultList(self):
        return(self.fault_list)

    def setFaultList(self, fault_list):
        self.fault_list = fault_list

    def printFaultList(self):
        print("Wire %s, Fault List: " %(self.index), end = ' ')
        for fault in self.fault_list:
            print("[%s]" %(fault), end = ' ')
        print("")

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
        self.fault_universe = []
        self.d_frontier = []
        self.target_fault = None

        fp = open(cir_path, "r")
        cir_lines = fp.readlines()

        for line in cir_lines:
            if line[-1] == '\n':
                line = line[:-1]
            words = line.split(" ")
            words = list(filter(None, words))
            if words == []:
                continue

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

    def initWireValue(self, inputs):
        for wire in self.wire_dict.values():
            wire.setValue(X)
        for i in range(len(inputs)):
            self.input_list[i].setValue(inputs[i])

    def initFaultList(self):
        for fault in self.fault_universe:
            wire = self.getWire(fault.wire_index)
            if (fault.stuck_val != wire.getValue()):
                wire.addFault(fault)

    def initFaultUniverse(self, fault_str_list = []):
        self.fault_universe = []
        for wire in self.wire_dict.values():
            wire.fault_list = set()
        if (fault_str_list):
            for fault_str in fault_str_list:
                fault_str_split = fault_str.split(" ")
                wire_index = fault_str_split[0]
                stuck_val = int(fault_str_split[1])
                fault = Fault(wire_index, stuck_val)
                self.fault_universe.append(fault)
        else:
            for wire_index, wire in self.wire_dict.items():
                for stuck_val in [0, 1]:
                    fault = Fault(wire_index, stuck_val)
                    self.fault_universe.append(fault)

    def getOutputs(self, inputs_str):
        inputs = [int(digit) for digit in inputs_str]
        self.initWireValue(inputs)
        wire_stack = []
        output_str = ""
        for output_wire in self.output_list:
            wire_stack.append(output_wire)
            while (wire_stack):
                wire = wire_stack.pop()
                if wire.getValue() == X:
                    gate = wire.driven[0]
                    output_value, unknown_list = gate.getValue()
                    if output_value == X:
                        wire_stack.append(wire)
                        wire_stack = wire_stack + unknown_list
                    else:
                        wire.setValue(output_value)

            output_str += str(output_wire.getValue())
        
        return(output_str)

    def getDetectedFaults(self, inputs_str):
        inputs = [int(digit) for digit in inputs_str]
        self.initWireValue(inputs)
        self.initFaultList()
        wire_stack = []
        detected_fault_list = set()
        for output_wire in self.output_list:
            wire_stack.append(output_wire)
            while (wire_stack):
                wire = wire_stack.pop()
                if wire.getValue() == X:
                    gate = wire.driven[0]
                    output_value, unknown_list = gate.getValue()
                    if output_value == X:
                        wire_stack.append(wire)
                        wire_stack = wire_stack + unknown_list
                    else:
                        wire.setValue(output_value)
                        output_fault_list = gate.getOutputFaultList()
                        wire.setFaultList(output_fault_list)
            
            detected_fault_list |= output_wire.getFaultList()

        detected_fault_str = "Num of detected faults: " + str(len(detected_fault_list)) + "\n"
        for fault in sorted(list(detected_fault_list), key = lambda fault: int(fault.wire_index)):
            detected_fault_str += str(fault) + "\n"
        
        return(detected_fault_list, detected_fault_str)
    
    def randomDetect(self, target_coverage, fault_str_list = []):
        coverage = 0
        detected_fault_list = set()
        test_set = set()
        cov_per_list = []
        self.initFaultUniverse(fault_str_list)
        # print("Fault Universe: ")
        # for fault in self.fault_universe.values():
            # print("%s" % (fault), end = ", ")
        while (coverage < target_coverage):
            rand_test_vec = [random.randint(0, 1) for i in range(len(self.input_list))]
            rand_test_str = ''.join([ str(bit) for bit in rand_test_vec])
            if (rand_test_str in test_set):
                continue
            else:
                test_set.add(rand_test_str)
            # print("\nRand Test Vec: %s" % (rand_test_str))
            # detected_fault_list |= self.getDetectedFaults(rand_test_str, fault_str_list)
            new_detected_fault, detected_fault_str = self.getDetectedFaults(rand_test_str)
            detected_fault_list |= new_detected_fault
            coverage = float(len(detected_fault_list)) / float(len(self.fault_universe))
            print("Test Vec Num: %d, Coverage: %f" % (len(test_set), coverage))
            # print("Detected faults: ")
            cov_per_list.append(coverage * 100)
            # for fault in detected_fault_list:
                # print("%s" % (fault), end = ", ")

        print("%d random vectors needed to achieve %f coverage" % (len(test_set), coverage))
        
        if (not NO_PLOT):
            x = np.array(range(1, len(test_set) + 1))
            y = np.array(cov_per_list)
            plt.plot(x, y)
            plt.scatter(x, y, s = 10, color = "blue")
            plt.xlabel(r"Test Vector Number", fontsize = 10)
            plt.ylabel(r"Coverage (%)", fontsize = 10)
            plt.xticks(np.array(range(0, len(test_set) + 2)))
            plt.show()

    def backtrace(self, wire_index_k, trace_val_k):
        val = trace_val_k
        wire_k = self.getWire(wire_index_k)
        while (not (wire_k in self.input_list)):
            gate_k = wire_k.driven[0]
            inversion = gate_k.inversion
            for wire_j in gate_k.driven:
                if (wire_j.getValue() == X):
                    break
            val = val ^ inversion
            wire_index_k = wire_j.index
            wire_k = wire_j
        
        return(wire_index_k, val)
    
    def objective(self):
        wire_l = self.getWire(self.target_fault.wire_index)
        if (wire_l.getValue() == X):
            return(wire_l.index, inv(self.target_fault.stuck_val))
        for gate_g in self.d_frontier:
            for wire_j in gate_g.driven:
                if (wire_j.getValue() == X):
                    break
        ctrl_val = gate_g.ctrl_val
        return(wire_j.index, inv(ctrl_val))

    def findXPath(self, gate):
        wire_next = gate.driving[0]
        if (wire_next.getValue() == X):
            if (wire_next in self.output_list):
                return(True)
            else:
                for gate_next in wire_next.driving:
                    if (self.findXPath(gate_next)):
                        return(True)
                return(False)
        else:
            return(False)


    def checkTestPossible(self):
        wire_l = self.getWire(self.target_fault.wire_index)
        if (wire_l.getValue() == X): # the target fault haven't been activated
            return(True)
        if (wire_l.getValue() == self.target_fault.stuck_val):
            return(False)
        for gate in self.d_frontier:
            if (self.findXPath(gate)):
                return(True)
        return(False)

    def imply(self, wire_index_j, val_j):
        wire_j = self.getWire(wire_index_j)
        if (wire_index_j == self.target_fault.wire_index and val_j != self.target_fault.stuck_val):
            if (self.target_fault.stuck_val == 0):
                wire_j.setValue(D)
            else:
                wire_j.setValue(D_bar)
        else:
            wire_j.setValue(val_j)
        if (wire_j in self.output_list):
            return
        for gate_next in wire_j.driving:
            wire_next = gate_next.driving[0]
            val_next, unknown_list = gate_next.getValue()
            wire_index_next = wire_next.index

            if (wire_j.getValue() in [D, D_bar] and val_next == X):
                self.d_frontier.append(gate_next)
            elif (gate_next in self.d_frontier):
                input_list = [input_wire.getValue() for input_wire in gate_next.driven]
                if (not ((D in input_list) or (D_bar in input_list))):
                    self.d_frontier.remove(gate_next)

            self.imply(wire_index_next, val_next)

    def PODEM(self):
        for po in self.output_list:
            if (po.getValue() in [D, D_bar]):
                return(True)
        if (not self.checkTestPossible()):
            return(False)
        (k, v_k) = self.objective()
        (j, v_j) = self.backtrace(k, v_k)
        self.imply(j, v_j)
        if (self.PODEM()):
            return(True)
        self.imply(j, inv(v_j))
        if (self.PODEM()):
            return(True)
        self.imply(j, X)
        return(False)

    def genTestSet(self):
        test_set = []
        fault_set = set(self.fault_universe)
        while (fault_set):
            self.target_fault = fault_set.pop()
            self.initWireValue([])
            if (self.PODEM()):
                new_test_vec = []
                new_test_str = ""
                for pi in self.input_list:
                    if (pi.getValue() == D):
                        test_bit = 1
                    elif (pi.getValue() == D_bar):
                        test_bit = 0
                    else:
                        test_bit = pi.getValue()
                    new_test_vec.append(test_bit)
                    new_test_str.join(str(test_bit))
                print(new_test_str)
                test_set.append(new_test_str)
                new_detected_fault_set, detected_fault_str = self.getDetectedFaults(new_test_str)
                fault_set -= new_detected_fault_set
            else:
                print("Fault %s is undetectable!" %(self.target_fault))


def run(netlist_path, input_file_path, output_file_path, fault_file_path = None):
    print("Netlist Path: %s" %netlist_path)
    print("Input File Path: %s" %input_file_path)
    print("Output File Path: %s" %output_file_path)

    fault_str_list = []
    if (fault_file_path):
        print("Fault File Path: %s" %fault_file_path)
        fault_file = open(fault_file_path, "r")
        print("Read the list of fault to be simulated...")
        for line in fault_file:
            line = line.replace("x", "0")
            line = line.replace("u", "0")
            line = line.replace("X", "0")
            line = line.replace("U", "0")
            fault_str_list.append(line)
        print("Reading completed, %d faults read" % (len(fault_str_list)))
        fault_file.close()
    else:
        print("No fault definition file provided")
        print("Simulate all the stuck-at fault in the circuit")


    cir = Circuit(netlist_path)
    input_file = open(input_file_path, 'r')
    output_file = open(output_file_path, 'w')

    cir.initFaultUniverse(fault_str_list)
    inputs_str = input_file.readline()
    inputs_str = inputs_str.replace("\n", "")
    inputs_str = inputs_str.replace("x", "0")
    inputs_str = inputs_str.replace("u", "0")
    inputs_str = inputs_str.replace("X", "0")
    inputs_str = inputs_str.replace("U", "0")
    detected_fault_list, detected_fault_str = cir.getDetectedFaults(inputs_str)
    output_file.write(detected_fault_str)

    print("Input: \n%s" %(inputs_str))
    print("Output: \n%s" %(detected_fault_str))

    input_file.close()
    output_file.close()

def rand_run(netlist_path, target_coverage_str, fault_file_path = None):
    print("Netlist Path: %s" %netlist_path)
    print("Target coverage: %s" %target_coverage_str)

    fault_str_list = []
    if (fault_file_path):
        print("Fault File Path: %s" %fault_file_path)
        fault_file = open(fault_file_path, "r")
        print("Read the list of fault to be simulated...")
        for line in fault_file:
            line.replace("x", "0")
            line.replace("u", "0")
            line.replace("X", "0")
            line.replace("U", "0")
            fault_str_list.append(line)
        print("Reading completed, %d faults read" % (len(fault_str_list)))
        fault_file.close()
    else:
        print("No fault definition file provided")
        print("Simulate all the stuck-at fault in the circuit")

    cir = Circuit(netlist_path)
    target_coverage = float(target_coverage_str)
    cir.randomDetect(target_coverage, fault_str_list)

        
if __name__ == "__main__":
    cir = Circuit("circuits/and_or.txt")
    cir.initFaultUniverse(["2 0"])
    cir.genTestSet()

    # if (len(sys.argv) == 1):
    #     run("circuits/s27.txt", "inputs/s27_input_1.txt", "outputs/s27_output_1.txt")
    #     run("circuits/s27.txt", "inputs/s27_input_2.txt", "outputs/s27_output_2.txt")
    #     run("circuits/s298f_2.txt", "inputs/s298f_2_input_1.txt", "outputs/s298f_2_output_1.txt")
    #     run("circuits/s298f_2.txt", "inputs/s298f_2_input_2.txt", "outputs/s298f_2_output_2.txt")
    #     run("circuits/s344f_2.txt", "inputs/s344f_2_input_1.txt", "outputs/s344f_2_output_1.txt")
    #     run("circuits/s344f_2.txt", "inputs/s344f_2_input_2.txt", "outputs/s344f_2_output_2.txt")
    #     run("circuits/s349f_2.txt", "inputs/s349f_2_input_1.txt", "outputs/s349f_2_output_1.txt")
    #     run("circuits/s349f_2.txt", "inputs/s349f_2_input_2.txt", "outputs/s349f_2_output_2.txt")
    # elif (len(sys.argv) >= 5 and sys.argv[1] == "-run"):
    #     run(*sys.argv[2:])
    # elif (len(sys.argv) >= 4 and sys.argv[1] == "-rand_run"):
    #     rand_run(*sys.argv[2:])
    # else:
    #     print("Usage 1: ")
    #     print("python fault_simulator.py (No parameter)")
    #     print("\tFunction: simulate the 4 given circuits: s27, s298f_2, s344f_2, s249f_2 using given test vectors, considering all stuck-at faults\n")
# 
    #     print("Usage 2: ")
    #     print("python fault_simulator.py -run NETLIST_FILE_PATH INPUT_FILE_PATH OUTPUT_FILE_PATH [FAULT_FILE_PATH]")
    #     print("\tFunction: simulate a circuit (defined in NETLIST_FILE) with a test vector provided in the INPUT_FILE, print the results to OUTPUT_FILE, considering the faults defined in FAULT_FILE (optional)")
    #     print("\tExample 1: python fault_simulator.py -run circuits\s27.txt inputs\s27_input_3.txt outputs\s27_output_3.txt")
    #     print("\tExample 2: python fault_simulator.py -run circuits\s27.txt inputs\s27_input_3.txt outputs\s27_output_3.txt faults\s27_fault_1.txt\n")
# 
    #     print("Usage 3: ")
    #     print("python fault_simulator.py -rand_run NETLIST_FILE_PATH TARGET_COVERAGE [FAULT_FILE_PATH]")
    #     print("\tFunction: apply random test vectors to a circuit (defined in NETLIST_FILE), count the number of vectors needed to achieve the TARGET_COVERAGE, considering the faults defined in FAULT_FILE (optional)")
    #     print("\tExample 1: python fault_simulator.py -rand_run circuits\s27.txt 0.9")
    #     print("\tExample 2: python fault_simulator.py -rand_run circuits\s27.txt 0.9 faults\s27_fault_1.txt\n")
        
    