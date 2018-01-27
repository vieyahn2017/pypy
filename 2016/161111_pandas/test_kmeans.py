#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import *
import time
import matplotlib.pyplot as plt
from kmeans import *
import codecs

## step 1: load data  
print "step 1: load data..."  
dataSet = [] 

# windows BOM干扰，这原始代码要出错
# fileIn = open('testSet.txt')  
# for line in fileIn.readlines():  
#     lineArr = line.strip().split('\t')  
#     dataSet.append([float(lineArr[0]), float(lineArr[1])])  

fileIn = open('testSet.txt') 
data = fileIn.read()
if data[:3] == codecs.BOM_UTF8:
	data = data[3:]

for line in data.split('\n')[:-1]:
    lineArr = line.strip().split(',') 
    dataSet.append([float(lineArr[0]), float(lineArr[1])])  

print dataSet

## step 2: clustering...  
print "step 2: clustering..."  
dataSet = mat(dataSet)  
k = 4 
centroids, clusterAssment = kmeans(dataSet, k)  
  
## step 3: show the result  
print "step 3: show the result..."  
showCluster(dataSet, k, centroids, clusterAssment)  
