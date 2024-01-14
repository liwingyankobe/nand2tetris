#project 7 - VM translator I
#nand2tetris

import re

path = 'StackArithmetic/StackTest/StackTest'

mapping = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
jump = {'eq': 'JEQ', 'gt': 'JGT', 'lt': 'JLT'}

def parseLine(line):
    args = re.split(' +|\t+', line)
    data = []
    for arg in args:
        if arg == '':
            continue
        if arg[:2] == '//':
            break
        data.append(arg)
    while len(data) < 3:
        data.append(None)
    return data[:3]

def arithmetic(command):
    global comparison
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
            asm += 'D=M-D\n@CS.' + i + '\nD;' + jump[command] + '\n'
            asm += 'D=0\n@CE.' + i + '\n0;JMP\n'
            asm += '(CS.' + i + ')\nD=-1\n(CE.' + i + ')\n'
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
        asm = '@static.' + ind + '\nD=M\n'
    asm += '@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    return asm

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
            asm += '@static.' + ind
        asm += '\nM=D\n'
    return asm

fr = open(path + '.vm', 'r')
lines = fr.read().split('\n')
fr.close()

fw = open(path + '.asm', 'w')
comparison = 0
for line in lines:
    data = parseLine(line)
    if not data[0]:
        continue
    if data[0] == 'push':
        fw.write(push(data[1], data[2]))
    elif data[0] == 'pop':
        fw.write(pop(data[1], data[2]))
    else:
        fw.write(arithmetic(data[0]))
fw.close()
