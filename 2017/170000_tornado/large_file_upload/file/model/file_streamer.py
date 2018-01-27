# -*- coding:utf-8 -*-
#!/usr/bin/env python

import os
import re
import time
from ..utils.thumbnail import thumb
from ..utils.fileforder import create_localtime_folder
from config import UPLOAD_PATH

THUMB_SIZE = 200

def ps_save2db(poststreamer, psdb, user='admin', printchunk=False):

    parts_chunk = []
    img_path = create_localtime_folder(UPLOAD_PATH)

    def checkinvalid(filename):
        if len(filename) == 0:
            raise Exception(">! file name check error !!!")
        #这个函数目前只这样简单写了，以后需要完善

    def rename(location, oldname):
        """poststreamer采用的tmpfile机制，这个方法把该临时文件名字转换成规范式的名字"""
        rstr = r"[\/\\\:\*\?\"\<\>\|]"      # '/\:*?"<>|'
        stripName = re.sub(rstr, "", oldname)
        _tmpName = time.strftime('%Y%m%d_%H%M%S__') + stripName
        newName = os.path.join(img_path, _tmpName)
        os.rename(location, newName)
        return newName
        #return os.path.splitext(newname);  #返回文件名和扩展名(shortname,extension)

    #for idx,part in enumerate(self.parts):  #内置的enumerate函数是取序列号
    for part in poststreamer.parts:
        try:
            part_chunk_={}
            part["tmpfile"].close()
            part_chunk_['username'] = user #以后完善时候，需要从页面读取文件上传者。直接在handler处赋值即可
            part_chunk_['size'] = part["size"]
            params = part["headers"][0].get("params",None)
            filename = params['filename']
            checkinvalid(filename)
            part_chunk_['filename'] = filename
            part_chunk_['contenttype'] = part["headers"][1].get("value", "text/plain")
            part_chunk_['location'] = rename(part["tmpfile"].name, filename)
            if part_chunk_['contenttype'].startswith('image'):
                part_chunk_['thumb'] = thumb(part_chunk_['location'], img_path, THUMB_SIZE)
            else:
                part_chunk_['thumb'] = None
            parts_chunk.append(part_chunk_)
            if printchunk:
                print part_chunk_

        except Exception:  #,e:   #非文件field，这里的e='filename' # print "Not File Field Error: %s" % e
            if printchunk:
                print "poststreamer.parts process --- Not File Field :", part["headers"][0].get("params")
            part["tmpfile"].close()
            os.unlink(part["tmpfile"].name) #DELETE FILE

    if printchunk:
        print '--File Field---------', parts_chunk

    for part_c in parts_chunk:
        try:
            psdb.insert("""INSERT INTO file_upload_test(filename, location, contenttype, thumb, size, username)
                            VALUES( %s,%s,%s,%s,%s,%s) RETURNING id;""",
                            part_c['filename'],
                            part_c['location'],
                            part_c['contenttype'],
                            part_c['thumb'],
                            part_c['size'],
                            part_c['username'])
            psdb.commit()
        except Exception, e:
            print "DB Insert Error: %s" % e
