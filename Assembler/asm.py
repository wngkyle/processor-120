#!/usr/bin/python3
import argparse

##################################################################################################################################
#                                                          MAIN                                                                  #
##################################################################################################################################

def print_machine_code(address, num):
    """
    print_line(address, num)
    Print a line of machine code in the required format.
    Parameters:
        address: int = RAM address of the instructions
        num: int = numeric value of machine instruction 

    For example: 
        >>> print_machine_code(3, 42)
        ram[3] = 16'b0000000000101010;    
    """
    instruction_in_input = format(num,'016b')
    print("ram[%s] = 16'b%s;" % (address, instruction_in_input))

def main():
    parser = argparse.ArgumentParser(description='Assemble E20 files into machine code')
    parser.add_argument('filename', help='The file containing assembly language, typically with .s suffix')
    cmdline = parser.parse_args()

    # our final output is a list of ints values representing
    # machine code instructions
    instructions=[]
    labels = {}
    address = 0

    # iterate through the line in the file, construct a list
    # of numeric values representing machine code
    with open(cmdline.filename) as f:
        for line in f:
            line = line.split("#",1)[0].strip()    # remove comments
            if (len(line) != 0) :
                line = line.split(" ")   # Parse the line by whitespaces
                instructions.append(line)  # TODO change this. generate the machine code
    
    instructions = all_to_lowercase(instructions)
    instructions, labels = marking_labels(instructions)
    instructions = remove_symbols(instructions)
    instructions = convert_assembly_to_machine(instructions, labels)

    # print out each instruction in the required format
    for address, instruction in enumerate(instructions):
        print_machine_code(address, instruction) 


##################################################################################################################################
#                                                 HELPER FUNCTIONS                                                               #
##################################################################################################################################

# this function converts negative decimal into 2's complement form
def negative_decimal_to_2_complement(num):
    binary = bin(num)[3:]
    new_binary = ""
    ones = 7 - len(binary)
    
    for i in range(ones):
        new_binary += "1"
    
    for i in range(len(binary)):
        if binary[i] == "1":
            new_binary += "0"
        else:
            new_binary += "1"

    result = binary_to_decimal(int(new_binary))
    result += 1
    return result

# given a binary input, this function will return a decimal output
def binary_to_decimal(input):
    result, i = 0, 0
    while(input != 0):
        digit = input % 10
        result = result + digit * pow(2, i)
        input = input//10
        i += 1
    return result

##################################################################################################################################
#                                         CONVERTING FROM ASSEMBLY TO MACHINE CODE                                               #
##################################################################################################################################
 
# add, sub, or, and, slt
# manage add, sub, or, and, slt operation
def instructions_with_three_registers(input, op):
    reg_dst, reg_srcA, reg_srcB = int(input[1]), int(input[2]), int(input[3])
    machine_code = op | reg_srcA << 10 | reg_srcB << 7 | reg_dst << 4
    return machine_code

# lw, sw, jeq, slti, addi
# manage lw, sw, jeq, slti, addi operation
def instructions_with_two_registers(input, op, labels, current_addr):
    if op == 32768 or op == 40960: # lw, sw
        if input[2].isdigit() or input[2].find("-") != -1: # if imm is not a label
            reg_addr, reg_dst, imm = int(input[3]), int(input[1]), int(input[2])
            if imm < 0: # imm < 0
                imm = negative_decimal_to_2_complement(int(input[2])) # convert to 2's complement
            machine_code = op | reg_addr << 10 | reg_dst << 7 | imm
            return machine_code
        else: # if imm is a label
            reg_addr, reg_dst, label_imm = int(input[3]), int(input[1]), labels[input[2]]
            machine_code = op | reg_addr << 10 | reg_dst << 7 | label_imm
            return machine_code
    elif op == 49152: # jeq
        if input[3].isdigit() or input[3].find("-") != -1: # if imm is not a label
            reg_srcA, reg_srcB, imm = int(input[1]), int(input[2]), int(input[3])
            #  pc = pc + 1 + rel_imm
            imm -= current_addr
            imm -= 1
            if imm < 0: # imm < 0
                imm = negative_decimal_to_2_complement(int(input[3])) # convert to 2's complement
            # else: # imm >= 0
            #     imm = int(input[3])
            machine_code = op | reg_srcA << 10 | reg_srcB << 7 | imm
            return machine_code
        else: # if imm is a label
            reg_srcA, reg_srcB, label_imm = int(input[1]), int(input[2]), labels[input[3]]
            #  pc = pc + 1 + rel_imm
            label_imm -= current_addr
            label_imm -= 1
            if label_imm < 0:
                label_imm = negative_decimal_to_2_complement(label_imm)
            machine_code = op | reg_srcA << 10 | reg_srcB << 7 | label_imm
            return machine_code
    else: # slti, addi
        if input[3].isdigit() or input[3].find("-") != -1: # if imm is not a label
            reg_dst, reg_src, imm = int(input[1]), int(input[2]), int(input[3])
            if imm < 0:
                imm = negative_decimal_to_2_complement(int(input[3]))
            machine_code = op | reg_dst << 7 | reg_src << 10 | imm
            
            return machine_code
        else: # if imm is a label
            reg_dst, reg_src, label_imm = int(input[1]), int(input[2]), labels[input[3]]
            machine_code = op | reg_dst << 7 | reg_src << 10 | label_imm
            return machine_code
         
# j, jal
# manage j, jal operation
def instructions_with_no_registers(input, op, labels):
    if op == 16384: # j
        if input[1].isdigit():
            imm = int(input[1])
            machine_code = op | imm
            return machine_code
        else:
            imm = labels[input[1]]
            machine_code = op | imm
            return machine_code
    else: # jal
        if input[1].isdigit():
            imm = int(input[1])
            machine_code = op | imm
            return machine_code
        else:
            imm = labels[input[1]]
            machine_code = op | imm
            return machine_code

# main function for converting assembly code to machine code
def convert_assembly_to_machine(instructions, labels):
    machine = []

    for i in range(len(instructions)):
        if instructions[i][0] == "add":
            machine.append(instructions_with_three_registers(instructions[i], 0))
        elif instructions[i][0] == "sub":
            machine.append(instructions_with_three_registers(instructions[i], 1))
        elif instructions[i][0] == "or":
            machine.append(instructions_with_three_registers(instructions[i], 2))
        elif instructions[i][0] == "and":
            machine.append(instructions_with_three_registers(instructions[i], 3))
        elif instructions[i][0] == "slt":
           machine.append(instructions_with_three_registers(instructions[i], 4))
        elif instructions[i][0] == "jr":
            machine_code = 8 | int(instructions[i][1]) << 10
            machine.append(machine_code)
        elif instructions[i][0] == "slti":
            machine.append(instructions_with_two_registers(instructions[i], 57344, labels, i))
        elif instructions[i][0] == "lw":
            machine.append(instructions_with_two_registers(instructions[i], 32768, labels, i))
        elif instructions[i][0] == "sw":
            machine.append(instructions_with_two_registers(instructions[i], 40960, labels, i))
        elif instructions[i][0] == "jeq":
            machine.append(instructions_with_two_registers(instructions[i], 49152, labels, i))
        elif instructions[i][0] == "addi":
            machine.append(instructions_with_two_registers(instructions[i], 8192, labels, i))
        elif instructions[i][0] == "j":
            machine.append(instructions_with_no_registers(instructions[i], 16384, labels))
        elif instructions[i][0] == "jal":
            machine.append(instructions_with_no_registers(instructions[i], 24576, labels))
        elif instructions[i][0] == "movi":
            temp = movi_to_addi(instructions[i])
            machine.append(instructions_with_two_registers(temp, 8192, labels, i))
        elif instructions[i][0] == "nop":
            temp = nop_to_add()
            machine.append(instructions_with_three_registers(temp, 0))
        elif instructions[i][0] == ".fill":
            machine.append(fill(instructions[i], labels))
        elif instructions[i][0] == "halt":
            temp = halt_to_j(i)
            machine.append(instructions_with_no_registers(temp, 16384, labels))
    
    return machine

# convert movi to equivalent addi instruction
def movi_to_addi(input):
    input = ["addi", input[1], "0", input[2]]
    return input

# convert nop to equivalent add instruction
def nop_to_add():
    input = ["add", "0", "0", "0"]
    return input

def fill(input, labels):
    if input[1].isdigit(): 
        machine_code = int(input[1])
    else:
        machine_code = labels[input[1]]
    return machine_code

# convert halt to equivalent j instruction
def halt_to_j(current_addr):
    input = ["j", str(current_addr)]
    return input

##################################################################################################################################
#                                              FORMATTING RAW ASSEMBLY CODE                                                      #
##################################################################################################################################
# convert everything to lowercase
def all_to_lowercase(instructions):
    for i in range(len(instructions)):
        for j in range(len(instructions[i])):
            instructions[i][j] = instructions[i][j].lower()
    return instructions

# set up labels and remove them from the instructions
def marking_labels(instructions):
    labels = {}
    to_remove = []
    counter = 0

    for i in range(len(instructions)):
        if instructions[i][0].find(":") != -1: # label found
            # one label with instruction in next line
            if len(instructions[i]) == 1: 
                # creates label with instruction address, and stores it in dictionary
                # Also slice the string, so colon is removed
                labels[instructions[i][0][:len(instructions[i][0])-1]] = i - counter
                # since there's only label in this line, this line will be removed later
                to_remove.append(i - counter)
                counter += 1
            
            # more than one label with instruction in the next line
            elif instructions[i][1].find(":") != -1 and instructions[i][len(instructions[i])-1].find(":") != -1: 
                print("HERE:", instructions[i])
                for j in range(len(instructions[i])):
                    labels[instructions[i][j][:len(instructions[i][j])-1]] = i - counter
                to_remove.append(i - counter)
                counter += 1
            
            # more than one label with instruction in the same line
            elif instructions[i][1].find(":") != -1:
                start = 0
                while(instructions[i][start].find(":") != -1):
                    start +=1 
                new_instruction = instructions[i][start:]
                for j in range(start):
                    labels[instructions[i][j][:len(instructions[i][j])-1]] = i - counter     
                instructions[i] = new_instruction           

            # one label with instruction in the same line
            else:
                # creates label along with the instruction address that it points to 
                # Also slice the string, so colon is removed
                labels[instructions[i][0][:len(instructions[i][0])-1]] = i - counter
                instructions[i] = instructions[i][1:]

    # remove single line labels from the list
    for i in to_remove:
        instructions.pop(i)
    return instructions, labels

# remove comma, spaces, and $ from the instruction line
# format lw and sw instructions properly
def remove_symbols(instructions):
    result = []
    sub_list =[]

    # removing "," 
    for i in range(len(instructions)):
        sub_list =[]
        for j in range(len(instructions[i])):
            if instructions[i][j].find(",") != -1:
                temp = instructions[i][j].split(",")
                for k in range(len(temp)):
                    if not(temp[k].isspace() or temp[k] == ""):
                        sub_list.append(temp[k])
            else:
                sub_list.append(instructions[i][j])
        result.append(sub_list)
        del sub_list

    # removing empty elements
    result = remove_empty_elements(result)

    # dealing with lw and sw
    # separate var1($1) in to var1, 1
    for i in range(len(result)):
        if result[i][0] == "lw" or result[i][0] == "sw":
            address = result[i][2]
            index = address.find("(")
            result[i][2] = result[i][2][0:index]
            result[i].append(address[index+1:len(address)-1])

    # removing "$"
    for i in range(len(result)):
        for j in range(len(result[i])):
            if result[i][j].find("$") != -1 and len(result[i][j]) == 2:
                result[i][j] = result[i][j][1:]
    return result

# remove empty elements in the instructions
def remove_empty_elements(instructions):
    result = []

    for i in range(len(instructions)):
        sub_list = []
        for j in range(len(instructions[i])):
            if not(instructions[i][j] == "" or instructions[i][j].isspace()):
                sub_list.append(instructions[i][j])
        result.append(sub_list)
        del sub_list

    return result


##################################################################################################################################
#                                                         OTHER                                                                  #
##################################################################################################################################
# for debugging purposes
# provide better code visualization
def print_compare(before, after):
    for i in range(len(before)):
        print(before[i], after[i])

if __name__ == "__main__":
    main()

##################################################################################################################################
#                                                         TESTS                                                                  #
##################################################################################################################################
# test for function instructions_with_two_registers
def test1(labels): 
    t1 = ['jeq', '1', '0', 'done'] # ram[1] = 16'b1100010000000010; 50178
    t2 = ['addi', '1', '1', '-1'] # ram[2] = 16'b0010010011111111; 9471
    t3 = ['addi', '1', '1', '-1'] # ram[4] = 16'b0010010011111111; 9471
    t4 = ['slti', '5', '1', '10'] # ram[4] = 16'b1110011010001010; 59018 
    t5 = ['jeq', '5', '6', 'done'] # ram[5] = 16'b1101011101111101; 55165
    t6 = ['addi', '1', '1', '-3'] # ram[6] = 16'b0010010011111101; 9469
    t7 = ['lw', '1', 'var1', '0'] # ram[0] = 16'b1000000010001001; 32905
    t8 = ['lw', '2', 'var2', '0'] # ram[1] = 16'b1000000100001010; 33034
    t9 = ['sw', '3', 'var3', '0'] # ram[4] = 16'b1010000110001011; 41355
    t10 = ['lw', '7', '11', '0'] # ram[5] = 16'b1000001110001011; 33675
    t11 = ['addi', '6', '5', 'var4'] # ram[7] = 16'b0011011100001100; 14092
    t12 = ['addi', '1', '0', '1'] # ram[0] = 16'b0010000010000001; 8321
    t13 = ['addi', '2', '0', '2'] # ram[2] = 16'b0010000100000010; 8450	
    t14 = ['addi', '3', '0', '3'] # ram[4] = 16'b0010000110000011; 8579

    #loop1 (Checked)
    # print(bin(instructions_with_two_registers(t1, 49152, labels, 1)))

    # loop2 (Checked)
    # print(instructions_with_two_registers(t2, 8192, labels, 2))
    # print(instructions_with_two_registers(t3, 8192, labels, 4))

    # loop3 (Checked)
    # print(instructions_with_two_registers(t4, 57344, labels, 4))
    # print(instructions_with_two_registers(t5, 49152, labels, 5))
    # print(instructions_with_two_registers(t6, 8192, labels, 6))

    # vars1 (Checked)
    # print(instructions_with_two_registers(t7, 32768, labels, 0))
    # print(instructions_with_two_registers(t8, 32768, labels, 1))
    # print(instructions_with_two_registers(t9, 40960, labels, 4))
    # print(instructions_with_two_registers(t10, 32768, labels, 5))
    # print(instructions_with_two_registers(t11, 8192, labels, 7))

    # subroutine1 (Checked)
    # print(instructions_with_two_registers(t12, 8192, labels, 0))
    # print(instructions_with_two_registers(t13, 8192, labels, 2))
    # print(instructions_with_two_registers(t14, 8192, labels, 4))

    # subroutine2

# test for function instructions_with_three_register
def test2(): 

    # vars1 (Checked)
    t1 = ['and', '3', '1', '2'] # ram[2] = 16'b0000010100110011; 1331
    t2 = ['or', '4', '1', '2'] # ram[3] = 16'b0000010101000010;	1346
    # print(instructions_with_three_registers(t1, 3))
    # print(instructions_with_three_registers(t2, 2))

    # subroutine2 (Checked)
    t3 = ['add', '2', '0', '1'] # ram[2] = 16'b0000000010100000; 160
    t4 = ['add', '3', '0', '1'] # ram[5] = 16'b0000000010110000; 176
    # print(instructions_with_three_registers(t3, 0))
    # print(instructions_with_three_registers(t4, 0))

    # other test cases (Checked)
    t5 = ["sub", "2", "6", "7"] # 000 110 111 010 0001 : 7073
    t6 = ["slt", "7", "1", "5"] # 000 001 101 111 0100 : 1780
    # print(instructions_with_three_registers(t5, 1))
    # print(instructions_with_three_registers(t6, 4))

# test for jr
def test3(): 
    # subroutine1 (Checked)
    t1 = ["jr", "7"] # ram[5] = 16'b0001110000001000; 7176
    machine_code = 8 | int(t1[1]) << 10
    print(machine_code)

# test for instructions_with_no_register
def test4(labels): 
    #loop1 (Checked)
    t1 = ['j', 'beginning'] # ram[3] = 16'b0100000000000001; 16385
    # print(instructions_with_no_registers(t1, 16384, labels))

    #loop2 (Checked)
    t2 = ['j', 'beginning'] # ram[1] = 16'b0100000000000011; 16387
    t3 = ['j', 'beginning'] # ram[5] = 16'b0100000000000011; 16387
    # print(instructions_with_no_registers(t2, 16384, labels))
    # print(instructions_with_no_registers(t3, 16384, labels))

    #loop3 (Checked)
    t4 = ['j', 'beginning'] # ram[2] = 16'b0100000000000100; 16388
    t5 = ['j', 'beginning'] # ram[7] = 16'b0100000000000100; 16388
    # print(instructions_with_no_registers(t4, 16384, labels))
    # print(instructions_with_no_registers(t5, 16384, labels))

    #subroutine1 (Checked)
    t6 = ['jal', 'proc'] # ram[1] = 16'b0110000000000100; 24580
    # print(instructions_with_no_registers(t6, 24576, labels))

    #subroutine2 (Checked)
    t7 = ['jal', 'quadruple'] # ram[1] = 16'b0110000000000111; 24583
    t8 = ['jal', 'quadruple'] # ram[4] = 16'b0110000000000111; 24583
    # print(instructions_with_no_registers(t7, 24576, labels))
    # print(instructions_with_no_registers(t8, 24576, labels))

    # other test cases (Checked)
    t9 = ["j", "20"] # 010 0000000010100  16404
    t10 = ["jal", "5698"] # 011 1011001000010 30274
    # print(instructions_with_no_registers(t9, 16384, labels))
    # print(instructions_with_no_registers(t10, 24576, labels))
