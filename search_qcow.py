# coding=utf-8
##!/usr/bin/python
# Filename: file_info.py
# https://github.com/Stavitsky/Qcow2-files-parsing/blob/master/file_info.py
import os
import sys
import json
import struct
from collections import OrderedDict  #for sorting keys in dictionary


OS = sys.platform #operation system

def get_info(curf, begin, read, param_of_unpack):
    """ Method read 'read' bytes of current file 'curf' from 'begin'-byte,
     unpack them with 'param_of_unpack'
    """
    curf.seek(begin)
    info = curf.read(read)
    info = struct.unpack(param_of_unpack, info)
    return  str(info[0])

def get_bf_name(qcowf, backing_file_offset_start, backing_file_size):
    """ Method returns backing file name """
    if int(backing_file_offset_start) == 0:
        return -1 #if backing missed
    else:
        int_bf_offset = int(backing_file_offset_start)
        int_bf_size = int(backing_file_size)

        qcowf.seek(int_bf_offset)
        info = qcowf.read(int_bf_size)  #read all backing file bytes
        info = struct.unpack(str(int_bf_size)+'s', info)  #unpack bf info
        return str(info[0])

def get_shapshot_info(qcowf, ss_offset):
    """Method returns dictionary with information about snapshot """
    qcowf.seek(int(ss_offset)+12)#length of id
    len_id = qcowf.read(2)
    len_id = struct.unpack('>H', len_id)

    qcowf.seek(int(ss_offset)+14)#length of name
    len_name = qcowf.read(2)
    len_name = struct.unpack('>H', len_name)

    qcowf.seek(int(ss_offset)+32)# size of ss
    ss_size = qcowf.read(4)
    ss_size = struct.unpack('>I', ss_size)

    qcowf.seek(int(ss_offset)+36)#size of extra data
    ex_data_size = qcowf.read(4)
    ex_data_size = struct.unpack('>I', ex_data_size)

    #offset to id position
    qcowf.seek(int(int(ss_offset)+40+int(ex_data_size[0])))
    ss_id = qcowf.read(int(len_id[0]))
    ss_id = struct.unpack('c', ss_id)

    #offset to name position
    qcowf.seek(int(int(ss_offset)+40+int(ex_data_size[0])+len_id[0]))
    ss_name = qcowf.read(int(len_name[0]))
    ss_name = struct.unpack(str(len_name[0])+'s', ss_name)

    #offset to padding to round up
    currentlength = \
        int(int(ss_offset)+40+int(ex_data_size[0])+len_id[0]+len_name[0])

    while currentlength % 8 != 0:
        currentlength += 1

    ssobj = {'id': ss_id[0], 'name':ss_name[0], 'virtual_size':ss_size[0]}

    return (ssobj, currentlength) #sorted snapshot info + its length

def get_file_dict(qcowf):
    """ Method returns dictionary with information about file """
    qcow_dict = {} #create dictionary of file info

    nb_ss = int(get_info(qcowf, 60, 4, '>I')) #number of snapshots
    ss_offset = get_info(qcowf, 64, 8, '>Q')  #snapshots offset
    filename = str(os.path.abspath(qcowf.name))
    size = str(os.stat(qcowf.name).st_size)
    virtual_size = get_info(qcowf, 24, 8, '>Q')
    backing_file = get_bf_name(
        qcowf, get_info(qcowf, 8, 8, '>Q'), get_info(qcowf, 16, 4, '>I'))

    if OS == 'win32':
        filename = filename.replace('\\', '/') #correct view of path to files

    qcow_dict['filename'] = filename
    qcow_dict['size'] = size
    qcow_dict['virtual_size'] = virtual_size

    if backing_file != -1:
        qcow_dict['backing_file'] = backing_file

    if nb_ss != 0: #if there are any snapshots in file
        qcow_dict['snapshots'] = []
        keyorder_ss = ["id", "name", "virtual_size"]
        for _ in range(1, nb_ss+1): #go through all snapshots
            ss_dict, ss_offset = get_shapshot_info(qcowf, ss_offset)
            qcow_dict['snapshots'].append(ss_dict)

    return qcow_dict


# End of file_info.py    

# Filename: search_qcow.py
# https://github.com/Stavitsky/Qcow2-files-parsing/blob/master/search_qcow.py

def parse_dirs(src, dirs=0, files=0, qfi_files=0, files_data=None, is_log=True):
    """ returns array of qcow files-data
        and counts total files, dirs and qcow files
        Method walk through directory and searchs qcow files
    """
    out_lines = []
    if files_data is None:
        files_data = []

    for each_file in os.listdir(src): #for each file in current folder
        file_wp = os.path.join(src, each_file) #full path to file (with folders)
        if os.path.isdir(file_wp): #if file_wp is folder
            dirs += 1
            out_lines.append('\nFolder: ' + file_wp)
            files_data, dirs, files, qfi_files = \
                parse_dirs(file_wp, dirs, files, qfi_files, files_data)
        elif os.stat(file_wp).st_size != 0:
            file_o = open(file_wp, 'rb') #opened file
            files += 1
            out_lines.append("\nFile: " + file_wp)
            if get_info(file_o, 0, 3, '3s') == 'QFI':
                qfi_files += 1
                out_lines.append(' - QFI-file')
                dict_of_file_data = get_file_dict(file_o)
                files_data.append(dict_of_file_data)
            file_o.close()
        else:
            files += 1
            out_lines.append("\nFile: " + file_wp + " - EMPTY-file")

    if is_log:
        sys.stdout.write(''.join(out_lines))
    return files_data, dirs, files, qfi_files


# End of search_qcow.py


def main():
    """ main function insert qcow files info to json outfile """

    currentpath = os.path.dirname(__file__)
    outfile = "search_qcow_trial.json"

    is_log = True # False
    files, q_dirs, q_files, qfi_files = parse_dirs(currentpath, is_log=is_log)
    # print files, q_dirs, q_files, qfi_files
    # files = [{'size': '2233073664', 'virtual_size': '42949672960', 'filename': 'D:/fsp_assets/FusionSphere openstack/service/kvm_euler_basetemplate-1.0.1/kvm_euler_basetempalate.qcow2'}] 
    # q_dirs, q_files, qfi_files === 0 5 1

    try:
        if q_files == 0:
            raise MyError("There are no any files in folder ('{0}').\n".format(currentpath))
    except MyError as err: #if error catched
        sys.stdout.write(err.message)
        exit(0)
    else: #if there are no any exceptions
        with open(outfile, 'w') as outfile:
            #indent - friendly view in json, ensure-russian letters in path
            json.dump(files, outfile, indent=2, ensure_ascii=False)
        #folders, include current
        sys.stdout.write('\n\nFoldes: {0}, files: {1}, Qcow-files: {2}.\n'.format(q_dirs, q_files, qfi_files))

main()
