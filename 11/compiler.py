#project 11 - compiler II
#nand2tetris

from os import listdir

path = 'GameOfLife'

keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var',
            'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
            'let', 'do', 'if', 'else', 'while', 'return']
symbols = '{}()[].,;+-*/&|<>=~'
alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
number = '0123456789'

# Parse the input source code
# 0 = keyword, 1 = symbol, 2 = integer, 3 = string, 4 = identifier
def tokenize(program):
    tokens = []
    terminal = ''
    i = 0
    while i < len(program):
        if program[i] in alphabet:
            terminal += program[i]
            i += 1
        elif program[i] in number:
            # integerConstant
            terminal += program[i]
            i += 1
            if len(terminal) == 1:
                while program[i] in number:
                    terminal += program[i]
                    i += 1
                tokens.append((terminal, 2))
                terminal = ''
        else:
            if len(terminal) > 0:
                if terminal in keywords:
                    # keyword
                    tokens.append((terminal, 0))
                else:
                    # identifier
                    tokens.append((terminal, 4))
                terminal = ''
            # ignore comments
            if program[i:i + 2] == '/*':
                i = program.find('*/', i + 2) + 2
            elif program[i:i + 2] == '//':
                i = program.find('\n', i + 2) + 1
            elif program[i] in symbols:
                # symbol
                tokens.append((program[i], 1))
                i += 1
            elif program[i] == '"':
                # stringConstant
                end = program.find('"', i + 1)
                tokens.append((program[i + 1:end], 3))
                i = end + 1
            else:
                i += 1
    return tokens

def compileClass(index):
    code = ''
    index += 3
    staticCount, fieldCount = 0, 0
    while tokens[index][0] != '}':
        # variables
        if tokens[index][0] == 'static':
            index, staticCount = compileClassVarDec(index, staticCount)
        elif tokens[index][0] == 'field':
            index, fieldCount = compileClassVarDec(index, fieldCount)
        # functions
        elif tokens[index][0] in ['constructor', 'function', 'method']:
            subcode, index = compileSubroutineDec(index, fieldCount)
            code += subcode
    return code
    
def compileClassVarDec(index, count):
    # domain type name1 (, name2);
    varDomain = 'static' if tokens[index][0] == 'static' else 'this'
    varType = tokens[index + 1][0]
    index += 2
    while True:
        classTable[tokens[index][0]] = (varDomain + ' ' + str(count), varType)
        count += 1
        if tokens[index + 1][0] == ';':
            break
        index += 2
    return index + 2, count
    
def compileSubroutineDec(index, fieldCount):
    # type return name(parameters)
    global className, subroutineTable
    subroutineTable = {}
    subroutineType = tokens[index][0]
    subroutineName = tokens[index + 2][0]
    if subroutineType == 'method':
        index = compileParameterList(index + 4, 1) + 2
    else:
        index = compileParameterList(index + 4, 0) + 2
    localCount = 0
    # var type name1 (, name2);
    while tokens[index][0] == 'var':
        index, localCount = compileVarDec(index, localCount)
    code = 'function ' + className + '.' + subroutineName + ' ' + str(localCount) + '\n'
    if subroutineType == 'constructor':
        # allocate memory for class variables
        code += 'push constant ' + str(fieldCount) + '\n'
        code += 'call Memory.alloc 1\n'
        code += 'pop pointer 0\n'
    elif subroutineType == 'method':
        # object pointer as first argument
        code += 'push argument 0\n'
        code += 'pop pointer 0\n'
    subcode, index = compileStatements(index)
    return code + subcode, index + 1
    
def compileParameterList(index, count):
    # type name (, type name)
    if tokens[index][0] == ')':
        return index
    while True:
        subroutineTable[tokens[index + 1][0]] = ('argument ' + str(count), tokens[index][0])
        count += 1
        if tokens[index + 2][0] == ')':
            break
        index += 3
    return index + 2

def compileVarDec(index, count):
    index += 2
    while True:
        subroutineTable[tokens[index][0]] = ('local ' + str(count), tokens[index - 1][0])
        count += 1
        if tokens[index + 1][0] == ';':
            break
        index += 2
    return index + 2, count
    
def compileStatements(index):
    code = ''
    while True:
        if tokens[index][0] == 'let':
            subcode, index = compileLet(index)
            code += subcode
        elif tokens[index][0] == 'if':
            subcode, index = compileIf(index)
            code += subcode
        elif tokens[index][0] == 'while':
            subcode, index = compileWhile(index)
            code += subcode
        elif tokens[index][0] == 'do':
            subcode, index = compileDo(index)
            code += subcode
        elif tokens[index][0] == 'return':
            subcode, index = compileReturn(index)
            code += subcode
        else:
            break
    return code, index

def compileDo(index):
    # do subroutineCall;
    code, index = compileSubroutineCall(index + 1)
    code += 'pop temp 0\n'
    return code, index + 1
    
def compileLet(index):
    # let variable = expression;
    if tokens[index + 1][0] in subroutineTable:
        varName = subroutineTable[tokens[index + 1][0]][0]
    else:
        varName = classTable[tokens[index + 1][0]][0]
    index += 3
    arrayCode = ''
    # variable[index]
    if tokens[index - 1][0] == '[':
        arrayCode, index = compileExpression(index)
        arrayCode += 'push ' + varName + '\nadd\npop pointer 1\n'
        index += 2
        varName = 'that 0'
    code, index = compileExpression(index)
    code += arrayCode + 'pop ' + varName + '\n'
    return code, index + 1
    
def compileWhile(index):
    # while (expression) {statements}
    global whileCount
    currWhile = str(whileCount)
    whileCount += 1
    code = 'label WS.' + currWhile + '\n'
    subcode, index = compileExpression(index + 2)
    code += subcode + 'not\nif-goto WE.' + currWhile + '\n'
    index += 2
    subcode, index = compileStatements(index)
    code += subcode + 'goto WS.' + currWhile + '\nlabel WE.' + currWhile + '\n'
    whileCount += 1
    return code, index + 1
    
def compileReturn(index):
    if tokens[index + 1][0] != ';':
        code, index = compileExpression(index + 1)
    else:
        # return void
        code, index = 'push constant 0\n', index + 1
    return code + 'return\n', index + 1
    
def compileIf(index):
    # if (expression) {statements}
    global ifCount
    currIf = str(ifCount)
    ifCount += 1
    code, index = compileExpression(index + 2)
    code += 'not\nif-goto IS.' + currIf + '\n'
    subcode, index = compileStatements(index + 2)
    code += subcode + 'goto IE.' + currIf + '\nlabel IS.' + currIf + '\n'
    # else {statements}
    if tokens[index + 1][0] == 'else':
        subcode, index = compileStatements(index + 3)
        code += subcode
    code += 'label IE.' + currIf + '\n'
    return code, index + 1
    
def compileExpression(index):
    # term (op term)
    op = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2', '/': 'call Math.divide 2',
          '&': 'and', '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq'}
    code, index = compileTerm(index)
    while tokens[index][0] in op:
        command = op[tokens[index][0]] + '\n'
        subcode, index = compileTerm(index + 1)
        code += subcode + command
    return code, index
    
def compileTerm(index):
    # -~ term
    if tokens[index][0] in '-~':
        opType = 'neg' if tokens[index][0] == '-' else 'not'
        code, index = compileTerm(index + 1)
        code += opType + '\n'
    # (expression)
    elif tokens[index][0] == '(':
        code, index = compileExpression(index + 1)
        index += 1
    # subroutine(...) or name.subroutine(...)
    elif tokens[index + 1][0] in '.(':
        code, index = compileSubroutineCall(index)
    # keyword constant
    elif tokens[index][1] == 0:
        if tokens[index][0] == 'true':
            code = 'push constant 0\nnot\n'
        elif tokens[index][0] == 'this':
            code = 'push pointer 0\n'
        else:
            code = 'push constant 0\n'
        index += 1
    # integer constant
    elif tokens[index][1] == 2:
        code = 'push constant ' + tokens[index][0] + '\n'
        index += 1
    # string constant
    elif tokens[index][1] == 3:
        code = 'push constant ' + str(len(tokens[index][0])) + '\n'
        code += 'call String.new 1\n'
        for c in tokens[index][0]:
            code += 'push constant ' + str(ord(c)) + '\n'
            code += 'call String.appendChar 2\n'
        index += 1
    # identifier
    else:
        if tokens[index][0] in subroutineTable:
            varName = subroutineTable[tokens[index][0]][0]
        else:
            varName = classTable[tokens[index][0]][0]
        index += 1
        arrayCode = ''
        # identifier[index]
        if tokens[index][0] == '[':
            arrayCode, index = compileExpression(index + 1)
            arrayCode += 'push ' + varName + '\nadd\npop pointer 1\n'
            index += 1
            varName = 'that 0'
        code = arrayCode + 'push ' + varName + '\n'
    return code, index

def compileSubroutineCall(index):
    global className
    callClass = None
    code = ''
    # name.subroutine(...)
    if tokens[index + 1][0] == '.':
        # local variable
        if tokens[index][0] in subroutineTable:
            callClass = subroutineTable[tokens[index][0]][1]
            code += 'push ' + subroutineTable[tokens[index][0]][0] + '\n'
            argCount = 1
        # global variable
        elif tokens[index][0] in classTable:
            callClass = classTable[tokens[index][0]][1]
            code += 'push ' + classTable[tokens[index][0]][0] + '\n'
            argCount = 1
        # class
        else:
            callClass = tokens[index][0]
            argCount = 0
        index += 4
    # subroutine(...)
    else:
        callClass = className
        code += 'push pointer 0\n'
        argCount = 1
        index += 2
    functionName = tokens[index - 2][0]
    subcode, index, argCount = compileExpressionList(index, argCount)
    code += subcode + 'call ' + callClass + '.' + functionName + ' ' + str(argCount) + '\n'
    return code, index + 1
    
def compileExpressionList(index, count):
    if tokens[index][0] == ')':
        return '', index, count
    code, index = compileExpression(index)
    count += 1
    while tokens[index][0] == ',':
        subcode, index = compileExpression(index + 1)
        code += subcode
        count += 1
    return code, index, count
    
files = listdir(path)
for file in files:
    if len(file) < 5 or file[-5:] != '.jack':
        continue
    fr = open(path + '/' + file, 'r')
    program = fr.read()
    fr.close()
    tokens = tokenize(program)
    className = file[:-5]
    fw = open(path + '/' + className + '.vm', 'w')
    classTable, subroutineTable = {}, {}
    whileCount, ifCount = 0, 0
    fw.write(compileClass(0))
    fw.close()