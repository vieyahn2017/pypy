#!/usr/bin/python
#encoding: utf-8

import string

the_date = "20180108"
deal_item_lines = ["201801030000000000237922201801041560000000000000000000000000000000002153202018010314344003160106A00000108 379 20180104",
                   "201801030000000000237922201801041560000000000000000000000000000000002153202018010314344003160106A00000109 379 20180104"]
deal_counts_8_bits = str(len(deal_item_lines)).zfill(8)

filled_variables = {"the_date": the_date,
                    "deal_counts_8_bits": deal_counts_8_bits,
                    "deal_item_lines": '\n'.join(deal_item_lines)}


content = """
OFDCFDAT
20
02
379
${the_date}
999
APPSHEETSERIALNO
TRANSACTIONCFMDATE
......
SHAREREGISTERDATE
${deal_counts_8_bits}
${deal_item_lines}
OFDCFEND
"""
template = string.Template(content)

trans_content = template.substitute(the_date=filled_variables["the_date"],
                                    deal_counts_8_bits=filled_variables["deal_counts_8_bits"],
                                    deal_item_lines=filled_variables["deal_item_lines"])
print trans_content

