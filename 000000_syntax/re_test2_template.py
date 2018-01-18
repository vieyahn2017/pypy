#!/usr/bin/python
#encoding: utf-8

### 用正则实现的 简单的模板替换

import random
import re

the_date = "20180108"
deal_item_lines = ["201801030000000000237922201801041560000000000000000000000000000000002153202018010314344003160106A00000108 379 20180104",
                   "201801030000000000237922201801041560000000000000000000000000000000002153202018010314344003160106A00000109 379 20180104"]
deal_counts_8_bits = str(len(deal_item_lines)).zfill(8)

filled_variables = {"the_date": the_date,
                    "deal_counts_8_bits": deal_counts_8_bits,
                    "deal_item_lines": '\n'.join(deal_item_lines)}


def sub_variable(text, key, value):
    return re.sub(r"{{[^}]*" + key + r"[^}]*}}", value, text)

def sub_variables(text, variables):
    for key in variables:
        text = sub_variable(text, key, variables[key])
    return text


template = """
OFDCFDAT
20
02
379
{{ the_date }}
999
APPSHEETSERIALNO
TRANSACTIONCFMDATE
......
SHAREREGISTERDATE
{{ deal_counts_8_bits }}
{{ deal_item_lines }}
OFDCFEND
"""

trans_template = sub_variables(template, filled_variables)
print trans_template

