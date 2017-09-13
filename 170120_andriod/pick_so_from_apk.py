#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import zipfile  
import os  
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

path = os.path.join(os.path.dirname(__file__), 'apk')  
so_path = os.path.join(os.path.dirname(__file__), 'so') 
  
apklist = os.listdir(path)  
  
for APK in apklist:
    print APK
    if APK.endswith(".zip"):  
        portion = os.path.splitext(APK)  
        apkname = portion[0]  
        abs_so_path = os.path.join(so_path, apkname) #/so/apkname/  
        abs_zipAPK_path = os.path.join(path, APK)  
        z = zipfile.ZipFile(abs_zipAPK_path, 'r') 
        print apkname, abs_so_path, abs_zipAPK_path
        solists = []  
        for filename in z.namelist():  
            if filename.endswith(".so"):  
                sofileName = os.path.basename(filename)  
                soSource = os.path.basename(os.path.dirname(filename)) 
                print filename, sofileName, soSource
                ''''' 
                make a dir with the source(arm?mips) 
                '''  
                storePath = os.path.join(abs_so_path, soSource) # e.g. /.../so/apkname/mips/  
                # 上一句报错Decode error - output not utf-8]，难不成是数据中文的原因
                if not os.path.exists(storePath):  
                    os.makedirs(storePath)  
  
                ''''' 
                copy the xxx.so file to the object path 
                '''  
                newsofile = os.path.join(storePath, sofileName)  
                f = open(newsofile, 'w')  
                f.write(z.read(filename)) 


# 这破程序，也就是ls而已