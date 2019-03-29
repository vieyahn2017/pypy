#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Caesar Cipher

import sys

def getMessageFromFile(f):
    try:
        fileobj = open(f, 'r')
        strings = fileobj.read()
        return strings
    finally:
        fileobj.close()

def getModeFromArg(arg):
    mode = arg.lower()
    if mode in 'encrypt e decrypt d'.split():
        return mode
    else:
        print('请输入"encrypt"或"e"或"decrypt"或"d"!')
        return None

def getTranslatedMessage(mode, message, key):
    if mode[0] == 'd':
        key = -key
    translated = ''
    for symbol in message:
        if symbol.isalpha():
            num = ord(symbol)
            num += key
            if symbol.isupper():
                if num > ord('Z'):
                    num -= 26
                elif num < ord('A'):
                    num += 26
            elif symbol.islower():
                if num > ord('z'):
                    num -= 26
                elif num < ord('a'):
                    num += 26

            translated += chr(num)
        else:
            translated += symbol
    return translated

def writeFile(newFileName, content):
    f = open(newFileName, 'w')
    f.write(content) 
    f.close()

def writeFileAndNameHead(newFileName, fileName, content):
    f = open(newFileName, 'w') 
    f.write("\\\\" + fileName)
    f.write('\n')
    f.write(content) 
    f.close()

if __name__ == '__main__':
    mode = 'e'
    if len(sys.argv) == 3:
        mode = getModeFromArg(sys.argv[2])
    message = getMessageFromFile(sys.argv[1])

    key = 10

    result = getTranslatedMessage(mode, message, key)
    writeFileAndNameHead("result.txt", sys.argv[1], result)
