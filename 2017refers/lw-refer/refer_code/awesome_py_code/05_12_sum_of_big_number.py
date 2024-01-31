#!/usr/bin/python  
#-*-coding:utf-8-*-
# 大数求和

d1 = '314159263334344444444444444444444445353535434'
d2 = '322224333333333453647586908344478888888888888888888'

# d1 = '3141592633'
# d2 = '2219999322299'

L1 = []
L2 = []

for i in range(0, len(d1)):
	L1.append(int(d1[i]))
for i in range(0, len(d2)):
	L2.append(int(d2[i]))

if(len(d1) > len(d2)):
	# print("d1 longer")
	for i in range(len(d1) - len(d2)):
		L2.insert(0, 0)
else:
	# print("d2 longer")
	for i in range(len(d2) - len(d1)):
		L1.insert(0, 0)	
print L1, '\n', L2

L = []  #Sum
for i in range(len(L1)):
	L.append(L1[i] + L2[i])
A = len(L)
L.insert(0, 0)
print "the sum begin of L:", L

while A >= 0:
	if((L[A]/10) >= 1):
		L[A] = L[A] % 10
		L[A-1] = L[A-1] + 1
	A = A -1

print "the sum end of L:", L
if(L[0] == 0):
	print "the sum = %s" % "".join(str(x) for x in L[1:])
else:
	print "the sum = %s" % "".join(str(x) for x in L)



