// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
@KBD
D=M
@ONE
D;JGT	// check if some key is pressed
@SCREEN
MD=0	// white
@ONEEND
0;JMP
(ONE)
@SCREEN
MD=-1	// black
(ONEEND)
@SCREEN
A=A+1
D=D-M
@LOOP	// check if update is needed
D;JEQ
@i
M=0
(PRINT) // print the color on the whole screen
@i
D=M
@8191
D=D-A
@LOOP
D;JEQ
@i
D=M
@SCREEN
A=A+D
D=M
A=A+1
M=D
@i
M=M+1
@PRINT
0;JMP