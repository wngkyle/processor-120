    lw $2, head($0) # load 34 in register 2
    addi $3, $0, head # stores the pointer
main:    
    add $1, $1, $2 # add current value in register 2 to register 1
    lw $3, 1($3) # stores address of next node in register 3
    jeq $3, $0, done # if address of next node is zero, then halt because zero is end of the linked list
    lw $2, 0($3) # stores the value of next node in register 2
    j main # jumps back to the start of the loop
done:
    halt

chain4:
    .fill 100
    .fill chain5
    .fill 300 
chain7:
    .fill 16384 
    .fill 909 
    .fill 0
chain1: 
    .fill 23
    .fill chain2 
head:   # beginning of linked list
    .fill 34 
    .fill chain1 
    .fill 82 
    .fill 10
chain3: 
    .fill 4
    .fill chain4 
    .fill 229 
    .fill 449
chain2: 
    .fill 0
    .fill chain3 
chain5:
    .fill 12 
    .fill 0  # end of linked list
    .fill 9999
chain6:
    .fill 99 
    .fill 49
