#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

s = pd.Series([1,3,5,np.nan,6,8])
print s

dates = pd.date_range('20130101', periods=6)
print dates

df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list('ABCD'))
print df

df2 = pd.DataFrame({ 'A' : 1.,
    'B' : pd.Timestamp('20130102'),
    'C' : pd.Series(1,index=list(range(4)),dtype='float32'),
    'D' : np.array([3] * 4,dtype='int32'),
    'E' : pd.Categorical(["test","train","test","train"]),
    'F' : 'foo' })
print df2
print df2.dtypes

df.head()
df.tail(3)
df.index
df.columns
df.values
df.describe()
df.T
df.sort_index(axis=1, ascending=False)
df.sort_values(by='B')

df['A']
df[0:3]
df['20130102':'20130104']
df.loc[dates[0]]
df.loc[:,['A','B']]
df.loc['20130102':'20130104',['A','B']]
df.loc['20130102',['A','B']]
df.loc[dates[0],'A']
df.at[dates[0],'A']
df.iloc[3]
df.iloc[3:5,0:2]
df.iloc[[1,2,4],[0,2]]
df.iloc[1:3,:]
df.iloc[:,1:3]
df.iloc[1,1]
df.iat[1,1]
df[df.A > 0]
df[df > 0]

df3 = df.copy()
df3['E'] = ['one', 'one','two','three','four','three']
df3[df3['E'].isin(['two','four'])]


s1 = pd.Series([1,2,3,4,5,6], index=pd.date_range('20130102', periods=6))
df['F'] = s1
df.at[dates[0],'A'] = 0
df.iat[0,1] = 0
df.loc[:,'D'] = np.array([5] * len(df))

df4 = df.copy()
df4[df4 > 0] = -df4
df4

# 缺失值处理
df1 = df.reindex(index=dates[0:4], columns=list(df.columns) + ['E'])
df1.loc[dates[0]:dates[1],'E'] = 1
df1.dropna(how='any')
df1.fillna(value=5)


df.mean() #执行描述性统计
df.mean(1)
s = pd.Series([1,3,5,np.nan,6,8], index=dates).shift(2)
df.sub(s, axis='index')

df.apply(np.cumsum) # 计算每一行的累积
df.apply(lambda x: x.max() - x.min())

# 直方图
s = pd.Series(np.random.randint(0, 7, size=10))
s.value_counts()

# String Methods
s = pd.Series(['A', 'B', 'C', 'Aaba', 'Baca', np.nan, 'CABA', 'dog', 'cat'])
s.str.lower()


# Merge
df = pd.DataFrame(np.random.randn(10, 4))
pieces = [df[:3], df[3:7], df[7:]]
pd.concat(pieces)
pd.concat(pieces) == df  #True

left = pd.DataFrame({'key': ['foo', 'foo'], 'lval': [1, 2]})
right = pd.DataFrame({'key': ['foo', 'foo'], 'rval': [4, 5]})
pd.merge(left, right, on='key')

left = pd.DataFrame({'key': ['foo', 'bar'], 'lval': [1, 2]})
right = pd.DataFrame({'key': ['foo', 'bar'], 'rval': [4, 5]})
pd.merge(left, right, on='key')

df = pd.DataFrame(np.random.randn(8, 4), columns=['A','B','C','D'])
s = df.iloc[3]
df.append(s, ignore_index=True)


# Grouping
df = pd.DataFrame({'A' : ['foo', 'bar', 'foo', 'bar','foo', 'bar', 'foo', 'foo'],
    'B' : ['one', 'one', 'two', 'three', 'two', 'two', 'one', 'three'],
    'C' : np.random.randn(8),
    'D' : np.random.randn(8)})
df.groupby('A').sum()
df.groupby(['A','B']).sum()


# Reshaping
tuples = list(zip(*[['bar', 'bar', 'baz', 'baz',
    'foo', 'foo', 'qux', 'qux'],
    ['one', 'two', 'one', 'two',
    'one', 'two', 'one', 'two']]))

index = pd.MultiIndex.from_tuples(tuples, names=['first', 'second'])
df = pd.DataFrame(np.random.randn(8, 2), index=index, columns=['A', 'B'])
df2 = df[:4]
stacked = df2.stack()
stacked.unstack()
stacked.unstack(1)
stacked.unstack(0)


# Pivot Tables 数据透视表
df = pd.DataFrame({'A' : ['one', 'one', 'two', 'three'] * 3,
    'B' : ['A', 'B', 'C'] * 4,
    'C' : ['foo', 'foo', 'foo', 'bar', 'bar', 'bar'] * 2,
    'D' : np.random.randn(12),
    'E' : np.random.randn(12)})
pd.pivot_table(df, values='D', index=['A', 'B'], columns=['C'])

# Time Series
rng = pd.date_range('1/1/2012', periods=100, freq='S')
ts = pd.Series(np.random.randint(0, 500, len(rng)), index=rng)
ts.resample('5Min').sum()
# 如将按秒采样的数据转换为按5分钟为单位进行采样的数据）
ts.resample('1Min').sum()
ts.resample('10S').sum()

rng = pd.date_range('3/6/2012 00:00', periods=5, freq='D')
ts = pd.Series(np.random.randn(len(rng)), rng)
ts
# Time zone representation
ts_utc = ts.tz_localize('UTC')
# Convert to another time zone
ts_utc.tz_convert('US/Eastern')

# 时间跨度转换 Converting between time span representations
rng = pd.date_range('1/1/2012', periods=5, freq='M')
ts = pd.Series(np.random.randn(len(rng)), index=rng)
ps = ts.to_period()
ps.to_timestamp()

# 时期和时间戳之间的转换 可以使用一些方便的算术函数
prng = pd.period_range('1990Q1', '2000Q4', freq='Q-NOV')
ts = pd.Series(np.random.randn(len(prng)), prng)
ts.index = (prng.asfreq('M', 'e') + 1).asfreq('H', 's') + 9
ts.head()


# Categorical  分类的，按类别的，绝对性的
df = pd.DataFrame({"id":[1,2,3,4,5,6], "raw_grade":['a', 'b', 'b', 'a', 'a', 'e']})
df["grade"] = df["raw_grade"].astype("category")
df["grade"]
# Name: grade, dtype: category
# Categories (3, object): [a, b, e]
df["raw_grade"]
# Name: raw_grade, dtype: object
# 
## Rename the categories to more meaningful names 
df["grade"].cat.categories = ["very good", "good", "very bad"]
# Reorder the categories and simultaneously add the missing categories
# 对类别进行重新排序，增加缺失的类别：
df["grade"] = df["grade"].cat.set_categories(["very bad", "bad", "medium", "good", "very good"])
df.sort_values(by="grade")
df.groupby("grade").size()


# Plotting
ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
ts = ts.cumsum()
ts.plot()
plt.show() 

df = pd.DataFrame(np.random.randn(1000, 4), index=ts.index, columns=['A', 'B', 'C', 'D'])
df = df.cumsum()
plt.figure(); df.plot(); plt.legend(loc='best'); plot.show()
#调用figure创建一个绘图对象，并且使它成为当前的绘图对象。不创建绘图对象直接调用plot,matplotlib会为我们自动创建一个绘图对象
#legend : 显示图示

df3 = pd.DataFrame(np.random.randn(1000, 2), columns=['B', 'C']).cumsum()
df3['A'] = pd.Series(list(range(len(df))))
df3.plot(x='A', y='B')
plt.show() 

# Other Plots
##
# bar or barh for bar plots
# hist for histogram  # Histograms 直方图; 柱状图;
# box for boxplot
# kde or density for density plots
# area for area plots
# scatter for scatter plots
# hexbin for hexagonal bin plots
# pie for pie plots

df2 = pd.DataFrame(np.random.rand(10, 4), columns=['a', 'b', 'c', 'd'])
df2.plot.bar(); plt.show()
#df2.plot.bar(stacked=True);
df2.plot.barh(stacked=True); plt.show()

df4 = pd.DataFrame({'a': np.random.randn(1000) + 1, 'b': np.random.randn(1000),
    'c': np.random.randn(1000) - 1}, columns=['a', 'b', 'c'])
plt.figure();
df4.plot.hist(alpha=0.5)

df = pd.DataFrame(np.random.rand(10, 4), columns=['a', 'b', 'c', 'd'])
df.plot.area();

df = pd.DataFrame(np.random.rand(50, 4), columns=['a', 'b', 'c', 'd'])
df.plot.scatter(x='a', y='b');

ax = df.plot.scatter(x='a', y='b', color='DarkBlue', label='Group 1');
df.plot.scatter(x='c', y='d', color='DarkGreen', label='Group 2', ax=ax);

df.plot.scatter(x='a', y='b', c='c', s=50);
df.plot.scatter(x='a', y='b', s=df['c']*200);

df = pd.DataFrame(np.random.randn(1000, 2), columns=['a', 'b'])
df['b'] = df['b'] + np.arange(1000)
df.plot.hexbin(x='a', y='b', gridsize=25)

ts = pd.Series(3 * np.random.rand(4), index=['a', 'b', 'c', 'd'], name='series')
ts.plot.pie(figsize=(6, 6))
ts.plot.pie(labels=['AA', 'BB', 'CC', 'DD'], colors=['r', 'g', 'b', 'c'], autopct='%.2f', fontsize=20, figsize=(6, 6))

df = pd.DataFrame(3 * np.random.rand(4, 2), index=['a', 'b', 'c', 'd'], columns=['x', 'y'])
df.plot.pie(subplots=True, figsize=(8, 4))


from pandas.tools.plotting import scatter_matrix
df = pd.DataFrame(np.random.randn(1000, 4), columns=['a', 'b', 'c', 'd'])
scatter_matrix(df, alpha=0.2, figsize=(6, 6), diagonal='kde')
# need scipy


# Getting Data In/Out
# CSV文件
df.to_csv('D:/t/foo.csv')
pd.read_csv('D:/t/foo.csv')

# HDF5存储
df.to_hdf('D:/t/foo.h5','df')
# HDFStore requires PyTables
# pip install tables-3.3.0-cp27-cp27m-win_amd64.whl
pd.read_hdf('D:/t/foo.h5','df')

# Excel文件
df.to_excel('D:/t/foo.xlsx', sheet_name='Sheet1')
pd.read_excel('D:/t/foo.xlsx', 'Sheet1', index_col=None, na_values=['NA'])
# need openpyxl