#!/usr/bin/env python
#-*-coding:utf-8 -*-
# @author:yanghao 
# @created:20170522
## Description: captcha for Webservices' Modules.


from PIL import Image,ImageDraw,ImageFont
import random
import math, string 
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


# number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
#             'v', 'w', 'x', 'y', 'z']
# ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
#             'V', 'W', 'X', 'Y', 'Z']

# def random_captcha_text(char_set=number + alphabet + ALPHABET, captcha_size=7):
#     captcha_text = []
#     for i in range(captcha_size):
#         c = random.choice(char_set)
#         captcha_text.append(c)
#     return captcha_text

number = ['2', '3', '4', '5', '6', '7', '8', '9']
alphabet = ['a', 'b',  'd', 'e', 'f', 'g', 'h', 'm', 'n',  'q', 'r', 't']
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',  'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']


class RandomChar(object):
    @staticmethod
    def Unicode():
        val = random.randint(0x4E00, 0x9FBF)
        return unichr(val) 

    @staticmethod
    def GB2312():
        head = random.randint(0xB0, 0xCF)
        body = random.randint(0xA, 0xF)
        tail = random.randint(0, 0xF)
        val = ( head << 8 ) | (body << 4) | tail
        str = "%x" % val
        return str.decode('hex').decode('gb2312') 

class RandomCharInSet(object):
    @staticmethod
    def get():
        char_set = number + alphabet + ALPHABET
        return random.choice(char_set)

class VerifyCode(object):
    def __init__(self, 
                       fontColor = (0, 0, 0),
                       size = (150, 40),
                       fontPath = 'ubuntu.ttf',
                       bgColor = (255, 255, 255),
                       fontSize = 35):
        self.size = size
        self.fontPath = fontPath
        self.bgColor = bgColor
        self.fontSize = fontSize
        self.fontColor = fontColor
        self.font = ImageFont.truetype(self.fontPath, self.fontSize)
        self.image = Image.new('RGB', size, bgColor) 
        self.code = ""

    def rotate(self):
        self.image.rotate(random.randint(0, 30), expand=0) 

    def drawText(self, pos, txt, fill):
        draw = ImageDraw.Draw(self.image)
        draw.text(pos, txt, fill=fill, font=self.font)

    def randRGB(self):
        return (random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)) 

    def randPoint(self):
        (width, height) = self.size
        return (random.randint(0, width), random.randint(0, height)) 

    def randLine(self, num):
        draw = ImageDraw.Draw(self.image)
        for i in range(0, num):
          draw.line([self.randPoint(), self.randPoint()], self.randRGB())

    def randSeed(self, num):
        gap = 5
        start = 0
        str_arr = []
        for i in range(0, num):
           # char = RandomChar().GB2312()
           char = RandomCharInSet().get()
           str_arr.append(char)
           x = start + self.fontSize * i + random.randint(0, gap)  #+ gap * i
           self.drawText((x, random.randint(0, 5)), char, self.randRGB())
           self.rotate()
        self.randLine(10) 
        self.code = ''.join(str_arr)

    def save_file(self, path):
        self.image.save(path)

    def save_stream(self):
        mstream = StringIO.StringIO()
        self.image.save(mstream, "GIF") 
        return mstream.getvalue()

if __name__ == "__main__":
    vc = VerifyCode(fontColor=(100,211, 90))
    vc.randSeed(4)
    print vc.code
    vc.save_file("1.jpeg")
