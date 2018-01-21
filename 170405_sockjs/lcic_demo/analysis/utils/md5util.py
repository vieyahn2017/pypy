# -*- coding:utf-8 -*- 
# --------------------
# Author:		Ken
# Description:	MD5工具类
# --------------------


def md5(str):
    import hashlib
    import types
    # print type(str)
    if type(str) is types.StringType:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    else:
        return ''
