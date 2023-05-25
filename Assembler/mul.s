    lw $2, multiplicand($0) # load multiplicand into register 2
    lw $3, multiplier($0) # load multiplier into register 3
    movi $4, 1 # bit mask
    movi $5, 63 # set up constant
    addi $5, $5, 1
    add $5, $5, $5 # value in register 5 equals 128
loopStart:
    jeq $4, $5, done 
    and $6, $4, $2 # check if bit exist
    jeq $6, $4, math # if exist, conduct addition
update:
    add $4, $4, $4 # update bit mask
    add $3, $3, $3 # update multiplier value
    j loopStart
math:
    add $1, $1, $3 # add value to register 1, where final result is stored
    j update # jump back to the main loop
done:
    halt
multiplicand:
    .fill 123
multiplier:
    .fill 119