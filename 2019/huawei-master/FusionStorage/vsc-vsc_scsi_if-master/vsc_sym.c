/********************************************************************
            Copyright (C) Huawei Technologies, 2012
  #���ߣ�Peng Ruilin (pengruilin@huawei.com)
  #����: sym ��ģ��
         ��ģ���/proc/kallsyms�ļ����ҵ�����kallsyms_lookup_name�ĵ�ַ��
         �����ô˺��������������ں˺�����Ӧ�ĵ�ַ��

********************************************************************/
#include "vsc_common.h"
#include "vsc_sym.h"

/**************************************************************************
 ��������  : ���ݽṹ�Ƿ������
          
 ��    ��  : 
 �� �� ֵ  : ��ʼ�����
**************************************************************************/
static int vsc_sym_data_align_chk(void) 
{
    if (sizeof(struct vsc_scsi_data_msg) != offsetof(struct vsc_scsi_data_msg, data)) {
        vsc_err("struct vsc_scsi_data_msg is not align.");
        return -EFAULT;
    }

    if (sizeof(struct vsc_scsi_data) != offsetof(struct vsc_scsi_data, vec)) {
        vsc_err("struct vsc_scsi_data is not align.");
        return -EFAULT;
    }

    if (sizeof(struct vsc_scsi_event) != offsetof(struct vsc_scsi_event, data)) {
        vsc_err("struct vsc_scsi_event is not align.");
        return -EFAULT;
    }

    if (sizeof(struct vsc_scsi_msg_data) != offsetof(struct vsc_scsi_msg_data, data)) {
        vsc_err("struct vsc_scsi_msg_data is not align.");
        return -EFAULT;
    }

    return 0;
}

/**************************************************************************
 ��������  : �������ų�ʼ��
          
 ��    ��  : 
 �� �� ֵ  : ��ʼ�����
**************************************************************************/
int __init vsc_sym_init(void)
{
    int retval = 0;

    /* �����Ϣ�ṹ�е�data�Ƿ���� */
    retval = vsc_sym_data_align_chk();
    if (retval ) {
        vsc_err("struct align check failed.\n");
    }
    return retval;
}

/**************************************************************************
 ��������  : sym�˳�����,sym���Ա�����ֵ�����跴��ʼ����
          
 ��    ��  : 
 �� �� ֵ  : 
**************************************************************************/
int vsc_sym_exit(void)
{
    return 0;
}

