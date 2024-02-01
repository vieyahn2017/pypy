#!/usr/bin/python
# -*- coding: utf-8 -*-

from basecode import *
## 需要注释掉basecode里的 from basecode_structs import *

# python basecode.py -s source.c 单独拎出来
if __name__ == '__main__':
    # gernel_test()
    src_code = "source.c"
    src_file = open(src_code, mode='r', encoding="utf8")
    ccode = src_file.read()
    ccode_result, class_name = FormatDecoder.parse_struct(ccode)
    exec(ccode_result)
    exec("%s().calculate_size(True)" % class_name)
    # loc = locals()
    # test_class = loc[class_name]
    # print(test_class)  # <class '__main__.ext_extent'>
    # exec("%s.__init__().calculate_size()" % test_class)  # 不行