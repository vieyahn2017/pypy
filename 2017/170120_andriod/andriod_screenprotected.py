from itertools import *

impossible = {'13': '2',
              '17': '4',
              '19': '5',
              '31': '2',
              '37': '5',
              '39': '6',
              '71': '4',
              '73': '5',
              '79': '8',
              '91': '5',
              '93': '6',
              '97': '8',
              '28': '5',
              '82': '5',
              '64': '5',
              '46': '5'
              }

def counts():
    iterlst = chain(*(permutations('123456789', i) for i in range(4, 10)))
    # ('9','8','7','6')生成这样的4-9位的字符元组 迭代器
    count = 0
    for i in iterlst:
        stri = ''.join(i)  # i = ('9','8','7','6') ; ''.join(('9','8','7','6')) ='9876'
        for k, v in impossible.items():
            if k in stri and v not in stri[:stri.find(k)]:
                break
            else:
                count += 1
    return count
    #这是原始代码，有bug


# permutations(iterable [,r]):
# 创建一个迭代器，返回iterable中所有长度为r的项目序列，如果省略了r，那么序列的长度与iterable中的项目数量相同：
# chain(iter1, iter2, ..., iterN):
# 给出一组迭代器(iter1, iter2, ..., iterN)，此函数创建一个新迭代器来将所有的迭代器链接起来，
# 返回的迭代器从iter1开始生成项， 直到iter1被用完，然后从iter2生成项，这一过程会持续到iterN中所有的项都被用完。

def counts():
    iterlst = chain(*(permutations('123456789', i) for i in range(4, 10)))
    # ('9','8','7','6')生成这样的4-9位的字符元组 迭代器
    count = 0
    for i in iterlst:
        stri = ''.join(i)  # i = ('9','8','7','6') ; ''.join(('9','8','7','6')) ='9876'
        iscount = True
        for k, v in impossible.items():
            if k in stri and v not in stri[:stri.find(k)]:
                iscount = False
                break
            else:
                pass
        if iscount:
            count += 1
    return count
    # 389112


# 　按照规则，1、3组合是不可能存在的，因为它会穿过2 
# 同样按照规则，如果中间的数字已经用过了，是可以穿过的，比如2、1、3，   2已经用过了，1是可以穿过2与3连接的。
# stri[:stri.find(k)] 返回k之前的stri子串



iterlst =  permutations('123456789', 4) 
# ('9','8','7','6')生成这样的4-9位的字符元组 迭代器
count = 0
for i in iterlst:
    stri = ''.join(i)  # i = ('9','8','7','6') ; ''.join(('9','8','7','6')) ='9876'
    iscount = True
    for k, v in impossible.items():
        if k in stri and v not in stri[:stri.find(k)]:
            iscount = False
            break
        else:
            pass
    if iscount:
        count += 1
print count






vertex = [1,3,7,9]
edge = [2,4,6,8]
center = [5]

impossible2 = {}
impossible3 = []
for i in range(1,10):
    if i in vertex:
        keys = [str(i)+str(j) for j in vertex if j!=i]
        values = [str((i+j)/2) for j in vertex if j!=i]
        impossible3 += zip(keys, values)
    elif i in edge:
        key = str(i)+str(10-i)
        value = str(5)
        #impossible3 += ((key,value)) #这样加怎么都会割裂为两个元素，就算是这样也不行 += tuple((key,value))
        impossible3.append((key,value))

impossible2 = dict(impossible3)

 
impossible2 = {'13': '2',
              '17': '4',
              '19': '5',
              '31': '2',
              '37': '5',
              '39': '6',
              '71': '4',
              '73': '5',
              '79': '8',
              '91': '5',
              '93': '6',
              '97': '8',
              '28': '5',
              '82': '5',
              '64': '5',
              '46': '5'
              }