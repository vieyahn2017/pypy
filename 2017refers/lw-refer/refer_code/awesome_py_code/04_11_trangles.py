#!/usr/bin/python  
#-*-coding:utf-8-*-

def trangles():
	L = [1]
	while True:
		yield L
		L = [sum(i) for i in zip([0] + L, L + [0])]

n = 0
for t in trangles():
	if(n != 1):
		print(t)
	n = n + 1
	if n > 5:
		break

"""
正常的杨辉三角应该是这样输出，这段程序也是这样输出的
[1]
[1, 1]
[1, 2, 1]
[1, 3, 3, 1]
[1, 4, 6, 4, 1]
[1, 5, 10, 10, 5, 1]

为了符合题干，在那边加了个if
"""

def trangles2():
	L = [1]
	while True:
		yield L
		L = [L[x] + L[x+1] for x in range(len(L) - 1)]
		L.insert(0, 1) # 首位插入1
		L.append(1)    # 尾部插入1
		if len(L) -1 > 5:
			break

for t in trangles2():
	print(t)
