#!/usr/bin/env python
# coding=utf-8

def read_file(fpath): 
    BLOCK_SIZE = 1024 
    with open(fpath, 'rb') as f: 
        while True: 
            block = f.read(BLOCK_SIZE) 
            if block: 
                yield block 
            else: 
                return



f = read_file("D:/t/taobao_cloth_dim_items.txt")


# 暂时读取三次
# for i in xrange(3):
#     print f.next()


# i = 0
# try:
#     while True:
#         f.next()
#         i += 1
# except StopIteration:
#     print i


# python专门为for关键字做了迭代器的语法糖。可以直接使用for循环
i = 0
for t in f:
    i += 1
print i
