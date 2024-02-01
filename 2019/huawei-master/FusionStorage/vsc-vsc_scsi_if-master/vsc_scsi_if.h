/********************************************************************
            Copyright (C) Huawei Technologies, 2015
  #作者：Peng Ruilin (pengruilin@huawei.com)
  #描述: vsc scsi中层接口模块
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

/* /proc/vsc目录指针，导出了符号共vsc驱动使用 */
extern struct proc_dir_entry *proc_vsc_root;

/* VSC注册给vsc scsi if的回调函数 */
struct vsc_scsi_host_operation {
    /* Scsi_Host指针 */
    struct scsi_host_template *sht;     
    /* scsi_transport_template指针 */
    struct scsi_transport_template *stt;
    /* 注册时，调用，用于加载Scsi Host对应的控制数据 */
    int (* load)(struct vsc_scsi_struct *, void *data, int size);
    /* 卸载驱动时调用，用于做一些清理工作 */
    int (* unload)(struct vsc_scsi_struct *, void *data, int size);

};

/* 从Scsh_Host获取vsc_scsi_host_operation指针 */
static inline struct vsc_scsi_struct *vsc_scsi_if_get_vss(struct Scsi_Host *sh)
{
    return (struct vsc_scsi_struct*) (shost_priv(sh));    
}

/* 封装的Scsi_Host结构体申请函数 */
struct vsc_scsi_struct *vsc_scsi_if_alloc(void);

/* 封装的Scsi_Host结构体释放函数 */
void vsc_scsi_if_free(struct vsc_scsi_struct * vss);

/* 将vsc的控制句柄设置到vsc scsi if */
int vsc_scsi_if_set_priv(struct vsc_scsi_struct * vss, void *private_data);

/* 获取设置的vsc控制句柄 */
void *vsc_scsi_if_get_priv(struct vsc_scsi_struct * vss);

/* 获取Scsi_Host句柄 */
struct Scsi_Host *vsc_scsi_if_get_host(struct vsc_scsi_struct * vss);

/* vsc向vsc scsi if注册回调函数 */
int vsc_scsi_if_register(struct vsc_scsi_host_operation *vsc_hop);

/* vsc注销回调函数 */
int vsc_scsi_if_unregister(void);

void *vsc_scsi_if_alloc_pool(int size);
void *vsc_scsi_if_get_pool(void);
void vsc_scsi_if_free_pool(void);
 
#endif



