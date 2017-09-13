#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from PIL import Image
import re
def image_size_off(rootDir):
    for lists in os.listdir(rootDir):
        #需要什么格式的图片自己手动改改就好了
        if lists[lists.rfind('.'):].lower() == '.jpg':
            path = os.path.join(rootDir, lists)
            im = Image.open(path)
            box = clipimage(im.size)
            region = im.crop(box)
            size = (250, 250)
            region.thumbnail(size, Image.ANTIALIAS)
            #这里保存thumbnail以后的结果
            region.save(
                #os.path.join("D:/", lists)) 
                os.path.join("", lists))  #os.path.dirname(os.path.dirname(__file__))
            box = ()

#取宽和高的值小的那一个来生成裁剪图片用的box
#并且尽可能的裁剪出图片的中间部分,一般人摄影都会把主题放在靠中间的,个别艺术家有特殊的艺术需求我顾不上
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


def main():
    '''这里输入的参数是图片文件的位置'''
    image_size_off("img")


if __name__ == '__main__':
    main()