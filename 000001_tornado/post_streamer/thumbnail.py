
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# --------------------
# Author:       Yh
# Description:
# --------------------

import os
from PIL import Image


def thumb(imgFile,outputDir="thumb/",size=200):
    """
    imgFile 原始图片文件
    在原始图片目录，新建thumb文件夹作为缩略图存放文件夹
    size是缩略图计划的长宽尺寸

    如果size=500，图片是600*400的，缩略图最后size是400
    """
    try:
        im = Image.open(imgFile)
        if (im.size[0]<size) & (im.size[1]<size):
            raise Exception('图片原始尺寸小于生成缩略图的size，出错')
    except Exception,e:
        print "Error: %s" % e
    box = clipimage(im.size)
    region = im.crop(box) #裁切图片
    _size = (size, size)
    #region.resize(_size, Image.ANTIALIAS)
    region.thumbnail(_size, Image.ANTIALIAS)
    (shotname,extension) = getFilenameAndExt(imgFile)
    outputFile = os.path.join(outputDir, shotname+'_'+str(size)+'x'+str(size)+extension )
    region.save(outputFile) 
    return outputFile


#取宽和高的值小的那一个来生成裁剪图片用的box
#并且尽可能的裁剪出图片的中间部分,一般人摄影都会把主题放在靠中间的,个别艺术家有特殊的艺术需求顾不上
def clipimage(size):
    width = int(size[0])
    height = int(size[1])
    box = ()
    if (width > height):
        dx = width - height
        box = (dx / 2, 0, height + dx / 2,  height)
    else:
        dx = height - width
        box = (0, dx / 2, width, width + dx / 2)
    return box

def getFilenameAndExt(filename):
    (filepath,tmpfilename) = os.path.split(filename)
    (shotname,extension) = os.path.splitext(tmpfilename)
    return shotname,extension


#print getFilenameAndExt("D://12//345.jpg")
#print thumb("1234.jpg")
#print thumb("D://123.jpg")
