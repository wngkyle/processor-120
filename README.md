# Processor 120

### Table of Contents

- [Assembler](#assembler)
- [Disassembler](#disassembler)
- [Simulator](#simulator)
- [Built With](#built-with)
- [Technology Used](#technology-used)

### Assembler

The assembler developed is case insensitive, meaning both uppercase or lowercase operation codes and labels are acceptable. This is done by converting all letters to lowercase even before starting formatting the instructions, so case doesn't affect the final result. The program also allows spaces between register values, immediate values, and labels as long as there is one space between the operation code and register or immediate values. For instance, `addi $6, $5, var4` is the most desired format, but the program also allows the following format: `addi $6,$5,var4`, `addi $6,$5 ,var4`, or `addi $6,$5,var4`. The only format that may cause error is when the space between operation code and register or immediate values is removed, or incorrect assembly code. For instance, like this: `addi$6,$5,var4`, `addi$6, $5, var4`, `jump 189`, or `sub $5$6@`. In addition, the program also tolerates multiple labels in one line. For instance, inputting the following set of instructions will not crash the program: 

 - `beginning: start: end: addi $5, $2, 0`

 - `beginning: start: end: done: addi $5, $2, 0`

 - `loop1: loop5: anotherLoopHere: lastLoop: addi $5, $2, 0`

After reading the instructions from the assembly language files, the program converts all uppercase letters in the instructions to lowercase using the `all_to_lowercase()` function. The reason why I chose to convert everything to lowercase first is because this will facilitate the formatting process a lot, and it also prevents double labeling when setting up the labels. With everything in lowercase, the program marks all the labels using the `marking_labels()` function. This function stores all the labels and the address they are pointing to in a dictionary. The name of the label is the key, and the address is the value. Instruction lines with only labels are also removed from the list called instructions in this function. Unnecessary elements like comma, $, (), and " " are then removed using the `remove_symbols()` function. This is because symbols might confuse the program when trying to convert from assembly to machine code. With everything formatted, the instructions along with the dictionary holding all the labels are then passed to the `convert_assembly_to_machine` function. Using other sub-functions like `instructions_with_three_registers()`, `instructions_with_two_registers()`, `instructions_with_no_registers()`, `movi_to_addi()`, `nop_to_add()`, `fill()`, and `halt_to_j()`, the `convert_assembly_to_machine()` functions converts all the assembly instructions into machine code and returns them back to `main()`. The results are then displayed using the given `print_machine_code()` function.

### Disassembler 

The program for disassembler can be divided into three major parts. The first part includes constants initialization, `load_machine_code function()`, `print_state function()`, and `main()`. `load_machine_code()` is used to load the machine code into the list named memory, and `print_state()` is used to print register value, pc value, and memory value after simulation.

The second part is the `simulation()` function, which is used to carry out the simulation and imitates how an E20 processor behaves. The instruction is first processed, creating different variables that contain `opCode`, `reg1`, `reg2`, `reg3`, `func`, `imm7`, and `imm13`. The program then enters a while loop that only stops when a halt command is detected. When a halt command is detected, the program jumps out of the loop. The first if statement in the loop takes care of all instructions with three register arguments. This includes `add`, `sub`, `or`, `and`, `slt`, `jr`. In `add`, if the result is out of range, only the least significant 13 bits will be taken. In `sub`, if the result is negative, it will be converted into 2's complement and stored as an unsigned 16-bit number. The second if statement handles `slti`, where the 7-bit immediate number is sign extended to perform an unsigned comparison. The third and fourth if statement handles lw and sw. The calculated memory address takes only the least significant 13 bits and the rest is ignored. The fifth if statement deals with `jeq`. If the comparison is true, `pc` is set to the sum of the current `pc` plus one plus the 7-bit signed immediate. The sixth if statement handles addi, and the seventh and eighth handles j and jal respectively. The instruction variables are updated at the end of every cycle.

The last part is the helper functions. `pc_out_of_range_check()` checks if `pc` is greater than 8191. If greater, the most significant 3 bits will be removed. sign_extend extends a 7-bit signed number to 16-bit. seven_bit_signed_number_to_decimal converts signed 7 bits into decimal form. negative_decimal_to_signed_16_bits converts a negative decimal into a signed 16-bit number.

In addition to the features described above, the simulator is capable of tolerating register $0 modification. Since register $0 is immutable, trying to modify it does not produce any effect but is valid. The simulator will simply ignore the instruction and move on to the next one. When the program reaches the last instruction, it will automatically loop back to the first instruction and continue executing the rest of the program until a halt command is detected. However, the program requires a correct machine code program and does not detect any machine code error.


### Simulator

This simulator simulates the operation of the processor. The strength of this simulator is it is capable of simulating up to two caches, and the configurations of the cache are not fixed. They can be customized and are specified by the users. However, the weakness is when incorrect cache size, associativity, or block size are passed into the parameters, the program does not automatically correct or detect the error. Users have to ensure the right values are passed to prevent any error or crash.

Since the fetch stage is not considered in this project, the only instructions that can modify and read memory are the `lw` and `sw` instructions. The two instructions have their own helper functions to help keep track of and update the current status of the memory and caches. For `lw`, `lw_two_caches()` is used when two caches are initialized, and `lw_one_cache()` is used when only one cache is initialized. Similarly, for `sw`, `sw_two_caches()` is used when there are two caches, and `sw_one_cache()` is used when there is only one cache. For both instructions, when called, the program will determine if one or two caches are initialized and then calculate the row and tag of the address in each cache.

For `lw`, with row and tag computed, the program will then the help functions to see if the value exists in the caches. For instance, when two caches are initialized, if miss in L1, it will search L2. If it misses again in L2, then it will pull the value from memory. If hit in L1, then it will stop the search and return. The same concept applies when there is only one cache. Any search in the cache that results in a miss will end up calling the `update_cache_and_status()` function. This function will update the missed value into the cache either from an upper-level cache or from the main memory. In addition, update_cache_and_status also updates the order in which blocks have been used to help implement the LRU policy for eviction.

For `sw`, the `update_cache_and_status()` function is called immediately after entering the function. The `sw` instruction also uses the write-through with a write-allocate policy for writing values. Lastly, the helper functions for both instructions also update the cache log whenever they are called regardless of the search result.

### Built With

- C++
- Python
- x86 Assembly Language

### Technologies Used 

- Microsoft Visual Studio Code
- Github


