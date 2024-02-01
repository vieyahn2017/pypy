/********************************************************************
            Copyright (C) Huawei Technologies, 2015
  #���ߣ�Peng Ruilin (pengruilin@huawei.com)
  #����: vsc scsi�в�ӿ�ģ��
********************************************************************/

#ifndef __VSC_SCSI_IF_H_
#define __VSC_SCSI_IF_H_

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/errno.h>
#include <linux/sched.h>
#include <linux/workqueue.h>
#include <linux/interrupt.h>
#include <linux/delay.h>
#include <linux/pci.h>
#include <linux/spinlock.h>
#include <linux/list.h>
#include <linux/sched.h>
#include <linux/kthread.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/poll.h>
#include <linux/completion.h>
#include <linux/version.h>

#include <scsi/scsi.h>
#include <scsi/scsi_cmnd.h>
#include <scsi/scsi_device.h>
#include <scsi/scsi_host.h>
#include <scsi/scsi_transport.h>
#include <scsi/scsi_transport_sas.h>
#include <scsi/scsi_dbg.h>
#include <scsi/scsi_tcq.h>

#include "vsc_version.h"

struct vsc_scsi_struct;

#define VSS_SCSI_LOAD_DATA_SIZE 4096

/* /proc/vscĿ¼ָ�룬�����˷��Ź�vsc����ʹ�� */
extern struct proc_dir_entry *proc_vsc_root;

/* VSCע���vsc scsi if�Ļص����� */
struct vsc_scsi_host_operation {
    /* Scsi_Hostָ�� */
    struct scsi_host_template *sht;     
    /* scsi_transport_templateָ�� */
    struct scsi_transport_template *stt;
    /* ע��ʱ�����ã����ڼ���Scsi Host��Ӧ�Ŀ������� */
    int (* load)(struct vsc_scsi_struct *, void *data, int size);
    /* ж������ʱ���ã�������һЩ������ */
    int (* unload)(struct vsc_scsi_struct *, void *data, int size);

};

/* ��Scsh_Host��ȡvsc_scsi_host_operationָ�� */
static inline struct vsc_scsi_struct *vsc_scsi_if_get_vss(struct Scsi_Host *sh)
{
    return (struct vsc_scsi_struct*) (shost_priv(sh));    
}

/* ��װ��Scsi_Host�ṹ�����뺯�� */
struct vsc_scsi_struct *vsc_scsi_if_alloc(void);

/* ��װ��Scsi_Host�ṹ���ͷź��� */
void vsc_scsi_if_free(struct vsc_scsi_struct * vss);

/* ��vsc�Ŀ��ƾ�����õ�vsc scsi if */
int vsc_scsi_if_set_priv(struct vsc_scsi_struct * vss, void *private_data);

/* ��ȡ���õ�vsc���ƾ�� */
void *vsc_scsi_if_get_priv(struct vsc_scsi_struct * vss);

/* ��ȡScsi_Host��� */
struct Scsi_Host *vsc_scsi_if_get_host(struct vsc_scsi_struct * vss);

/* vsc��vsc scsi ifע��ص����� */
int vsc_scsi_if_register(struct vsc_scsi_host_operation *vsc_hop);

/* vscע���ص����� */
int vsc_scsi_if_unregister(void);

void *vsc_scsi_if_alloc_pool(int size);
void *vsc_scsi_if_get_pool(void);
void vsc_scsi_if_free_pool(void);
 
#endif



