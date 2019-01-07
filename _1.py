# -*- coding: utf-8 -*-
import sys
import collections
           
def SolveComment(ss):
    state = 0
    listOut = []
    for c in ss:
        if state == 0:
            if c == '/':
                state = 1
            elif c == '\'':
                state = 6
            elif c == '\"':
                state = 8         
            else:
                listOut.append(c)
        elif state == 1:
            if c == '*':
                state = 2
            elif c == '/':
                state = 4
            else:
                listOut.append('/')
                listOut.append(c)
                state = 0
        elif state == 2:
            if c == '*':
                state = 3
            else:
                state = 2
        elif state == 3:
            if c == '/':
                listOut.append(' ')
                state = 0
            elif c == '*':
                state = 3
            else:
                state = 2
        elif state == 4:
            if c == '\\':
                state = 5
            elif c == '\n':
                listOut.append(c)
                state = 0
        elif state == 5:
            if c == '\\':
                state = 5
            else:
                state = 4
        elif state == 6:
            if c == '\\':
                state = 7
            elif c == '\'':
                listOut.append(c)
                state = 0
        elif state == 7:
            state = 6
        elif state == 8:
            if c == '\\':
                state = 9
            elif c == '\"':
                listOut.append(c)
                state = 0
        elif state == 9:
            state = 8     
        
        if state==6 or state==7 or state==8 or state==9:
            listOut.append(c)

    return listOut

def wordSlice(s):
    length = len(s)
    i = 0
    ret = []
    state = 0
    listTemp = []
    while i<length:
        if state == 0:
            if s[i] in [' ','\t','\n']:
                state = 0
            else:
                if len(ret) == 2:
                    ret.append(s[i:].strip())
                    break
                listTemp.append(s[i])
                state = 1
        else:
            if s[i] in [' ','\t','\n']:
                ret.append(''.join(listTemp))
                listTemp = []
                state = 0
            else:
                listTemp.append(s[i])
                state = 1
                    
        i += 1
    if listTemp != []:
        ret.append(''.join(listTemp))
    if len(ret) == 2:
        ret.append(None)
    return ret

def decodeFloat(s):
    i = len(s) - 1
    while i>=0 and s[i] in ('f','F','l','L'):
        i -= 1
    return float(s[:i+1])

def decodeInt(s):
    for x in ('u','U','l','L','ll','LL','i64','I64'):
        idx = s.find(x)
        if idx != -1:
            s = s[:idx]

    symbol = 1
    if s[0] == '-':
        symbol = -1
    if s[0] == '-' or s[0] == '+':
        s = s[1:]
    if s[0] == '0':
        if len(s) == 1: # '0'
            return 0
        elif s[1] == 'x' or s[1] == 'X': # '0x...'
            return int(s[2:],16) * symbol
        else: # '0..'
            return int(s[1:],8) * symbol
    else:
        return int(s) * symbol

def aggregateSlice(s):
    state = 0
    count = 0  # 聚合嵌套计数
    listTemp = []
    ret = []
    for c in s:
        if state == 0:
            if c == ',':
                ret.append(''.join(listTemp).strip())
                listTemp = []
                state = 0
            elif c == '\'':
                listTemp.append(c)
                state = 1
            elif c == '\"':
                listTemp.append(c)
                state = 2
            elif c == '{':
                listTemp.append(c)
                count += 1
                state = 5
            else:
                listTemp.append(c)
                state = 0
        elif state == 1:
            if c == '\\':
                listTemp.append(c)
                state = 3
            elif c == '\'':
                listTemp.append(c)
                state = 0
            else:
                listTemp.append(c)
                state = 1
        elif state == 2:
            if c == '\\':
                listTemp.append(c)
                state = 4
            elif c == '\"':
                listTemp.append(c)
                state = 0
            else:
                listTemp.append(c)
                state = 2
        elif state == 3:
            listTemp.append(c)
            state = 1
        elif state == 4:
            listTemp.append(c)
            state = 2
        elif state == 5:
            if c == '{':
                listTemp.append(c)
                count += 1
                state = 5
            elif c == '}':
                listTemp.append(c)
                count -= 1
                if count == 0:
                    state = 0
                else:
                    state = 5
            else:
                listTemp.append(c)
                state = 5

    if count != 0:
        raise ValueError('{} is not compatiable,input: %s' % s)
    if listTemp != []:
         ret.append(''.join(listTemp).strip())
    return ret

def decodeAggregate(s):
    elements = aggregateSlice(s[1:-1])
    ret = []
    for e in elements:
        ret.append(getValue(e))
    return tuple(ret)

def decodeChar(s):
    s = s[1:-1]
    ret = 0
    try:
        ret = ord(s)
    except TypeError as e:
        if s[0] == '\\':    # 转义错误 : 1.16进制不可转 2.8进制数字大于三个 3.未知转义字符
            if s[1] == 'x' or s[1] == 'X':
                ret = int(s[2:],16)
            elif len(s) > 4:
                ret = ord(s[:4])
            else:
                ret = ord(s[-1])
        elif len(s) > 1:
            ret = ord(s[-1])
    finally:
        return ret

def decodeStr(s):
    wide = False
    listTemp = []
    state = 0
    for c in s:
        if state == 0:
            if c == 'L':
                wide = True
                state = 0
            elif c == '\"':
                state = 1
        elif state == 1:
            if c == '\"':
                state = 0
            elif c == '\\':
                state = 2
            else:
                listTemp.append(c)
                state = 1
        elif state == 2:      
            listTemp.append('\\')
            listTemp.append(c)
            state = 1

    string = ''.join(listTemp)
    if wide:
        return unicode(string)
    else:
        return string



def getValue(s):
    if s==None or s=='':
        return None

            # bool
    if s == 'false':
        return False
    elif s == 'true':
        return True
    elif s[0] == '\'':
        return decodeChar(s) # char
    elif s[0] == '\"' or s[0] == 'L':
        return decodeStr(s) #string
    elif s[0] == '{':
        return decodeAggregate(s) # aggregate
    elif '.' in s or 'e' in s or 'E' in s or 'f' in s or 'F' in s:
        return decodeFloat(s) # float
    else:
        return decodeInt(s) # int

def printValue(v):
    if isinstance(v,bool):
        if v:
            return 'true'
        else:
            return 'false'
    elif isinstance(v , int):
        return str(v)
    elif isinstance(v , float):
        return str(v)
    elif isinstance(v , str):
        return '\"' + v + '\"'
    elif isinstance(v , unicode):
        return 'L\"' + v + '\"'
    elif isinstance(v , tuple):
        s = '{'
        for i in range(0,len(v)):
            s += printValue(v[i])
            if i != len(v) -1:
                s += ','
        s += '}'
        return s
    else:
        return ''


class PyMacroParser(object):
    def __init__(self):
        self.srcCode = ''
        self.dic = {}
        self.bUpdate = True
        return super(PyMacroParser, self).__init__()

    def preDefine(self,s):
        self.dic = {}
        for word in s.split(';'):
            if word == '':
                continue
            self.dic[word] = None
        self.bUpdate = True

    def load(self,filePath):
        self.dic = {}
        self.bUpdate = True
        with open(filePath,'r') as f:
            self.srcCode = ''.join(SolveComment(f.read()))

    def do(self):
        length = len(self.srcCode)
        i = 0
        outterState = [True]
        preBranch = []
        bExecute = True

        while i<length:
            if self.srcCode[i] == '#':
                i += 1
                listTemp = []
                while i<length and self.srcCode[i] != '#':
                    listTemp.append(self.srcCode[i])
                    i += 1
                words = wordSlice(''.join(listTemp))
                
                if len(words) < 1:
                    continue

                if words[0] == 'define':
                    if len(words) != 3:
                        continue
                    if bExecute:
                        self.dic[words[1]] = getValue(words[2])

                elif words[0] == 'ifdef':
                    outterState.append(bExecute)
                    r = words[1] in self.dic
                    preBranch.append(r)
                    bExecute = r and bExecute
                                            
                elif words[0] == 'ifndef':
                    outterState.append(bExecute)                    
                    r = words[1] not in self.dic
                    preBranch.append(r)
                    bExecute = r and bExecute
                    
                elif words[0] == 'else':
                    bExecute = outterState[-1] and (not preBranch[-1])
                   
                elif words[0] == 'endif':
                    bExecute = outterState.pop()
                    preBranch.pop()  
                    
                elif words[0] == 'undef':
                    if bExecute:
                        if words[1] not in self.dic:
                            raise ValueError('%s is not exist in self.dic' % words[1])
                        else:
                            del self.dic[words[1]]
                    
            else:
                i += 1

        self.bUpdate = False

    def dumpDict(self):
        if self.bUpdate:
            self.do()
        return self.dic
    

    def dump(self,f):
        if self.bUpdate:
            self.do()
        strOut = ''
        for key,value in self.dic.items():
            strOut = strOut + '#define ' + key + ' ' + printValue(value) + '\n'
        with open(f,'w') as f:
            f.write(strOut)


t_py = PyMacroParser()
t_py.load('C:\\Users\\10405\\source\\repos\\1\\testInput.cpp')
t_py.preDefine('MC1;MC2')


t_py.dumpDict()
t_py.dump('C:\\Users\\10405\\source\\repos\\1\\testOutput.cpp')

