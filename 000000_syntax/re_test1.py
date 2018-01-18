#!/usr/bin/python
#encoding: utf-8

import random
import re

content = """
 1 <?xml version="1.0"?>
 2 <collection shelf="New Arrivals">
 3     <movie title="Enemy Behind">
 4        <type>War, Thriller</type>
 5        <format>DVD</format>
 6        <year>2003</year>
 7        <rating>PG</rating>
 8        <stars>10</stars>
 9        <description>Talk about a US-Japan war</description>
10     </movie>
11     <movie title="Transformers">
12        <type>Anime, Science Fiction</type>
13        <format>DVD</format>
14        <year>1989</year>
15        <rating>R</rating>
16        <stars>8</stars>
17        <description>A schientific fiction</description>
18     </movie>
19        <movie title="Trigun">
20        <type>Anime, Action</type>
21        <format>DVD</format>
22        <episodes>4</episodes>
23        <rating>PG</rating>
24        <stars>10</stars>
25        <description>Vash the Stampede!</description>
26     </movie>
27     <movie title="Ishtar">
28        <type>Comedy</type>
29        <format>VHS</format>
30        <rating>PG</rating>
31        <stars>2</stars>
32        <description>Viewable boredom</description>
33     </movie>
34 </collection>
"""

print re.sub(r'\n\s*\d+\s', '\n', content)
# 删除行前的数字（可能数字前带一个空格）
