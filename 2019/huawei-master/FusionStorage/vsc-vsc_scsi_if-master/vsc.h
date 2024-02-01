/********************************************************************
            Copyright (C) Huawei Technologies, 2012
  #����:  vsc �ӿ��ļ�

********************************************************************/
#include <linux/types.h>

#ifndef _VSC_H_
#define _VSC_H_

/* Ĭ�ϵ�������и��� */
/*����ȫ�ֲ���g_io_depth_per_lun��g_max_lun_per_vbs�����ֵ����*/
#define VSC_DEFAULT_MAX_CMD_NUMBER     (2048*2048)

/* ÿ��lun���������� */
/*����ȫ�ֲ���g_io_depth_per_lun�����ֵ����*/
#define VSC_DEFAULT_LUN_CMD_NUMBER     2048

/* ����CDB���ݳ��� */
#define VSC_MAX_CDB_LEN                256

/* ����������ʱʱ�� ��λ:�� */
#define VSC_RQ_MAX_TIMEOUT             120

/* ����target�쳣��ʱʱ�� ��λ:�� */
#define VSC_MAX_TARGET_ABNORMAL_TIMEOUT    6000

/* SCSI����ϲ���һ����ഫ����������� */
#define MAX_BATCH_SCSI_CMD_COUNT       (4)

/* SCSI��Ӧ�ϲ���һ����ഫ�����Ӧ���� */
#define MAX_BATCH_SCSI_RSP_COUNT       (4)

/* SCSI CDB��󳤶� */
#define MAX_CDB_LENGTH                 (16)

/* SCSI CMDЯ�����ݵ���󳤶� */
#define SCSI_MAX_DATA_BUF_SIZE         (256)

#define MAX_SCSI_MSG_AND_CDB_LENGTH  \
    ((sizeof(struct vsc_scsi_msg)+MAX_CDB_LENGTH)*MAX_BATCH_SCSI_CMD_COUNT)

#define MAX_SCSI_DATA_AND_RSP_LENGTH  \
    ((SCSI_MAX_DATA_BUF_SIZE+sizeof( struct vsc_scsi_rsp_msg))*MAX_BATCH_SCSI_RSP_COUNT)

#define VSC_IOCTL_NAME                 "vsc"            /* vsc-ioctl �ļ��� */

/* ioctl �ӿ� */
#define VSC_IOCTL_BASE                 (0x4B)           /* 'K' == 0x4B  */

#define VSC_ADD_HOST           _IO(VSC_IOCTL_BASE, 0)   /* ��������HOST */
struct vsc_ioctl_cmd_add_host {
    __u32        host;          /* HOST��ţ�ͨ��port������� */
    __u32        sys_host_id;   /* ��ϵͳע���scsi host id */
    __u32        max_channel;   /* ���ͨ���� */
    __u32        max_lun;       /* ���lun���� */
    __u32        max_id;        /* ���target���� */
    __u32        max_cmd_len;   /* ���CDB����� */
    __u32        max_nr_cmds;   /* HOST����������� */
    __u32        cmd_per_lun;   /* ÿ��lun����������� */
    __u32        sg_count;      /* ��������С�����㹫ʽΪ������С*sg_count��*/  
};

#define VSC_RMV_HOST           _IO(VSC_IOCTL_BASE, 1)   /* ɾ������HOST */
struct vsc_ioctl_cmd_rmv_host {
    __u32       host;            /* host���*/
};

#define VSC_ATTACH_HOST        _IO(VSC_IOCTL_BASE, 20)   /* �ҽ���������� */
struct vsc_ioctl_cmd_attatch_host {
    __u32        host;           /* host���*/
};

#define VSC_ADD_DISK           _IO(VSC_IOCTL_BASE, 10)   /* ���Ӵ��� */
#define VSC_RMV_DISK           _IO(VSC_IOCTL_BASE, 11)   /* ɾ������ */
/* �豸��ʶ�ṹ */
struct vsc_ioctl_disk {
    __u32        host;          /* HOST��� */
    __u32        channel;       /* ͨ���� */
    __u32        id;            /* target��� */
    __u32        lun;           /* lun��� */
};

#define VSC_SET_DISK_STAT      _IO(VSC_IOCTL_BASE, 12)   /* ���õ�������״̬ */  
#define VSC_GET_DISK_STAT      _IO(VSC_IOCTL_BASE, 13)   /* ��ȡ��������״̬ */

/* ����״̬ */
#define VSC_DISK_CREATED         1          /* �Ѿ������豸������û�д���sysfs�ļ� */
#define VSC_DISK_RUNNING         2          /* SCSI�豸״̬Ϊ���� �������ã�*/
#define VSC_DISK_CANCEL          3          /* ��ʼɾ���豸 */
#define VSC_DISK_DEL             4          /* �豸�Ѿ���ɾ�� */
#define VSC_DISK_QUIESCE         5          /* �豸Ϊ��� */
#define VSC_DISK_OFFLINE         6          /* SCSI�豸״̬Ϊ���� (������) */
#define VSC_DISK_BLOCK           7          /* SCSI�豸״̬Ϊ���� �������ã�*/
#define VSC_DISK_CREATED_BLOCK   8          /* �豸��������ʽ���� */
#define VSC_DISK_PREPARE_DELETE  9          /* �豸�Ѿ���Ԥɾ��*/

struct vsc_ioctl_disk_stat {
    __u32         host;          /* HOST��� */
    __u32         channel;       /* ͨ���� */
    __u32         id;            /* target��� */
    __u32         lun;           /* lun��� */
    __u32         stat;          /* ����״̬ */
};

#define VSC_DISK_RQ_TIMEOUT    _IO(VSC_IOCTL_BASE, 14)        /* ���ô���������г�ʱʱ�� */
struct vsc_ioctl_rq_timeout {
    __u32        host;          /* HOST��� */
    __u32        channel;       /* ͨ���� */
    __u32        id;            /* target��� */
    __u32        lun;           /* lun��� */
    __u32        timeout;       /* ��ʱʱ�䣬��λΪ�� */
};

#define VSC_SET_TARGET_ABNORMAL_TIMEOUT   _IO(VSC_IOCTL_BASE, 15) /* ����target�����쳣��ʱʱ�� */
struct vsc_ioctl_set_tg_abn_timeout {
    __u32        host;          /* HOST��� */
    __u32        timeout;       /* ��ʱʱ�䣬��λΪ�� */
};

/* ���������޲�������Ҫ��attach֮��ִ�� */
#define VSC_DETACH_HOST        _IO(VSC_IOCTL_BASE, 21)   /* �ͷ���������� */
#define VSC_SUSPEND_HOST       _IO(VSC_IOCTL_BASE, 30)   /* ������������� */
#define VSC_RESUME_HOST        _IO(VSC_IOCTL_BASE, 31)   /* �ָ���������� */

#define VSC_ADD_DISK_VOL_NAME  _IO(VSC_IOCTL_BASE, 32)
#define VSC_PREPARE_RMV_VOL    _IO(VSC_IOCTL_BASE, 33)
#define VSC_QUERY_DISK_VOL     _IO(VSC_IOCTL_BASE, 34)
#define VSC_RESUME_HOST_ALL    _IO(VSC_IOCTL_BASE, 35)

#define VSC_VOL_NAME_LEN       96
#define VSC_MAX_DISK_PER_HOST  512 
struct vsc_ioctl_disk_vol_name {
    __u32       host; /* ϵͳhost id����Դvsc_add_device_by_vol_nameʱsh->host_no;vsc�������ط�δ��ע����Ϊ�ڲ�host id */
    __u32       channel;
    __u32       id;
    __u32       lun;
    __u32       state;      /*ONLINE/DELETE*/
    char        vol_name[VSC_VOL_NAME_LEN];
    __u8        extend[0];  /* ������չ�ֶΣ���Ӱ��ԭ���� */
};

struct vsc_ioctl_query_vol {
    __u32 host;
    __u32 vol_num;
    struct vsc_ioctl_disk_vol_name volumes[VSC_MAX_DISK_PER_HOST];
};

/* ���ݶ�д����Ϣ���� */
#define VSC_MSG_TYPE_SCSI_CMD      0       /* scsi������Ϣ���� */
#define VSC_MSG_TYPE_EVENT         1       /* �쳣������Ϣ���� */
#define VSC_MSG_TYPE_SCSI_DATA     2       /* SCSI������Ϣ���� */

/* �¼����� */
#define VSC_EVENT_TYPE_ABORT       1       /* abort��Ϣ�¼� */
#define VSC_EVENT_TYPE_RESET_DEV   2       /* ��λ�豸�¼� */

/* scsi������Ϣ���� */
/* �����˽ṹ�������裬��Ҫ��Ӧ�ĵ���pad��Ա�Ĵ�С */
struct vsc_scsi_msg_data {
    __u32     data_type;                          /* �������� */
    __u32     data_len;                           /* ���ݳ��� */
    __u8      pad[0];                             /* ��֤data���뵽sizeof(�˽ṹ��Ĵ�С) */
    __u8      data[0];  /*lint !e157*/            /* �������� */
};

/* SCSI����abort��Ϣ */
struct vsc_event_abort {
    __u32     cmd_sn;                 /* �������к� */
    __u32     host;                   /* host��� */
    __u32     channel;                /* ͨ���� */
    __u32     id;                     /* target��� */
    __u32     lun;                    /* lun��� */    
};

/* SCSI���λ�豸��Ϣ */
struct vsc_event_reset_dev {
    __u32     cmd_sn;                 /* �������к� */
    __u32     host;                   /* host��� */
    __u32     channel;                /* ͨ���� */
    __u32     id;                     /* target��� */
    __u32     lun;                    /* lun��� */    
};

/* EVENT����ֵ */
#define VSC_EVENT_SUCCESS          0       /* �¼��ɹ� */

/* SCSI�����¼������Ϣ */
struct vsc_event_result {
    __u32     result;                 /* ��Ϣ������ɹ�Ϊ��VSC_EVENT_SUCCESS�� ����δ������ */
};

/* SCSI�����¼���Ϣ������vsc_scsi_event�������Ϊ4K*/ 
/* �����˽ṹ�������裬��Ҫ��Ӧ�ĵ���pad��Ա�Ĵ�С */
struct vsc_scsi_event {
    __u32      type;                   /* ���������, �����ֶ�ΪVSC_MSG_TYPE_EVENTʱ��������Ϣ��Ч */  
    __u32      reserved[2];            /* �����ֶ� */    
    __u32      event_sn;               /* �¼����к� */
    __u32      tag;                    /* event�¼���־ */
    __u32      data_length;            /* ���ݳ��ȣ����4K */
    __u8       pad[4];                 /* ��֤data���뵽sizeof(�˽ṹ��Ĵ�С) */
    __u8       data[0];                /* �������� ����vsc_scsi_msg_data�Ľṹ */
};

/* ������Ϣ */
struct vsc_sense_data {
    __u8       scsi_status;            /* SCSI�豸״̬��Ĭ�Ϸ���0 */
    __u8       sense_len;              /* �����볤�� */
    __u8       sense_info[0];          /* ������Ϣ */
};

/* DATA�������� 
 * ��struct vsc_scsi_msg_data��data_typeΪVSC_MSG_DATA_TYPE_DATAʱ
 * ��dataָ��˽ṹ
 */
struct vsc_iovec
{
	__u64      iov_base;               /* �û�̬���ݵ�ַ��������Ϊ32λʱ����λ��д0 */
	__u32      iov_len;                /* iov���ݳ��� */
    __u8       pad[4];                 /* ǿ��32λ��64Ϊ��С���� */
};

#define VSC_MSG_DATA_TYPE_CDB      1   /* CDB�������� */
#define VSC_MSG_DATA_TYPE_DATA     2   /* ��д�������� */
#define VSC_MSG_DATA_TYPE_SENSE    3   /* ������Ϣ���� */

/* ��ȡ������������Ϣ */
struct vsc_scsi_data {
    __u32     data_type;               /* ������������� */
    __u32     data_len;                /* ������Ϣvec�ĳ��� */
    __u32     nr_iovec;                /* iovec�ĸ��� */
    __u32     total_iovec_len;         /* ÿ��iovec��iov_len�ĳ����ܺ� */
    __u32     offset;                  /* �����ƫ�Ƶ�ַ */
    __u8      pad[0];                  /* ��֤vec���뵽sizeof(�˽ṹ��Ĵ�С) */
    __u8      vec[0];  /*lint !e157*/  /* DATA���ݣ��˽ṹָ��struct vsc_iovec*/
};


/* SCSI���ݽ�������Ϣ */
struct vsc_scsi_data_msg
{
    __u32     type;                    /* ���������, �����ֶ�ΪVSC_MSG_TYPE_SCSI_DATAʱ��������Ϣ��Ч */  
    __u32     reserved[2];             /* �����ֶ� */
    __u32     cmd_sn;                  /* �������к� */
    __u32     tag;                     /* scsi����ʶ���־ */
    __u32     scsi_data_len;           /* ������Ϣ�ĳ��� */
    __u8      pad[0];                  /* ��֤vec���뵽sizeof(�˽ṹ��Ĵ�С) */
    __u8      data[0];  /*lint !e157*/ /* ��ȡ���������ͣ�ָ��struct vsc_scsi_data*/
};

/* ���������� */
#define    VSC_MSG_DATA_DIR_BIDIRECTIONAL   0   /* ˫������ */
#define    VSC_MSG_DATA_DIR_TO_DEVICE       1   /* ���豸д������ */
#define    VSC_MSG_DATA_DIR_FROM_DEVICE     2   /* ���豸��ȡ���� */
#define    VSC_MSG_DATA_DIR_NONE            3   /* ���������� */

/* SCSI������Ϣ */ 
struct vsc_scsi_msg {
    __u32     type;                    /* ���������, �����ֶ�ΪVSC_MSG_TYPE_SCSI_CMDʱ��������Ϣ��Ч*/
    __u32     reserved[2];             /* �����ֶ� */
    __u32     cmd_sn;                  /* �������к� */
    __u32     tag;                     /* scsi����ʶ���־ */
    __u32     host;                    /* host��� */
    __u32     channel;                 /* ͨ���� */
    __u32     id;                      /* target��� */
    __u32     lun;                     /* lun��� */
    __u32     direction;               /* ���ݷ��� */
};

/* SCSI���������� */
#define CMD_SUCCESS             0x0000               /* ����ִ�гɹ� */
#define CMD_FAILURE             0x0001               /* ���󣬴�����ϸԭ����sense�����У����������κδ���������SCSI�в㴦�� */
#define CMD_INVALID             0x0002               /* ��Ѱַ�����ڵ�Ӳ���豸ʱ�����ش˴���֪ͨ�в��豸δ���� */
#define CMD_CONNECTION_LOST     0x0003               /* �豸���Ӷ�ʧ��֪ͨSCSI�в�������� */
#define CMD_TIMEOUT             0x0004               /* SCSI���ʱ��֪ͨSCSI�в����ʱ */
#define CMD_PROTOCOL_ERR        0x0005               /* ��Ϣ����֪ͨ�в�����������Զ�Ӧ��SCSI���� */
#define CMD_NEED_RETRY          0x0006               /* ֪ͨSCSI�в����Զ�Ӧ��SCSI���� */

/* SAM�淶������ */
#define GOOD                     0x00                /* Ӳ������ */
#define CHECK_CONDITION          0x01                /* ���sense���� */
#define CONDITION_GOOD           0x02                /* ״̬���� */
#define BUSY                     0x04                /* æ */
#define INTERMEDIATE_GOOD        0x08
#define INTERMEDIATE_C_GOOD      0x0a
#define RESERVATION_CONFLICT     0x0c
#define COMMAND_TERMINATED       0x11                /* ����ж� */
#define QUEUE_FULL               0x14                /* ������ */


/* scsi�����Ӧ��Ϣ */
struct vsc_scsi_rsp_msg {
    __u32     type;                   /* ��������֣����ֶ�ΪVSC_MSG_TYPE_SCSI_CMD��������Ϣ��Ч */ 
    __u32     reserved[2];            /* �����ֶ� */    
    __u32     cmd_sn;                 /* �������к� */
    __u32     tag;                    /* scsi����ʶ���־ */
    __u32     command_status;         /* SCSI����״̬���������Ľӿڣ���Ӧ���������ĺ� */
    __u32     scsi_status;            /* target��״̬���ϱ���SCSI�в㣬��ӦSAM-3�淶�Ĵ�����*/
};

#endif // END _VSC_H_
