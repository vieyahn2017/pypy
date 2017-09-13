# -*- coding:utf-8 -*-
import time,os

def create_localtime_folder(basePath = 'D:\\'):
    thisYear = str(time.localtime()[0])
    thisMonth = str(time.localtime()[1])
    thisDay =  str(time.localtime()[2]) #time.strftime("%Y-%m-%d", time.localtime()) '2016-9-19'
    if basePath.endswith('\\'):
        yearPath = basePath + thisYear
    else:
        yearPath = basePath + '\\' + thisYear
    monthPath = yearPath + '\\' +thisMonth
    dayPath = monthPath + '\\' + thisDay
    if not os.path.exists(yearPath):
        os.mkdir(yearPath)
    if not os.path.exists(monthPath):
        os.mkdir(monthPath)
    if not os.path.exists(dayPath):
        os.mkdir(dayPath)
        #os.popen("explorer.exe" + " " + dayPath) #是想打开该文件夹 os.popen("explorer.exe" + " " + 'D:')
        #os.popen("exit")
    return dayPath

#create_localtime_folder()