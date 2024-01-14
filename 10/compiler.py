#project 10 - compiler I
#nand2tetris

from os import listdir

path = 'ArrayTest'

keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var',
            'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
            'let', 'do', 'if', 'else', 'while', 'return']
symbols = '{}()[].,;+-*/&|<>=~'
alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
number = '0123456789'

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
                    tokens.append((terminal, 0))
                else:
                    tokens.append((terminal, 4))
                terminal = ''
            if program[i:i + 2] == '/*':
                i = program.find('*/', i + 2) + 2
            elif program[i:i + 2] == '//':
                i = program.find('\n', i + 2) + 1
            elif program[i] in symbols:
                tokens.append((program[i], 1))
                i += 1
            elif program[i] == '"':
                end = program.find('"', i + 1)
                tokens.append((program[i + 1:end], 3))
                i = end + 1
            else:
                i += 1
    return tokens

def token2XML(token):
    tags = ['keyword', 'symbol', 'integerConstant', 'stringConstant', 'identifier']
    replace = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}
    content = replace[token[0]] if token[0] in replace else token[0]
    return '<' + tags[token[1]] + '> ' + content + ' </' + tags[token[1]] + '>\n'

def tokenizerXML(tokens, name):
    fw = open(path + '/' + name + 'TP.xml', 'w')
    fw.write('<tokens>' + '\n')
    for token in tokens:
        fw.write(token2XML(token))
    fw.write('</tokens>' + '\n')
    fw.close()

def compileClass(index):
    code = '<class>\n'
    for _ in range(3):
        code += token2XML(tokens[index])
        index += 1
    while tokens[index][0] != '}':
        if tokens[index][0] in ['static', 'field']:
            subcode, index = compileClassVarDec(index)
            code += subcode
        elif tokens[index][0] in ['constructor', 'function', 'method']:
            subcode, index = compileSubroutineDec(index)
            code += subcode
    code += token2XML(tokens[index]) + '</class>\n'
    return code, index + 1
    
def compileClassVarDec(index):
    code = '<classVarDec>\n'
    for _ in range(3):
        code += token2XML(tokens[index])
        index += 1
    while tokens[index][0] != ';':
        for _ in range(2):
            code += token2XML(tokens[index])
            index += 1
    code += token2XML(tokens[index]) + '</classVarDec>\n'
    return code, index + 1
    
def compileSubroutineDec(index):
    code = '<subroutineDec>\n'
    for _ in range(4):
        code += token2XML(tokens[index])
        index += 1
    subcode, index = compileParameterList(index)
    code += subcode + token2XML(tokens[index])
    index += 1
    subcode, index = compileSubroutineBody(index)
    code += subcode + '</subroutineDec>\n'
    return code, index
    
def compileParameterList(index):
    code = '<parameterList>\n'
    if tokens[index][0] == ')':
        code += '</parameterList>\n'
        return code, index
    for _ in range(2):
        code += token2XML(tokens[index])
        index += 1
    while tokens[index][0] == ',':
        for _ in range(3):
            code += token2XML(tokens[index])
            index += 1
    code += '</parameterList>\n'
    return code, index
    
def compileSubroutineBody(index):
    code = '<subroutineBody>\n'
    code += token2XML(tokens[index])
    index += 1
    while tokens[index][0] == 'var':
        subcode, index = compileVarDec(index)
        code += subcode
    subcode, index = compileStatements(index)
    code += subcode + token2XML(tokens[index]) + '</subroutineBody>\n'
    return code, index + 1
    
def compileVarDec(index):
    code = '<varDec>\n'
    for _ in range(3):
        code += token2XML(tokens[index])
        index += 1
    while tokens[index][0] != ';':
        for _ in range(2):
            code += token2XML(tokens[index])
            index += 1
    code += token2XML(tokens[index]) + '</varDec>\n'
    return code, index + 1
    
def compileStatements(index):
    code = '<statements>\n'
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
    code += '</statements>\n'
    return code, index

def compileDo(index):
    code = '<doStatement>\n'
    code += token2XML(tokens[index])
    index += 1
    subcode, index = compileSubroutineCall(index)
    code += subcode + token2XML(tokens[index]) + '</doStatement>\n'
    return code, index + 1
    
def compileLet(index):
    code = '<letStatement>\n'
    for _ in range(2):
        code += token2XML(tokens[index])
        index += 1
    if tokens[index][0] == '[':
        code += token2XML(tokens[index])
        index += 1
        subcode, index = compileExpression(index)
        code += subcode + token2XML(tokens[index])
        index += 1
    code += token2XML(tokens[index])
    index += 1
    subcode, index = compileExpression(index)
    code += subcode + token2XML(tokens[index]) + '</letStatement>\n'
    return code, index + 1
    
def compileWhile(index):
    code = '<whileStatement>\n'
    for _ in range(2):
        code += token2XML(tokens[index])
        index += 1
    subcode, index = compileExpression(index)
    code += subcode
    for _ in range(2):
        code += token2XML(tokens[index])
        index += 1
    subcode, index = compileStatements(index)
    code += subcode + token2XML(tokens[index]) + '</whileStatement>\n'
    return code, index + 1
    
def compileReturn(index):
    code = '<returnStatement>\n'
    code += token2XML(tokens[index])
    index += 1
    if tokens[index][0] != ';':
        subcode, index = compileExpression(index)
        code += subcode
    code += token2XML(tokens[index]) + '</returnStatement>\n'
    return code, index + 1
    
def compileIf(index):
    code = '<ifStatement>\n'
    for _ in range(2):
        code += token2XML(tokens[index])
        index += 1
    subcode, index = compileExpression(index)
    code += subcode
    for _ in range(2):
        code += token2XML(tokens[index])
        index += 1
    subcode, index = compileStatements(index)
    code += subcode + token2XML(tokens[index])
    index += 1
    if tokens[index][0] == 'else':
        for _ in range(2):
            code += token2XML(tokens[index])
            index += 1
        subcode, index = compileStatements(index)
        code += subcode + token2XML(tokens[index])
        index += 1
    code += '</ifStatement>\n'
    return code, index
    
def compileExpression(index):
    op = '+-*/&|<>='
    code = '<expression>\n'
    subcode, index = compileTerm(index)
    code += subcode
    while tokens[index][0] in op:
        code += token2XML(tokens[index])
        index += 1
        subcode, index = compileTerm(index)
        code += subcode
    code += '</expression>\n'
    return code, index
    
def compileTerm(index):
    code = '<term>\n'
    if tokens[index][0] in '-~':
        code += token2XML(tokens[index])
        index += 1
        subcode, index = compileTerm(index)
        code += subcode
    elif tokens[index][0] == '(':
        code += token2XML(tokens[index])
        index += 1
        subcode, index = compileExpression(index)
        code += subcode + token2XML(tokens[index])
        index += 1
    elif tokens[index + 1][0] in '.(':
        subcode, index = compileSubroutineCall(index)
        code += subcode
    else:
        code += token2XML(tokens[index])
        index += 1
        if tokens[index - 1][1] == 4 and tokens[index][0] == '[':
            code += token2XML(tokens[index])
            index += 1
            subcode, index = compileExpression(index)
            code += subcode + token2XML(tokens[index])
            index += 1
    code += '</term>\n'
    return code, index

def compileSubroutineCall(index):
    code = token2XML(tokens[index])
    index += 1
    if tokens[index][0] == '.':
        for _ in range(2):
            code += token2XML(tokens[index])
            index += 1
    code += token2XML(tokens[index])
    index += 1
    subcode, index = compileExpressionList(index)
    code += subcode + token2XML(tokens[index])
    return code, index + 1
    
def compileExpressionList(index):
    code = '<expressionList>\n'
    if tokens[index][0] == ')':
        code += '</expressionList>\n'
        return code, index
    subcode, index = compileExpression(index)
    code += subcode
    while tokens[index][0] == ',':
        code += token2XML(tokens[index])
        index += 1
        subcode, index = compileExpression(index)
        code += subcode
    code += '</expressionList>\n'
    return code, index
    
files = listdir(path)
for file in files:
    if len(file) < 5 or file[-5:] != '.jack':
        continue
    fr = open(path + '/' + file, 'r')
    program = fr.read()
    fr.close()
    tokens = tokenize(program)
    fw = open(path + '/' + file[:-5] + 'P.xml', 'w')
    code, index = compileClass(0)
    fw.write(code)
    fw.close()