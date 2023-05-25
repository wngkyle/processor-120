# A simple loop, counting down from 10

    movi $1,10         # Initialize counter to 10
beginning:
    jeq $1, $0,done     # if $1 == $0, go to done
    addi $1, $1,-1      # Decrement $1
    j beginning         # go to top of loop
done: halt                # we've finished

#--
#--
#--MACHINE CODE
# ram[0] = 16'b0010000010001010;		// movi $1,10
# ram[1] = 16'b1100010000000010;		// beginning: jeq $1,$0,done
# ram[2] = 16'b0010010011111111;		// addi $1,$1,-1
# ram[3] = 16'b0100000000000001;		// j beginning
# ram[4] = 16'b0100000000000100;		// done: halt 
#--
#--
ram[0] = 16'b0010000010001010;
ram[1] = 16'b1100010000000010;
ram[2] = 16'b0010010011111111;
ram[3] = 16'b0100000000000001;
ram[4] = 16'b0100000000000100;