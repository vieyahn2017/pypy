#!/usr/bin/python
# -*- coding: utf-8 -*-

from basecode import *

# python basecode.py -c ext4_extent -h "10 00 00 00  01 00 02 00 1E 86 00 00" 单独拎出来
def decode_hex(class_type, hex_input):

    loc = locals()
    try:
        exec("test_obj = {}()".format(class_type))
    except NameError:
        print('param <class> %s  is not existed.' % class_type)
        print('%s -c <class> -h <hex chars input>' % sys.argv[0])
        exit(1)
    test_obj = loc['test_obj']
    test_obj_size = test_obj.calculate_size()

    formater = FormatDecoder('input')
    input_bytes, input_length = formater.parse_chr_array_2_bytes(hex_input)
    if input_length < test_obj_size:
        print("input hex size [%s] less than sizeof(%s)=[%s]" % (input_length, class_type, test_obj_size))
        exit(1)
    elif input_length > test_obj_size:
        print("input hex size [%s] more than sizeof(%s)=[%s], " % (input_length, class_type, test_obj_size))
        input_bytes = input_bytes[:test_obj_size]
        print("only use the previous required data: %s" % input_bytes)

    test_obj.decode(input_bytes)
    # test_obj.tojson_print1()
    test_obj.print_cmp_with_hex(formater.parse_chr_array_2_hex_list(hex_input))


def test01():
    class_type = "ext4_extent"
    hex_input = "10 00 00 00  01 00 02 00 1E 86 00 00"
    decode_hex(class_type, hex_input)


"""
以这个inode=18为例，来研究extent_tree吧

00000120  00 00 08 00 01 00 00 00  0a f3 01 00 04 00 00 00  |................|
00000130  00 00 00 00 00 00 00 00  04 00 00 00 b0 84 00 00  |................|
00000140  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000150  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000160  00 00 00 00  

debugfs:  stat <18>
EXTENTS:
(0-3):33968-33971

"""

if __name__ == '__main__':
    class_type = "ext4_extent_header"
    hex_input = "0a f3 01 00 04 00 00 00  00 00 00 00"
    decode_hex(class_type, hex_input)
    class_type = "ext4_extent_idx"
    hex_input = "00 00 00 00  04 00 00 00 b0 84 00 00 "
    decode_hex(class_type, hex_input)