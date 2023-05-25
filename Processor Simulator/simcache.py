#!/usr/bin/python3

import argparse
import re

def print_cache_config(cache_name, size, assoc, blocksize, num_rows):
    """
    Prints out the correctly-formatted configuration of a cache.

    cache_name -- The name of the cache. "L1" or "L2"

    size -- The total size of the cache, measured in memory cells.
        Excludes metadata

    assoc -- The associativity of the cache. One of [1,2,4,8,16]

    blocksize -- The blocksize of the cache. One of [1,2,4,8,16,32,64])

    num_rows -- The number of rows in the given cache.

    sig: str, int, int, int, int -> NoneType
    """

    summary = "Cache %s has size %s, associativity %s, " \
        "blocksize %s, rows %s" % (cache_name,
        size, assoc, blocksize, num_rows)
    print(summary)

# Print out cache configurations
def print_cache_specs(cache_config):
    L1rows = int(cache_config[0] / (cache_config[1]*cache_config[2]))
    print_cache_config("L1", cache_config[0], cache_config[1], cache_config[2], L1rows)
    if len(cache_config) == 6:
        L2rows = int(cache_config[3] / (cache_config[4]*cache_config[5]))
        print_cache_config("L2", cache_config[3], cache_config[4], cache_config[5], L2rows)

def print_log_entry(cache_name, status, pc, addr, row):
    """
    Prints out a correctly-formatted log entry.

    cache_name -- The name of the cache where the event
        occurred. "L1" or "L2"

    status -- The kind of cache event. "SW", "HIT", or
        "MISS"

    pc -- The program counter of the memory
        access instruction

    addr -- The memory address being accessed.

    row -- The cache row or set number where the data
        is stored.

    sig: str, str, int, int, int -> NoneType
    """
    log_entry = "{event:8s} pc:{pc:5d}\taddr:{addr:5d}\t" \
        "row:{row:4d}".format(row=row, pc=pc, addr=addr,
            event = cache_name + " " + status)
    print(log_entry)

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

def main():
    parser = argparse.ArgumentParser(description='Simulate E20 cache')
    parser.add_argument('filename', help=
        'The file containing machine code, typically with .bin suffix')
    parser.add_argument('--cache', help=
        'Cache configuration: size,associativity,blocksize (for one cache) '
        'or size,associativity,blocksize,size,associativity,blocksize (for two caches)')
    cmdline = parser.parse_args()

    # Variable initiation
    memory = []
    for i in range(8192):
        memory.append(0)
    pc = 0
    regs = [0,0,0,0,0,0,0,0]
    cache_log = []

    # Loading machine code into the memory
    with open(cmdline.filename) as file:
        load_machine_code(file, memory)

    # memory, pc, regs = simulation(memory, pc, regs)

    if cmdline.cache is not None:
        parts = cmdline.cache.split(",")
        if len(parts) == 3 or len(parts) == 6:
            cache_config = [int(x) for x in parts]
        else:
            raise Exception("Invalid cache config")
        
        memory, pc, regs, cache_log = simulation(memory, pc, regs, cache_config, cache_log) # simulate the program
        print_cache_specs(cache_config) # print out the cache configuration
        for i in range(len(cache_log)): # print out each log entry 
            print_log_entry(cache_log[i][0], cache_log[i][1], cache_log[i][2], cache_log[i][3], cache_log[i][4])

def simulation(memory, pc, regs, cache_config, cache_log):
    # first initialization
    ir = memory[pc]
    opCode = ir >> 13
    reg1 = (ir >> 10) & 7
    reg2 = (ir >> 7) & 7
    reg3 = (ir >> 4) & 7
    func = ir & 15
    imm7 = ir & 127
    imm13 = ir & 8191

    # cache variables 
    twoCaches = False
    L1blocksize = cache_config[2]
    L1row = int(cache_config[0] / (cache_config[1]*L1blocksize))
    L1cache = create_cache(L1row, cache_config[1])
    L1status = create_status(L1row, cache_config[1])
    if (len(cache_config) == 6):
        twoCaches = True
        L2blocksize = cache_config[5]
        L2row = int(cache_config[3] / (cache_config[4]*L2blocksize))
        L2cache = create_cache(L2row, cache_config[4])
        L2status = create_status(L2row, cache_config[4])

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
                if twoCaches: # L1 and L2 cache
                    row = [(address//L1blocksize)%L1row, (address//L2blocksize)%L2row]
                    tag = [(address//L1blocksize)//L1row, (address//L2blocksize)//L2row]
                    L1cache, L1status, L2cache, L2status, cache_log = lw_two_caches(address, pc, row, tag, L1cache, L1status, L2cache, L2status, cache_log)
                else: # Only L1 cache, no L2 cache
                    row = (address//L1blocksize)%L1row
                    tag = (address//L1blocksize)//L1row
                    L1cache, L1status, cache_log = lw_one_cache(address, pc, row, tag, L1cache, L1status, cache_log)
            pc += 1
        elif opCode == 5: # sw
            # if address is out of range, ignore the first three bits
            address = pc_out_of_range_check(regs[reg1] + seven_bit_signed_number_to_decimal(imm7)) 
            memory[address] = regs[reg2]
            if twoCaches: # L1 and L2 cache
                row = [(address//L1blocksize)%L1row, (address//L2blocksize)%L2row]
                tag = [(address//L1blocksize)//L1row, (address//L2blocksize)//L2row]
                L1cache, L1status, L2cache, L2status, cache_log = sw_two_caches(address, pc, row, tag, L1cache, L1status, L2cache, L2status, cache_log)
            else: # Only L1 cache, no L2 cache
                row = (address//L1blocksize)%L1row
                tag = (address//L1blocksize)//L1row
                L1cache, L1status, cache_log = sw_one_cache(address, pc, row, tag, L1cache, L1status, cache_log)
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

    return memory, virtual_pc, regs, cache_log

# Handles lw instructions with L1 and L2 cache 
def lw_two_caches(addr, pc, row, tag, L1cache, L1status, L2cache, L2status, cache_log):
    if tag[0] in L1cache[row[0]]: # hit in L1 cache
        cache_log.append(["L1", "HIT", pc, addr, row[0]])
    else: 
        cache_log.append(["L1", "MISS", pc, addr, row[0]])
        if tag[1] in L2cache[row[1]]: # hit in L2 cache, miss in L1 cache
            cache_log.append(["L2", "HIT", pc, addr, row[1]])
            L1cache, L1status = update_cache_and_status(row[0], tag[0], L1cache, L1status)
        else: # miss in L2 cache, miss in L1 cache
            cache_log.append(["L2", "MISS", pc, addr, row[1]])
            L1cache, L1status = update_cache_and_status(row[0], tag[0], L1cache, L1status)
            L2cache, L2status = update_cache_and_status(row[1], tag[1], L2cache, L2status)
    return L1cache, L1status, L2cache, L2status, cache_log

# Handles lw instructions with only L1 cache, no L2 cache
def lw_one_cache(addr, pc, row, tag, L1cache, L1status, cache_log):
    if tag in L1cache[row]: # hit in L1 cache
        cache_log.append(["L1", "HIT", pc, addr, row])
    else: # miss in L1 cache
        cache_log.append(["L1", "MISS", pc, addr, row])
        L1cache, L1status = update_cache_and_status(row, tag, L1cache, L1status)
    return L1cache, L1status, cache_log

# Handles sw instructions with L1 and L2 cache 
def sw_two_caches(addr, pc, row, tag, L1cache, L1status, L2cache, L2status, cache_log):
    cache_log.append(["L1", "SW", pc, addr, row[0]])
    cache_log.append(["L2", "SW", pc, addr, row[1]])
    L1cache, L1status = update_cache_and_status(row[0], tag[0], L1cache, L1status) # update L1 cache and L1 blocks order
    L2cache, L2status = update_cache_and_status(row[1], tag[1], L2cache, L2status) # update L2 cache and L2 blocks order
    return L1cache, L1status, L2cache, L2status, cache_log

# Handles sw instructions with only L1 cache, no L2 cache
def sw_one_cache(addr, pc, row, tag, L1cache, L1status, cache_log):
    cache_log.append(["L1", "SW", pc, addr, row])
    L1cache, L1status = update_cache_and_status(row, tag, L1cache, L1status) # update L1 cache and L1 blocks order
    return L1cache, L1status, cache_log

# Update and evict caches based on LRU policy 
def update_cache_and_status(row, tag, cache, status):
    LRU_index = find_LRU_index(status[row]) # index of the least recently used block
    for i in range(len(status[row])): # update the order list since a new access is made
        if status[row][i] < status[row][LRU_index]:
            status[row][i] += 1
    status[row][LRU_index] = 0 # set the block that is accessed to the front of the list or order
    cache[row][LRU_index] = tag # update the tag value in cache
    return cache, status

# Find the index of the least recently used block in a specific row
def find_LRU_index(list):
    temp = list[0]
    index = 0
    for i in range(len(list)): # loop through the elements to check order
        if list[i] > temp:
            temp = list[i]
            index = i
    return index

# Use to create and initialize cache
def create_cache(row, col):
    output = []
    for i in range(row):
        temp = []
        for j in range(col):
            temp.append(-1)
        output.append(temp)
    return output

# Create a 2D list that is later used to track the order of which blocks are accessed
def create_status(row, col):
    output = []
    for i in range(row):
        temp = []
        for j in range(col):
            temp.append(j)
        output.append(temp)
    return output

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