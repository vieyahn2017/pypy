/********************************************************************
            Copyright (C) Huawei Technologies, 2012
  #���ߣ�Peng Ruilin (pengruilin@huawei.com)
  #����: vsc��������ͷ�ļ�
********************************************************************/

#ifndef __VSC_MAIN_H_
#define __VSC_MAIN_H_

struct vsc_ctrl_info;

/* ��ȡhost���  */
extern unsigned int vsc_ctrl_get_host_no(struct vsc_ctrl_info *h);

extern void vsc_ctrl_info_put(struct vsc_ctrl_info *h);

extern void vsc_ctrl_info_get(struct vsc_ctrl_info *h);

/* ����host no���ҿ��ƿ� */
extern struct vsc_ctrl_info * vsc_get_ctrl_by_host( unsigned int host_no );

/*  ���host��ϵͳ�� */
extern struct vsc_ctrl_info *vsc_register_host( struct vsc_ioctl_cmd_add_host *host_info );

/* ɾ��ָ����host */
extern int vsc_remove_host(struct vsc_ctrl_info *h);

/* �ͷ����п��ƾ�� */
extern void vsc_remove_all_host( void ) ;

/* ȡ���ӹ�host*/
extern int vsc_scsi_detach(struct vsc_ctrl_info *h, int is_timeout);

/* ����host */
extern int vsc_suspend_host(struct vsc_ctrl_info *h);

/* �ָ�host */
extern int vsc_resume_host(struct vsc_ctrl_info *h);
extern int vsc_resume_host_all(struct vsc_ctrl_info *h, int __user *p_user);

/* �ӹ�host */
extern int vsc_scsi_attach(struct vsc_ctrl_info *h, struct file *file,  struct task_struct *task);

/* ioctl�ȴ� */
extern unsigned int vsc_poll_wait(struct file *file, poll_table *wait);

/* ����������ȡ�Ľ��� */
extern void vsc_interrupt_sleep_on_read(struct vsc_ctrl_info *h);

/* ��Ӵ��� */
extern int vsc_add_device(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun);
extern int vsc_add_device_by_vol_name(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun, char *vol_name);

/* ɾ������ */
extern int vsc_rmv_device(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun);
extern int vsc_set_delete_by_vol_name(struct vsc_ctrl_info *h, char *vol_name);
extern void vsc_query_vol(struct vsc_ctrl_info *h, struct vsc_ioctl_query_vol *query_vol);

/* ���ô���״̬ */
extern int vsc_set_device_stat(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun, enum scsi_device_state stat);

/* ��ȡ����״̬ */
extern int vsc_get_device_stat(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun,  enum scsi_device_state *stat);

/* ���ô��̶��г�ʱʱ�� */
extern int vsc_set_device_rq_timeout(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun, int timeout);

/* ����target�����쳣��ʱʱ�� */
extern int vsc_set_tg_abn_timeout(struct vsc_ctrl_info *h, __u32 timeout);

/* ��ȡ���� */
extern ssize_t vsc_get_msg(struct vsc_ctrl_info *h, struct file *file, char __user *  user_ptr, int len);

/* ��Ӧ���� */
extern ssize_t vsc_response_msg(struct vsc_ctrl_info *h, const char __user *  user_ptr, int len);

/* ����豸ͷû����fs�㱻���� */
extern int vsc_check_if_dev_mounted(const char* name);

/* ��scsi_device��ȡgendisk */
extern void * vsc_get_gendisk_from_scsi_device(struct scsi_device* sdev);


#endif


