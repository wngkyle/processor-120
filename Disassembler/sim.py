#!/usr/bin/python3
"""
CS-UY 2214
Kyle 
E20 simulator
sim.py
"""
from collections import namedtuple
import re
import argparse

# Some helpful constant values that we'll be using.
Constants = namedtuple("Constants",["NUM_REGS", "MEM_SIZE", "REG_SIZE"])
constants = Constants(NUM_REGS = 8, 
                      MEM_SIZE = 2**13,
                      REG_SIZE = 2**16)

def load_machine_code(machine_code, mem):
    """
    Loads an E20 machine code file into the list
    provided by mem. We assume that mem is
    large enough to hold the values in the machine
    code file.
    sig: list(str) -> list(int) -> NoneType
    """
    machine_code_re = re.compile("^ram\[(\d+)\] = 16'b(\d+);.*$")
    expectedaddr = 0
    for line in machine_code:
        match = machine_code_re.match(line)
        if not match:
            raise ValueError("Can't parse line: %s" % line)
        addr, instr = match.groups()
        addr = int(addr,10)
        instr = int(instr,2)
        if addr != expectedaddr:
            raise ValueError("Memory addresses encountered out of sequence: %s" % addr)
        if addr >= len(mem):
            raise ValueError("Program too big for memory")
        expectedaddr += 1
        mem[addr] = instr

def print_state(pc, regs, memory, memquantity):
    """
    Prints the current state of the simulator, including
    the current program counter, the current register values,
    and the first memquantity elements of memory.
    sig: int -> list(int) -> list(int) - int -> NoneType
    """
    print("Final state:")
    print("\tpc="+format(pc,"5d"))
    for reg, regval in enumerate(regs):
        print(("\t$%s=" % reg)+format(regval,"5d"))
    line = ""
    for count in range(memquantity):
        line += format(memory[count], "04x")+ " "
        if count % 8 == 7:
            print(line)
            line = ""
    if line != "":
        print(line)

def main():
    # initializing variables
    memory = []
    for i in range(8192):
        memory.append(0)
    pc = 0
    regs = [0,0,0,0,0,0,0,0]

    parser = argparse.ArgumentParser(description='Simulate E20 machine')
    parser.add_argument('filename', help='The file containing machine code, typically with .bin suffix')
    cmdline = parser.parse_args()

    with open(cmdline.filename) as file:
        load_machine_code(file, memory)

    memory, pc, regs = simulation(memory, pc, regs)
    print_state(pc, regs, memory, 128)

def simulation(memory, pc, regs):
    # first initialization
    ir = memory[pc]
    opCode = ir >> 13
    reg1 = (ir >> 10) & 7
    reg2 = (ir >> 7) & 7
    reg3 = (ir >> 4) & 7
    func = ir & 15
    imm7 = ir & 127
    imm13 = ir & 8191

    while(opCode != 2 or pc != imm13): # while opCode != halt
        if opCode == 0:
            if func != 8: # add, sub, or, and, slt
                if reg3 != 0: # check if regDst is $0, if is $0, then no modification will be made to the register
                    if func == 0: # add
                        aluOut = regs[reg1] + regs[reg2]
                        if aluOut > 65535: # if result out of range, ignore the out of range bit, only possible to overflow 1 bit so just minus 65536
                            regs[reg3] = aluOut - 65536
                        else:
                            regs[reg3] = aluOut
                    elif func == 1: # sub
                        aluOut = regs[reg1] - regs[reg2]
                        if aluOut < 0: # If result is negative, convert to 2's complement
                            regs[reg3] = aluOut & 65535
                        else:
                            regs[reg3] = aluOut
                    elif func == 2: # or
                        regs[reg3] = regs[reg1] | regs[reg2]
                    elif func == 3: # and
                        regs[reg3] = regs[reg1] & regs[reg2]
                    else: # slt
                        regs[reg3] = int(regs[reg1] < regs[reg2])
                pc += 1
            else: # jr
                pc = regs[reg1]
        elif opCode == 7: # slti
            if reg2 != 0: # check if regDst is $0, if is $0, then no modification will be made to the register
                regs[reg2] = int(regs[reg1] < sign_extend(imm7))
            pc += 1
        elif opCode == 4: # lw
            if reg2 != 0: # check if regDst is $0, if is $0, then no modification will be made to the register
                # if address is out of range, ignore the first three bits
                address = pc_out_of_range_check(regs[reg1] + seven_bit_signed_number_to_decimal(imm7))
                regs[reg2] = memory[address]
            pc += 1
        elif opCode == 5: # sw
            # if address is out of range, ignore the first three bits
            address = pc_out_of_range_check(regs[reg1] + seven_bit_signed_number_to_decimal(imm7)) 
            memory[address] = regs[reg2]
            pc += 1
        elif opCode == 6: # jeq
            if regs[reg1] == regs[reg2]:
                pc = pc + 1 + seven_bit_signed_number_to_decimal(imm7)
            else:
                pc += 1
        elif opCode == 1: # addi
            if reg2 != 0: # check if regDst is $0, if is $0, then no modification will be made to the register
                aluOut = regs[reg1] + seven_bit_signed_number_to_decimal(imm7)
                if aluOut > 65535: # if result out of range, ignore the out of range bit, only possible to overflow 1 bit so just minus 65536
                    regs[reg2] = aluOut - 65536
                elif aluOut < 0: # register underflow
                    print("aluOut:", aluOut)
                    regs[reg2] = aluOut & 65535
                else:
                    regs[reg2] = aluOut
            pc += 1
        elif opCode == 2: # j
            pc = imm13 # jumps unconditionally to imm
        else: # jal
            regs[7] = pc + 1 # stores the address of the next intruction in register $7
            pc = imm13 # jumps unconditionally to imm

        # if pc is out of range, ignore the first three bits
        virtual_pc = pc_out_of_range_check(pc)

        # update variables
        ir = memory[virtual_pc]
        opCode = ir >> 13
        reg1 = (ir >> 10) & 7
        reg2 = (ir >> 7) & 7
        reg3 = (ir >> 4) & 7
        func = ir & 15
        imm7 = ir & 127
        imm13 = ir & 8191

    return memory, virtual_pc, regs

# Check if pc is out of range
def pc_out_of_range_check(input):
    if input > 8191 or input < 0: 
        input = input & 8191
    return input

# sign extend 7-bit to 16-bit 
def sign_extend(input):
    if input >= 64:
        input = input | 65408
    return input

# Convert 7-bit signed number to decimal form
def seven_bit_signed_number_to_decimal(input):
    if input >= 64:
        input = input & 63
        input -= 64
    return input

if __name__ == "__main__":
    main()
#ra0Eequ6ucie6Jei0koh6phishohm9
