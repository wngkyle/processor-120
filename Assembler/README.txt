Name: Kyle Wang
Email: ww2301@nyu.edu

The E20 assembler program is completed. It was able to pass the 9 test cases on Gradescope. The assembler developed is case insensitive, 
meaning both uppercase or lowercase operation codes and labels are acceptable. This is done by converting all letters to lowercase even 
before start formatting the instructions, so case doesn't affect the final result. The program also allow spaces between register values,
immediate values, and labels as long as there is one space between operation code and register or immediate values. For instance, 
{addi $6, $5, var4} is the most desired format, but the program also allow the following format: {addi $6,$5,var4}, {addi $6,$5 ,var4},
or {addi $6,$5,var4}. The only format that may cause error is when the space between operation code and register or immmediate values is
removed, or incorrect assembly code. For instance, like this: {addi$6,$5,var4}, {addi$6, $5, var4}, {jump 189}, or {sub $5$6@}.
In addition, the program also tolerates mutliple labels in one line. For instance, inputting the following set of instructions will not 
crash the program: 

 - beginning: start: end:
        addi $5, $2, 0
 - beginning: start: end: done: addi $5, $2, 0
 - loop1: loop5: anotherLoopHere: lastLoop:
        addi $5, $2, 0

After reading the instructions from the assembly language files, the program converts all uppercase letters in the instructions to lowercase
using the all_to_lowercase() function. The reason why I chose to convert everything to lowercase first is because this will facilite the 
formatting process a lot, and it also prevent double labelling when setting up the labels. With everything in lowercase, the program marks 
all the labels using the marking_labels() function. This function stores all the labels and the address they are pointing to in a dictionary. 
The name of the label is the key, and the address is the value. Instruction lines with only labels are also removed from the list called
instructions in this function. Unnecessary elements like comma, $, (), and " " are then removed using the remove_symbols() function. This is
because symbols might confused the program when trying to convert from assembly to machine code. With everything formatted, the instructions 
along with the dictionary holding all the labels are then passed to the convert_assembly_to_machine function. Using other sub-functions like 
instructions_with_three_registers(), instructions_with_two_registers(), instructions_with_no_registers(), movi_to_addi(),  nop_to_add(), 
fill(), and halt_to_j(), the convert_assembly_to_machine() functions converts all the assembly instructions into machine code and returns 
them back to main(). The results are then displayed using the given print_machine_code() function. 

