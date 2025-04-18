#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
基础类型参考BaseCode._type_map,实际由struct模块提供
嵌套自定义类型时,需要在子类中重新定义_type_map,并把BaseCode类的_type_map深拷贝到子类中
"""

import traceback
import inspect
import struct
import json
import re
import pprint
import getopt
import sys
import time
import copy

# main正常，需要这边import。因为存在交叉引用，因此这边打开的时候，basecode_structs本身执行会失败
from basecode_structs import *

GLOBAL_SIZE_DICT = {}
GLOBAL_SIZE_DICT["ext4_extent"] = 12
GLOBAL_SIZE_DICT["ext4_extent_idx"] = 12
GLOBAL_SIZE_DICT["ext4_extent_header"] = 12
GLOBAL_SIZE_DICT["ext4_inode"] = 160


def my_try_except_warpper(is_exit=False, err_msg=None):
    def _try_except_warpper(actual_do):
        def add_robust(*args, **keyargs):
            try:
                return actual_do(*args, **keyargs)
            except:
                print("Error: ", traceback.format_exc())
                print('Error execute: {}'.format(actual_do.__name__))
                if err_msg:
                    print(err_msg)
                if is_exit:
                    exit(1)
        return add_robust
    return _try_except_warpper


class EncodeError(Exception):
    def __init__(self, error_info='error'):
        super().__init__(self)
        self.error_info = error_info

    def __str__(self):
        return self.error_info


def debug_log(*obj):
    return # 调试时打开
    info = inspect.getframeinfo(inspect.currentframe().f_back, 0)

    print(*obj, '| ' + info.filename, info.function, info.lineno)


## not used
def has_class_attr(name, attr):
    """
    判断类中是否有类属性
    :param name: 类名
    :param attr: 类属性名
    :return:
    """
    token_list = eval('dir(' + name + ')')
    if attr in token_list:
        return True
    return False


class FieldType(object):
    # 把之前的tuple格式的field改成现在的FieldType，简直太清爽
    __slots__ = ('ctype', 'name', 'raw_field', 'name', 'reverse', 'length')

    def __init__(self, ctype, name, **kwargs):
        self.ctype = ctype
        self.name = name
        self.reverse = kwargs.get("reverse", False)
        self.length = int(kwargs.get("length", 1))
        self.raw_field = kwargs.get("raw_field", "")

    def __getitem__(self, key):
        if key == 0:
            return self.ctype
        elif key == 1:
            return self.name
        elif key == 2:
            return {"length": self.length, "reverse": self.reverse}

    def is_addtional(self):
        if self.length > 1:
            return True
        # if self.reverse:
        #     return True
        return False

    def get_field_length(self):
        return self.length

    def is_little_endian(self):
        return self.reverse

    def get_endian_char(self):
        # !网络序（同大端序），> (big-endian) ， < (little-endian)
        return "<" if self.reverse else ">"

    def get_raw_field(self):
        # get这样调用函数，set直接赋值也可以通过kwargs传递
        return self.raw_field

    @staticmethod
    def get_little_endian_int16(int_num):
        hex_str_raw = hex(int_num)
        hex_str = hex_str_raw[2:].rjust(4, '0')
        hex_le = '0x' + hex_str[2:4] + hex_str[0:2]
        return int(hex_le, 16)

    @staticmethod
    def get_little_endian_int32(int_num):
        hex_str_raw = hex(int_num)
        hex_str = hex_str_raw[2:].rjust(8, '0')
        hex_le = '0x' + hex_str[6:8] + hex_str[4:6] + hex_str[2:4] + hex_str[0:2]
        return int(hex_le, 16)

    @staticmethod
    def get_little_endian_int64(int_num):
        hex_str_raw = hex(int_num)
        hex_str = hex_str_raw[2:].rjust(16, '0')
        hex_le = '0x' + hex_str[15:16] + hex_str[13:14]+ hex_str[11:12]+ hex_str[9:10] + hex_str[6:8] + hex_str[4:6] + hex_str[2:4] + hex_str[0:2]
        return int(hex_le, 16)

    @staticmethod
    def get_little_endian_hex(hex_str):
        pass


class BaseCode(object):

    _type_map_index_pack_tag = 1
    _type_map_index_pack_size = 2  # unused
    _type_map = {
        # C类型:(说明, 编码标志)
        'char': ('int', 'B'),
        'string': ('str', 'B'),
        'uint32_t': ('int', 'I'),
        'int32_t': ('int', 'i'),
        'int64_t': ('int', 'q'),
        'uint64_t': ('int', 'Q'),
        'uint16_t': ('short', 'H'),
        'int16_t': ('short', 'h'),
        'float': ('float', 'f'),
        'double': ('double', 'd'),
    }

    # 每种基础类型所占字节数
    _ctype_size_map = {'I': 4, 'B': 1, 'i': 4, 'b': 1, 'Q': 8, 'q': 8, 'f': 4, 'd': 8, 'h': 2, 'H': 2}

    _fields_index_ctype = 0
    _fields_index_value_name = 1
    _fields_index_array_length = 2 # 之前的第三个参数的数字length
    _fields_index_addtion_dict = 2 # 现在我改成字典 {"length":1, "reverse":True}  reverse=True，表示小端序

    # 用元组，扩展性很差，改成FieldType，为了兼容性良好，__init__构造的一致，实现了__getitem__，也支持[]读取
    _fields = [
        # (C类型, 变量名)
        FieldType('uint32_t', 'nUint'),
        FieldType('string', 'szString', **{"length": 20}),
        FieldType('int32_t', 'nInt3'),
        FieldType('uint32_t', 'nUintArray', **{"length": 4}),
    ]

    def __init__(self):
        """
        初始都置空
        """
        for one in self._fields:
            setattr(self, one[self._fields_index_value_name], None)


    def encode(self, nest=1):
        data = b''
        tmp = b''
        debug_log("&" * nest, self.__class__.__name__, "encode struct start :")
        for one in self._fields:
            debug_log("#" * nest, "encode one element:", one)
            ctype = one[self._fields_index_ctype]
            value = getattr(self, one[self._fields_index_value_name])

            if one.is_addtional():
                # _addtions = one[self._fields_index_addtion_dict]
                # if type(_addtions) != dict:
                #     print("param one[2] error: %s", _addtions)
                #     exit(1)
                endian_char = one.get_endian_char()
                length = one.get_field_length()
                if length > 1:
                    tmp = self._encode_array(ctype, value, length, endian_char)
                else: # 这子域的是复制外面那个else分支的代码，只是修改了endian_char
                    if ctype not in BaseCode._type_map:
                        tmp = value.encode(nest + 1)
                    else:
                        fmt = endian_char + self._type_map[ctype][self._type_map_index_pack_tag]
                        tmp = struct.pack(fmt, value)

            else:
                # 不是基础类型,即嵌套定义
                if ctype not in BaseCode._type_map:
                    tmp = value.encode(nest + 1)
                else:  # !网络序（同大端序），> (big-endian) ， < (little-endian)
                    fmt = '!' + self._type_map[ctype][self._type_map_index_pack_tag]
                    tmp = struct.pack(fmt, value)
                    # debug_log(fmt, type(value), value)
            debug_log("#" * nest,"encode one element:", len(tmp), tmp)
            data += tmp
        debug_log("&" * nest, self.__class__.__name__, "encode end: len=", len(data), data)
        return data

    def _encode_array(self, ctype, value, max_length, endian_char="!"):
        """
        打包数组
        如果是字符串类型 需要做下特殊处理
        :param ctype:
        :param value:
        :param max_length:
        :param endian_char --  !网络序（同大端序），> (big-endian) ， < (little-endian)
        :return:
        """
        debug_log('ctype:', ctype, type(ctype))
        if ctype == 'string':
            max_length -= 1  # 字符串长度需要减一
            value = bytes(value, encoding='utf8')
            #print(value)

        if len(value) > max_length:
            raise EncodeError('the length of  array is too long')

        # # # pack长度
        # data = struct.pack(endian_char + 'H', len(value))
        # debug_log("array count:", len(value), "value:", value, type(value))
        data = b""
        # pack数组内容
        for one in value:
            #debug_log("self._type_map[ctype][1]=", self._type_map[ctype][self._type_map_index_pack_tag], one)
            if ctype not in BaseCode._type_map:
                data += one.encode()
            else:
                data += struct.pack(endian_char + self._type_map[ctype][self._type_map_index_pack_tag], one)
        return data

    def decode(self, data, offset=0, nest=1):
        """
        :param data:
        :return:
        """
        debug_log("&" * nest, self.__class__.__name__, "decode struct start :")
        for one in self._fields:
            debug_log("#" * nest, "decode one element:", one)
            ctype = one[self._fields_index_ctype]

            if one.is_addtional():
                # _addtions = one[self._fields_index_addtion_dict]
                # if type(_addtions) != dict:
                #     print("param one[2] error: %s", _addtions)
                #     exit(1)
                endian_char = one.get_endian_char()
                length = one.get_field_length()
                if length > 1:
                    offset = self._decode_array(one, data, offset, nest)
                else: # 这子域的是复制外面那个else分支的代码，只是修改了endian_char
                    ctype_attr = self._type_map[ctype]
                    if ctype not in BaseCode._type_map:
                        value = eval(ctype + '()')
                        offset = value.decode(data, offset, nest)
                        setattr(self, one[self._fields_index_value_name], value)
                    else:
                        fmt = endian_char + ctype_attr[self._type_map_index_pack_tag]
                        value, = struct.unpack_from(fmt, data, offset)
                        offset += self._ctype_size_map[ctype_attr[self._type_map_index_pack_tag]]
                        debug_log(one, one[self._fields_index_value_name])
                        setattr(self, one[self._fields_index_value_name], value)

            else:
                ctype_attr = self._type_map[ctype]
                endian_char = one.get_endian_char()
                if ctype not in BaseCode._type_map:
                    value = eval(ctype + '()')
                    offset = value.decode(data, offset, nest)
                    setattr(self, one[self._fields_index_value_name], value)
                else:
                    fmt = endian_char + ctype_attr[self._type_map_index_pack_tag]
                    value, = struct.unpack_from(fmt, data, offset)
                    offset += self._ctype_size_map[ctype_attr[self._type_map_index_pack_tag]]
                    debug_log(one, one[self._fields_index_value_name])
                    setattr(self, one[self._fields_index_value_name], value)
            debug_log("#" * nest, "decode one element end:", offset, one)
        return offset

    def _decode_array(self, field, data, offset, nest):
        ctype = field[self._fields_index_ctype]
        # array_num, = struct.unpack_from('!H', data, offset)  # 之前该同学的代码会把长度序列化和反序列化
        # offset += 2
        array_num = field.get_field_length()
        value = []
        ctype_attr = self._type_map[ctype]
        endian_char = field.get_endian_char()
        debug_log("$" * nest, "decode array count", array_num, field)

        while array_num > 0:
            array_num -= 1
            if ctype not in BaseCode._type_map:
                one = eval(ctype + '()')
                offset = one.decode(data, offset, nest)
                value.append(one)
            else:
                one, = struct.unpack_from(endian_char + ctype_attr[self._type_map_index_pack_tag], data, offset)
                value.append(one)
                offset += self._ctype_size_map[ctype_attr[self._type_map_index_pack_tag]]

        if ctype == 'string':
            # 这里是因为字符串是按照单个字符解包,会解成python的int,通过chr()转化为字符型
            # value = [97,98]
            # list(map(chr,value)) 后等于 ['a','b']
            # ''.join() 就转成'ab'

            value = ''.join(list(map(chr, value)))
            value = bytes(value, encoding='latin1').decode('utf8')


        setattr(self, field[self._fields_index_value_name], value)
        debug_log("$" * nest, "decode array ok", array_num, field)
        return offset

    def tprint(self, tab=0):
        prefix = '  ' * tab
        debug_log(prefix, self.__class__, ":")
        for one in self._fields:
            ctype = one[self._fields_index_ctype]
            value = getattr(self, one[self._fields_index_value_name])
            if ctype not in BaseCode._type_map:
                debug_log(prefix, one[self._fields_index_value_name] + ' =')
                if type(value) == list:
                    [el.tprint(tab + 1) for el in value]
                else:
                    value.tprint(tab + 1)
            else:
                debug_log(prefix, one[self._fields_index_value_name] + ' =', value)

    def todict(self):
        """
        把字段转成字典
        :param ret:
        :return:
        """
        ret = {}
        for one in self._fields:
            ctype = one[self._fields_index_ctype]
            key = one[self._fields_index_value_name]
            value = getattr(self, key)
            # print(key + ' =', value)
            if ctype not in BaseCode._type_map:
                # 自定义类型
                if type(value) == list:
                    # 数组
                    ret[key] = [el.todict() for el in value]
                else:
                    ret[key] = value.todict()

            else:
                # 基本类型
                ret[key] = value

        return ret


    def tojson_print1(self):
        print(json.dumps(self.todict(), indent=4, separators=(', ', ': '), ensure_ascii=False))

    def tojson_print2(self):  # 美观度不如1
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(self.todict())

    @staticmethod
    def parse_hex_str_2_time(hex_str):
        """ '0x6215e413' to '2022-02-23 15:36:51' """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(hex_str, 16)))

    @staticmethod
    def parse_hex_str_ipv4_address(hex_str):
        """ '0x33200954' to '51.32.9.84' """
        ip_p3 = hex_str[-8:-6]
        ip_p2 = hex_str[-6:-4]
        ip_p1 = hex_str[-4:-2]
        ip_p0 = hex_str[-2:]
        return ".".join([str(int(x, 16)) for x in [ip_p3, ip_p2, ip_p1, ip_p0]])

    @staticmethod
    def print_cmp_with_hex_static(ctype, _input_data):
        loc = locals()
        exec("test_obj = {}();".format(ctype))
        test_obj = loc["test_obj"]
        test_obj.print_cmp_with_hex(_input_data)

    def print_cmp_with_hex(self, _input_data):
        """
        输出诸如
        struct ext4_extent {
            __le32  ee_block      : 00 00 00 00 :  0      : 0
            __le16  ee_len        : 01 00       :  0x1    : 1
            __le16  ee_start_hi;  : 00 00       :  0      : 0
            __le32  ee_start_lo;  : 1e 86 00 00 :  0x861e : 34334
        };

        嵌套的自动解包：
            先把嵌套类型的名字和原始数据打出来
            再把参入放入yield_params
            最后用exec调用执行转换

        占位格式化
        mat = "{:020}\t{:010}\t{:12}"  # 冒号后面指定输出宽度，冒号后的第一个0表示用0占位
        print(mat.format(1,2,3333))    # 00000000000000000001    0000000002              3333

        """

        results = []
        results.append("struct %s {" % self.__class__.__name__)

        yield_params = []

        key_width = 30
        mat = "    {:10}{:%s} : {:30}: {:30} : {:20} {:20}" % key_width
        mat2 = "    {:10}{:%s} : {:62} : {:20}" % key_width
        offset = 0
        for one in self._fields:
            key = one[self._fields_index_value_name]
            value = getattr(self, key)
            raw_field = one.get_raw_field()
            ctype = one[self._fields_index_ctype]

            if ctype not in BaseCode._type_map:
                length = one.get_field_length()
                ctype_size = 12  ### 要实际计算，之前测试全是ext4_extent的三个对象，都是12的size
                # 已知类型，直接返回其size
                if ctype in GLOBAL_SIZE_DICT.keys():
                    ctype_size = GLOBAL_SIZE_DICT[ctype]
                else:
                    # 未知类型，实时计算
                    # 可能还需要import类型
                    loc = locals()
                    exec("_size_by_exec = %s().calculate_size(True)" % ctype)
                    ctype_size = loc["_size_by_exec"]
                    GLOBAL_SIZE_DICT[ctype] = ctype_size
                for i in range(length):
                    hex_data = []
                    for i in range(ctype_size):
                        hex_data.append(_input_data[offset + i])
                    offset += ctype_size
                    hex_list_str = " ".join(hex_data)
                    line_str = mat2.format(" ", raw_field, hex_list_str, " sizeof=%s" % ctype_size)
                    results.append(line_str)
                    yield_params.append((ctype, hex_data))
            else:
                ctype_size = self._ctype_size_map[self._type_map[ctype][self._type_map_index_pack_tag]]
                ctype_length = 1
                if type(value) == list:
                    ctype_length = len(value)

                hex_data = []
                for i in range(ctype_size * ctype_length):
                    hex_data.append(_input_data[offset + i])
                offset += ctype_size * ctype_length
                if one.is_little_endian():
                    hex_list_str = " ".join(hex_data)
                    hex_str = "0x" + "".join(hex_data[::-1])
                else:
                    hex_list_str = " ".join(hex_data)
                    hex_str = "0x" + "".join(hex_data)

                if not value:
                    value = int(hex_str, 16)  # exec调用的时候，上面的value获取值似乎有问题
                if type(value) == list:
                    if ctype == "char":
                        value = ''.join([chr(c) for c in value])
                    else:
                        value = str(value)
                # print(raw_field, key, hex_list_str, hex_str, value, " ")
                if len(hex_list_str) > 23:
                    hex_list_str = hex_list_str[:15] + "..." +  hex_list_str[-11:]
                if len(hex_str) > 23:
                    hex_str = hex_str[:18] + "..." +  hex_str[-8:]
                line_str = mat.format(raw_field, key, hex_list_str, hex_str, value, " ")
                if "\r" in line_str: # 修正了一个输出格式不对的bug
                    line_str = line_str.replace("\r", "")
                if "\n" in line_str:
                    line_str = line_str.replace("\n", "")
                if key.endswith("time"):
                    try:
                        time_parse = BaseCode.parse_hex_str_2_time(hex_str)
                        line_str = mat.format(raw_field, key, hex_list_str, hex_str, value, " : " + time_parse)
                    except:
                        pass
                if key.endswith("ipv4_address"):
                    try:
                        ip_parse = BaseCode.parse_hex_str_ipv4_address(hex_str)
                        line_str = mat.format(raw_field, key, hex_list_str, hex_str, value, " : " + ip_parse)
                    except:
                        pass

                results.append(line_str)

        results.append("}")
        print('\n'.join(results))

        if yield_params:
            print(" >>> extend instances :")
            # print(yield_params)
            for ctype1, hex_data1 in yield_params:
                BaseCode.print_cmp_with_hex_static(ctype1, hex_data1)

    def calculate_size(self, is_print=False):
        """
        最新：已经完成嵌套的功能，但是局限性在于：
        必须在 【# 自定义类型】处，手动import嵌套的子类型，要不然会报类型找不到
        而且：嵌套的子类型是通过exec来执行的，debug会出错。
        （因此：最新把exec代码局限在_exec_calc_size内部函数里）
        """
        result = 0
        for one in self._fields:
            ctype = one[self._fields_index_ctype]
            key = one[self._fields_index_value_name]
            if ctype in BaseCode._type_map: # 基本类型
                if not one.is_addtional():
                    result += self._ctype_size_map[self._type_map[ctype][self._type_map_index_pack_tag]]
                else:
                    length = one.get_field_length()
                    result += length * self._ctype_size_map[self._type_map[ctype][self._type_map_index_pack_tag]]
            else:
                # 自定义类型

                # 自定义类型的size，如果动态获取，只能通过exec，局限性略大
                def _exec_calc_size(ctype_name):
                    from basecode_structs import ext4_extent
                    from basecode_structs import ext4_extent_header
                    loc = locals()
                    # exec("test_obj = {}();print(test_obj)".format(ctype))
                    exec("test_obj = {}();".format(ctype))
                    test_obj = loc["test_obj"]
                    _ctype_size = test_obj.calculate_size()
                    return _ctype_size

                one_ctype_size = 0
                # 已知类型，直接返回其size
                if ctype in GLOBAL_SIZE_DICT.keys():
                    one_ctype_size = GLOBAL_SIZE_DICT[ctype]
                else:
                    one_ctype_size = _exec_calc_size(ctype)
                    GLOBAL_SIZE_DICT[ctype] = one_ctype_size

                if not one.is_addtional():
                    result += one_ctype_size
                else:
                    length = one.get_field_length()
                    result += length * one_ctype_size

        if is_print:
            print("    # [calculate_size]: class %s, size=%s" % (self.__class__.__name__, result))
        return result


class FormatDecoder(object):

    def __init__(self, ptype='input'):
        self.ptype = ptype
        self.input_raw = None
        self.input_length = 0
        self.input_bytes = bytes([0])
        self.output_data = None
        self.test_obj = None

    @staticmethod
    def parse_struct(ccode):
        """
        struct ext4_extent_header {
            __le16	eh_magic;	/* probably will support different formats
                                (i add a new line)       #define EXT4_EXT_MAGIC		cpu_to_le16(0xf30a)
                                */
            __le16	eh_entries;	/* number of valid entries */
            __le16	eh_max;		/* capacity of store in entries */
            __le16	eh_depth;	/* has tree real underlying blocks? */
                                // i add a new line
            __le32	eh_generation;	// generation of the tree
        };

        c代码的定义 转换成 python代码：
        class ext4_extent_header(BaseCode):
            _fields = [
                FieldType('uint16_t', 'eh_magic', **{"raw_field": "__le16", "reverse": True}),
                FieldType('uint16_t', 'eh_entries', **{"raw_field": "__le16", "reverse": True}),
                FieldType('uint16_t', 'eh_max', **{"raw_field": "__le16", "reverse": True}),
                FieldType('uint16_t', 'eh_depth', **{"raw_field": "__le16", "reverse": True}),
                FieldType('uint32_t', 'eh_generation', **{"raw_field": "__le32", "reverse": True}),
            ]
        """

        content1 = re.sub(r'/\*.*?\*/', '', ccode, flags=re.S)  # 删除代码中的注释
        content = re.sub(r'(//.*)', '', content1)  # 删除代码中的注释
        lines = content.split("\n")
        start_line_no = 0
        for i, line in enumerate(lines):
            if "struct" in line:
                start_line_no = i
                break

        new_lines = []
        python_codes = []
        for line in lines[start_line_no + 1:]:
            line_strip = line.strip()
            if line_strip == '};':
                break
            if line_strip == '':
                continue
            new_lines.append(line_strip.rstrip(";").replace("\t", "    "))
        # print(new_lines)

        max_key_width = 18
        for field_line in new_lines:
            key_width1 = len(field_line) - 10
            if key_width1 > max_key_width:
                max_key_width = key_width1

        def _get_class_name(struct_line):
            arr1 = struct_line.replace("\t", "    ").split(" ")
            return list(filter(lambda x: x, arr1))[1]

        space_regex = re.compile('\s+')

        def _parse_line_field(field_line, key_width=18):
            # c语言的代码__le16	ee_start_hi  转换成python代码，本文件定义的field格式 ('uint16_t', 'ee_start_hi', {"reverse": True}),
            arr2 = space_regex.split(field_line)
            # print(arr2)
            field_name = arr2[-1]  # field_name = arr2[1]
            field_type = arr2[0]
            field_type_mapped = "char"
            field_addtional_reverse = False
            if len(arr2) > 2:
                field_type = " ".join(arr2[:-1])

            if field_type == "u8":
                field_type_mapped = "char"
            elif field_type == "_u8":
                field_type_mapped = "char"
            elif field_type == "__u8":
                field_type_mapped = "char"
            elif field_type == "u16":
                field_type_mapped = "uint16_t"
            elif field_type == "_u16":
                field_type_mapped = "uint16_t"
            elif field_type == "__u16":
                field_type_mapped = "uint16_t"
            elif field_type == "u32":
                field_type_mapped = "uint32_t"
            elif field_type == "_u32":
                field_type_mapped = "uint32_t"
            elif field_type == "__u32":
                field_type_mapped = "uint32_t"
            elif field_type == "u64":
                field_type_mapped = "uint64_t"
            elif field_type == "_u64":
                field_type_mapped = "uint64_t"
            elif field_type == "__u64":
                field_type_mapped = "uint64_t"
            elif field_type == "__be16":
                field_type_mapped = "uint16_t"
            elif field_type == "__be32":
                field_type_mapped = "uint32_t"
            elif field_type == "__be64":
                field_type_mapped = "uint64_t"
            elif field_type == "__le16":
                field_type_mapped = "uint16_t"
            elif field_type == "__le32":
                field_type_mapped = "uint32_t"
            elif field_type == "__le64":
                field_type_mapped = "uint64_t"
            elif field_type == "unsigned short":
                field_type_mapped = "uint16_t"
            elif field_type == "unsigned int":
                field_type_mapped = "uint32_t"
            elif field_type == "unsigned long":
                field_type_mapped = "uint64_t"
            elif field_type == "unsigned long long":
                field_type_mapped = "uint64_t"
            elif field_type == "short":
                field_type_mapped = "int16_t"
            elif field_type == "int":
                field_type_mapped = "int32_t"
            elif field_type == "long":
                field_type_mapped = "int64_t"
            elif field_type == "long long":
                field_type_mapped = "int64_t"
            else:
                if "struct" in field_type:
                    # print("[%s] not base datatype, not supported." % field_type)
                    # field_type_mapped = field_type   # 原计划原值返回，但是会不可执行，直接return吧
                    field_type_mapped = field_type.split(" ")[1]
                elif "union" in field_type:
                    # print("[%s] not base datatype, not supported." % field_type)
                    # field_type_mapped = field_type   # 原计划原值返回，但是会不可执行，直接return吧
                    return
                else:
                    return

            if field_type in ["__le16", "__le32", "__le64"]:
                field_addtional_reverse = True

            # 占位格式化
            mat = "        FieldType({:12}\t{:%s}\t{:48})," % key_width
            addtional_dict = {"raw_field": field_type}
            if field_addtional_reverse:
                addtional_dict["reverse"] = True
            if field_name.endswith("]"):
                field_size = field_name.split("[")[1][:-1]
                addtional_dict["length"] = int(field_size)
                field_name = field_name.split("[")[0]
            addtional_dict_str = '**' + str(addtional_dict).replace("'", '"')
            field_code = mat.format("'%s'," % field_type_mapped, "'%s'," % field_name, addtional_dict_str)
            return field_code

        try:
            class_name = _get_class_name(lines[start_line_no])

            python_codes.append("class {}(BaseCode):".format(class_name))
            python_codes.append("    _fields = [")
            for field_line in new_lines:
                _parse_field = _parse_line_field(field_line, max_key_width)
                if _parse_field:
                    python_codes.append(_parse_field)
            python_codes.append("    ]")

            ccode_result = "\n".join(python_codes)
            print(ccode_result)
            return ccode_result, class_name

        except Exception as e:
            # print("Error: ", e)
            print("Error: ", traceback.format_exc())
            print("struct source format error")
            exit(1)

    @my_try_except_warpper(is_exit=True, err_msg="Decode hex data source format error")
    def parse_chr_array_2_bytes(self, chrs):
        """
        10 00 00 00  01 00 02 00  1E 86 00 00
        转换成<class 'bytes'>
        b'\x00\x00\x00\x10\x00\x01\x00\x02\x00\x00\x86\x1e'
        也支持 10000000010002001E860000

        === 严格来说，要严格校验chrs的格式
        """
        raw_data = []
        if " " in chrs:
            raw_data = list(filter(lambda x: x, chrs.split(" ")))
        else:
            for i, x in enumerate(chrs):
                if i % 2:
                    raw_data.append(chrs[i - 1] + x)
        hex_2_dec_data = [int(item, 16) for item in raw_data]
        result = bytes(hex_2_dec_data)
        print("[parse_chr_array_2_bytes]: %s" % result)
        if self.ptype == "input":
            self.input_bytes = result
            self.input_length = len(hex_2_dec_data)
        return result, len(hex_2_dec_data)

    def parse_chr_array_2_hex_list(self, chrs):
        """
        输入chrs 从hexdump来的 数据样式为  ' 00 00 c8 00 00 00 20 03  00 00 28 00 f3 35 0f 03  '
        输入chrs 内容没有被分割 数据样式为  '000064000000900100001400e87c8701'
        hex格式化输出使用，因此在parse_chr_array_2_bytes剪了部分代码过来
        输出：['00', '00', 'c8', '00', '00', '00', '20', '03', '00', '00', '28', '00', 'f3', '35', '0f', '03']
        """
        raw_data = []
        if " " in chrs:
            raw_data = list(filter(lambda x: x, chrs.split(" ")))
        else:
            for i, x in enumerate(chrs):
                if i % 2:
                    raw_data.append(chrs[i - 1] + x)
        if self.ptype == "input":
            self.output_data = raw_data
        return raw_data

    def decode_hex(self, class_type):
        loc = locals()
        try:
            exec("test_obj = {}()".format(class_type))
        except NameError:
            print("NameError when decode_hex")
            help(sys.argv[0])
        test_obj = loc['test_obj']
        test_obj_size = test_obj.calculate_size()

        if self.input_length < test_obj_size:
            print("input hex size [%s] less than sizeof(%s)=[%s]" % (self.input_length, class_type, test_obj_size))
            exit(1)
        elif self.input_length > test_obj_size:
            print("input hex size [%s] more than sizeof(%s)=[%s], " % (self.input_length, class_type, test_obj_size))
            self.input_bytes = self.input_bytes[:test_obj_size]
            print("only use the previous required data: %s" % self.input_bytes)

        test_obj.decode(self.input_bytes)
        self.test_obj = test_obj

    def parse_to_bytes(self, **kwargs):
        if self.ptype == "input":
            self.input_raw = kwargs.get("input")
            return self.parse_chr_array_2_bytes(self.input_raw)
        print("type is unsupported")

    def parse_to_hex_list(self):
        if self.ptype == "input":
            return self.parse_chr_array_2_hex_list(self.input_raw)
        print("type is unsupported")

    def show_output(self):
        if self.test_obj and self.output_data:
            # self.test_obj.tojson_print1()
            self.test_obj.print_cmp_with_hex(self.output_data)

    def run(self):
        if self.test_obj and self.output_data:
            # self.test_obj.tojson_print1()
            self.test_obj.print_cmp_with_hex(self.output_data)


class FormatDecoderHexdump(FormatDecoder):

    def __init__(self, rst_file=''):
        super().__init__(ptype="hexdump")
        self.rst_file = rst_file or "hexdump.rst"

    @my_try_except_warpper(is_exit=True, err_msg="Decode hexdump file hexdump.rst format error")
    def parse_to_bytes(self, **kwargs):
        raw_data = []
        with open(self.rst_file) as file1:
            rcode = file1.read()
            for line in rcode.split("\n"):  # line = "00000400  00 00 c8 00 00 00 20 03  00 00 28 00 f3 35 0f 03  |...... ...(..5..|"
                line_parse = line.split("|")[0][9:]
                raw_data.extend(self.parse_chr_array_2_hex_list(line_parse))
        hex_2_dec_data = [int(item, 16) for item in raw_data]
        result = bytes(hex_2_dec_data)
        print("[parse_hexdump_rst]: %s" % result)
        self.input_bytes = result
        self.input_length = len(hex_2_dec_data)

    def parse_to_hex_list(self):
        """
        hex格式化输出使用，因此在parse_hexdump_rst_2_bytes剪了部分代码过来
        """
        raw_data = []
        with open(self.rst_file) as file1:
            rcode = file1.read()
            for line in rcode.split("\n"):
                line_parse = line.split("|")[0][9:]
                raw_data.extend(self.parse_chr_array_2_hex_list(line_parse))
        self.output_data = raw_data


class FormatDecoderVib(FormatDecoder):
    def __init__(self, rst_file=''):
        super().__init__(ptype="vib")
        self.rst_file = rst_file or "vib2xxd.rst"

    @my_try_except_warpper(is_exit=True, err_msg="Decode hexdump file vib2xxd.rst format error")
    def parse_to_bytes(self, **kwargs):
        # FC新环境没有hexdump，用vi来操作，vi -b ttt1 二进制打开文件  :%!xxd 转换成十六进制
        raw_data = []
        with open(self.rst_file) as file1:
            rcode = file1.read()
            for line in rcode.split("\n"):  # line = "00000400: 0000 6400 0000 9001 0000 1400 e87c 8701  ..d..........|.."
                line_parse = "".join(line.split(":")[1][1:40].split(" "))
                raw_data.extend(self.parse_chr_array_2_hex_list(line_parse))
        hex_2_dec_data = [int(item, 16) for item in raw_data]
        result = bytes(hex_2_dec_data)
        print("[parse_vib2xxd_rst]: %s" % result)
        self.input_bytes = result
        self.input_length = len(hex_2_dec_data)

    def parse_to_hex_list(self):
        raw_data = []
        with open(self.rst_file) as file1:
            rcode = file1.read()
            for line in rcode.split("\n"):
                line_parse = "".join(line.split(":")[1][1:40].split(" "))
                raw_data.extend(self.parse_chr_array_2_hex_list(line_parse))
        self.output_data = raw_data


### 以下是基本功能测试片段
class ext4_extent__test(BaseCode):
    _fields =[
        FieldType('uint32_t', 'ee_block', **{"reverse": True}),
        FieldType('uint16_t', 'ee_len', **{"reverse": True}),
        FieldType('uint16_t', 'ee_start_hi', **{"reverse": True}),
        FieldType('uint32_t', 'ee_start_lo', **{"reverse": True}),
    ]

class ext4_extent__unreverse(BaseCode):
    _fields =[
        FieldType('uint32_t', 'ee_block'),
        FieldType('uint16_t', 'ee_len'),
        FieldType('uint16_t', 'ee_start_hi'),
        FieldType('uint32_t', 'ee_start_lo'),
    ]

class ext4_extent_header_mytest2(BaseCode):
    _fields = [
        FieldType('uint16_t', 'eh_magic', **{"reverse": True}),
        FieldType('uint16_t', 'eh_entries', **{"reverse": True}),
        FieldType('uint16_t', 'eh_max', **{"reverse": True}),
        FieldType('uint16_t', 'eh_depth', **{"reverse": True}),
        FieldType('uint32_t', 'eh_generation', **{"reverse": True}),
        # FieldType('uint64_t', 'test_field'),
    ]
    
class EXT4_TEST():
    @staticmethod
    def ext4_test():
        # 【10 00 00 00  01 00 02 00  1E 86 00 00】的ext4_extent（sizeof=12），
        # 10是ee_len， 02 00是ee_start_hi; 1E 86 00 00 ee_start_lo; 高16位，低32位，合在一起是 0x00020000861E
        print("ext4_test running====")
        extent1 = ext4_extent__unreverse() # b'\x00\x00\x00\x10\x00\x01\x00\x02\x00\x00\x86\x1e'
        extent1.ee_block = 16
        extent1.ee_len = 1
        extent1.ee_start_hi = 2
        extent1.ee_start_lo = 34334  # 0x861E
        data1 = extent1.encode()
        print('extent1 **final:', len(data1), type(data1), data1)

        print("extent2")
        extent2 = ext4_extent__unreverse()
        extent2.decode(data1)
        extent2.tojson_print1()

        print("c1")  # 因为是小端对象，不能这么赋值了
        c1 = ext4_extent__test()
        c1.ee_block = 16
        c1.ee_len = 1
        c1.ee_start_hi = 2
        c1.ee_start_lo = 34334  # 0x861E
        data_c1 = c1.encode()
        print('c1 **final:', len(data_c1), type(data_c1), data_c1)

        print("c2")
        c2 = ext4_extent__test()
        c2.decode(data_c1)
        c2.tojson_print1()

        """
        c1 **final: 12 <class 'bytes'> b'\x00\x00\x00\x10\x00\x01\x00\x02\x00\x00\x86\x1e'
        c2
        {
            "ee_block": 268435456, 
            "ee_len": 256, 
            "ee_start_hi": 512, 
            "ee_start_lo": 512098304  # 是 0x1E860000
        }
        """

        print("c3")  # 因为是小端对象，不能这么赋值了
        c3 = ext4_extent__test()
        c3.ee_block = FieldType.get_little_endian_int32(16)     # hex(268435456) '0x10000000'
        c3.ee_len = FieldType.get_little_endian_int16(1)        # hex(256) '0x0100
        c3.ee_start_hi = FieldType.get_little_endian_int16(2)   #  hex(512) '0x0200'
        c3.ee_start_lo = FieldType.get_little_endian_int32(34334)  # 0x861E  ## hex(512098304) '0x1e860000'
        data_c3 = c3.encode()
        print('c3 **final:', len(data_c3), type(data_c3), data_c3)

        print("c4")
        c4 = ext4_extent__test()
        c4.decode(data_c3)
        c4.tojson_print1()

        print("ttt")
        ttt = ext4_extent__test()
        formater = FormatDecoder()
        tttbytes0 = formater.parse_chr_array_2_bytes('10000000010002001E860000')
        print(tttbytes0)
        tttbytes = formater.parse_chr_array_2_bytes('10 00 00 00  01 00 02 00  1E 86 00 00')
        print(tttbytes)
        ttt.decode(tttbytes[0])
        ttt.tojson_print1()

    @staticmethod
    def ext4_ccode_test1():
        print("ext4_ccode_test1 running====")
        ccode = """
            int i;
            int cl;
        struct ext4_extent_header_mytest {
            __le16	eh_magic;	/* probably will support different formats
                                (i add a new line)       #define EXT4_EXT_MAGIC		cpu_to_le16(0xf30a)
                                */
            __le16	eh_entries;	/* number of valid entries */
            __le16	eh_max;		/* capacity of store in entries */
            __le16	eh_depth;	/* has tree real underlying blocks? */
                                // i add a new line
            __le32	eh_generation;	// generation of the tree
            unsigned       long long   test_field;
        };
        """
        length = 0
        ccode_result, class_name = FormatDecoder.parse_struct(ccode)
        ccode_result += "\n"
        ccode_result += "test_obj = {}()".format(class_name)
        ccode_result += "\n"
        ccode_result += "length = test_obj.calculate_size()"
        ccode_result += "\n"
        ccode_result += "print(length)"
        # eval(ccode_result)  # eval new对象 - 报错 SyntaxError: invalid syntax
        # eval("test_obj = {}()".format(class_name))
        # eval("length = test_obj.calculate_size()")
        # 换成exec，结合locals搞定
        loc = locals()
        exec(ccode_result)
        class_ext4_extent_header_mytest = loc['ext4_extent_header_mytest']
        print(class_ext4_extent_header_mytest)
        test_obj =class_ext4_extent_header_mytest()
        test_obj.calculate_size()

    @staticmethod
    def ext4_ccode_test2():
        print("ext4_ccode_test2 running====")
        test_obj = ext4_extent_header_mytest2()
        length = test_obj.calculate_size()
        print(length)

    @staticmethod
    def ext4_ccode_test3():
        print("ext4_ccode_test3 running====")
        exec("ext4_extent_header_mytest2().calculate_size()")
        exec("test_obj = ext4_extent_header_mytest2(); test_obj.calculate_size()")

        loc = locals()
        exec("test_obj = ext4_extent_header_mytest2()")  # 这里exec的对象，下文中无法使用
        # 为了修正这样的错误，你需要在调用 exec() 之前使用 locals() 函数来得到一个局部变量字典。 之后你就能从局部字典中获取修改过后的变量值了。
        test_obj = loc['test_obj']
        print(test_obj)
        length = test_obj.calculate_size()
        print(length)

    @staticmethod
    def ext4_inode_hexdump_test():
        print("\n\next4_ccode_test3 running====")
        print("\n========ext4_inode_hexdump_test========")
        input_bytes = b'\xa0\x81\x00\x00\x18\x1b\x00\x00\x13\xe4\x15bY\xe4\x15bY\xe4\x15b\x00\x00\x00\x00\x00\x00\x01\x00\x10\x00\x00\x00\x00\x00\x08\x00\x01\x00\x00\x00\n\xf3\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x88\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x8a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x03\xac\xb3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00g\xe3\x00\x00 \x00\xe9\xa2(\xaa\x96\xd7(\xaa\x96\xd7\xac\xda\xc4C\x13\xe4\x15b\xac\xda\xc4C\x00\x00\x00\x00\x00\x00\x00\x00'
        # input_length = len(input_bytes) # 160
        test_obj = ext4_inode()
        test_obj.decode(input_bytes)

        _input_data = ['a0', '81', '00', '00', '18', '1b', '00', '00',  '13', 'e4', '15', '62', '59', 'e4', '15', '62',
                       '59', 'e4', '15', '62', '00', '00', '00', '00',  '00', '00', '01', '00', '10', '00', '00', '00',
                       '00', '00', '08', '00', '01', '00', '00', '00',  '0a', 'f3', '02', '00', '04', '00', '00', '00',
                       '00', '00', '00', '00', '00', '00', '00', '00',  '01', '00', '00', '00', '00', '88', '00', '00',
                       '01', '00', '00', '00', '01', '00', '00', '00',  '00', '8a', '00', '00', '00', '00', '00', '00',
                       '00', '00', '00', '00', '00', '00', '00', '00',  '00', '00', '00', '00', '00', '00', '00', '00',
                       '00', '00', '00', '00', '05', '03', 'ac', 'b3',  '00', '00', '00', '00', '00', '00', '00', '00',
                       '00', '00', '00', '00', '00', '00', '00', '00',  '00', '00', '00', '00', '67', 'e3', '00', '00',
                       '20', '00', 'e9', 'a2', '28', 'aa', '96', 'd7',  '28', 'aa', '96', 'd7', 'ac', 'da', 'c4', '43',
                       '13', 'e4', '15', '62', 'ac', 'da', 'c4', '43', '00', '00', '00', '00', '00', '00', '00', '00']
        test_obj.print_cmp_with_hex(_input_data)

    @staticmethod
    @my_try_except_warpper()
    def ext4_sb_hexdump_test():
        print("\n\next4_sb_hexdump_test running====")
        print("\n========ext4_super_block_hexdump_test========")
        test_obj = ext4_super_block()
        hexdump_rst="test/hexdump_ext4_super_block.rst"
        formater = FormatDecoderHexdump(hexdump_rst)
        formater.parse_to_bytes()
        test_obj.decode(formater.input_bytes)
        formater.parse_to_hex_list()
        test_obj.print_cmp_with_hex(formater.output_data)

    @staticmethod
    @my_try_except_warpper()
    def gernel_test():
        EXT4_TEST.ext4_test()
        EXT4_TEST.ext4_ccode_test1()
        EXT4_TEST.ext4_ccode_test2()
        EXT4_TEST.ext4_ccode_test3()
        EXT4_TEST.ext4_inode_hexdump_test()
        EXT4_TEST.ext4_sb_hexdump_test()


## 拆分到basecode_structs始终还有问题，嵌套子类型不能声明在那边，eval的时候找不到
class ext4_extent(BaseCode):
    _fields = [
        FieldType('uint32_t', 'ee_block', **{"raw_field": "__le32", "reverse": True}),
        FieldType('uint16_t', 'ee_len', **{"raw_field": "__le16", "reverse": True}),
        FieldType('uint16_t', 'ee_start_hi', **{"raw_field": "__le16", "reverse": True}),
        FieldType('uint32_t', 'ee_start_lo', **{"raw_field": "__le32", "reverse": True}),
    ]
    # [calculate_size]: class ext_extent, size=12

class ext4_extent_idx(BaseCode):
    _fields = [
        FieldType('uint32_t', 'ei_block', **{"raw_field": "__le32", "reverse": True}),
        FieldType('uint32_t', 'ei_leaf_lo', **{"raw_field": "__le32", "reverse": True}),
        FieldType('uint16_t', 'ei_leaf_hi', **{"raw_field": "__le16", "reverse": True}),
        FieldType('uint16_t', 'ei_unused', **{"raw_field": "__u16"}),
    ]
    # [calculate_size]: class ext4_extent_idx, size=12

class ext4_extent_header(BaseCode):
    _fields = [
        FieldType('uint16_t', 'eh_magic', **{"raw_field": "__le16", "reverse": True}),
        FieldType('uint16_t', 'eh_entries', **{"raw_field": "__le16", "reverse": True}),
        FieldType('uint16_t', 'eh_max', **{"raw_field": "__le16", "reverse": True}),
        FieldType('uint16_t', 'eh_depth', **{"raw_field": "__le16", "reverse": True}),
        FieldType('uint32_t', 'eh_generation', **{"raw_field": "__le32", "reverse": True}),
    ]
    # [calculate_size]: class ext4_extent_header, size=12


if __name__ == '__main__1':
    EXT4_TEST.gernel_test()

# 不用动name了，直接在这改0和1
TEST_SWITCH = 0


def help(selfname):
    print('<hex input> is missing')
    print('%s -c <class> -h <hex chars input>' % selfname)
    print('%s -c <class> -r <hexdump/vi>' % selfname)
    exit(1)

# python basecode.py -s source.c
# python basecode.py -c ext4_extent -h "10 00 00 00  01 00 02 00 1E 86 00 00"
# python basecode.py -c ext4_inode -r hexdump
# python basecode.py -c ext4_super_block -r vi
if __name__ == '__main__':
    if TEST_SWITCH:
        EXT4_TEST.gernel_test()
        exit(0)

    class_type = None
    hex_input = None
    hex_rst_type = None
    src_code = None
    try:
        shortargs = 'c:h:r:s:'
        longargs = ['--class', '--hex',  '--resource', '--source']
        opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
        for opt, arg in opts:
            if opt in ("-c", "--class"):
                class_type = arg
            elif opt in ("-h", "--hex"):
                hex_input = arg
            elif opt in ("-r", "--resource_type"):
                hex_rst_type = arg
            elif opt in ("-s", "--source"):
                src_code = arg

        if src_code:
            file0 = open(src_code, mode='r')
            ccode = file0.read()
            ccode_result, class_name = FormatDecoder.parse_struct(ccode)
            exit(0)

        if class_type:
            formater = FormatDecoder('input')
            if hex_input:
                formater.parse_to_bytes(input=hex_input)
            elif hex_rst_type:
                if hex_rst_type in ["hexdump", "hd"]:
                    formater = FormatDecoderHexdump()
                    formater.parse_to_bytes()
                elif hex_rst_type == "vi":
                    formater = FormatDecoderVib()
                    formater.parse_to_bytes()
                else:
                    help(sys.argv[0])
            else:
                help(sys.argv[0])

            formater.decode_hex(class_type)
            formater.parse_to_hex_list()
            formater.show_output()

    except getopt.GetoptError:
        print('%s -c <class> -h <hex chars input>' % sys.argv[0])
        print('%s -s <source code>' % sys.argv[0])
        exit(2)
