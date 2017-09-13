# -*- coding: utf-8 -*-

def A(m, n):
    res = 1
    for i in range(m, m-n, -1):
        res *= i
    return res


def C(m, n):
    res = A(m, n)
    for i in range(1, n+1):
        res /= i
    return res

# annother way
def C2(m, n):
    return A(m,n)/A(n,n);

def SumA(m, range_i):
    sum = 0
    for i in range_i:
        sum += A(m, i)
    return sum

def SumC(m, range_i):
    sum = 0
    for i in range_i:
        sum += C(m, i)
    return sum


# range(1,5) #代表从1到5(不包含5)
# [1, 2, 3, 4]
# >>> range(1,5,2) #代表从1到5，间隔2(不包含5)
# [1, 3]
# >>> range(5) #代表从0到5(不包含5)
# [0, 1, 2, 3, 4]
