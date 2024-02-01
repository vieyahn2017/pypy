/********************************************************************
            Copyright (C) Huawei Technologies, 2012
  #����:  

********************************************************************/
#include "vsc_common.h"

static int vsc_ioctl_majorno; 
static struct class *vsc_class;
/**************************************************************************
 ��������  : ���Ӵ���
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_add_disk(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_disk disk;
    struct vsc_ctrl_info *h = NULL;
    int ret;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&disk, p_user, sizeof(disk))) {
        return -EFAULT;
    }

    /* ����host���ƾ�� */
    h = vsc_get_ctrl_by_host(disk.host);
    if (!h) {
        return -ENODEV;
    }

    ret = vsc_add_device(h, disk.channel, disk.id, disk.lun);
    vsc_ctrl_info_put(h);
    return ret;
}

static int vsc_dev_add_disk_by_vol_name(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_disk_vol_name disk_vol;
    struct vsc_ctrl_info *h = NULL;
    int ret;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&disk_vol, p_user, sizeof(disk_vol))) {
        return -EFAULT;
    }

    /* ����host���ƾ�� */
    h = vsc_get_ctrl_by_host(disk_vol.host);
    if (!h) {
        return -ENODEV;
    }

    ret = vsc_add_device_by_vol_name(h, disk_vol.channel, disk_vol.id,
                                         disk_vol.lun, disk_vol.vol_name);
    vsc_ctrl_info_put(h);
    return ret;
}

/**************************************************************************
 ��������  : ɾ��
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_rmv_disk(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_disk disk;
    struct vsc_ctrl_info *h = NULL;
    int ret;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&disk, p_user, sizeof(disk))) {
        return -EFAULT;
    }

    /* ����host���ƾ�� */
    h = vsc_get_ctrl_by_host(disk.host);
    if (!h) {
        return -ENODEV;
    }

    ret = vsc_rmv_device(h, disk.channel, disk.id, disk.lun);
    vsc_ctrl_info_put(h);
    return ret;
}
static int vsc_dev_rmv_disk_by_vol_name(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_disk_vol_name disk_vol;
    struct vsc_ctrl_info *h = NULL;
    int ret;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&disk_vol, p_user, sizeof(disk_vol))) {
        return -EFAULT;
    }

    h = vsc_get_ctrl_by_host(disk_vol.host);
    if (!h) {
        return -ENODEV;
    }

    ret = vsc_set_delete_by_vol_name(h, disk_vol.vol_name);
    vsc_ctrl_info_put(h);
    return ret;
}

static int vsc_dev_query_vol(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_query_vol *query_vol;
    struct vsc_ctrl_info *h = NULL;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    query_vol = kzalloc(sizeof(*query_vol), GFP_NOWAIT);
    if (NULL == query_vol)
    {
        return -ENOMEM;
    }

    if (copy_from_user(query_vol, p_user, sizeof(*query_vol))) {
        kfree(query_vol);
        return -EFAULT;
    }

    h = vsc_get_ctrl_by_host(query_vol->host);
    if (!h) {
        kfree(query_vol);
        return -ENODEV;
    }

    vsc_query_vol(h, query_vol);
    vsc_ctrl_info_put(h);

    if (copy_to_user(p_user, query_vol, sizeof(*query_vol))) {
        kfree(query_vol);
        return -EFAULT;
    }

    kfree(query_vol);
    return 0;
}
/**************************************************************************
 ��������  : �����豸״̬
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_set_disk_stat(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_disk_stat disk_stat;
    struct vsc_ctrl_info *h = NULL;
    int ret;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&disk_stat, p_user, sizeof(disk_stat))) {
        return -EFAULT;
    }

    /* ����host���ƾ�� */
    h = vsc_get_ctrl_by_host(disk_stat.host);
    if (!h) {
        return -ENODEV;
    }

    ret = vsc_set_device_stat(h, disk_stat.channel, disk_stat.id, disk_stat.lun, (enum scsi_device_state)disk_stat.stat);
    vsc_ctrl_info_put(h);
    return ret;
}

/**************************************************************************
 ��������  : ��ȡ�豸״̬
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_get_disk_stat(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_disk_stat disk_stat;
    struct vsc_ctrl_info *h = NULL;
    enum scsi_device_state sdev_stat = 0;
    int retval = 0;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&disk_stat, p_user, sizeof(disk_stat))) {
        return -EFAULT;
    }

    /* ����host���ƾ�� */
    h = vsc_get_ctrl_by_host(disk_stat.host);
    if (!h) {
        vsc_err("get ctrl for host failed when get disk[%u:%u:%u:%u] stat, will return -ENODEV\n", 
            disk_stat.host, disk_stat.channel, disk_stat.id, disk_stat.lun);
        return -ENODEV;
    }

    retval =  vsc_get_device_stat(h, disk_stat.channel, disk_stat.id, disk_stat.lun, &sdev_stat);
    vsc_ctrl_info_put(h);
    if (retval) {
        return retval;
    }

    disk_stat.stat = (__u32)sdev_stat;

    if (copy_to_user(p_user, &disk_stat, sizeof(disk_stat))) {
        return -EFAULT;
    }

    return 0;
}

/**************************************************************************
 ��������  : ���ô���������г�ʱʱ��
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_set_disk_rq_timeout(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_rq_timeout rq_timeout;
    struct vsc_ctrl_info *h = NULL;
    int ret;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&rq_timeout, p_user, sizeof(rq_timeout))) {
        return -EFAULT;
    }

    /* ����host���ƾ�� */
    h = vsc_get_ctrl_by_host(rq_timeout.host);
    if (!h) {
        return -ENODEV;
    }

    ret = vsc_set_device_rq_timeout(h, rq_timeout.channel, rq_timeout.id, rq_timeout.lun, rq_timeout.timeout);
    vsc_ctrl_info_put(h);
    return ret;
}

/**************************************************************************
 ��������  : ����target�����쳣��ʱʱ��
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_set_tg_abn_timeout(char __user *p_user)
{
    struct vsc_ioctl_set_tg_abn_timeout timeout;
    struct vsc_ctrl_info *h = NULL;
    int ret;

    if (!p_user) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&timeout, p_user, sizeof(timeout))) {
        return -EFAULT;
    }

    if (timeout.timeout > VSC_MAX_TARGET_ABNORMAL_TIMEOUT){
        return -EINVAL;
    }

    /* ����host���ƾ�� */
    h = vsc_get_ctrl_by_host(timeout.host);
    if (!h) {
        return -ENODEV;
    }

    ret = vsc_set_tg_abn_timeout(h, timeout.timeout);
    vsc_ctrl_info_put(h);
    return ret;
}


/**************************************************************************
 ��������  : ɾ��HOST
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_rmv_host(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_cmd_rmv_host host;
    struct vsc_ctrl_info *h = NULL;
    int ret;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&host, p_user, sizeof(host))) {
        return -EFAULT;
    }

    /* ����host���ƾ�� */
    h = vsc_get_ctrl_by_host(host.host);
    if (!h) {
        return -ENODEV;
    }

    ret = vsc_remove_host(h); 
    vsc_ctrl_info_put(h);
    return ret;
}

/**************************************************************************
 ��������  : ����HOST
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_add_host(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_cmd_add_host host_info;
    struct vsc_ctrl_info *h = NULL;

    if (!p_user || !file) {
        return -EINVAL;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    if (copy_from_user(&host_info, p_user, sizeof(host_info))) {
        vsc_err("add host: copy from user failed\n");
        return -EFAULT;
    }

    h = vsc_register_host(&host_info); 
    
    /* ���������host id�ش���vbs,��������жϷ���ֵλ�ò��ܶԵ�����ΪVBS����
     * ���ص���-EXIST */
    if (copy_to_user(p_user, &host_info, sizeof(host_info))) {
        vsc_err("add host: copy to user failed\n");
        return -EFAULT;
    }
    if (IS_ERR(h)) {
        vsc_dbg("add host: register host failed, ret = %ld\n", PTR_ERR(h));
        return PTR_ERR(h);
    }
    return 0;
}

/**************************************************************************
 ��������  : �ӹ�HOST
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_attach_host(struct file *file, char __user *p_user)
{
    struct vsc_ioctl_cmd_attatch_host cmd_attach;
    struct vsc_ctrl_info *h = NULL;
    int retval = 0;

    /* �����ļ��Ƿ��Ѿ��ӹ�����host */
    h = file->private_data;
    if (h) {
        /* ����Ѿ��ӹܣ�ֱ�ӷ��ش��� */
        return -EALREADY;
    }

    /* ������������ */
    if (copy_from_user(&cmd_attach, p_user, sizeof(cmd_attach))) {
        return -EFAULT;
    }

    if (!capable(CAP_SYS_ADMIN)) {
        return -EPERM;
    }

    h = vsc_get_ctrl_by_host(cmd_attach.host);
    if (!h) {
        return -ENODEV;
    }

    /* ���host�ӹ�״̬ */
    retval = vsc_scsi_attach(h, file, current); 
    if (retval) {
        return retval;
    }

    /* �ӹ�host */
    file->private_data = h;

    vsc_info("Host %d is attached by %s(%d)\n", vsc_ctrl_get_host_no(h), current->comm, current->pid);

    return 0;
}

/**************************************************************************
 ��������  : �ͷ�HOST
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_detach_host(struct file *file)
{
    struct vsc_ctrl_info *h = NULL;
    int ret;
    /* ����host���ڷǽӹ�״̬ */
    h = file->private_data;
    if (!h) {
        /* ���û�нӹܣ�ֱ�ӷ��ش��� */
        return -EBADF;
    }

    vsc_info("Host %d is detached from %s(%d)\n", vsc_ctrl_get_host_no(h), current->comm, current->pid);
    /* ȡ������ */
    file->private_data = NULL;
    ret = vsc_scsi_detach(h, 0);
    vsc_ctrl_info_put(h);
    return ret;
}

/**************************************************************************
 ��������  : ����HOST
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_suspend_host(struct file *file, char __user *p_user)
{
    struct vsc_ctrl_info *h = NULL;

    h = file->private_data;
    if (!h) {
        /* ���û�нӹܣ�ֱ�ӷ��ش��� */
        return -EBADF;
    }

    /* ����host���� */
    return vsc_suspend_host(h);
}

/**************************************************************************
 ��������  : �ָ�HOST
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_resume_host(struct file *file, char __user *p_user)
{
    struct vsc_ctrl_info *h = NULL;

    h = file->private_data;
    if (!h) {
        /* ���û�нӹܣ�ֱ�ӷ��ش��� */
        return -EBADF;
    }

    /* �ָ�host�������� */
    return vsc_resume_host(h);
}

/**************************************************************************
 ��������  : �ָ����е�HOST�� ��IO�·�ʱ���ݻHOST����IOת��
 ��    ��  : p_user          �������
 �� �� ֵ  : 0:�ɹ�  ������ʧ��
**************************************************************************/
static int vsc_dev_resume_host_all(struct file *file, char __user *p_user)
{
    struct vsc_ctrl_info *h = NULL;

    h = file->private_data;
    if (!h) {
        /* ���û�нӹܣ�ֱ�ӷ��ش��� */
        return -EBADF;
    }

    return vsc_resume_host_all(h, (int __user *)p_user);
}

/**************************************************************************
 ��������  : ioctl�ӿ�
 ��    ��  : vsc_cmnd_list *c       scsi������ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static long vsc_dev_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    long ret = 0;
    char __user *p_user = (char __user *)arg;  

    if ( VSC_TRACE_IOCTL_EVENT & trace_switch) {
        printk("IOCTL cmd %X from %d(%s)\n", cmd, current->pid, current->comm);
    }
    switch (cmd)  {     
        case VSC_ADD_HOST:
            ret = vsc_dev_add_host(file, p_user);
            break;
        case VSC_RMV_HOST:
            ret = vsc_dev_rmv_host(file, p_user);
            break;
        case VSC_ATTACH_HOST:
            ret = vsc_dev_attach_host(file, p_user);
            break;
        case VSC_DETACH_HOST:
            ret = vsc_dev_detach_host(file);
            break;
        case VSC_SUSPEND_HOST:
            ret = vsc_dev_suspend_host(file, p_user);
            break;
        case VSC_RESUME_HOST:
            ret = vsc_dev_resume_host(file, p_user);
            break;
        case VSC_RESUME_HOST_ALL:
            ret = vsc_dev_resume_host_all(file, p_user);
            break;
        case VSC_ADD_DISK:  
            ret = vsc_dev_add_disk(file, p_user);
            break;
        case VSC_RMV_DISK:
            ret = vsc_dev_rmv_disk(file, p_user);
            break;
        case VSC_ADD_DISK_VOL_NAME:
            ret = vsc_dev_add_disk_by_vol_name(file, p_user);
            break;
        case VSC_PREPARE_RMV_VOL:
            ret = vsc_dev_rmv_disk_by_vol_name(file, p_user);
            break;
        case VSC_QUERY_DISK_VOL:
            ret = vsc_dev_query_vol(file, p_user);
            break;
        case VSC_SET_DISK_STAT:
            ret = vsc_dev_set_disk_stat(file, p_user);
            break;
        case VSC_GET_DISK_STAT:
            ret = vsc_dev_get_disk_stat(file, p_user);
            break;
        case VSC_DISK_RQ_TIMEOUT:
            ret = vsc_dev_set_disk_rq_timeout(file, p_user);
            break;
        case VSC_SET_TARGET_ABNORMAL_TIMEOUT:
            ret = vsc_dev_set_tg_abn_timeout(p_user);
            break;            
        default:
            ret = -ENOTTY;
            break;
    }
    
    return ret;
}

static long vsc_dev_compat_ioctl(struct file *file, unsigned int ioctl, unsigned long arg)
{
    return vsc_dev_ioctl(file, ioctl, arg);
}

/**************************************************************************
 ��������  : ���豸�ļ��ӿ�
 ��    ��  : inode:         �ڵ�ָ��
             file:          �ļ�ָ��
 �� �� ֵ  : ��
**************************************************************************/
static int vsc_dev_open(struct inode *inode, struct file *file)
{   
    file->private_data = NULL;
    file->f_flags = file->f_flags;
    return 0;
}

/**************************************************************************
 ��������  : �ļ�poll������
 ��    ��  : file:          �ļ�ָ��
 �� �� ֵ  : ��
**************************************************************************/
static unsigned int vsc_dev_poll(struct file *file, poll_table *wait)
{
//    struct vsc_ctrl_info *h = NULL;

//    h = file->private_data;
//    if (!h) {
//        return 0;
//    } /* [review] duplicate  */

    return vsc_poll_wait(file, wait);
}

/**************************************************************************
 ��������  : �ļ���ȡ����
 ��    ��  : file:          �ļ�ָ��
             buf            ���ݻ���
             len            ����
             ppos           ƫ��
 �� �� ֵ  : ��
**************************************************************************/
static ssize_t vsc_dev_read(struct file *file, char __user *user_buf, size_t count, loff_t *ppos)
{
    struct vsc_ctrl_info *h = file->private_data;

    if (unlikely(!h)) {
        return -EBADF;   
    }

    return vsc_get_msg(h, file, user_buf, count);
}

/**************************************************************************
 ��������  : �ļ�д�뺯��
 ��    ��  : file:          �ļ�ָ��
             buf            ���ݻ���
             len            ����
             ppos           ƫ��
 �� �� ֵ  : ��
**************************************************************************/
static ssize_t vsc_dev_write(struct file *file,
                  const char __user *user_buf,
                  size_t count, loff_t *ppos)
    
{
    struct vsc_ctrl_info *h = file->private_data;

    if (unlikely(!h)) {
        return -EBADF;   
    }

    return vsc_response_msg(h, user_buf, count);
}

/**************************************************************************
 ��������  : ����ˢ�£���Ҫ����close�����ʱ���˳�
 ��    ��  : file:          �ļ�ָ��
 �� �� ֵ  : ��
**************************************************************************/
static int vsc_dev_f_flush(struct file *file, fl_owner_t ownid)
{
    struct vsc_ctrl_info *h = file->private_data;

    if (unlikely(!h)) {
        return 0;   
    }

    /* ���û�нӹ��κ�host����ֱ�ӷ��� */
    if (!file->private_data) {
        return 0;
    }

    /* ������ʱ��ֱ�ӷ��� */
    if (file->f_flags & O_NONBLOCK) {
        return 0;
    }

    /* ���������Ľ��� */
    vsc_interrupt_sleep_on_read(h);
    return 0;
}

/**************************************************************************
 ��������  : �ر��ļ����˳�
 ��    ��  : inode:         �ڵ�ָ��
             file:          �ļ�ָ��
 �� �� ֵ  : ��
**************************************************************************/
static int vsc_dev_release(struct inode *inode, struct file *file)
{
    struct vsc_ctrl_info *h = file->private_data;
    int ret;

    if (unlikely(!h)) {
        return 0;   
    }

    /* ���û�нӹ��κ�host����ֱ�ӷ��� */
    if (!file->private_data) {
        return 0;
    }

    h = file->private_data;
    file->private_data = NULL;

    vsc_info("Host %d unexpected detached from %s(%d) as file closed.\n", vsc_ctrl_get_host_no(h), current->comm, current->pid);

    /* ����HOST��������״̬ */
    ret = vsc_scsi_detach(h, 1);
    vsc_ctrl_info_put(h);
    return ret;
}


static const struct file_operations vsc_ioctl_fops = {
    .owner             = THIS_MODULE,
    .open              = vsc_dev_open,
    .flush             = vsc_dev_f_flush,
    .release           = vsc_dev_release,
    .read              = vsc_dev_read,
    .write             = vsc_dev_write,
    .poll              = vsc_dev_poll,
    .unlocked_ioctl    = vsc_dev_ioctl,
#ifdef CONFIG_COMPAT
    .compat_ioctl      = vsc_dev_compat_ioctl,
#endif
};

int vsc_ioctl_init(void)
{
    int majorno = -1;
    int ret     = -1;
    struct device *vsc_dev = NULL;
    
    majorno = register_chrdev(0, VSC_IOCTL_NAME, &vsc_ioctl_fops);
    if (majorno < 0) {
        vsc_err("register_chrdev %s failed, majorno:%d\n", VSC_IOCTL_NAME, majorno);
        ret = majorno;
        goto err_ret;
    }

    vsc_ioctl_majorno = majorno;
    
    vsc_class = vsc_class_create(THIS_MODULE, VSC_IOCTL_NAME);    
    if (IS_ERR(vsc_class)) {
        vsc_err("class_create[%p] failed\n", vsc_class);
        ret = PTR_ERR(vsc_class);
        goto err_ret;
    }

#if (LINUX_VERSION_CODE == KERNEL_VERSION(2, 6, 18))
    vsc_dev = vsc_device_create(vsc_class, NULL, MKDEV(vsc_ioctl_majorno, 0), 
                                  VSC_IOCTL_NAME);
#else
    vsc_dev = vsc_device_create(vsc_class, NULL, MKDEV(vsc_ioctl_majorno, 0), 
                            NULL, VSC_IOCTL_NAME);
#endif
    if (IS_ERR(vsc_dev)) {
        vsc_err("device_create[%p] failed\n", vsc_dev);
        ret = PTR_ERR(vsc_dev);
        goto err_ret;
    }

    return 0;
    
err_ret:
    if (!IS_ERR(vsc_dev)) {
        vsc_device_destroy(vsc_class, MKDEV(vsc_ioctl_majorno, 0));
    }
    
    if (!IS_ERR(vsc_class)) {
        vsc_class_destroy(vsc_class);
        vsc_class = NULL;
    }
    
    if ( majorno >= 0) {
       unregister_chrdev(vsc_ioctl_majorno, VSC_IOCTL_NAME); 
    }
    
    return ret;
}

void vsc_ioctl_exit(void)
{
    vsc_device_destroy(vsc_class, MKDEV(vsc_ioctl_majorno, 0));
    vsc_class_destroy(vsc_class);
    vsc_class = NULL;
    unregister_chrdev(vsc_ioctl_majorno, VSC_IOCTL_NAME);
    return;
}
