# project 6 - assembler
# nand2tetris

program = 'pong/Pong'

symbols = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576
}
for i in range(16):
    symbols['R' + str(i)] = i

comp = {
    '0': '101010',
    '1': '111111',
    '-1': '111010',
    'D': '001100',
    'X': '110000',
    '!D': '001101',
    '!X': '110001',
    '-D': '001111',
    '-X': '110011',
    'D+1': '011111',
    'X+1': '110111',
    'D-1': '001110',
    'X-1': '110010',
    'D+X': '000010',
    'D-X': '010011',
    'X-D': '000111',
    'D&X': '000000',
    'D|X': '010101'
}

dest = {
    '': '000',
    'M': '001',
    'D': '010',
    'MD': '011',
    'DM': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111',
    'ADM': '111'
}

jump = {
    '': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

fr = open(program + '.asm', 'r')
lines = fr.read().split('\n')
fr.close()

line_count = 0
for i in range(len(lines)):
    # ignore space, tab, comments
    comment = lines[i].find('//')
    if comment > -1:
        lines[i] = lines[i][:comment]
    lines[i] = lines[i].replace(' ', '')
    lines[i] = lines[i].replace('\t', '')
    if lines[i] == '':
        continue
    # label
    if lines[i][0] == '(':
        label = lines[i][1:-1]
        if label not in symbols:
            symbols[label] = line_count
    else:
        line_count += 1

available = 16
fw = open(program + '.hack', 'w')
for line in lines:
    if line == '' or line[0] == '(':
        continue
    # a-command
    if line[0] == '@':
        value = line[1:]
        if value[0] in '0123456789':
            address = int(value)
        elif value in symbols:
            address = symbols[value]
        else:
            symbols[value] = available
            address = available
            available += 1
        instruction = format(address, '016b')
    # c-command
    else:
        instruction = '111'
        cstart = line.find('=') + 1
        cend = line.find(';')
        if cend < 0:
            cend = len(line)
        cstr = line[cstart:cend]
        if 'M' in cstr:
            cstr = cstr.replace('M', 'X')
            instruction += '1'
        else:
            cstr = cstr.replace('A', 'X')
            instruction += '0'
        instruction += comp[cstr] if cstr in comp else comp[cstr[::-1]]
        instruction += dest[line[:max(0, cstart - 1)]]
        instruction += jump[line[cend + 1:]]
    fw.write(instruction + '\n')
fw.close()