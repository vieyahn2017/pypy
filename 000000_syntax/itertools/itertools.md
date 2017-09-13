#Python的namedtuple使用详解

##1.　chain的使用

```python
for item in  itertools.chain(listone,listtwo):   #合并
```

##2.　count的使用

```python
for item in itertools.count(100):  
# 从100开始，cout返回一个无界的迭代器
```


##3.  cycle的使用
功能：从列表中取元素，到列表尾后再从头取...   
无限循环，因为cycle生成的是一个无界的失代器   

```python
total = 50

for i  in  itertools.cycle(range(10)):
    print i,
    total -= 1
    if total % 10 == 0:
        print ';'
    if total < 0:
        break

# 0 1 2 3 4 5 6 7 8 9 ;
# 0 1 2 3 4 5 6 7 8 9 ;
# 0 1 2 3 4 5 6 7 8 9 ;
# 0 1 2 3 4 5 6 7 8 9 ;
# 0 1 2 3 4 5 6 7 8 9 ;
# 0
```

##4.  ifilter的使用
ifilter(fun,iterator) 返回一个可以让fun返回True的迭代器
```python
for i in itertools.ifilter(lambda x: x and x>5, range(-10,20)):
    print i,
    
# 6 7 8 9 10 11 12 13 14 15 16 17 18 19
```


##5.  imap的使用
imap(fun, iterator)   
返回一个迭代器，对iterator中的每个项目调用fun


##6.  islice的使用
islice()(seq, [start,] stop [, step])    
功能：返回迭代器，其中的项目来自　将seq，从start开始,到stop结束，以step步长切割后


##7.  izip的使用

izip(*iterator)   
功能：返回迭代器，项目是元组，元组来自*iterator的组合

```python
# itertools.izip   和 zip(build-in方法)

listone = ['a','b','c']
listtwo = ['11','22','abc']
zip(listone, listtwo)

# [('a', '11'), ('b', '22'), ('c', 'abc')]

listone = ['a','b','c']
listtwo = ['11','22','abc']
for item in itertools.izip(listone, listtwo):
    print item,

# ('a', '11') ('b', '22') ('c', 'abc')

itertools.izip(listone, listtwo)
# <itertools.izip at 0x499af88>

```
### izip
文档中的描述：   
Make an iterator that aggregates elements from each of the iterables. Like zip() except that it returns an iterator instead of a list. Used for lock-step iteration over several iterables at a time.   
把不同的迭代器的元素聚合到一个迭代器中。类似zip（）方法，但是返回的是一个迭代器而不是一个list。用于同步迭代一次几个iterables 

###zip
文档中这样描述：   
This function returns a list of tuples, where the i-th tuple contains the i-th element from each of the argument sequences or iterables. The returned list is truncated in length to the length of the shortest argument sequence.   
就是把多个序列或者是迭代器的元素，组合成元组。返回的元组的长度是所有输入序列中最短的.   

如果输入的两个序列都是特别大的情况，zip就会很慢了。


##8.  repeate

```python
repeate(elem [,n])
```


