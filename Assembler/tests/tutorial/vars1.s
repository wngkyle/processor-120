# Examples of variables in memory.
# var1 is a label identifying a memory address
# containing 30, and var2 is a label identifying
# a memory address containing 5. We load the value
# at var1 into $1, and the value at var2 into $2.
# Then we AND them into $3, and OR them into $4.
# Then we store $3 into var3.

    lw $1,var1($0)    # read from address var1 + 0 #0
    lw $2,var2($0)    # read from address var2 + 0 #1
    and $3, $1, $2     # AND the values together  #2
    or $4, $1, $2      # then OR them together  #3
    sw  $3,var3($0)    # write the AND result into memory #4
    lw  $7,11($0)      # read same value back, using numeric address #5
    movi $5, var3      # put the address (not the value!) in $5 #6
    addi $6,$5,var4    # 7

    halt               # program ends #8

var1:
    .fill 30 # 9

var2:
    .fill 5 # 10

var3:
    .fill 0 # 11

var4: # 12
#--
#--
#--MACHINE CODE
# ram[0] = 16'b1000000010001001;		// lw $1,var1($0)
# ram[1] = 16'b1000000100001010;		// lw $2,var2($0)
# ram[2] = 16'b0000010100110011;		// and $3,$1,$2
# ram[3] = 16'b0000010101000010;		// or $4,$1,$2
# ram[4] = 16'b1010000110001011;		// sw $3,var3($0)
# ram[5] = 16'b1000001110001011;		// lw $7,11($0)
# ram[6] = 16'b0010001010001011;		// movi $5,var3
# ram[7] = 16'b0011011100001100;		// addi $6,$5,var4
# ram[8] = 16'b0100000000001000;		// halt 
# ram[9] = 16'b0000000000011110;		// var1: .fill 30
# ram[10] = 16'b0000000000000101;		// var2: .fill 5
# ram[11] = 16'b0000000000000000;		// var3: .fill 0
#--
#--

