Kyle Wang
ww2301@nyu.edu
N17024217

The E20 simulator is completed. The program developed completely by myself. The only resources that I used is the E20 instruction manual 
and the multicycle circuit diagram provided to us. 

The program can be divided into three major parts. The first part is the given starter code, which contain constants initialization,  
load_machine_code function, print_state function, and main. load_machine_code is used load the machine code into the list named 
memory, and print_state is used to print register value, pc value, and memory value after simulation. 

The second part is the simulation function, which is used to carry out the simulation and imitates how an E20 processor behaves. The 
instruction is first processed, creating different variables that contain opCode, reg1, reg2, reg3, func, imm7, and imm13. The program 
then enters a while loop that only stops when a halt command is detected. When a halt command is detected, the program jumps out of the
loop. The first if statement in the loop takes care of all instructions with three register arguments. This includes add, sub, or, and, 
slt, jr. In add, if the result is out of range, only the least significant 13 bits will be taken. In sub, if the result is negative, it 
will be converted into 2's complement and stored as an unsigned 16 bits number. The second if statement handles slti, where the 7 bits 
immediate number is sign extended to performed an unsigned comparison. The third and fourth if statement handles lw and sw. The calculated 
memory address takes only the least significant 13 bits and the rest is ignored. The fifth if statement deals with jeq. If the comparison 
is true, pc is set to the sum of current pc plus one plus the 7 bits signed immediate. The sixth if statement handles addi, and the seventh 
and eighth handles j and jal respectively. The instruction variables are updated at the end of every cycle. 

The last part is the helper functions. pc_out_of_range_check checks if pc is greater than 8191. If greater, the most significant 3 bits will
be removed. sign_extend extends 7 bits signed number to 16 bits. seven_bit_signed_number_to_decimal converts signed 7 bits into decimal form. 
negative_decimal_to_signed_16_bits converts a negative decimal into signed 16 bits number. 

In addition to the features described above, the simulator is capable of tolerating register $0 modification. Since register $0 is immutable, 
trying to modify it does not produce any effect but is valid. The simulator will simply ignore the instruction and move on to the next one. 
When the program reaches the last instruction, it will automtically loops back to the first instruction and continue on executing the rest
of the program until a halt command is detected. However, the program requires correct machine code program and does not detect any machine code
error. 



