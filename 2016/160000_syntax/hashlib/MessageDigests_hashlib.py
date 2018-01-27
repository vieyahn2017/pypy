#! /usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
#src = raw_input("Input string : ")
src = 'abcdef'
funcNameList = ["MD5","SHA1","SHA224","SHA256","SHA384","SHA512"]
funcMap = {
"MD5"            :      lambda cnt : hashlib.md5(cnt).hexdigest(),
"SHA1"           :      lambda cnt : hashlib.sha1(cnt).hexdigest(),
"SHA224"         :      lambda cnt : hashlib.sha224(cnt).hexdigest(),
"SHA256"         :      lambda cnt : hashlib.sha256(cnt).hexdigest(),
"SHA384"         :      lambda cnt : hashlib.sha384(cnt).hexdigest(),
"SHA512"         :      lambda cnt : hashlib.sha512(cnt).hexdigest()
}
for funcName in funcNameList :
    print funcName,"\t:\t",funcMap[funcName](src)