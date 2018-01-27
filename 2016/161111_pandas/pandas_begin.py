#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
2016April Python学习笔记 - Pandas学习

Python Data Analysis Library 或 pandas 是基于NumPy 的一种工具，该工具是为了解决数据分析任务而创建的。Pandas 纳入了大量库和一些标准的数据模型，提供了高效地操作大型数据集所需的工具。pandas提供了大量能使我们快速便捷地处理数据的函数和方法。你很快就会发现，它是使Python成为强大而高效的数据分析环境的重要因素之一。百度


Series 和 DataFrame 分别对应于一维的序列和二维的表结构。 
pandas 约定俗成的导入方法如下：
"""

from pandas import Series,DataFrame
import pandas as pd

# Series 可以看做一个定长的有序字典。基本任意的一维数据都可以用来构造 Series 对象
# DataFrame 是一个表格型的数据结构。DataFrame 的构造方法与 Series 类似，只不过可以同时接受多条一维数据源，每一条都会成为单独的一列

# 切片:
df[:2]
df["one":"three"]
df.ix[:2,:3] #前两行三列
df.ix[:,"year":"year"]

# 使用函数:
f = lambda x:x.max()-x.min()
df.apply(f,axis=0)
df.apply(f,axis=1)

# 用numpy统计个数:
ucount = np.array(df['username']!='-1').sum()

# 同时统计多列满足条件的个数:
subject_list = ['math','english','music']
count_list = (df[df['username']!='-1'].loc[:, subject_list]).apply(lambda x: (x > 0).sum(), axis=0)
for pos,x in enumerate(count_list):
    mydict[subject_list[pos]] = x

# 统计单列不同分组的个数
didf = df[df['username']!=-1].groupby('sex')['id'].count()
mydict['man'] = didf['man']
mydict['woman'] = didf['woman']
