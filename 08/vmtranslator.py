#project 8 - VM translator II
#nand2tetris

import re
from os import listdir

path = '../09/'
appname = 'GameOfLife'
bootstrap = True

mapping = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
jump = {'eq': 'JEQ', 'gt': 'JGT', 'lt': 'JLT'}

def parseLine(line):
    # ignore space, tab
    args = re.split(' +|\t+', line)
    data = []
    # ignore comments
    for arg in args:
        if arg == '':
            continue
        if arg[:2] == '//':
            break
        data.append(arg)
    while len(data) < 3:
        data.append(None)
    return data[:3]

# new function
def newf(name, local):
    global fname, comparison, raddr
    fname = name
    comparison, raddr = 0, 0
    asm = '(' + name + ')\n'
    # initialize local variables to 0
    if int(local) > 0:
        asm += '@' + local + '\nD=A\n@R13\nM=D\n'
        asm += '(' + name + '$$I)\n'
        asm += '@SP\nA=M\nM=0\n@SP\nM=M+1\n@R13\nMD=M-1\n'
        asm += '@' + name + '$$I\nD;JGT\n'
    return asm

# call function
def call(name, arg):
    global fname, raddr
    # copy return address
    asm = '@' + fname + '$$R.' + str(raddr) + '\n'
    asm += 'D=A\n@SP\nA=M\nM=D\n'
    # copy current pointers
    for addr in ['LCL', 'ARG', 'THIS', 'THAT']:
        asm += '@' + addr +'\nD=M\n@SP\nM=M+1\nA=M\nM=D\n'
    # set new pointers
    asm += '@SP\nMD=M+1\n@LCL\nM=D\n'
    asm += '@' + str(5 + int(arg)) + '\nD=D-A\n@ARG\nM=D\n'
    # jump to function
    asm += '@' + name + '\n0;JMP\n'
    asm += '(' + fname + '$$R.' + str(raddr) + ')\n'
    raddr += 1
    return asm

# return from function
def freturn():
    # save return address
    asm = '@LCL\nD=M\n@5\nD=D-A\nA=D\nD=M\n@R14\nM=D\n'
    # save return value
    asm += '@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n'
    # restore pointers
    asm += '@ARG\nD=M+1\n@SP\nM=D\n'
    asm += '@LCL\nD=M\n@R13\nM=D-1\nA=M\nD=M\n@THAT\nM=D\n'
    asm += '@R13\nM=M-1\nA=M\nD=M\n@THIS\nM=D\n'
    asm += '@R13\nM=M-1\nA=M\nD=M\n@ARG\nM=D\n'
    asm += '@R13\nM=M-1\nA=M\nD=M\n@LCL\nM=D\n'
    # return
    asm += '@R14\nA=M\n0;JMP\n'
    return asm

def init():
    return '@256\nD=A\n@SP\nM=D\n' + call('Sys.init', '0')

def arithmetic(command):
    global comparison, fname
    i = str(comparison)
    asm = '@SP\nA=M-1\n'
    if command == 'neg':
        asm += 'D=-M\n'
    elif command == 'not':
        asm += 'D=!M\n'
    else:
        asm += 'D=M\nA=A-1\n'
        if command == 'add':
            asm += 'D=M+D\n'
        elif command == 'sub':
            asm += 'D=M-D\n'
        elif command in jump:
            asm += 'D=M-D\n@' + fname + '$$CS.' + i + '\nD;' + jump[command] + '\n'
            asm += 'D=0\n@' + fname + '$$CE.' + i + '\n0;JMP\n'
            asm += '(' + fname + '$$CS.' + i + ')\nD=-1\n(' + fname + '$$CE.' + i + ')\n'
            comparison += 1
        elif command == 'and':
            asm += 'D=M&D\n'
        elif command == 'or':
            asm += 'D=M|D\n'
    asm += '@SP\n'
    if command not in ['neg', 'not']:
        asm += 'M=M-1\n'
    asm += 'A=M-1\nM=D\n'
    return asm

# push value to stack
def push(seg, ind):
    if seg == 'constant':
        asm = '@' + ind + '\nD=A\n'
    elif seg in mapping:
        asm = '@' + mapping[seg] + '\nD=M\n@' + ind + '\nA=D+A\nD=M\n'
    elif seg == 'pointer':
        asm = '@R' + str(int(ind) + 3) + '\nD=M\n'
    elif seg == 'temp':
        asm = '@R' + str(int(ind) + 5) + '\nD=M\n'
    elif seg == 'static':
        global file
        asm = '@' + file[:-3] + '.' + ind + '\nD=M\n'
    asm += '@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    return asm

# pop value from stack
def pop(seg, ind):
    if seg in mapping:
        asm = '@' + mapping[seg] + '\nD=M\n@' + ind + '\nD=D+A\n@R13\nM=D\n'
        asm += '@SP\nM=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n'
    else:
        asm = '@SP\nM=M-1\nA=M\nD=M\n'
        if seg == 'pointer':
            asm += '@R' + str(int(ind) + 3)
        elif seg == 'temp':
            asm += '@R' + str(int(ind) + 5)
        elif seg == 'static':
            global file
            asm += '@' + file[:-3] + '.' + ind
        asm += '\nM=D\n'
    return asm

def label(label_name):
    global fname
    return '(' + fname + '$' + label_name + ')\n'

def goto(label_name):
    global fname
    asm = '@' + fname + '$' + label_name + '\n'
    asm += '0;JMP\n'
    return asm

# jump when top of stack is nonzero
def if_goto(label_name):
    global fname
    asm = '@SP\nM=M-1\nA=M\nD=M\n'
    asm += '@' + fname + '$' + label_name + '\n'
    asm += 'D;JNE\n'
    return asm

fw = open(path + appname + '/' + appname + '.asm', 'w')
comparison, raddr = 0, 0
fname = ''
if bootstrap:
    fw.write(init())

files = listdir(path + appname)
for file in files:
    if len(file) < 3 or file[-3:] != '.vm':
        continue
    fr = open(path + appname + '/' + file, 'r')
    lines = fr.read().split('\n')
    fr.close()
    for line in lines:
        data = parseLine(line)
        if not data[0]:
            continue
        if data[0] == 'push':
            fw.write(push(data[1], data[2]))
        elif data[0] == 'pop':
            fw.write(pop(data[1], data[2]))
        elif data[0] == 'label':
            fw.write(label(data[1]))
        elif data[0] == 'goto':
            fw.write(goto(data[1]))
        elif data[0] == 'if-goto':
            fw.write(if_goto(data[1]))
        elif data[0] == 'function':
            fw.write(newf(data[1], data[2] if data[2] else '0'))
        elif data[0] == 'call':
            fw.write(call(data[1], data[2]))
        elif data[0] == 'return':
            fw.write(freturn())
        else:
            fw.write(arithmetic(data[0]))
            
fw.close()
