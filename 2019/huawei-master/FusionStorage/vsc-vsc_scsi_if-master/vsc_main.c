/********************************************************************
            Copyright (C) Huawei Technologies, 2012
  #���ߣ�Peng Ruilin (pengruilin@huawei.com)
  #����: virtual storage controller����scsi�����ģ��
********************************************************************/
#include "vsc_common.h"
#include <linux/proc_fs.h>
#if LINUX_VERSION_CODE == KERNEL_VERSION(3, 10, 0)
#include <linux/internal.h>
#endif
#include <scsi/scsi_transport.h>


#include <linux/jiffies.h>
#include <linux/time.h>

//#define __VSC_LATENCY_DEBUG__

/* ÿ��vbs���ʹ�õ�host */
#define MAX_HOST_NR_PER_VBS      (8)

/* ÿ��server���֧�ֵ�vbs */
#define MAX_VBS_NR_PER_SERVER    (8)

/* scsi host id����ʼ��host id=offset+vbs_id*max_host_per_vbs */
#define SCSI_HOST_BASE_OFFSET    0x10

/* ���proc�ļ��� */
#define VSC_PROC_FILE_NAME_LEN    64

/* Ĭ�ϵ��¼����� */
#define VSC_DEFAULT_EVENT_NUMBER  8

/* abort��Ϣ�ȴ���ʱʱ�� */
#define VSC_ABORT_EVENT_WAIT_TIME 15

/* �豸��λ���¼��ȴ�ʱ�� */
#define VSC_RESET_EVENT_WAIT_TIME 30

/* ��ȡ���� */
#define VSC_MODE_READ             1

/* д������ */
#define VSC_MODE_WRITE            2

/* ����sg_count */
#define VSC_MAX_SG_COUNT          8192

/* ÿ��host�ܻ�������cmd���� */
/* ÿ��vbs��IODEPTH 256, ÿ��host�����32���� */
#define VSC_MAX_CMD_NUM           (256 * 32)


/* �¼��������� */
enum event_shoot_type {
    EVENT_SHOOT_NOSHOOT        = 0,
    EVENT_SHOOT_SHOOT          = 1,
    EVENT_SHOOT_ABORT          = 2,
};

/* �¼����� */ 
/* [zr] ����������� */
enum queue_type {
    VSC_LIST_REQQ              = 1,
    VSC_LIST_COMQ              = 2,
    VSC_LIST_RSPQ              = 3,
};

/* �¼����ڵĶ��� */
enum event_list_stat {
    EVENT_LIST_STAT_INIT               = 0,
    EVENT_LIST_STAT_REQUEST            = 1,
    EVENT_LIST_STAT_READ_COMP             ,
    EVENT_LIST_STAT_RESP                  ,
};

/* �¼��������� */
enum event_type {
    EVENT_TIMEOUT                 = 0,
    EVENT_SHOOT                   = 1,
    EVENT_ABORT                   = 2,
};

/* ����״̬ */
enum cmd_stat {
    CMD_STAT_INIT                 = 0,
    CMD_STAT_REQUEST              = 1,
    CMD_STAT_READ_COMP            = 2,
    CMD_STAT_RESP                 = 3,
    CMD_STAT_CANCELED,       
};

struct vsc_event_list;
typedef int (*event_callback)(struct vsc_ctrl_info *h, enum event_type type, struct vsc_event_list *e,
                                int data_type, void *data, int data_len);
struct vsc_event_list {
    struct list_head              list;
    __u32                         event_index;           /* �¼����� */
    __u32                         event_sn;              /* �¼����к� */
    enum event_list_stat          stat;                  /* �¼�����״̬ */
    struct vsc_ctrl_info          *h;
    int                           event_data_len;        /* ��Ϣ���ݳ��� */
    unsigned char                 event_data[PAGE_SIZE]; /* �¼����� */
    unsigned long                 event_priv;            /* event˽���¼� */
    event_callback                event_callback;        /* event�¼��ص����� */
    wait_queue_head_t             wait;                  /* �ȴ������¼� */ 
    int                           shoot;                 /* �Ƿ񴥷���Ϣ */
    atomic_t                      refcnt;                /* �ṹ�����ü��� */
};

struct vsc_cmnd_list {
    struct list_head              list;
    __u32                         cmd_index;             /* �������� */
    enum cmd_stat                 stat;                  /* ����״̬ */
    void                          *scsi_cmd;
    __u32                         cmd_sn;                /* �������к� */
    struct vsc_ctrl_info          *h;
    atomic_t                      refcnt;                /* �ṹ�����ü��� */

#ifdef __VSC_LATENCY_DEBUG__
    // for read: start_queue->get_scmd->back_data->back_rsp
    // for write: start_queue->get_scmd->get_data->back_rsp
    __u64 start_queue_time;
    __u64 get_scmd_time;
    __u64 get_data_time;
    __u64 back_data_time;
    __u64 back_rsp_time;
#endif
};

struct vsc_ctrl_statics {
    unsigned int                  reset_dev_count;       /* ��λ����ļ��� */
    unsigned int                  abort_cmd_count;       /* ���������������� */
    unsigned int                  read_fail_count;       /* vsc�ļ���ȡʧ�ܴ��� */
    unsigned int                  write_fail_count;      /* vsc�ļ�д��ʧ�ܴ��� */
};

struct vsc_host_mgr;

struct vsc_ctrl_info {
    spinlock_t                    lock;
    atomic_t                      ref_cnt;               /* ���ü��� */
    //struct list_head              list;
    struct Scsi_Host              *scsi_host;            /* scsi_host�ṹ��ָ�� */
    int                           vbs_host_id;           /* vbsͨ��port�����host id������osע���host id��һ�� */
    struct vsc_host_mgr           *silbing_hosts;        /* �͵�ǰhost����ͬһ��vbs��host���� */

    int                           nr_cmds;               /* ������scsi������� */

    unsigned int                  io_running;            /* host�����ڴ�������������� */

    struct list_head              reqQ;                  /* ����������� */
    struct list_head              cmpQ;                  /* ��ȡ���������� */
    struct list_head              rspQ;                  /* �ȴ���Ӧ���� */
    unsigned int                  Qdepth;
    __u64                         cmd_sn;                /* �������к� */
    struct vsc_cmnd_list          **cmd_pool_tbl;        /* ���л���� */
    unsigned long                 *cmd_pool_bits;        /* ������ʹ��ӳ��� */

    struct list_head              event_reqQ;            /* �¼�������� */
    struct list_head              event_rspQ;            /* �¼���Ӧ���� */
    int                           nr_events;             /* �¼����� */
    __u64                         event_sn;              /* �¼����к� */
    struct vsc_event_list         **event_pool_tbl;      /* �¼����� */
    unsigned long                 *event_pool_bits;      /* �¼������ʹ��ӳ��� */

    wait_queue_head_t             queue_wait;            /* �����¼� */ 

    unsigned int                  suspend;               /* ���ݷ��͹��� */         

    struct file                   *file;                 /* �򿪵��ļ���Ϣ */
    int                           wakeup_pid;            /* �˳�ʱ�Ƿ���Ҫ���ѽ��� */
    struct vsc_ctrl_statics       stat;

    struct timer_list             target_abnormal_timer; /* �����쳣��ʱ�� */
    __u32                         target_abnormal_time;  /* �����쳣����ʱ�� */
    atomic_t                      target_abnormal_lock;  /* �Ƿ����ڽ���attach��timer */

    unsigned int get_cmd_times;  /*ȡcmd����*/
    unsigned int get_cmd_total;  /*ȡcmd����*/
    unsigned int get_cdb_times;  /*ȡcdb����*/
    unsigned int get_cdb_total;  /*ȡcdb����*/
    unsigned int put_rsp_times;  /*��Ӧ����*/
    unsigned int put_rsp_total;  /*��Ӧ��������*/

#ifdef __VSC_LATENCY_DEBUG__
    __u64 write_cmd_count;
    __u64 read_cmd_count;

    __u64 write_stage1_total;
    __u64 write_stage2_total;
    __u64 write_stage3_total;
    __u64 write_total;

    __u64 read_stage1_total;
    __u64 read_stage2_total;
    __u64 read_stage3_total;
    __u64 read_total;
#endif
};

/* ��vbs��¼���е�host */
struct vsc_host_mgr {
    struct list_head node;
    __u32 vbs_id;               /*ͨ��vbsע���host id����*/
    __u32 host_count;           /*��vbsע���host����*/
    __u32 active_host_count;    /*�host����*/
    struct vsc_ctrl_info* host_list[MAX_HOST_NR_PER_VBS];
};

#define VSC_DATA_MAGIC            0x615461442d437356     /* VsC-DaTa */
#define VSC_DATA_VER_MAJOR        (1)                    /* �������汾�ţ����汾����������������������*/ 
#define VSC_DATA_VER_MINOR        (1)                    /* ���ݴ�Ҫ�汾�ţ���Ҫ�汾�ţ������ݼ��ݣ�ǰ�����ݼ��ݡ�*/

struct vsc_scsi_data_head {
    unsigned long                 magic;                 /* ħ�� */
    unsigned int                  ver_major;             /* �汾�� */
    unsigned int                  ver_minor;             /* ��Ҫ�汾�� */
    unsigned long                 size;                  /* ���ݳ��� */
    unsigned long                 reserved[32];          /* �����ֶ� */
} __attribute__ ((packed));

struct vsc_scsi_data_struct {
    struct vsc_scsi_data_head     head;                  /* ����ͷ */
    __u64                         cmd_sn;                /* �������к� */
    __u64                         event_sn;              /* �¼����к� */
    unsigned int                  suspend;               /* ���ݷ��͹��� */
    int                           vbs_host_id; 
    struct vsc_ctrl_statics       stat;                  /* ͳ������ */
} __attribute__ ((packed));

#define VSC_SCSI_DEVICE_RESERVE_SIZE    (2 * 1024)
/* �����ݽṹ�Ĵ�С���ܳ��� VSC_SCSI_DEVICE_RESERVE_SIZE
 * �Ȳ����漰��������ݵı�����뱣����Щ���ݼ������ļ���*/
struct vsc_scsi_device_resrve_data {
    struct vsc_scsi_data_head       head;
    struct vsc_ioctl_disk_vol_name  disk_vol;
    atomic64_t                      disk_io_count;
}__attribute__ ((packed));

/* ��ÿ��vbs�Ĺ���ṹ������ */
static struct list_head g_host_mgr_list;

/* scsi������ϲ�����Ҫ����ڴ棬ʹ��ջ�ڴ治���ʣ�����slab */
static struct kmem_cache *scsi_buf_slab = NULL;
static mempool_t *scsi_buf_pool = NULL;
#define MIN_SCSI_CMD_RESERVED    2048

static DEFINE_MUTEX(ctrl_info_list_lock);
static DEFINE_MUTEX(ctrl_host_reg_lock);


#ifdef DRIVER_VER
static char banner[] __initdata = KERN_INFO "Huawei Cloudstorage virtual storage controller driver "DRIVER_VER" initialized.\n";
#else
static char banner[] __initdata = KERN_INFO "Huawei Cloudstorage virtual storage controller driver initialized.\n";
#endif

#if (LINUX_VERSION_CODE == KERNEL_VERSION(2, 6, 18)) 
    #define QUEUE_FLAG_BIDI        7    /* queue supports bidi requests */
#endif

static uint io_per_host = 4;
module_param(io_per_host, uint, 0644);
MODULE_PARM_DESC(io_per_host, "IOs'll be send to one host when enable multi-fd,0-disable,0|1|2|4");

uint io_per_host_shift = 2;

/**************************************************************************
 ��������  : host_info������飬��register host��ʱ�����
 ��    ��  : struct hlist_head *list  hash����
             vsc_cmnd_list *c         scsi������ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static inline int check_host_info(struct vsc_ioctl_cmd_add_host *host_info)
{
    if (unlikely(!host_info)) {
        return -EFAULT;
    }

    if (host_info->max_cmd_len > VSC_MAX_CDB_LEN
        || host_info->max_cmd_len <= 0
        || host_info->sg_count > VSC_MAX_SG_COUNT 
        || host_info->sg_count <= 0
        || host_info->max_nr_cmds > VSC_DEFAULT_MAX_CMD_NUMBER
        || host_info->max_nr_cmds <= 0
        || host_info->cmd_per_lun > VSC_DEFAULT_LUN_CMD_NUMBER 
        || host_info->cmd_per_lun <= 0
        || host_info->cmd_per_lun > host_info->max_nr_cmds
        || host_info->max_channel <= 0
        || host_info->max_id <= 0
        || host_info->max_lun <= 0) {
        return -EINVAL;
    }
    return 0;
}


/**************************************************************************
 ��������  : ���¼���ӵ����� 
 ��    ��  : struct hlist_head *list  hash����
             vsc_cmnd_list *c         scsi������ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static inline void add_eventQ(struct list_head *list, struct vsc_event_list *c)
{
    list_add_tail(&c->list, list);
}

/**************************************************************************
 ��������  : ���¼��Ӷ�����ɾ��
 ��    ��  : vsc_cmnd_list *c       scsi������ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static inline void remove_eventQ(struct vsc_event_list *c)
{
    list_del_init(&c->list);
}

/**************************************************************************
 ��������  : ��������뵽������  
 ��    ��  : struct list_head *list   hash����
             vsc_cmnd_list *c         scsi������ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static inline void addQ(struct list_head *list, struct vsc_cmnd_list *c)
{
    list_add_tail(&c->list, list);
}

/**************************************************************************
 ��������  : �Ӷ�����ɾ������ 
 ��    ��  : vsc_cmnd_list *c       scsi������ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static inline void removeQ(struct vsc_cmnd_list *c)
{
    list_del_init(&c->list);
}

static inline int list_size(struct list_head *list)
{
    int count = 0;
    struct list_head *temp;

    list_for_each(temp, list)
    {
        count++;
    }

    return count;
}

/* VBS��������host id��bit 15~8 vbs id(port)��bit 7~0 host index within vbs */
static inline __u32 vsc_get_vbs_id_by_host_id(__u32 host_id)
{
    //return (host_id - SCSI_HOST_BASE_OFFSET) / MAX_HOST_NR_PER_VBS - 1;
    return (host_id >> 8) & 0xFFFF;
}

static inline __u32 vsc_get_host_index_in_vbs(__u32 host_id)
{
    //return host_id % MAX_HOST_NR_PER_VBS;
    return host_id & 0xFF;
}

static inline __u64 vsc_get_usec(void)
{
    struct timeval tv;
    do_gettimeofday(&tv);

    return tv.tv_sec * 1000000 + tv.tv_usec;
}

/*static void vsc_debug_buf(char *buffer, int len)
{    
    char temp[128];// �������16���ֽڣ�128���ֽ�������װ������    
    int temp_len;    
    int out_len = len/16*16;    
    int i,j;     

    // ��16���ֽ�һ�У�ѭ����� 
    for (i=0;i<out_len;i+=16){        
        temp_len=0;        
        for (j=0;j<16;j++){            
            temp_len += sprintf(temp+temp_len, "%02x ", buffer[i+j]&0xFF);        
        }        
        vsc_err("%s\n", temp);    
    }     

    // ��������16���ֽڵ�һ��   
    temp_len=0; 
    for (i=out_len;i<len;i++){       
        temp_len += sprintf(temp+temp_len, "%02x ", buffer[i]&0xFF);    
    }   

    vsc_err("%s\n", temp);
} */  

/**************************************************************************
 ��������  : ������õ��¼�������
 ��    ��  : struct list_head *list  ����
 �� �� ֵ  : vsc_event_list*         ���õ��¼�������
**************************************************************************/
static struct vsc_event_list *vsc_event_alloc(struct vsc_ctrl_info *h)
{
    int i;
    struct vsc_event_list *e = NULL;

    if (unlikely(!h)) {
        return NULL;
    }

    /* ����bitλ���ҿ��õĻ����� */
    do {
        i = find_first_zero_bit(h->event_pool_bits, h->nr_events);
        /*
          * [zr]
          * x86 ��û���ҵ�0 bit ʱ����size; 
          * arm ��û���ҵ�0 bit ʱ����size+1
          * ���ԱȽ�ͨ�õķ�ʽӦ���ж�(i >= h->nr_cmds)
          */
        if (i == h->nr_events)
            return NULL;
    } while (test_and_set_bit
         (i & (BITS_PER_LONG - 1),
          h->event_pool_bits + (i / BITS_PER_LONG)) != 0);

    /* �����е�bitλ����ȡ���õ�������� */
    e = h->event_pool_tbl[i];
    memset(e, 0, sizeof(*e));

    /* ��ʼ������ */
    INIT_LIST_HEAD(&e->list);
    e->event_index = i;
    e->stat = EVENT_LIST_STAT_INIT;
    e->h = h;
    h->event_sn++;
    e->event_sn = (__u32)h->event_sn;
    e->event_data_len = 0;
    e->shoot = EVENT_SHOOT_NOSHOOT;
    atomic_set(&e->refcnt, 1);    
    init_waitqueue_head(&e->wait);
    
    return e;
}

/**************************************************************************
 ��������  : ��ȡ���ü��� 
 ��    ��  : struct list_head *list  ����
             vsc_event_list *e       �¼����ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static void vsc_event_get(struct vsc_event_list *e)
{
    if (unlikely(!e)) {
        return ;
    }

    atomic_inc(&e->refcnt);
}

/**************************************************************************
 ��������  : �ͷŻ����� 
 ��    ��  : struct list_head *list  ����
             vsc_event_list *e       �¼����ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static void vsc_event_put(struct vsc_event_list *e)
{
    int i;
    struct vsc_ctrl_info *h = NULL;

    if (unlikely(!e) ) {
        return ;
    }

    h = e->h;
    /* ���ü����ݼ� */
    if (atomic_dec_and_test(&e->refcnt)) {
        if (e->event_index >= h->nr_events) {
            return;
        }

        /* ����������λ�ã��������Ӧ��λ��*/
        i = e->event_index;
        e->stat = EVENT_LIST_STAT_INIT;

        clear_bit(i & (BITS_PER_LONG - 1), h->event_pool_bits + (i / BITS_PER_LONG));
    }
}


/**************************************************************************
 ��������  : ����¼�
 ��    ��  : struct vsc_event_list *e �¼�ָ��
             callback                 �¼��ص�����
             event_data               �¼�����
             event_data_len           �¼����ݳ���
             event_priv               �¼�˽������
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
static int vsc_event_add(struct vsc_event_list *e, event_callback callback, int event_type, 
                            void *event_data, int event_data_len, unsigned long event_priv)
{
    struct vsc_ctrl_info *h;
    struct vsc_scsi_msg_data *msg_data;

    if (unlikely(!e) || unlikely(!event_data) || !callback) {
        return -EFAULT;
    }

    /* �����Ч�� */
    if (event_data_len >= sizeof(e->event_data) - sizeof(*msg_data)) {
        return -EINVAL;
    }

    h = e->h;

    msg_data = (struct vsc_scsi_msg_data *)(e->event_data);
    /* �����¼����� */
    memcpy(msg_data->data, event_data, event_data_len);
    msg_data->data_len = event_data_len;
    msg_data->data_type = event_type;
    e->event_data_len = event_data_len + sizeof(*msg_data);

    /*ע���¼����� */
    e->event_callback = callback;
    e->event_priv = event_priv;

    /* �����û�̬�����ȡ�¼� */
    spin_lock_bh(&h->lock);
    add_eventQ(&e->h->event_reqQ, e);
    spin_unlock_bh(&h->lock);
    wake_up_interruptible(&e->h->queue_wait);  

    return 0;
}

/**************************************************************************
 ��������  : �¼����Ѻ���
 ��    ��  : struct vsc_event_list *e �¼�ָ��
             time                     ��ʱʱ��
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
static int vsc_event_wait_timeout(struct vsc_event_list *e, unsigned long time)
{
    int retval;
    
    vsc_event_get(e);
    retval = wait_event_timeout(e->wait, e->shoot, time);
    if (0 == retval) {
        /* �ȴ���ʱ��������*/
        if (e->event_callback) {
            e->event_callback(e->h, EVENT_TIMEOUT, e, 0, NULL, 0);
        }
    }

    /* ���������ABORT���򷵻�ABORT */
    if (EVENT_SHOOT_ABORT == e->shoot) {
        if (e->event_callback) {
            e->event_callback(e->h, EVENT_ABORT, e, 0, NULL, 0);
        }
    }

    vsc_event_put(e);

    return retval;
}

/**************************************************************************
 ��������  : �¼�ɾ��
 ��    ��  : struct vsc_event_list *e �¼�ָ��
 �� �� ֵ  : 
**************************************************************************/
static int vsc_event_del(struct vsc_event_list *e)
{
    struct vsc_ctrl_info *h = NULL;

    if (unlikely(!e)) {
        return -EFAULT;
    }

    /* �����¼� */
    if (waitqueue_active(&e->wait)) {
        e->shoot = EVENT_SHOOT_ABORT;
        wake_up(&e->wait);
    }

    h = e->h;
    spin_lock_bh(&h->lock);
    if (!list_empty(&e->list)) {
        remove_eventQ(e);
    }
    spin_unlock_bh(&h->lock);

    vsc_event_put(e);

    return 0;
}

/**************************************************************************
 ��������  : �˳�����event�¼�
 ��    ��  : struct vsc_ctrl_info *h  host���ƾ��
 �� �� ֵ  : 0: �ɹ�, ����: scsi�в������
**************************************************************************/
static int vsc_abort_all_event(struct vsc_ctrl_info *h)
{
    struct vsc_event_list *e;

    if (unlikely(!h) ) {
        return -EINVAL;
    }
    
    spin_lock_bh(&h->lock);
    while (!list_empty(&h->event_reqQ)) {
        e = list_first_entry(&h->event_reqQ, struct vsc_event_list, list);
        remove_eventQ(e);
        spin_unlock_bh(&h->lock);
        if (waitqueue_active(&e->wait)) {
            e->shoot = EVENT_SHOOT_ABORT;
            wake_up(&e->wait);
        }
        spin_lock_bh(&h->lock);
    }
    spin_unlock_bh(&h->lock);

    spin_lock_bh(&h->lock);
    while (!list_empty(&h->event_rspQ)) {
        e = list_first_entry(&h->event_rspQ, struct vsc_event_list, list);
        remove_eventQ(e);
        spin_unlock_bh(&h->lock);
        if (waitqueue_active(&e->wait)) {
            e->shoot = EVENT_SHOOT_ABORT;
            wake_up(&e->wait);
        }
        spin_lock_bh(&h->lock);
    }
    spin_unlock_bh(&h->lock);

    return 0;
}


/**************************************************************************
 ��������  : ������õĻ�����
 ��    ��  : struct list_head *list  ����
 �� �� ֵ  : vsc_cmd_list*            ���õ��������
**************************************************************************/
static struct vsc_cmnd_list *vsc_cmd_alloc(struct vsc_ctrl_info *h)
{
    int i;
    struct vsc_cmnd_list *c = NULL;

    if (unlikely(!h)) {
        return NULL;
    }

    /* ����bitλ���ҿ��õĻ����� */
    do {
        i = find_first_zero_bit(h->cmd_pool_bits, h->nr_cmds);
        /*
                * [zr]
                * x86 ��û���ҵ�0 bit ʱ����size; 
                * arm��û���ҵ�0 bit ʱ����size+1  //implemented in arch/arm/lib/findbit.S
                * ���ԱȽ�ͨ�õķ�ʽӦ���ж�(i >= h->nr_cmds)
                */
        if (i == h->nr_cmds)
            return NULL;
    } while (test_and_set_bit
         (i & (BITS_PER_LONG - 1),
          h->cmd_pool_bits + (i / BITS_PER_LONG)) != 0);

    /* �����е�bitλ����ȡ���õ�������� */
    c = h->cmd_pool_tbl[i];

    /* ��ʼ������ */
    INIT_LIST_HEAD(&c->list);
    c->cmd_index = i;
    c->stat = CMD_STAT_INIT;
    c->h = h;
    c->scsi_cmd = NULL;
    h->cmd_sn++;
    c->cmd_sn = (__u32)h->cmd_sn;
    atomic_set(&c->refcnt, 1);  
    
    return c;
}

/**************************************************************************
 ��������  : ��ȡ����ṹ���ü��� 
 ��    ��  : struct list_head *list  ����
             vsc_event_list *e       �¼����ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static void vsc_cmd_get(struct vsc_cmnd_list *c)
{
    if (unlikely(!c)) {
        return ;
    }

    atomic_inc(&c->refcnt);
}

/**************************************************************************
 ��������  : �ͷŻ����� 
 ��    ��  : vsc_cmnd_list *c         scsi������ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static void vsc_cmd_put(struct vsc_cmnd_list *c)
{
    int i;
    struct vsc_ctrl_info *h = NULL;
    struct scsi_cmnd *scmd = NULL;

    if (unlikely(!c) ) {
        return ;
    }

    h = c->h;
    /* ���ü����ݼ� */
    if (atomic_dec_and_test(&c->refcnt)) {
        if (c->cmd_index >= h->nr_cmds) {
            return;
        }
        scmd = (struct scsi_cmnd *) c->scsi_cmd;
        if (likely(scmd) && scmd->host_scribble == (void*)c) {
            scmd->host_scribble = NULL;
        }

        /* ����������λ�ã��������Ӧ��λ��*/
        i = c->cmd_index;
        
        clear_bit(i & (BITS_PER_LONG - 1), h->cmd_pool_bits + (i / BITS_PER_LONG));
    }
}

void vsc_debug_host(struct vsc_ctrl_info *h)
{
    struct vsc_cmnd_list *c = NULL;
    struct list_head *temp = NULL;

    if (!h)
        return;

    vsc_err("*************************Req Queue*************************\n");
    spin_lock_bh(&h->lock);
    list_for_each (temp, &h->reqQ) {
        c = list_entry(temp, struct vsc_cmnd_list, list);

        vsc_err("host = %u, cmd_sn = %d, tag = %d cmd_stat = %d\n",
            vsc_ctrl_get_host_no(h), c->cmd_sn, c->cmd_index, c->stat);

    }
    spin_unlock_bh(&h->lock);

    vsc_err("*************************Cmp Queue*************************\n");
    spin_lock_bh(&h->lock);
    list_for_each (temp, &h->cmpQ) {
        c = list_entry(temp, struct vsc_cmnd_list, list);

        vsc_err("host = %u, cmd_sn = %d, tag = %d cmd_stat = %d\n",
            vsc_ctrl_get_host_no(h), c->cmd_sn, c->cmd_index, c->stat);

    }
    spin_unlock_bh(&h->lock);

    vsc_err("*************************Rsp Queue*************************\n");
    spin_lock_bh(&h->lock);
    list_for_each (temp, &h->rspQ) {
        c = list_entry(temp, struct vsc_cmnd_list, list);

        vsc_err("host = %u, cmd_sn = %d, tag = %d cmd_stat = %d\n",
            vsc_ctrl_get_host_no(h), c->cmd_sn, c->cmd_index, c->stat);

    }
    spin_unlock_bh(&h->lock);
}

void vsc_debug_cmd(int host_no)
{
    __u32 i;
    struct vsc_host_mgr *mgr = NULL;
    __u32 vbs_id = vsc_get_vbs_id_by_host_id(host_no);
    __u32 host_index = vsc_get_host_index_in_vbs(host_no);

    if (host_index >= MAX_HOST_NR_PER_VBS) {
        return;
    }

    /* �����ָ��hostͬһ��vbs��host��cmd��Ϣ */
    mutex_lock(&ctrl_info_list_lock);
    list_for_each_entry(mgr, &g_host_mgr_list, node) {
        if (mgr->vbs_id == vbs_id && mgr->host_count <= MAX_HOST_NR_PER_VBS) {
            for (i=0;i<mgr->host_count;i++){
                vsc_debug_host(mgr->host_list[i]);
            }

            mutex_unlock(&ctrl_info_list_lock);
            return;
        }
    }
    mutex_unlock(&ctrl_info_list_lock);
}

/**************************************************************************
 ��������  : ��ȡctrl_infoָ��
 ��    ��  : struct scsi_device *sdev       scsi�豸ָ��
 �� �� ֵ  : struct vsc_ctrl_info *         host���ƾ��
**************************************************************************/
static inline struct vsc_ctrl_info *sdev_to_ctrl_info(struct scsi_device *sdev)
{
    struct vsc_scsi_struct *vss = vsc_scsi_if_get_vss(sdev->host);
    if (!vss) {
        return NULL;
    }
    return (struct vsc_ctrl_info *) vsc_scsi_if_get_priv(vss);
}

/**************************************************************************
 ��������  : ��ѯscsi�����Ӧ��struct vsc_cmnd_list *cָ��
 ��    ��  : struct scsi_cmnd *sc   sc����ָ��
 �� �� ֵ  : struct vsc_cmnd_list *cָ��
**************************************************************************/
static inline struct vsc_cmnd_list *sc_to_cmnd_list(struct scsi_cmnd *sc)
{
    return (struct vsc_cmnd_list *)sc->host_scribble;
}

/**************************************************************************
 ��������  : ����host
 ��    ��  : svsc_ctrl_info *h:         host���ƾ��
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
int vsc_suspend_host(struct vsc_ctrl_info *h)
{
    if (!h) {
        return -EBADF;
    }

    scsi_block_requests(h->scsi_host);
    h->suspend = 1;

    return 0;
}

/**************************************************************************
 ��������  : �ָ�host
 ��    ��  : svsc_ctrl_info *h:         host���ƾ��
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
int vsc_resume_host(struct vsc_ctrl_info *h)
{
    if (!h) {
        return -EBADF;
    }

    scsi_unblock_requests(h->scsi_host);
    h->suspend = 0;

    return 0;
}

/**************************************************************************
 ��������  : �ָ�host
 ��    ��  : svsc_ctrl_info *h:         host���ƾ��
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
int vsc_resume_host_all(struct vsc_ctrl_info *h, int __user *p_user)
{
    int active_host_count = 0;
    struct vsc_host_mgr *vhmgr = NULL;
    int i = 0;
    int ret = 0;

    vhmgr = h->silbing_hosts;
    if (!vhmgr) {
        return -EBADF;
    }

    ret = get_user(active_host_count, p_user);
    if (ret || (active_host_count > vhmgr->host_count)) {
        vsc_err("set active host count failed, host_count: %d, "
                "active_host_count: %d\n", vhmgr->host_count,
                vhmgr->active_host_count);
        return ret;
    }

    vhmgr->active_host_count = active_host_count;
    for (i = 0; i < vhmgr->host_count; i++) {
        h = vhmgr->host_list[i];
        if (!h) {
            continue;
        }
        /* �ָ�host�������� */
        ret = vsc_resume_host(h);
        if (ret) {
            vsc_err("resume host[%d] failed, roll back\n", i);
            while (i > 0) {
                i--;
                h = vhmgr->host_list[i];
                if (!h) {
                    continue;
                }
                vsc_suspend_host(h);
            }
            return ret;
        }
    }

    return ret;
}

/**************************************************************************
 ��������  : poll_wait�ӿ�
 ��    ��  : file *file:                file �ļ����
             svsc_ctrl_info *h:         host���ƾ��
             poll_table *wait          poll wait����
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
unsigned int vsc_poll_wait(struct file *file, poll_table *wait)
{
    unsigned int             mask = 0;
    struct vsc_ctrl_info *h = NULL;

    if (!file ) {
        /* Here should return 0 on error [zr] */
        //return -EFAULT;  
        return 0;
    }

    h = file->private_data;
    if (!h) {
        return 0;
    }

    /* ��select���̼����ض��� */
    poll_wait(file, &h->queue_wait, wait);
    
    /* ��������ݿ��Զ��������ÿɶ���־ */
    spin_lock_bh(&h->lock);
    if (!list_empty(&h->cmpQ) || !list_empty(&h->event_reqQ)) {
        mask |= (POLLIN | POLLRDNORM); 
    }
    spin_unlock_bh(&h->lock);

    return mask;
}

/**************************************************************************
 ��������  : ��scsi����������
 ��    ��  : svsc_ctrl_info *h:     host���ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static inline void vsc_start_io(struct vsc_ctrl_info *h)
{
    struct vsc_cmnd_list *c;

    spin_lock_bh(&h->lock);
    while (!list_empty(&h->reqQ)) {
        /* ����������л�ȡ��һ������ */
        c = list_first_entry(&h->reqQ, struct vsc_cmnd_list, list);

        /* �����������ɾ������ */
        removeQ(c);
        h->Qdepth--;

        /* ֪ͨscsi��������ִ��scsi���� */
        c->stat = CMD_STAT_REQUEST;
        addQ(&h->cmpQ, c);
        spin_unlock_bh(&h->lock);

        if (waitqueue_active(&h->queue_wait)) {
            wake_up_interruptible(&h->queue_wait);
        }
        /* [zr] ����ÿ��һ��IO��cmpQ��Ҫ���»�ȡ��,��ȡ�߳�ÿ��cmpQ��ժ��һ��IO�ҵ�rspQ��Ҳ��Ҫ��ȡ��,
                 �����᲻�ᵼ��queuecommand��ʱ�ϳ�? */
        /* --SMP��ÿ��queuecommand�������ܶ��scsi_cmnd, ����������Ծ����ܼ��������е�ʱ��, ��������� */
        spin_lock_bh(&h->lock);
    }
    spin_unlock_bh(&h->lock);
}

static inline int vsc_is_readwrite_cmd(unsigned char cmd_type)
{
    switch (cmd_type) {
        case WRITE_6:
        case WRITE_10:
        case WRITE_12:
        case WRITE_16:
        case READ_6:
        case READ_10:
        case READ_12:
        case READ_16:
            return 1;
        default:
            return 0;
    }
}

static inline int vsc_is_read_cmd(unsigned char cmd_type)
{
    switch (cmd_type) {
        case READ_6:
        case READ_10:
        case READ_12:
        case READ_16:
            return 1;
        default:
            return 0;
    }
}

static inline int vsc_is_write_cmd(unsigned char cmd_type)
{
    switch (cmd_type) {
        case WRITE_6:
        case WRITE_10:
        case WRITE_12:
        case WRITE_16:
            return 1;
        default:
            return 0;
    }
}

/**************************************************************************
 ��������  : ��scsi����������
 ��    ��  : svsc_ctrl_info *h:     host���ƾ��
             vsc_cmnd_list *c       scsi������ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static inline void vsc_enqueue_cmd_and_start_io(struct vsc_ctrl_info *h, struct vsc_cmnd_list *c)
{
    spin_lock_bh(&h->lock);
    addQ(&h->reqQ, c);
    h->Qdepth++;
    h->io_running++;
    spin_unlock_bh(&h->lock);
    /* [zr] ���м�᲻�����������߳���h->reqQ�Ϲ�I/O����? */
    /* --SMP, ���ж��CPUͬʱ�� */
    vsc_start_io(h);
}

/**************************************************************************
 ��������  : vsc scsi �������
 ��    ��  : struct scsi_cmnd *sc        scsi��������ָ��
             done                         scsi��������в�֪ͨ�ص�����
 �� �� ֵ  : 0: �ɹ���������scsi�в������
**************************************************************************/

#ifdef DEF_SCSI_QCMD
static int vsc_scsi_queue_command_lck(struct scsi_cmnd *sc, void (*done)(struct scsi_cmnd *)) 
#else
static int vsc_scsi_queue_command(struct scsi_cmnd *sc, void (*done)(struct scsi_cmnd *)) 
#endif
{
    struct vsc_ctrl_info *orig_h = NULL;
    struct vsc_ctrl_info *h = NULL;
    struct vsc_cmnd_list *c = NULL;
    __u64 sn = 0;
    __u32 host_index = 0;
    struct vsc_host_mgr *silbing_hosts = NULL;
    struct vsc_scsi_device_resrve_data *sdev_reserve_data = NULL;
    struct scsi_device *sdev = sc->device;
    int active_host_count = 0;
    
    orig_h = sdev_to_ctrl_info(sdev);
    if (unlikely(!orig_h)) {
        return SCSI_MLQUEUE_HOST_BUSY;
    }

    if (unlikely(VSC_DISK_PREPARE_DELETE ==
                 ((struct vsc_ioctl_disk_vol_name *)(&sdev->sdev_data[0]))->state)) {
        sc->result = DID_NO_CONNECT << 16;
        done(sc);
        return 0;
    }

    /* [zr] ����ΪʲôҪ�ͷ�host_lock? */
    /* --Ϊ�˼��ٹ��жϵ�ʱ��, �в��ڵ�queuecommand֮���Ѿ������ж� */
    spin_unlock_irq(orig_h->scsi_host->host_lock);

    /* io_per_host = 0: ��fdģʽ
       io_per_host > 0: ��fdģʽ��io���������͸�host_per_vbs��host��ÿ��host����io_per_host��io
       ���io running��0��ʹ�ö�fd�����io running��0��ʹ�õ�fd��ʱ�Ӹ���
    */
    if (likely(io_per_host > 0)) {
        silbing_hosts = orig_h->silbing_hosts;
        sdev_reserve_data = (struct vsc_scsi_device_resrve_data *)(&sdev->sdev_data[0]);
            
        if (unlikely(!silbing_hosts || !sdev_reserve_data)) {
            vsc_err("silbing_hosts=%p, sdev_reserve_data=%p",
                            silbing_hosts, sdev_reserve_data);
            /* ǰ���Ѿ������������˵�scsi��֮ǰ������� */
            spin_lock_irq(orig_h->scsi_host->host_lock);
            return SCSI_MLQUEUE_HOST_BUSY;
        }

        /* �Ƕ�д����Ĭ����0���̴߳�����vbs����һ�� */
        if (likely(vsc_is_readwrite_cmd(sc->cmnd[0]))) {
            /* ÿ����ά��һ������������֤ÿ�����io�ڸ����߳��Ͼ��� */
            sn = atomic64_add_return(1, &sdev_reserve_data->disk_io_count);

            active_host_count = (0 != silbing_hosts->active_host_count) ?
                  silbing_hosts->active_host_count : silbing_hosts->host_count;
            if (unlikely(0 == active_host_count)) {
                vsc_err("invalid host_index=%d, sn=%llu, host_count=%d, active_host_count=%d",
                             host_index, sn, silbing_hosts->host_count,
                             silbing_hosts->active_host_count);
                return SCSI_MLQUEUE_HOST_BUSY;
            }
            /* io��������ͬһ��vbs�Ĳ�ͬhost�ϣ�ÿ��host�Ϸ�һ�� */
            host_index = ((__u32)sn >> io_per_host_shift) % active_host_count;
            if (unlikely(host_index >= MAX_HOST_NR_PER_VBS)) {
                vsc_err("invalid host_index=%d, sn=%llu, host_count=%d, active_host_count=%d",
                             host_index, sn, silbing_hosts->host_count,
                             silbing_hosts->active_host_count);
                /* ǰ���Ѿ������������˵�scsi��֮ǰ������� */
                spin_lock_irq(orig_h->scsi_host->host_lock);
                return SCSI_MLQUEUE_HOST_BUSY;
            }
        }
        else {
            host_index = 0;
        }
        h = silbing_hosts->host_list[host_index];
    }
    else {
        h = orig_h;
    }
    
    if (unlikely(!h)) {
        /* ǰ���Ѿ������������˵�scsi��֮ǰ������� */
        spin_lock_irq(orig_h->scsi_host->host_lock);
        return SCSI_MLQUEUE_HOST_BUSY;
    }

    /* ��ȡ���õĻ����� */
    spin_lock_bh(&h->lock);
    c = vsc_cmd_alloc(h);
    spin_unlock_bh(&h->lock);
    if (unlikely(c == NULL)) {
        spin_lock_irq(orig_h->scsi_host->host_lock);
        return SCSI_MLQUEUE_HOST_BUSY;
    }
   
    /* ����������ɵĻص�֪ͨ������ַ */
    sc->scsi_done = done;    

    /* ���������ַ���Ա�����ABORT��ʱ��ʹ�� */
    sc->host_scribble = (unsigned char *) c;
    c->scsi_cmd = sc;
#ifdef __VSC_LATENCY_DEBUG__
    c->start_queue_time = vsc_get_usec();
#endif

    /* ��scsi������봦������� */
    vsc_enqueue_cmd_and_start_io(h, c);

    spin_lock_irq(orig_h->scsi_host->host_lock);

    return 0;
}
#ifdef DEF_SCSI_QCMD
static DEF_SCSI_QCMD(vsc_scsi_queue_command)
#endif
/**************************************************************************
 ��������  : scsi�豸ɨ�迪ʼ�ص�����
 ��    ��  : Scsi_Host *sh:     scsi�豸ɨ������ص�����
             elapsed_time       �ķ�ʱ��
 �� �� ֵ  : 1�� �ɹ���0�������ȴ�
**************************************************************************/
static int vsc_scan_finished(struct Scsi_Host *sh, unsigned long elapsed_time)
{
    return 1; 
}

/**************************************************************************
 ��������  scsi�豸ɨ�迪ʼ�ص�����
 ��    ��  : Scsi_Host *sh:     scsi host���ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static void vsc_scan_start(struct Scsi_Host *sh)
{
    return;
}

/**************************************************************************
 ��������  : ���������е�����������Ӷ�����ɾ��
 ��    ��  : vsc_cmnd_list *c         scsi������ƾ��
 �� �� ֵ  : 0: �ɹ�, ����: scsi�в������
**************************************************************************/
static int vsc_each_queue_remove(struct vsc_ctrl_info *h, void (*callback)
            (struct vsc_ctrl_info *, struct vsc_cmnd_list *, enum queue_type) )
{
    struct vsc_cmnd_list *c = NULL;

    /* ѭ������reqQ�����е�scsi���� */
    spin_lock_bh(&h->lock);
    while (!list_empty(&h->reqQ)) {
        c = list_first_entry(&h->reqQ, struct vsc_cmnd_list, list);
        removeQ(c);
        h->io_running--;
        spin_unlock_bh(&h->lock);
        vsc_cmd_get(c);
        callback(h, c, VSC_LIST_REQQ);
        vsc_cmd_put(c);
        spin_lock_bh(&h->lock);
    }
    spin_unlock_bh(&h->lock);
    

    /* ѭ������cmpQ�����е�scsi���� */
    spin_lock_bh(&h->lock);
    while (!list_empty(&h->cmpQ)) {
        c = list_first_entry(&h->cmpQ, struct vsc_cmnd_list, list);
        removeQ(c);
        h->io_running--;
        spin_unlock_bh(&h->lock);
        vsc_cmd_get(c);
        callback(h, c, VSC_LIST_COMQ);
        vsc_cmd_put(c);
        spin_lock_bh(&h->lock);
    }
    spin_unlock_bh(&h->lock);

    /* ѭ������rspQ�����е�scsi���� */
    spin_lock_bh(&h->lock);
    while (!list_empty(&h->rspQ)) {
        c = list_first_entry(&h->rspQ, struct vsc_cmnd_list, list);
        removeQ(c);
        h->io_running--;
        spin_unlock_bh(&h->lock);
        vsc_cmd_get(c);
        callback(h, c, VSC_LIST_RSPQ);
        vsc_cmd_put(c);
        spin_lock_bh(&h->lock);
    }
    spin_unlock_bh(&h->lock);

    return 0;
}

static int vsc_each_queue_remove_by_device(struct vsc_ctrl_info *h, void (*callback)
            (struct vsc_ctrl_info *, struct vsc_cmnd_list *, enum queue_type), struct scsi_cmnd *sc )
{
    struct vsc_cmnd_list *c = NULL;
    struct list_head *pos = NULL;
    struct list_head *next = NULL;
    struct scsi_cmnd *temp_sc = NULL;
    struct scsi_device *sdev = sc->device;
    LIST_HEAD(handleQ);

    /* ѭ������reqQ������ָ�����scsi���� */
    spin_lock_bh(&h->lock);
    list_for_each_safe(pos, next, &h->reqQ) {
        c = list_entry(pos, struct vsc_cmnd_list, list);
        temp_sc = c->scsi_cmd;
        if (temp_sc->device == sdev) {
            removeQ(c);
            c->stat = CMD_STAT_CANCELED;
            addQ(&handleQ, c);
            h->io_running--;
        }
    }
    spin_unlock_bh(&h->lock);

    list_for_each_safe(pos, next, &handleQ) {
        c = list_entry(pos, struct vsc_cmnd_list, list);
        removeQ(c);
        vsc_cmd_get(c);
        callback(h, c, VSC_LIST_REQQ);
        vsc_cmd_put(c);
    }

    /* ѭ������cmpQ������ָ�����scsi���� */
    spin_lock_bh(&h->lock);
    list_for_each_safe(pos, next, &h->cmpQ) {
        c = list_entry(pos, struct vsc_cmnd_list, list);
        temp_sc = c->scsi_cmd;
        if (temp_sc->device == sdev) {
            removeQ(c);
            c->stat = CMD_STAT_CANCELED;
            addQ(&handleQ, c);
            h->io_running--;
        }
    }
    spin_unlock_bh(&h->lock);

    list_for_each_safe(pos, next, &handleQ) {
        c = list_entry(pos, struct vsc_cmnd_list, list);
        removeQ(c);
        vsc_cmd_get(c);
        callback(h, c, VSC_LIST_COMQ);
        vsc_cmd_put(c);
    }

    /* ѭ������rspQ������ָ�����scsi���� */
    spin_lock_bh(&h->lock);
    list_for_each_safe(pos, next, &h->rspQ) {
        c = list_entry(pos, struct vsc_cmnd_list, list);
        temp_sc = c->scsi_cmd;
        if (temp_sc->device == sdev) {
            removeQ(c);
            c->stat = CMD_STAT_CANCELED;
            addQ(&handleQ, c);
            h->io_running--;
        }
    }
    spin_unlock_bh(&h->lock);

    list_for_each_safe(pos, next, &handleQ) {
        c = list_entry(pos, struct vsc_cmnd_list, list);
        removeQ(c);
        vsc_cmd_get(c);
        callback(h, c, VSC_LIST_RSPQ);
        vsc_cmd_put(c);
    }

    return 0;
}

/**************************************************************************
 ��������  : abort������еĻص�����
 ��    ��  : struct vsc_ctrl_info *h  host���ƾ��
             vsc_cmnd_list *c         scsi������ƾ��
             list_type                ����������������
 �� �� ֵ  : ��
**************************************************************************/
static void vsc_abort_cmd_callback(struct vsc_ctrl_info *h, struct vsc_cmnd_list *c, enum queue_type list_type)
{
    struct scsi_cmnd *sc = NULL;

    if (unlikely(!c) || unlikely(!h) ) {
        return;
    }
    
    //vsc_err("Abort command, ");
    switch (list_type) {
    case VSC_LIST_REQQ:
        vsc_err_limit("Abort host:%u reqQ: sn:%u, stat = %u\n", vsc_ctrl_get_host_no(h), c->cmd_sn, c->stat);
        h->Qdepth--;
        break;
    case VSC_LIST_COMQ:
        vsc_err_limit("Abort host:%u cmpQ: sn:%u, stat = %u\n", vsc_ctrl_get_host_no(h), c->cmd_sn, c->stat);
        break;
    case VSC_LIST_RSPQ:
        vsc_err_limit("Abort host:%u rspQ: sn:%u, stat = %u\n", vsc_ctrl_get_host_no(h), c->cmd_sn, c->stat);
        break;
    default:
        break;
    }
    sc = c->scsi_cmd;
    if (!sc)
    {
        vsc_err("fatal error, host:%u sn:%u, stat = %u\n", vsc_ctrl_get_host_no(h), c->cmd_sn, c->stat);
        vsc_cmd_put(c);
        return;
    }

    sc->result = DID_SOFT_ERROR << 16;
    /* ֪ͨ�ϲ������������ */
    sc->scsi_done(sc);

    /* �ͷ��������� */
    vsc_cmd_put(c);

    return;
}


/**************************************************************************
 ��������  : �˳�����scsi����Ĵ���
 ��    ��  : struct vsc_ctrl_info *h  host���ƾ��
 �� �� ֵ  : 0: �ɹ�, ����: scsi�в������
**************************************************************************/
static int vsc_abort_all_cmd(struct vsc_ctrl_info *h)
{
    if (unlikely(!h) ) {
        return -EINVAL;
    }

    return vsc_each_queue_remove(h, vsc_abort_cmd_callback);
}

static int vsc_abort_all_cmd_by_device(struct vsc_ctrl_info *h, struct scsi_cmnd *sc)
{
    if (unlikely(!h) ) {
        return -EINVAL;
    }

    return vsc_each_queue_remove_by_device(h, vsc_abort_cmd_callback, sc);
}

/**************************************************************************
 ��������  : abort������еĻص�����
 ��    ��  : struct vsc_ctrl_info *h  host���ƾ��
             vsc_cmnd_list *c         scsi������ƾ��
             list_type                ����������������
 �� �� ֵ  : ��
**************************************************************************/
static void vsc_requeue_cmd_callback(struct vsc_ctrl_info *h, struct vsc_cmnd_list *c, enum queue_type list_type)
{
    struct scsi_cmnd *sc = NULL;

    //printk("Requeue command, ");
    switch (list_type) {
    case VSC_LIST_REQQ:
        vsc_err_limit("Requeue host:%u reqQ: sn:%u, stat = %u\n", vsc_ctrl_get_host_no(h), c->cmd_sn, c->stat);
        h->Qdepth--;
        break;
    case VSC_LIST_COMQ:
        vsc_err_limit("Requeue host:%u cmpQ: sn:%u, stat = %u\n", vsc_ctrl_get_host_no(h), c->cmd_sn, c->stat);
        break;
    case VSC_LIST_RSPQ:
        vsc_err_limit("Requeue host:%u rspQ: sn:%u, stat = %u\n", vsc_ctrl_get_host_no(h), c->cmd_sn, c->stat);
        break;
    default:
        break;
    }

    sc = c->scsi_cmd;
    if (!sc)
    {
        vsc_err("fatal error, host:%u sn:%u, stat = %u\n", vsc_ctrl_get_host_no(h), c->cmd_sn, c->stat);
        vsc_cmd_put(c);
        return;
    }

    sc->result = DID_REQUEUE << 16;
    /* ��Ӧ�����ʽΪ��������� */
    sc->scsi_done(sc);

    /* �ͷ��������� */
    vsc_cmd_put(c);

    return;
}

/**************************************************************************
 ��������  : ���½��������������� 
 ��    ��  : vsc_cmnd_list *c         scsi������ƾ��
 �� �� ֵ  : 0: �ɹ�, ����: scsi�в������
**************************************************************************/
static int vsc_requeue_all_cmd(struct vsc_ctrl_info *h)
{
    if (unlikely(!h) ) {
        return -EINVAL;
    }

    return vsc_each_queue_remove(h, vsc_requeue_cmd_callback);
}

static int vsc_requeue_all_cmd_by_device(struct vsc_ctrl_info *h, struct scsi_cmnd *sc)
{
    if (unlikely(!h) ) {
        return -EINVAL;
    }

    return vsc_each_queue_remove_by_device(h, vsc_requeue_cmd_callback, sc);
}

/**************************************************************************
 ��������  : abort�¼��ص�����
 ��    ��  : vsc_ctrl_info *h            host���ƾ��
             enum event_type type        �¼���Ӧ����
             vsc_event_list *e           �¼�ָ��
             data_type                   �¼���������
             data                        ������ָ��
             data_len                    �¼����ݳ���
 �� �� ֵ  : 0: �ɹ�, ����: ������
**************************************************************************/
static int vsc_abort_event_callback(struct vsc_ctrl_info *h, enum event_type type,
                    struct vsc_event_list *e, int data_type, void *data, int data_len)
{
    struct vsc_event_result *abort_rsp;
    /* �����ʱ�����������ͷ��¼����򷵻�SUCCESS*/
    if (EVENT_TIMEOUT == type || EVENT_ABORT == type) {
        spin_lock_bh(&h->lock);
        if (!h->file) {
            /* ���hostû�б��ӹܣ��򷵻�SUCCESS��֪ͨSCSI�ϲ����� */
            e->event_priv = SUCCESS;
        }
        /* <zr> ���������host�Ǳ��ӹ��˵�, ��ʱ��ֱ�Ӹ�ML��abortʧ��? */
        spin_unlock_bh(&h->lock);
        return 0;
    }

    // [zr] EVENT_SHOOT == type, when go here, that means triggered by user write event rsp.
    if (VSC_EVENT_TYPE_ABORT != data_type) {
        vsc_err("abort event data type is invalid, host is %u, type is %d\n", 
            vsc_ctrl_get_host_no(h), data_type);
        return -EINVAL;
    }

    abort_rsp = data;
    
    /* ���������Ч�� */
    if (data_len != sizeof(*abort_rsp)) {
        return -EINVAL;
    }

    if (abort_rsp->result) {
        vsc_err("abort event failed, host is %u, result is %u\n", 
            vsc_ctrl_get_host_no(h), abort_rsp->result);
        e->event_priv = FAILED;
    } else {
        e->event_priv = SUCCESS;
    }

    return 0;
}

/**************************************************************************
 ��������  : scsi�в�abort�ص�����
 ��    ��  : struct scsi_cmnd *scsicmd  scsi�в�����
 �� �� ֵ  : 0: �ɹ�, ����: scsi�в������
**************************************************************************/
static int vsc_eh_abort(struct scsi_cmnd *sc)
{
    struct vsc_ctrl_info *h = NULL;
    struct vsc_cmnd_list *c = NULL;
    struct vsc_event_list *e = NULL;
    int result = 0;
    struct vsc_event_abort event_abort;

    c = sc_to_cmnd_list(sc);
    if (!c) {
        vsc_err_limit("vsc abort: Get cmnd list failed.maybe it was freed by scsi_done\n");
        scsi_print_command(sc);
        return SUCCESS;
    }

    /* ��ȡ�������ü��� */
    vsc_cmd_get(c);
    h = c->h;
    h->stat.abort_cmd_count++;
    spin_lock_bh(&h->lock);
    e = vsc_event_alloc(h);
    spin_unlock_bh(&h->lock);
    if (!e) {
        /* ������������ */
        vsc_cmd_put(c);  
        /* [zr] ���ﲻ��Ҫ���������ͷŵ���? ������ʱ��target��û��abort������� */
        return FAILED;
    }

    event_abort.cmd_sn = c->cmd_sn;
    /* io�п��ܱ��ַ��ǹ���host������event��Ҫ�ַ���ʵ�ʵ�host������ǰhost */
    //event_abort.host = sc->device->host->host_no;
    event_abort.host = vsc_ctrl_get_host_no(h);
    event_abort.channel = sc->device->channel;
    event_abort.id = sc->device->id;
    event_abort.lun = sc->device->lun;

    vsc_err_limit("add abort_command event host:%u/%u channel:%u id:%u lun:%u cmd_sn:%d event_sn:%d tag:%d\n",
            vsc_ctrl_get_host_no(h), event_abort.host, event_abort.channel,
            event_abort.id, event_abort.lun, event_abort.cmd_sn, e->event_sn, e->event_index);

    /* ����¼�������event˽��������Ϊ����ֵ*/
    vsc_event_add(e, vsc_abort_event_callback, VSC_EVENT_TYPE_ABORT, 
                    &event_abort, sizeof(event_abort), FAILED);

    /* �ȴ�15s */
    vsc_event_wait_timeout(e, HZ * VSC_ABORT_EVENT_WAIT_TIME);

    /* ���ɹ�ABORT�����ͷŶ�Ӧ����Ϣ */
    if (SUCCESS == e->event_priv) {
        
        /* ���������¼���������ԣ�������ʧ�ܣ���ֱ�ӷ��ش��� */
        spin_lock_bh(&h->lock);
        if (unlikely(!list_empty(&c->list))) { /* <zr> Ϊʲô���зǿ���unlikely? */
            
            /* �����������ɾ������ */
            removeQ(c);
            h->io_running--;
            spin_unlock_bh(&h->lock);
            
            /* �ͷ��������� */
            vsc_cmd_put(c);
            
            /* <zr> �����в���δ����ٷ���, ��Ҫ�ٿ����� */
            sc->result = DID_ABORT << 16;
            sc->scsi_done(sc);
        } else {
            spin_unlock_bh(&h->lock);
        }
    } else {
        vsc_err("abort command sn:%u failed, host:%u\n", event_abort.cmd_sn, 
            vsc_ctrl_get_host_no(h));
    }
    result = e->event_priv;
    vsc_event_del(e);
    vsc_cmd_put(c);
    
    /* [zr] ���result��SUCCESS���в�����Ը�����,
        �����SUCCESS����ô�в��Դ��������δ���? ������������������������ô����? 
        --�ȴ������в�Ĵ����� */
    return result;
}

/**************************************************************************
 ��������  : reset dev�¼��ص�����
 ��    ��  : vsc_ctrl_info *h            host���ƾ��
             enum event_type type        �¼���Ӧ����
             vsc_event_list *e           �¼�ָ��
             data_type                   �¼���������
             data                        ������ָ��
             data_len                    �¼����ݳ���
 �� �� ֵ  : 0: �ɹ�, ����: ������
**************************************************************************/
static int vsc_reset_dev_event_callback(struct vsc_ctrl_info *h, enum event_type type,
                     struct vsc_event_list *e, int data_type, void *data, int data_len)
{
    struct vsc_event_result *reset_rsp;
    /* �����ʱ�����������ͷ��¼����򷵻�SUCCESS*/
    if (EVENT_TIMEOUT == type || EVENT_ABORT == type) {
        spin_lock_bh(&h->lock);
        if (!h->file) {
            /* ���hostû�б��ӹܣ��򷵻�SUCESS��֪ͨSCSI�ϲ����� */
            e->event_priv = SUCCESS;
        }
        spin_unlock_bh(&h->lock);
        return 0;
    }

    if (VSC_EVENT_TYPE_RESET_DEV != data_type) {
        vsc_err("reset device data type is invalid, host is %u, type is %d\n", 
                vsc_ctrl_get_host_no(h), data_type);
        return -EINVAL;
    }

    reset_rsp = data;
    
    /* ���������Ч�� */
    if (data_len != sizeof(*reset_rsp)) {
        return -EINVAL;
    }

    if (reset_rsp->result) {
        vsc_err("reset device failed, host is %u, result is %u\n", 
            vsc_ctrl_get_host_no(h), reset_rsp->result);
        e->event_priv = FAILED;
    } else {
        e->event_priv = SUCCESS;
    }

    return 0;       
}

/**************************************************************************
 ��������  : scsi�в㸴λ�ص�����
 ��    ��  : struct scsi_cmnd *scsicmd  scsi�в�����
 �� �� ֵ  : 0: �ɹ�, ����: scsi�в������
**************************************************************************/
static int vsc_eh_device_reset_handler(struct scsi_cmnd *sc)
{
    struct vsc_ctrl_info *h = NULL;
    struct vsc_cmnd_list *c = NULL;
    struct vsc_event_list *e = NULL;
    int result = 0;
    struct vsc_event_reset_dev event_reset;
    struct vsc_host_mgr *silbing_hosts = NULL;
    int i = 0;

    c = sc_to_cmnd_list(sc);
    if (!c) {
        vsc_err_limit("vsc reset dev: Get cmnd list failed.maybe it was freed by scsi_done\n");
        scsi_print_command(sc);
        return SUCCESS;  /* interal retval, 0x2003 */
    }
    /* ��ȡ�������ü��� */
    vsc_cmd_get(c);

    h = c->h;
    h->stat.reset_dev_count++;
    spin_lock_bh(&h->lock);
    e = vsc_event_alloc(h);
    spin_unlock_bh(&h->lock);
    if (!e) {
        /* ������������ */
        vsc_cmd_put(c);
        /* [zr] ����Ҫ�ͷŸ�������? */
        return FAILED;
    }

    silbing_hosts = h->silbing_hosts;
    
    event_reset.cmd_sn = c->cmd_sn;
    /* io�п��ܱ��ַ��ǹ���host������event��Ҫ�ַ���ʵ�ʵ�host������ǰhost */
    //event_reset.host = sc->device->host->host_no;
    event_reset.host = vsc_ctrl_get_host_no(h);
    event_reset.channel = sc->device->channel;
    event_reset.id = sc->device->id;
    event_reset.lun = sc->device->lun;

    vsc_err_limit("add reset_host event host:%u/%u channel:%u id:%u lun:%u cmd_sn:%d event_sn:%d\n",
            vsc_ctrl_get_host_no(h), h->scsi_host->host_no, event_reset.channel,
            event_reset.id, event_reset.lun, event_reset.cmd_sn, e->event_sn);

    /* ����¼�������event˽��������Ϊ����ֵ��Ĭ�Ϸ��سɹ�*/
    vsc_event_add(e, vsc_reset_dev_event_callback, VSC_EVENT_TYPE_RESET_DEV, 
                    &event_reset, sizeof(event_reset), FAILED);

    /* �ȴ�30s */
    vsc_event_wait_timeout(e, HZ * VSC_RESET_EVENT_WAIT_TIME);
    result = e->event_priv;

    h = c->h;
    vsc_err("device reset, host is %u, result is %X\n", vsc_ctrl_get_host_no(h), result);

    /* <zr> ����ֻ��device reset handler, Ϊʲô������host�µ�cmd��eventȫ�����ͷ���, 
        ������ֻ�ͷŸ����lun device��ص���Դ?? */
    /* ���۳ɹ���񣬶������ͷ����е���Դ */
    /* <liaodf> �ĳɶ��̺߳�io���ַ����host�����resetֻ�ͷŵ�ǰhost��io�����ɹ���
       �в������scmd�ͷţ�����host�Ĳ���io�ͻ�����⣻���Ա�������vbs������host*/
    /* <liaodf 20151225>����device resetʵ�����൱��host reset���Ѹ�vbs������io���ͷŵ���
       �޸��߼�Ϊdevice reset��ֻ�������ioͬһ�����ϵ�io */
    if (SUCCESS == e->event_priv) {
        /* ��������������ӣ��ͷŶ�Ӧ����Դ */
        for (i=0; i<silbing_hosts->host_count; i++) {
            vsc_requeue_all_cmd_by_device(silbing_hosts->host_list[i], sc);
        }
    } else {
        /* �ͷ���������ͷŶ�Ӧ����Դ */
        for (i=0;i<silbing_hosts->host_count;i++) {
            vsc_abort_all_cmd_by_device(silbing_hosts->host_list[i], sc);
        }
    }

    vsc_event_del(e);
    vsc_cmd_put(c);  /* [zr] ������cmd�ᱻ�ͷŵ� */ 

    return result;   
}

/**************************************************************************
 ��������  : �ӹ�scsi target
 ��    ��  : svsc_ctrl_info *h:     host���ƾ��
             struct file *file      �����ļ�
             task                   ������Ϣ
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
int vsc_scsi_attach(struct vsc_ctrl_info *h, struct file *file,  struct task_struct *task)
{
    if (!h) {
        return -EFAULT;
    }

    if (!file) {
        return -EFAULT;
    }

    spin_lock_bh(&h->lock);
    if (h->file) {
        spin_unlock_bh(&h->lock);
        return -EBUSY;
    }

    /* �����ʱ���������� ��������*/ 
    /* [zr] vsc_target_abnormal() is running */
    if (atomic_inc_return(&h->target_abnormal_lock) > 1) {
        atomic_dec(&h->target_abnormal_lock);
        spin_unlock_bh(&h->lock);
        return -EAGAIN;
    } 
    
    del_timer_sync(&h->target_abnormal_timer);
    
    h->file = file;
    spin_unlock_bh(&h->lock);

    if (!h->suspend) {
        vsc_resume_host(h);
    }
    
    atomic_dec(&h->target_abnormal_lock);

    return 0;
}

/**************************************************************************
 ��������  : ���߼�غ���
 ��    ��  : unsigned long arg  ��غ�������                    
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
void vsc_target_abnormal(unsigned long arg)
{
    struct vsc_ctrl_info *h = (struct vsc_ctrl_info *)arg;
    struct scsi_device *sdev = NULL;

    if (unlikely(!h)) {
        return;
    }    
        
    if (atomic_inc_return(&h->target_abnormal_lock) > 1) {
        atomic_dec(&h->target_abnormal_lock);
        vsc_info("host[%u] may be attaching\n", vsc_ctrl_get_host_no(h));
        return;
    }

    vsc_info("offline abnormal host[%u], timeout:%us\n", vsc_ctrl_get_host_no(h), h->target_abnormal_time);

    /* ��ֹɾ��ʱ�����������豸 */
    vsc_resume_host(h);

    /* ���������ڴ����е��¼� */
    vsc_abort_all_event(h);
  
    /* ������������ */
    vsc_abort_all_cmd(h);

    /* ������host�´��̶�����Ϊ���� */
    shost_for_each_device(sdev, h->scsi_host) {
        scsi_device_set_state(sdev, SDEV_OFFLINE);
    }

    atomic_dec(&h->target_abnormal_lock);
   
    return;
}

/**************************************************************************
 ��������  : ȡ���ӹ�scsi target
 ��    ��  : struct vsc_ctrl_info *h:         host���ƾ��
             int is_timeout                   �Ƿ����ö�ʱ�� 0 ��ʾ������ 1 ��ʾ����
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
int vsc_scsi_detach(struct vsc_ctrl_info *h, int is_timeout)
{
    int retval = 0;

    if (!h) {
        return -EFAULT;
    }

    spin_lock_bh(&h->lock);
    if (!h->file) {
        spin_unlock_bh(&h->lock);
        return -EPERM;
    }

    h->file = NULL;
    spin_unlock_bh(&h->lock);

    /* ��������IO���·� */
    scsi_block_requests(h->scsi_host);
    
    /* �ͷ����е��¼����� */
    retval = vsc_abort_all_event(h);
    if (retval < 0) {
        return retval;
    }

    /* �������е��������¼��뵽scsi�в����� */
    retval = vsc_requeue_all_cmd(h);
    if (retval < 0) {
        return retval;
    }

    /* ����û�̬����������read����������֪ͨ�˳� */
    if (waitqueue_active(&h->queue_wait)) {
        wake_up_interruptible(&h->queue_wait);
    }

    // Modified by z00108977  for DTS2012091802520
    if (is_timeout) {
        /* �����target�쳣���µ�detach, ������suspend��־, ���������û���Ҫ�Լ�����resume */
        h->suspend = 1;

        if (h->target_abnormal_time > 0) {
            /* �����붨ʱ�� */
            mod_timer(&h->target_abnormal_timer, h->target_abnormal_time * HZ + jiffies);
            vsc_dbg("Startup timer, timeout:%us, host_no:%u\n", h->target_abnormal_time, vsc_ctrl_get_host_no(h));
        }
    }

    return 0;
}

/**************************************************************************
 ��������  : �ı�������
 ��    ��  : struct scsi_device *sdev      scsi�豸���
             int qdepth                    ���
 �� �� ֵ  : 0: �ɹ���������������
**************************************************************************/
/* [zr] ����ص���������ʲôʱ�򱻵��õ�?  
  --��scsi_add_lun��ʱ��ע���device_attribute, ��echo 255 > /sys/block/sdx/device/queue_depth��ʱ�����
  Ҳ�����ڷ���struct sysfs_ops��store����ʱ������ */

#if (LINUX_VERSION_CODE < KERNEL_VERSION(2, 6, 32))
static int vsc_change_queue_depth(struct scsi_device *sdev, int qdepth)
#else
static int vsc_change_queue_depth(struct scsi_device *sdev, int qdepth, int reason)
#endif
{
    struct vsc_ctrl_info *h = sdev_to_ctrl_info(sdev);

    if (unlikely(!h)) {
        return -EFAULT;
    }

#if (LINUX_VERSION_CODE >= KERNEL_VERSION(2, 6, 32))
    if (reason != SCSI_QDEPTH_DEFAULT) {
        return -ENOTSUPP;
    }
#endif

    if (qdepth < 1) {
        qdepth = 1;
    } else {
        if (qdepth > h->nr_cmds) {
            qdepth = h->nr_cmds;
        }
    }

    scsi_adjust_queue_depth(sdev, scsi_get_tag_type(sdev), qdepth);
    return (int)(sdev->queue_depth);
}

/* [zr] slave_alloc <- scsi_alloc_sdev <- scsi_probe_and_add_lun <- 
   __scsi_add_device <- scsi_add_device */
static int vsc_slave_alloc(struct scsi_device *sdev)
{
    set_bit(QUEUE_FLAG_BIDI, &sdev->request_queue->queue_flags);
    return 0;
}

/* [zr] slave_configure <- scsi_add_lun <- scsi_probe_and_add_lun <- 
   __scsi_add_device <- scsi_add_device */
static int vsc_slave_configure(struct scsi_device *sdev)
{
    blk_queue_bounce_limit(sdev->request_queue, BLK_BOUNCE_ANY);
    blk_queue_dma_alignment(sdev->request_queue, 0);

    return 0;
}

/**
 * vsch_bios_param - fetch head, sector, cylinder info for a disk
 * @sdev: scsi device struct
 * @bdev: pointer to block device context
 * @capacity: device size (in 512 byte sectors)
 * @params: three element array to place output:
 *              params[0] number of heads (max 255)
 *              params[1] number of sectors (max 63)
 *              params[2] number of cylinders
 *
 * Return nothing.
 */
static int
vsch_bios_param(struct scsi_device *sdev, struct block_device *bdev,
                sector_t capacity, int params[])
{
    int        heads;
    int        sectors;
    sector_t    cylinders;
    ulong         dummy;

    heads = 64;
    sectors = 32;

    dummy = heads * sectors;
    cylinders = capacity;
    sector_div(cylinders, dummy);

    /*
     * Handle extended translation size for logical drives
     * > 1Gb
     */
    if ((ulong)capacity >= 0x200000) {
        heads = 255;
        sectors = 63;
        dummy = heads * sectors;
        cylinders = capacity;
        sector_div(cylinders, dummy);
    }

    /* return result */
    params[0] = heads;
    params[1] = sectors;
    params[2] = cylinders;

    return 0;
}

/**
 *    vsc scsi host template
 **/
static struct scsi_host_template vsc_driver_template = {
    .module                   = THIS_MODULE,
    .name                     = "vsc",
    .proc_name                = "vsc",
    .queuecommand             = vsc_scsi_queue_command,
    .this_id                  = -1,
    .can_queue                = 1,
    .max_sectors              = 8192,
    .sg_tablesize             = 128,
    .use_clustering            = ENABLE_CLUSTERING,
    .bios_param               = vsch_bios_param,
    .eh_abort_handler         = vsc_eh_abort,
    .eh_device_reset_handler  = vsc_eh_device_reset_handler,
    .change_queue_depth       = vsc_change_queue_depth,
    .slave_alloc              = vsc_slave_alloc,
    .slave_configure          = vsc_slave_configure,
    .scan_finished            = vsc_scan_finished,
    .scan_start               = vsc_scan_start,
};

static struct scsi_device *__vsc_scsi_device_lookup(struct Scsi_Host *shost,
        uint channel, uint id, uint lun)
{
    struct scsi_device *sdev;

    list_for_each_entry(sdev, &shost->__devices, siblings) {
        if (sdev->channel == channel && sdev->id == id &&
                sdev->lun ==lun && sdev->sdev_state != SDEV_DEL)
            return sdev;
    }

    return NULL;
}

static struct scsi_device *__vsc_scsi_device_lookup_by_vol_name(struct Scsi_Host *shost,
                                                                char *vol_name)
{
    struct scsi_device *sdev;
    struct vsc_scsi_device_resrve_data *sdev_reserve_data = NULL;
    
    list_for_each_entry(sdev, &shost->__devices, siblings) {
       sdev_reserve_data = (struct vsc_scsi_device_resrve_data *) &(sdev->sdev_data[0]); 
       if (NULL == sdev_reserve_data) {
           continue;
       }
       if (!strncmp(sdev_reserve_data->disk_vol.vol_name, vol_name, VSC_VOL_NAME_LEN)) {
            return sdev;
       }
    }
    return NULL;
}

static struct scsi_device *vsc_scsi_device_lookup(struct Scsi_Host *shost,
        uint channel, uint id, uint lun)
{
    struct scsi_device *sdev;
    unsigned long flags;

    spin_lock_irqsave(shost->host_lock, flags);
    sdev = __vsc_scsi_device_lookup(shost, channel, id, lun);
    if (sdev && scsi_device_get(sdev))
        sdev = NULL;
    spin_unlock_irqrestore(shost->host_lock, flags);

    return sdev;
}

static struct scsi_device *vsc_scsi_device_lookup_by_vol_name(struct Scsi_Host *shost, char *vol_name)
{
    struct scsi_device *sdev;
    unsigned long flags;

    spin_lock_irqsave(shost->host_lock, flags);
    sdev = __vsc_scsi_device_lookup_by_vol_name(shost, vol_name);
    if (sdev && scsi_device_get(sdev))
        sdev = NULL;
    spin_unlock_irqrestore(shost->host_lock, flags);

    return sdev;
}

/**************************************************************************
 ��������  : ��host�����һ���豸
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             channel:  ͨ����
             id :      target id���
             lun :      lun���
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
int vsc_add_device(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun)
{
    struct Scsi_Host *sh = NULL;
    struct scsi_device *sdev = NULL;
    int error = 0;

    if (!h) {
        return -EINVAL;
    }

    /* ����Ӧ��HOST�Ƿ��Ѿ��ӹܣ����û�нӹܣ����ؽ�ֹ����*/
    if (!(h->file)) {
        return -EACCES;
    }

    sh = h->scsi_host;
    /* VBS ��������Ҫ��host Ϊsuspend ״̬ʱ������add device. */
//    /* ���host ��������״̬���򷵻�ʧ�� */
//    if (sh->host_self_blocked == 1) {
//        return -EBUSY;
//    }

    /* ����Ӧ���豸�Ƿ���� */
    sdev = vsc_scsi_device_lookup(sh, channel, id, lun);
    if (sdev) {
        scsi_device_put(sdev);
        return -EEXIST;
    }

    /* ��scsi�в�ע���豸 */
    error = scsi_add_device(sh, channel, id, lun); 
    if (error) {
        vsc_err("scsi_add_device() failed, device to be added: [%u %u %u %u], err=%d\n", 
            vsc_ctrl_get_host_no(h), channel, id, lun, error);
        return error;
    }
    
    vsc_info("Disk [%u %u %u %u] added success!\n", vsc_ctrl_get_host_no(h), channel, id, lun);
    return 0;
}

int vsc_add_device_by_vol_name(struct vsc_ctrl_info *h, unsigned int channel,
                               unsigned int id, unsigned int lun, char *vol_name)
{
    struct Scsi_Host *sh = NULL;
    struct scsi_device *sdev = NULL;
    struct vsc_scsi_device_resrve_data *sdev_reserve_data = NULL;
    int error = 0;

    if (!h || !vol_name) {
        return -EINVAL;
    }

    /* ����Ӧ��HOST�Ƿ��Ѿ��ӹܣ����û�нӹܣ����ؽ�ֹ����*/
    if (!(h->file)) {
        return -EACCES;
    }

    sh = h->scsi_host;
    /* VBS ��������Ҫ��host Ϊsuspend ״̬ʱ������add device. */
//    /* ���host ��������״̬���򷵻�ʧ�� */
//    if (sh->host_self_blocked == 1) {
//        return -EBUSY;
//    }

    /* ����Ӧ���豸�Ƿ���� */
    sdev = vsc_scsi_device_lookup(sh, channel, id, lun);
    if (sdev) {
        scsi_device_put(sdev);
        return -EEXIST;
    }

    /* ��scsi�в�ע���豸 */
    error = scsi_add_device(sh, channel, id, lun); 
    if (error) {
        vsc_err("scsi_add_device() failed, sdev [%u %u %u %u], err=%d\n", 
            vsc_ctrl_get_host_no(h), channel, id, lun, error);
        return error;
    }
    
    sdev = vsc_scsi_device_lookup(sh, channel, id, lun);
    if (!sdev) {
        return -ENODEV;
    }
    sdev_reserve_data = (struct vsc_scsi_device_resrve_data *) &(sdev->sdev_data[0]);
    sdev_reserve_data->head.magic = VSC_DATA_MAGIC;
    sdev_reserve_data->head.ver_major = VSC_DATA_VER_MAJOR;
    sdev_reserve_data->head.ver_minor = VSC_DATA_VER_MINOR;
    memcpy(sdev_reserve_data->disk_vol.vol_name, vol_name, VSC_VOL_NAME_LEN);
    sdev_reserve_data->disk_vol.state = VSC_DISK_RUNNING;
    sdev_reserve_data->disk_vol.host = sh->host_no;
    sdev_reserve_data->disk_vol.channel = sdev->channel;
    sdev_reserve_data->disk_vol.id = sdev->id;
    sdev_reserve_data->disk_vol.lun = sdev->lun;
    
    /* ��ʼ��ÿ�����io�����������ڶ��̼߳�ַ� */
    atomic64_set(&sdev_reserve_data->disk_io_count, 1);
    scsi_device_put(sdev);

    vsc_info("Disk [%u %u %u %u] volume(%s) added success!\n",
                vsc_ctrl_get_host_no(h), channel, id, lun, vol_name);
    return 0;
}

/**************************************************************************
 ��������  : ��host��ɾ��һ���豸
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             channel:  ͨ����
             id :      target id���
             lun :      lun���
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
int vsc_rmv_device(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun)
{
    struct Scsi_Host *sh = NULL;
    struct scsi_device *sdev = NULL;

    if ((!h) || (!h->scsi_host)) {
        vsc_err("input para is null [%u %u %u]\n",channel, id, lun);
        return -EINVAL;
    }

    sh = h->scsi_host;
    /* ���host ��������״̬���򷵻�ʧ�� */
    if (sh->host_self_blocked == 1) {
        return -EBUSY;
    }

    sdev = vsc_scsi_device_lookup(sh, channel, id, lun);
    if (!sdev) {
        vsc_err("lookup scsi device sdev failed [%u %u %u %u] \n",
            vsc_ctrl_get_host_no(h), channel, id, lun);
        return -ENODEV;
    }
#if (LINUX_VERSION_CODE == KERNEL_VERSION(3, 0, 93))
    sdev->is_visible = 1; /*avoid OS bug*/
#endif
    scsi_remove_device(sdev);
    vsc_info("disk [%u %u %u %u] removed!\n", vsc_ctrl_get_host_no(h), channel, id, lun);

    scsi_device_put(sdev);
    return 0;
}

int vsc_set_delete_by_vol_name(struct vsc_ctrl_info *h, char *vol_name)
{
    struct Scsi_Host *sh = NULL;
    struct scsi_device *sdev = NULL;
    struct vsc_scsi_device_resrve_data *sdev_reserve_data = NULL;

    if ((!vol_name) || (!h) || (!h->scsi_host)) {
        vsc_err("para is null, vol_name: %p, vsc_host: %p, scsi_host: %p\n",
                vol_name, h, h?h->scsi_host:NULL);
        return -EINVAL;
    }
    sh = h->scsi_host;

    sdev = vsc_scsi_device_lookup_by_vol_name(sh, vol_name);
    if (!sdev) {
        vsc_err("lookup scsi device failed, host_no: %u, vol_name: %s \n",
                vsc_ctrl_get_host_no(h), vol_name);
        return -ENODEV;
    }
    sdev_reserve_data = (struct vsc_scsi_device_resrve_data *) &sdev->sdev_data[0];

    sdev_reserve_data->disk_vol.state = VSC_DISK_PREPARE_DELETE;

    vsc_info("disk [host_no: %u volume(%s)] set to delete flag!\n",
                vsc_ctrl_get_host_no(h), vol_name);
    
    scsi_device_put(sdev);
    return 0;
}

void vsc_query_vol(struct vsc_ctrl_info *h, struct vsc_ioctl_query_vol *query_vol)
{
    struct Scsi_Host *shost = h->scsi_host;
    struct vsc_ioctl_disk_vol_name *des = &query_vol->volumes[0];
    struct vsc_scsi_device_resrve_data *sdev_reserve_data = NULL;
    struct scsi_device *sdev;
    unsigned long flags;

    query_vol->vol_num = 0;
    spin_lock_irqsave(shost->host_lock, flags);
    list_for_each_entry(sdev, &shost->__devices, siblings) {
       if (query_vol->vol_num >= VSC_MAX_DISK_PER_HOST) {
           vsc_info("vol_num[%u] is bigger than VSC_MAX_DISK_PER_HOST [512]\n", query_vol->vol_num);
           break;
       }
       sdev_reserve_data = (struct vsc_scsi_device_resrve_data*) &(sdev->sdev_data[0]); 
       if (sdev->sdev_state == SDEV_DEL)
       {
           vsc_info("maybe disk(%d,%d,%d,%d) state: %u have deleted but it's "
                   "refcount is not zero\n", sdev->host->host_no, sdev->channel,
                    sdev->id, sdev->lun, sdev->sdev_state);
           continue;
       }
       memcpy(des, &sdev_reserve_data->disk_vol, sizeof(*des));
       query_vol->vol_num++;
       des++;
    }
    spin_unlock_irqrestore(shost->host_lock, flags);
}

/**************************************************************************
 ��������  : ���ô���״̬
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             channel:  ͨ����
             id :      target id���
             lun :     lun���
             stat :    �豸״̬
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
int vsc_set_device_stat(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id,
                            unsigned int lun, enum scsi_device_state stat)
{
    struct Scsi_Host *sh = NULL;
    struct scsi_device *sdev = NULL;
    enum scsi_device_state oldstate;
    int retval = 0;

    if (!h) {
        return -EINVAL;
    }

    sh = h->scsi_host;
    sdev = vsc_scsi_device_lookup(sh, channel, id, lun);
    if (!sdev) {
        return -ENODEV;
    }

    
    /* ״̬��� */
    oldstate = sdev->sdev_state;
    switch (stat) {
    case SDEV_RUNNING:
        switch (oldstate) {
        case SDEV_CREATED:
        case SDEV_OFFLINE:
        case SDEV_QUIESCE:
        case SDEV_BLOCK:
            break;
        default:
            retval = -EINVAL;
            goto out;
        }
        break;
    case SDEV_OFFLINE:
        switch (oldstate) {
        case SDEV_CREATED:
        case SDEV_RUNNING:
        case SDEV_QUIESCE:
        case SDEV_BLOCK:
            break;
        default:
            retval = -EINVAL;
            goto out;
        }
        break;
    case SDEV_BLOCK:
        switch (oldstate) {
        case SDEV_RUNNING:
#if (LINUX_VERSION_CODE == KERNEL_VERSION(2, 6, 18))
        case SDEV_CREATED:
#else
        case SDEV_CREATED_BLOCK:
#endif
            break;
        default:
            retval = -EINVAL;
            goto out;
        }
        break;
    default:
        retval = -EINVAL;
        goto out;
    }

    retval = scsi_device_set_state(sdev, stat);
out:    
    scsi_device_put(sdev);

    return retval;
}

/**************************************************************************
 ��������  : ��ȡ����״̬ 
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             channel:  ͨ����
             id :      target id���
             lun :     lun���
             stat :    �豸״̬  
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
int vsc_get_device_stat(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun,  enum scsi_device_state *stat)
{
    struct Scsi_Host *sh = NULL;
    struct scsi_device *sdev = NULL;

    if (!h || !stat) {
        return -EINVAL;
    }

    sh = h->scsi_host;
    sdev = vsc_scsi_device_lookup(sh, channel, id, lun);
    if (!sdev) {
        vsc_err("scsi lookup dev [%u:%u:%u:%u] failed when get disk stat, return -ENODEV\n", 
            vsc_ctrl_get_host_no(h), channel, id, lun);
        return -ENODEV;
    }

    *stat = sdev->sdev_state;
    
    scsi_device_put(sdev);

    return 0;
}

/**************************************************************************
 ��������  : ����������г�ʱʱ��
 ��    ��  : sdev:    ��Ҫ���õ�scsi device
             timeout : ��ʱʱ��  
 �� �� ֵ  : ��
**************************************************************************/
static void vsc_blk_queue_rq_timeout(struct scsi_device *sdev, unsigned int timeout)
{
#if (LINUX_VERSION_CODE == KERNEL_VERSION(2, 6, 18))
    sdev->timeout = timeout;
#else
    sdev->request_queue->rq_timeout = timeout;
#endif
}

/**************************************************************************
 ��������  : ����������г�ʱʱ��
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             channel:  ͨ����
             id :      target id���
             lun :     lun���
             timeout : ��ʱʱ��  
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
int vsc_set_device_rq_timeout(struct vsc_ctrl_info *h, unsigned int channel, unsigned int id, unsigned int lun, int timeout)
{
    struct Scsi_Host *sh = NULL;
    struct scsi_device *sdev = NULL;

    if (!h) {
        return -EINVAL;
    }

    if (timeout <= 0 || timeout > VSC_RQ_MAX_TIMEOUT) {
        return -EINVAL;
    }

    sh = h->scsi_host;
    sdev = vsc_scsi_device_lookup(sh, channel, id, lun);
    if (!sdev) {
        return -ENODEV;
    }

    vsc_blk_queue_rq_timeout(sdev, timeout * HZ);
    
    scsi_device_put(sdev);

    return 0;
}

/**************************************************************************
 ��������  : ����target�����쳣��ʱʱ��
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             timeout : ��ʱʱ��  
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
int vsc_set_tg_abn_timeout(struct vsc_ctrl_info *h, __u32 timeout)
{
    if (!h) {
        return -EINVAL;
    }

    h->target_abnormal_time = timeout;

    return 0;
}


/**************************************************************************
 ��������  : ���û�̬�������ݵ��ں�
 ��    ��  : vsc_cmnd_list *c:     ����ָ��
             command_status        ����ִ�н��
 �� �� ֵ  : ��
**************************************************************************/
inline void vsc_sense_check(struct vsc_cmnd_list *c, __u32 command_status) 
{
    struct scsi_cmnd *sc = NULL;
    sc = c->scsi_cmd;

    /* <zr> ����Ĵ����֧���result��msg_byte��status_byte�������ǵ���, ��Щ��Ϣ�ڷ���
        DID_NO_CONNECT/DID_ERROR/DID_TIME_OUT/DID_SOFT_ERROR/DID_ERROR֮�󣬺���SCSI�в�
        ��sd��Ͳ�����Ҫ�������? */
    switch (command_status) {
    case CMD_SUCCESS:
        break;
    case CMD_FAILURE:
        break;
    case CMD_INVALID:
        vsc_err_limit("sense, invalid command.\n");
        sc->result = DID_NO_CONNECT << 16;
        break;
    case CMD_CONNECTION_LOST:
        sc->result = DID_ERROR << 16;
        vsc_err_limit("connection lost error.\n");
        break;
    case CMD_TIMEOUT:
        sc->result = DID_TIME_OUT << 16;
        vsc_err_limit("timedout\n");
        break;
    case CMD_PROTOCOL_ERR:
        sc->result = DID_SOFT_ERROR << 16;
        vsc_err_limit("unknown error: (CMD_PROTOCOL_ERR).\n");
        break;
    case CMD_NEED_RETRY:
        sc->result = DID_REQUEUE << 16;
        break;
    default:
        sc->result = DID_ERROR << 16;
        vsc_err_limit("unknown command status\n");
        break;
    }
}

/**************************************************************************
 ��������  : �û�̬��vsc��ȡ���scsi cmd��cdb���ݣ����16��
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             user_ptr              �û�̬��Ӧ����ָ��
             len                   ���ݳ���
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/

struct vsc_msg_cdb
{
    struct vsc_scsi_msg smsg;
    char cdb[MAX_CDB_LENGTH];
};

static ssize_t vsc_get_multi_scsi_cmd_and_cdb(struct vsc_ctrl_info *h, char  __user *  user_ptr, int len)
{
    struct vsc_cmnd_list *c = NULL;
    struct vsc_cmnd_list *c_arr[MAX_BATCH_SCSI_CMD_COUNT] = {NULL};
    struct vsc_msg_cdb smsg_cdb[MAX_BATCH_SCSI_CMD_COUNT];
    struct scsi_cmnd *sc[MAX_BATCH_SCSI_CMD_COUNT] = {NULL};
    int count = 0;
    int index = 0;
    int left_count = 0;
    int retval = 0;

    if (unlikely(!h)) {
        return -EFAULT;
    }

    if (unlikely(len != MAX_SCSI_MSG_AND_CDB_LENGTH)) {
        vsc_err("%s():%d expect_len %d actual_len %u \n", __FUNCTION__, __LINE__,
            (int)MAX_SCSI_MSG_AND_CDB_LENGTH, len);
        return -EINVAL;
    }

    spin_lock_bh(&h->lock);
    if (unlikely(list_empty(&h->cmpQ))) {
        spin_unlock_bh(&h->lock);
        retval = -ENODATA;
        goto errout;
    }

    while (!list_empty(&h->cmpQ)) {
        c = list_first_entry(&h->cmpQ, struct vsc_cmnd_list, list);

        /* �Ӷ�ȡ������������ɾ������ */
        removeQ(c);
        
        /* ��ӵ��ȴ���ɶ��� */
        addQ(&h->rspQ, c);
        
        /* ͨ�����ݰ�c��¼������������ķ�ʽ�����DTS2015101408787���� */
        c_arr[count] = c;

        count++;
        if (count >= MAX_BATCH_SCSI_CMD_COUNT) {
            /* һ����ഫ��MAX_BATCH_SCSI_CMD_COUNT������ */
            break;
        }
    }

    h->get_cmd_times++;
    h->get_cmd_total += count;

    left_count = list_size(&h->cmpQ);
    spin_unlock_bh(&h->lock);

    /* 
       �������ݴ��������У�Ҳ�п���ͬʱ����device reset����Ȼ�������vbs��������ʱ�����и����صĺ��;
       ��Ϊ�����Ѿ��������������Ƴ�������������Ҳ�����������쳣��ֹ��������ϲ�ǰ�İ汾Ҳ������������ 
     */
    for (index = 0; index < count; index++) {
        c = c_arr[index];
        sc[index] = c->scsi_cmd;

        /* �޸�״̬Ϊ�ȴ���ɣ�ֱ����״̬�����ٱ������в����������������ʧ���������� */
        c->stat = CMD_STAT_READ_COMP;

    #ifdef __VSC_LATENCY_DEBUG__
        if (vsc_is_write_cmd(sc[index]->cmnd[0])) {
            h->write_cmd_count++;
            c->get_scmd_time = vsc_get_usec();
            h->write_stage1_total += c->get_scmd_time - c->start_queue_time;
        }
        else if (vsc_is_read_cmd(sc[index]->cmnd[0])) {
            h->read_cmd_count++;
            c->get_scmd_time = vsc_get_usec();
            h->read_stage1_total += c->get_scmd_time - c->start_queue_time;
        }
    
        if (vsc_is_readwrite_cmd(sc[index]->cmnd[0])) {
            if (c->get_scmd_time > c->start_queue_time && c->get_scmd_time - c->start_queue_time > 2000000) {
                vsc_err("too long in queue, host(%d) cmd_sn(%d) tag(%d) start_queue(%llu) get_scmd(%llu)",
                        vsc_ctrl_get_host_no(h), c->cmd_sn, c->cmd_index,
                        c->start_queue_time, c->get_scmd_time);
            }
        }
    #endif

        /* �������ݵ��û�̬ */
        smsg_cdb[index].smsg.type = VSC_MSG_TYPE_SCSI_CMD;
        smsg_cdb[index].smsg.cmd_sn = c->cmd_sn;
        smsg_cdb[index].smsg.tag = c->cmd_index;
        //smsg_cdb[index].smsg.host = sc[index]->device->host->host_no;
        smsg_cdb[index].smsg.host = vsc_ctrl_get_host_no(h);
        smsg_cdb[index].smsg.channel = sc[index]->device->channel;
        smsg_cdb[index].smsg.id = sc[index]->device->id;
        smsg_cdb[index].smsg.lun = sc[index]->device->lun;
        smsg_cdb[index].smsg.direction = sc[index]->sc_data_direction;
    #if (LINUX_VERSION_CODE == KERNEL_VERSION(2, 6, 18))
        memcpy(smsg_cdb[index].cdb, sc[index]->cmnd, COMMAND_SIZE(sc[index]->cmnd[0]));
    #else
        memcpy(smsg_cdb[index].cdb, sc[index]->cmnd, scsi_command_size(sc[index]->cmnd));
    #endif
    }

    /* �ڵ�һ����Ϣ�б�ʾʵ�ʷ���cmd���� */
    smsg_cdb[0].smsg.reserved[0] = count;
    smsg_cdb[0].smsg.reserved[1] = left_count;

    /* ������Ϣͷ */  /* 40 Bytes */
    if (copy_to_user(user_ptr, smsg_cdb, sizeof(struct vsc_msg_cdb) * count)) {
        vsc_err("Get cmd: copy msg head failed, host is %u, count = %d.\n", vsc_ctrl_get_host_no(h), count);
        retval = -EFAULT;
        goto errout;
    }

    /* ������Ϣ */
    if (unlikely(VSC_TRACE_REQ_SCSI_CMD & trace_switch)) {
        for (index = 0; index < count; index++) {
            vsc_err("[%d:%d:%d:%d] sn:%u tag:%d  direct:%u  sg_count:%u  sg_len:%u",
                    smsg_cdb[index].smsg.host, smsg_cdb[index].smsg.channel, smsg_cdb[index].smsg.id, smsg_cdb[index].smsg.lun,
                    smsg_cdb[index].smsg.cmd_sn, smsg_cdb[index].smsg.tag, smsg_cdb[index].smsg.direction,
                    scsi_sg_count(sc[index]), scsi_bufflen(sc[index]));
            scsi_print_command(sc[index]);
        }
    }

    return sizeof(struct vsc_msg_cdb) * count;

errout:
    /* ��Ϣδ��ȡ�ߣ����¼�����У���������ԭ˳��Ż�cmpQ���޷���ȫ��֤����Ϊ�µ�io������cmpQ�Ϸ� */
    if (count > 0) {
        spin_lock_bh(&h->lock);
        for (index = 0; index < count; index++) {
            c = c_arr[index];
            c->stat = CMD_STAT_REQUEST;
            /* �Ӷ�ȡ������������ɾ������ */
            removeQ(c);
            /* �ŵ�ͷ������Ϊ�Ǵ�ͷ��ȡ����������֤ԭ˳�� */
            list_add(&c->list, &h->cmpQ); 
        }
        spin_unlock_bh(&h->lock);
    }

    return retval;
}

/**************************************************************************
 ��������  : ��ȡ�¼�����
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             user_ptr              �û�̬��Ӧ����ָ��
             len                   ���ݳ���
 �� �� ֵ  : ssize_t�����ݳ��ȣ�������������
**************************************************************************/
static ssize_t vsc_get_event(struct vsc_ctrl_info *h, char  __user *  user_ptr, int len)
{
    struct vsc_event_list *e = NULL;
    struct vsc_scsi_event event;
    char __user *user = user_ptr;
    int retval = 0;

    event.reserved[0] = 1;
    event.reserved[1] = 0;

    if (!h) {
        return -EFAULT;
    }

    /* <zr> ����Ӧ���ж����len����Ч�� */
    if (len < (sizeof(event) + sizeof(struct vsc_scsi_msg_data) 
                + sizeof(struct vsc_event_abort))) {
        return -EINVAL;
    }

    spin_lock_bh(&h->lock);
    if (list_empty(&h->event_reqQ)) {
        spin_unlock_bh(&h->lock);
        retval = -ENODATA;
        goto errout;
    }
    e = list_first_entry(&h->event_reqQ, struct vsc_event_list, list);
    /* �Ӷ�ȡ������������ɾ������ */
    remove_eventQ(e);
    add_eventQ(&h->event_rspQ, e);
    if (!list_empty(&h->cmpQ) || !list_empty(&h->event_reqQ)) {
        event.reserved[1] = 1;
    }

    spin_unlock_bh(&h->lock);

    /* �����¼���Ϣͷ */
    user += sizeof(event);
    
    /* �����¼���Ϣ */  /* sizeof(struct vsc_scsi_msg_data) + sizeof(struct vsc_event_abort) or 
                            sizeof(struct vsc_scsi_msg_data) + sizeof(struct vsc_event_reset_dev) 
                            = 8+20 = 28 Bytes */
    if (copy_to_user(user, e->event_data, e->event_data_len)) {
        vsc_err("Get event: copy event head failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        retval = -EFAULT;
        goto errout;
    }

    /* ����¼���Ϣͷ */
    event.type = VSC_MSG_TYPE_EVENT;
    event.event_sn = e->event_sn;
    event.tag = e->event_index;
    event.data_length = e->event_data_len;

    /* �����¼�ͷ */   /* 28 Bytes */
    if (copy_to_user(user_ptr, &event, sizeof(event))) {
        vsc_err("Get event: copy event failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        retval = -EFAULT;
        goto errout;
    }

    /* ������Ϣ */
    if ( unlikely(VSC_TRACE_REQ_EVENT & trace_switch )) {
        struct vsc_scsi_msg_data *event_msg = NULL;
        
        event_msg = (struct vsc_scsi_msg_data *)(e->event_data);
        vsc_err("event req: host:%u sn:%u   tag: %u   len: %u  type:%u\n", vsc_ctrl_get_host_no(h), 
                event.event_sn, event.tag, event.data_length, event_msg->data_type);
    }

    /* ����״̬Ϊ�ȴ���Ӧ */
    e->stat = EVENT_LIST_STAT_READ_COMP;

    return sizeof(event) + event.data_length;

errout:
    /* �¼�δ��ȡ�ߣ����¼������ */
    if (e) {
        spin_lock_bh(&h->lock);
        remove_eventQ(e);
        add_eventQ(&h->event_reqQ, e);
        spin_unlock_bh(&h->lock);
    }

    return retval;
}

/**************************************************************************
 ��������  : scsi�����ȡ����
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             user_ptr              �û�̬��Ӧ����ָ��
             len                   ���ݳ���
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/
static ssize_t vsc_get_scsi_cmd_msg(struct vsc_ctrl_info *h, struct file *file,
                                        char  __user *  user_ptr, int len)
{
    ssize_t retval = 0;
    int do_get_event = 0;

    if (!h || !user_ptr) {
        return -EFAULT;
    }
   
    /* ѭ������cmpQ�����е�scsi���� */
    spin_lock_bh(&h->lock);
    while (list_empty(&h->cmpQ) && list_empty(&h->event_reqQ)) {
        spin_unlock_bh(&h->lock);
        if (file->f_flags & O_NONBLOCK) {
            retval = -EAGAIN;
            goto errout_no_count;
        }
        
        /* ������ȡ������£��ȴ�֪ͨ�¼� */
        retval = wait_event_interruptible(h->queue_wait, 
            !list_empty(&h->cmpQ) || !list_empty(&h->event_reqQ) || h->wakeup_pid);
        if (retval < 0) {
            goto errout;    // -ERESTARTSYS
        }

        /* ����Ƿ���Ϊdetach�˳� */
        if (unlikely(h->wakeup_pid)) {
            h->wakeup_pid = 0;
            retval = -EINTR;
            goto errout_no_count;
        }

        spin_lock_bh(&h->lock);
    }

    /* ���ȴ����¼���Ϣ */
    if (unlikely(!list_empty(&h->event_reqQ))) {
        do_get_event = 1;
    }
    spin_unlock_bh(&h->lock);

    /* <zr> �ͷ�h->lock֮����Ϣ���ܱ�����߳�ȡ��,��ʱ���п������±�Ϊ��, �������
       vsc_get_event()/vsc_get_scsi_cmd()�оͻ᷵��ENODATAʧ��,���readҲ�᷵��ʧ��, 
       ����������? */
    if (unlikely(do_get_event)) {
        retval = vsc_get_event(h, user_ptr, len);
    } else {
        retval = vsc_get_multi_scsi_cmd_and_cdb(h, user_ptr, len);
    }
    
    if (unlikely(retval < 0)) {
        goto errout;
    }

    return retval;
errout:
    h->stat.read_fail_count++;
errout_no_count:

    return retval;
}

/**************************************************************************
 ��������  : ���û�̬iovec�и�������
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             struct vsc_scsi_data  �û�̬������Ϣ
             char  __user *  user_ptr �û�̬iovec��ʼ��ַ
             unsigned char         �ں�̬����
             unsigned int len      �ں�̬���ݳ���
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/
static ssize_t vsc_copy_data_to_iovec(struct vsc_ctrl_info *h, struct vsc_scsi_data *scsi_data,
                            const char *user, unsigned char *from_ptr, unsigned int len)
{
    struct vsc_iovec *iovec;
    int i = 0;
    ssize_t retval = 0;
    unsigned char *from = from_ptr;
    unsigned int left_len = len;
    unsigned int copy_len = 0;
    ssize_t total_len = 0;

    /* ��ȡָ��ƫ�Ƶ����� */
    left_len -= scsi_data->offset;
    from += scsi_data->offset;

    for ( i = 0; i < scsi_data->nr_iovec && left_len > 0; i++) {
        iovec = (struct vsc_iovec *)user;

        /* �������ݵ��û�̬ */
        copy_len = min(iovec->iov_len, left_len);
        if (copy_to_user((void __user *)iovec->iov_base, from, copy_len)) {
            vsc_err("copy data to user failed, host is %u.\n", vsc_ctrl_get_host_no(h));
            retval = -EFAULT;
            goto errout;
        }
        from += copy_len;
        left_len -= copy_len;
        total_len += copy_len;

        user += sizeof(struct vsc_iovec);
    }
    return total_len;

errout:
    return retval;
}

/**************************************************************************
 ��������  : ���û�̬iovec�и������ݵ��ں�
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             struct vsc_scsi_data *scsi_data iovec����ͷָ��
             user_ptr              iovecָ��
             unsigned to_ptr       �ں�̬����
             unsigned int len      �ں�̬���ݳ���
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/
static ssize_t vsc_copy_data_from_iovec(struct vsc_ctrl_info *h, struct vsc_scsi_data *scsi_data,
                                const char *user, unsigned char *to_ptr, unsigned int len)
{
    struct vsc_iovec *iovec;
    int i = 0;
    ssize_t retval = 0;
    unsigned char *to = to_ptr;
    unsigned int left_len = len;
    unsigned int copy_len = 0;
    ssize_t total_len = 0;

    /* ��ȡָ��ƫ�Ƶ����� */
    left_len -= scsi_data->offset;
    to += scsi_data->offset;

    for ( i = 0; i < scsi_data->nr_iovec && left_len > 0; i++) {
        iovec = (struct vsc_iovec *)user;

        /* ��������from �û�̬ */
        copy_len = min(iovec->iov_len, left_len);
        if (copy_from_user(to, (void __user *)iovec->iov_base, copy_len)) {
            vsc_err("copy data from user failed, host is %u.\n", vsc_ctrl_get_host_no(h));
            retval = -EFAULT;
            goto errout;
        }
        to += copy_len;
        left_len -= copy_len;
        total_len += copy_len;

        user += sizeof(struct vsc_iovec);
    }
    return total_len;

errout:
    return retval;
}

#ifndef for_each_sg
#define for_each_sg(sglist, sg, nr, __i)    \
    for (__i = 0, sg = (sglist); __i < (nr); __i++, sg++ )
#endif

#if (LINUX_VERSION_CODE == KERNEL_VERSION(2, 6, 18))
static inline void *sg_virt(struct scatterlist *sg)
{
    return page_address(sg->page) + sg->offset;
}

static inline struct scatterlist *sg_next(struct scatterlist *sg)
{
    return ++sg;
}
#endif

void vsc_dump_scsi_data(struct vsc_scsi_data *scsi_data)
{
    int count = 0;
    struct vsc_iovec *iovec = (struct vsc_iovec *)scsi_data->vec;
    __u32 nr_iovec;
    
    vsc_err("scsi_data={%d %d %d %d %d}\n", scsi_data->data_type,
            scsi_data->data_len, scsi_data->nr_iovec,
            scsi_data->total_iovec_len, scsi_data->offset);

    nr_iovec = (SCSI_MAX_DATA_BUF_SIZE - sizeof(struct vsc_scsi_msg_data) -
                sizeof(struct vsc_scsi_data)) / sizeof(struct vsc_iovec);

    if (scsi_data->nr_iovec > nr_iovec) {
        return;
    }
    
    for (count=0;count<scsi_data->nr_iovec;count++) {
        vsc_err("%d/%d iovec_base=0x%llx iovec_len=%d", count, scsi_data->nr_iovec,
                iovec[count].iov_base, iovec[count].iov_len);
    }
}

void vsc_dump_scsi_sgl(struct scsi_cmnd *sc)
{
    struct scatterlist *sl = NULL;
    struct scatterlist *sl_first = NULL;
    int j = 0;
    
    if (!sc) {
        return;
    }
    
    scsi_print_command(sc);
    
    sl = scsi_sglist(sc);
    sl_first = scsi_sglist(sc);
    
    for_each_sg(sl_first, sl, scsi_sg_count(sc), j) {
        vsc_err("%d/%d addr=0x%p len=%d", j, scsi_sg_count(sc), sg_virt(sl), sl->length);
    }    
}

void vsc_dump_scsi_rsp(struct vsc_scsi_rsp_msg *rsp_msg)
{
    if (!rsp_msg) {
        return;
    }

    vsc_err("rsp_msg={%d %d %d %d %d %d %d}", rsp_msg->type, rsp_msg->reserved[0], rsp_msg->reserved[1],
            rsp_msg->cmd_sn, rsp_msg->tag, rsp_msg->command_status, rsp_msg->scsi_status);
}

/**************************************************************************
 ��������  : ����scsi���ݵ��û�̬�ռ� 
 ��    ��  : vsc_cmnd_list *c:     ����ָ��
             struct vsc_scsi_data *scsi_data iovec����ͷָ��
             user_ptr              �û�����ָ��
 �� �� ֵ  : 0�� �������ݵĳ��ȣ�������������
**************************************************************************/
inline int vsc_copy_sg_buff_to_iovec(struct scsi_cmnd *sc, struct vsc_scsi_data *scsi_data,
        const char *user)
{
    int i = 0;
    int j = 0;
    int sl_offset = 0;  /* sl��ƫ��λ�� */
    int sl_seek_offset = 0;  /* Ѱַʱ���ܵ�ƫ���� */
    struct vsc_iovec *iovec;
    //struct scsi_cmnd *sc = NULL;
    struct scatterlist *sl = NULL;
    struct scatterlist *sl_first = NULL;
    int copy_len = 0;
    int iov_base_offset = 0;
    int sl_data_offset = 0;
    int left_len = 0;
    int totallen = 0;

    //sc = c->scsi_cmd;
    sl_first = scsi_sglist(sc);

    /* ƫ�Ƶ�ָ����λ�� */
    for_each_sg(sl_first, sl, scsi_sg_count(sc), j) {
        sl_seek_offset += sl->length;
        if (sl_seek_offset > scsi_data->offset) {
            left_len = sl_seek_offset - scsi_data->offset;
            sl_offset = j;
            break;
        }
    }

    sl_first = sl;
    if (unlikely(!sl_first)) {
        vsc_err("fatal error, invalid sgl, sg_buflen=%d sg_count=%d.\n",
                scsi_bufflen(sc), scsi_sg_count(sc));
        vsc_dump_scsi_sgl(sc);
        vsc_dump_scsi_data(scsi_data);
        return -EINVAL;
    }

    if (unlikely(scsi_data->nr_iovec == 0)) {
        vsc_err("fatal error, invalid iovec, sg_buflen=%d sg_count=%d.\n",
                scsi_bufflen(sc), scsi_sg_count(sc));
        vsc_dump_scsi_sgl(sc);
        vsc_dump_scsi_data(scsi_data);
        return -EINVAL;
    }

    /* ��д����ʱ�жϣ��û�̬��д�����ݳ��Ⱥ�ʵ�ʿ��������ݳ��ȱ���һ�� */
    if (unlikely(vsc_is_readwrite_cmd(sc->cmnd[0]) && scsi_bufflen(sc) != scsi_data->total_iovec_len)) {
        vsc_err("fatal error, mismatch buflen, sg_buflen=%d sg_count=%d.\n",
                scsi_bufflen(sc), scsi_sg_count(sc));
        vsc_dump_scsi_sgl(sc);
        vsc_dump_scsi_data(scsi_data);
        return -EIO;
    }

    for ( i = 0; i < scsi_data->nr_iovec && sl_first; i++) {
        iovec = (struct vsc_iovec *)user;

        iov_base_offset = 0;
        /* ����һ��λ�ÿ�ʼ */
        for_each_sg (sl_first, sl, scsi_sg_count(sc) - sl_offset, j) {
            /* ����Ƿ���Ҫƫ�Ƹ���sg_list */
            if (left_len > 0 && left_len <= sl->length) {
                /* �������Ӧ��ƫ���� */
                sl_data_offset = sl->length - left_len;
            } else {
                sl_data_offset = 0;
            }

            /* ����С�ĳ��ȸ������� */
            copy_len = min(sl->length - sl_data_offset, iovec->iov_len - iov_base_offset);

            if (copy_to_user((void __user *)iovec->iov_base + iov_base_offset, sg_virt(sl) + sl_data_offset, copy_len)) {
                vsc_err("copy to user failed, sg_buflen=%d sg_count=%d copylen=%d.\n",
                        scsi_bufflen(sc), scsi_sg_count(sc),totallen);
                vsc_dump_scsi_sgl(sc);
                vsc_dump_scsi_data(scsi_data);
                return -EFAULT;
            }
            
            iov_base_offset += copy_len;
            sl_data_offset += copy_len;
            totallen += copy_len;

            left_len = sl->length - sl_data_offset - (iovec->iov_len - iov_base_offset);
            /* ���iovecС��sl->length����˵�����ݻ�û�и�����ɣ�����Ҫ�������� */
            if (left_len > 0) {
                /* ��ǰslû�и�����ɣ���Ҫ�ٴθ��� */
                sl_first = sl;
                break;
            } else {
                left_len = 0;
            }

            if (iov_base_offset >= iovec->iov_len) {
                /* ��sgͷ��ָ����һ����ͬʱ��ֵj++ */
                sl_first = sg_next(sl);
                j++;
                break;
            }
        }
        /* �����Ѿ�����ĸ��� */
        sl_offset += j;

        user += sizeof(struct vsc_iovec);
    }

    /* ��д����ʱ�жϣ��û�̬��д�����ݳ��Ⱥ�ʵ�ʿ��������ݳ��ȱ���һ�� */
    if (unlikely(vsc_is_readwrite_cmd(sc->cmnd[0]) && totallen != scsi_data->total_iovec_len)) {
        vsc_err("fatal error, mismatch copylen, sg_buflen=%d sg_count=%d copylen=%d.\n",
                scsi_bufflen(sc), scsi_sg_count(sc),totallen);
        vsc_dump_scsi_sgl(sc);
        vsc_dump_scsi_data(scsi_data);
        return -EIO;
    }
    
    return totallen;
}

/**************************************************************************
 ��������  : ���û�̬�������ݵ��ں�
 ��    ��  : vsc_cmnd_list *c:     ����ָ��
             struct vsc_scsi_data *scsi_data iovec����ͷָ��
             user_ptr              �û�����ָ��
             user_len              �û����ݳ���
 �� �� ֵ  : 0�� �������ݵĳ��ȣ�������������
**************************************************************************/
inline int vsc_copy_sg_buff_from_iovec(struct scsi_cmnd *sc, struct vsc_scsi_data *scsi_data,
        const char *  user)
{
    int i = 0;
    int j = 0;
    int sl_offset = 0;  /* sl��ƫ��λ�� */
    int sl_seek_offset = 0;  /* Ѱַʱ���ܵ�ƫ���� */
    struct vsc_iovec *iovec;
    //struct scsi_cmnd *sc = NULL;
    struct scatterlist *sl = NULL;
    struct scatterlist *sl_first = NULL;
    int copy_len = 0;
    int iov_base_offset = 0;
    int sl_data_offset = 0;
    int left_len = 0;
    int totallen = 0;

    //sc = c->scsi_cmd;
    sl_first = scsi_sglist(sc);

    /* ƫ�Ƶ�ָ����λ�� */
    for_each_sg (sl_first, sl, scsi_sg_count(sc), j) {
        sl_seek_offset += sl->length;
        if (sl_seek_offset > scsi_data->offset) {
            left_len = sl_seek_offset - scsi_data->offset;
            sl_offset = j;
            break;
        }
    }

    sl_first = sl;
    if (unlikely(!sl_first)) {
        vsc_err("fatal error, invalid sgl, sg_buflen=%d sg_count=%d.\n",
                scsi_bufflen(sc), scsi_sg_count(sc));
        vsc_dump_scsi_sgl(sc);
        vsc_dump_scsi_data(scsi_data);
        return -EINVAL;
    }

    if (unlikely(scsi_data->nr_iovec == 0)) {
        vsc_err("fatal error, invalid iovec, sg_buflen=%d sg_count=%d.\n",
                scsi_bufflen(sc), scsi_sg_count(sc));
        vsc_dump_scsi_sgl(sc);
        vsc_dump_scsi_data(scsi_data);
        return -EINVAL;
    }

    /* ��д����ʱ�жϣ��û�̬��д�����ݳ��Ⱥ�ʵ�ʿ��������ݳ��ȱ���һ�� */
    if (unlikely(vsc_is_readwrite_cmd(sc->cmnd[0]) && scsi_bufflen(sc) != scsi_data->total_iovec_len)) {
        vsc_err("fatal error, mismatch buflen, sg_buflen=%d sg_count=%d.\n",
                scsi_bufflen(sc), scsi_sg_count(sc));
        vsc_dump_scsi_sgl(sc);
        vsc_dump_scsi_data(scsi_data);
        return -EIO;
    }
    
    for ( i = 0; i < scsi_data->nr_iovec && sl_first; i++) {
        iovec = (struct vsc_iovec *)user;

        iov_base_offset = 0;
        /* ����һ��λ�ÿ�ʼ */
        for_each_sg (sl_first, sl, scsi_sg_count(sc) - sl_offset, j) {
            /* ����Ƿ���Ҫƫ�Ƹ���sg_list */
            if (left_len > 0 && left_len <= sl->length) {
                /* �������Ӧ��ƫ���� */
                sl_data_offset = sl->length - left_len;
            } else {
                sl_data_offset = 0;
            }

            /* ����С�ĳ��ȸ������� */
            copy_len = min(sl->length - sl_data_offset, iovec->iov_len - iov_base_offset);

            if (copy_from_user(sg_virt(sl) + sl_data_offset, (void __user *)iovec->iov_base + iov_base_offset, copy_len)) {
                vsc_err("copy from user failed, sg_buflen=%d sg_count=%d copylen=%d.\n",
                        scsi_bufflen(sc), scsi_sg_count(sc),totallen);
                vsc_dump_scsi_sgl(sc);
                vsc_dump_scsi_data(scsi_data);
                return -EFAULT;
            }

            iov_base_offset += copy_len;
            sl_data_offset += copy_len;
            totallen += copy_len;

            left_len = sl->length - sl_data_offset - (iovec->iov_len - iov_base_offset);
            /* ���iovecС��sl->length����˵�����ݻ�û�и�����ɣ�����Ҫ�������� */
            if (left_len > 0) {
                /* ��ǰslû�и�����ɣ���Ҫ�ٴθ��� */
                sl_first = sl;
                break;
            } else {
                left_len = 0;
            }

            if (iov_base_offset >= iovec->iov_len) {
                /* ��sgͷ��ָ����һ����ͬʱ��ֵj++ */
                sl_first = sg_next(sl);
                j++;
                break;
            }
        }
        /* �����Ѿ�����ĸ��� */
        sl_offset += j;

        user += sizeof(struct vsc_iovec);
    }

    /* ��д����ʱ�жϣ��û�̬��д�����ݳ��Ⱥ�ʵ�ʿ��������ݳ��ȱ���һ�� */
    if (unlikely(vsc_is_readwrite_cmd(sc->cmnd[0]) && totallen != scsi_data->total_iovec_len)) {
        vsc_err("fatal error, mismatch copylen, sg_buflen=%d sg_count=%d copylen=%d.\n",
                scsi_bufflen(sc), scsi_sg_count(sc),totallen);
        vsc_dump_scsi_sgl(sc);
        vsc_dump_scsi_data(scsi_data);
        return -EIO;
    }

    return totallen;
}

/**************************************************************************
 ��������  : ���ݲ�ͬ��scsi�����������û�̬�ͺ�̬��������
 ��    ��  : scsi_data             �����������Ϣ
             mode                  ��дģʽ
             vsc_ctrl_info *h:     host���ƾ��
             user_ptr              �û�̬��Ӧ����ָ��
             len                   ���ݳ���
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/
static ssize_t vsc_xfer_data(struct vsc_scsi_data* scsi_data, unsigned int mode, struct vsc_ctrl_info *h,
                              const char *user, struct scsi_cmnd* scsi_cmnd)
{
    struct scsi_cmnd* sc = scsi_cmnd;
    ssize_t retval = 0;
    
    switch (scsi_data->data_type) {
    case VSC_MSG_DATA_TYPE_CDB:
        if (VSC_MODE_READ != mode) {
            vsc_err("request cmd: write CDB is not permited, host is %u.\n", vsc_ctrl_get_host_no(h));    
            retval = -EACCES;
            goto errout;
        }
        /* ����CDB���û�̬ */

    h->get_cdb_total++;

#if (LINUX_VERSION_CODE == KERNEL_VERSION(2, 6, 18))
    retval = vsc_copy_data_to_iovec(h, scsi_data, user, sc->cmnd, COMMAND_SIZE(sc->cmnd[0]));
#else
    retval = vsc_copy_data_to_iovec(h, scsi_data, user, sc->cmnd, scsi_command_size(sc->cmnd));
#endif
        if (retval < 0) {
            vsc_err("request cmd: copy CDB failed, host = %u, retval = %ld\n", vsc_ctrl_get_host_no(h), retval);
            goto errout;
        }
        break;
        
    case VSC_MSG_DATA_TYPE_DATA:
        if (VSC_MODE_READ == mode) {
            /* �������ݵ��û�̬ */
            retval = vsc_copy_sg_buff_to_iovec(sc, scsi_data, user);
            if (retval < 0) {
                vsc_err_limit("request cmd: copy sg buff to iovec failed, host is %u.\n", vsc_ctrl_get_host_no(h));  
                goto errout;
            }
        } else if (VSC_MODE_WRITE == mode) {
            /* д�����ݵ�sglist */
            retval = vsc_copy_sg_buff_from_iovec(sc, scsi_data, user);
            if (retval < 0) {
                vsc_err_limit("request cmd: copy sg buff from iovec failed, host is %u.\n", vsc_ctrl_get_host_no(h));  
                goto errout;
            }
        } else {
            retval = -EFAULT;
            vsc_err("invalid xfer_mode %d.\n", mode);
            goto errout;
        }
        break;
        
    case VSC_MSG_DATA_TYPE_SENSE:
        if (VSC_MODE_WRITE != mode) {
            vsc_err("request cmd: read sense is not permited, host is %u.\n", vsc_ctrl_get_host_no(h));    
            retval = -EACCES;
            goto errout;
        }
        /* ���ƴ�����Ϣ��sc���� */
        retval = vsc_copy_data_from_iovec(h, scsi_data, user, sc->sense_buffer, SCSI_SENSE_BUFFERSIZE);
        if (retval < 0) {
            vsc_err("request cmd: copy sense data failed, host = %u, retval = %lu\n", vsc_ctrl_get_host_no(h), retval); 
            goto errout;
        }
        break;
        
    default:
        vsc_err("request msg error: vsc_scsi_data type is invalid, host = %u, type = %d\n", 
            vsc_ctrl_get_host_no(h), scsi_data->data_type); 
        retval = -EIO;
        goto errout;
        break;
    }
    
errout:
    return retval;
}


/**************************************************************************
 ��������  : scsi�������ݴ���
 ��    ��  : mode                  ��дģʽ
             vsc_ctrl_info *h:     host���ƾ��
             user_ptr              �û�̬��Ӧ����ָ��
             len                   ���ݳ���
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/
static ssize_t vsc_scsi_cmd_data(unsigned int mode, struct vsc_ctrl_info *h,
        char *user, int len, int *data_len)
{
    struct vsc_scsi_data_msg *scsi_data_msg;
    struct vsc_scsi_data *scsi_data;
    char *iovec;
    //const char __user *user = user_ptr;
    ssize_t retval = 0;
    struct vsc_cmnd_list *c = NULL;
    //int scsi_data_len = 0;
    struct scsi_cmnd *sc = NULL;
    int totallen = 0;

    scsi_data_msg = (struct vsc_scsi_data_msg *)user;
    scsi_data = (struct vsc_scsi_data *)(user + sizeof(struct vsc_scsi_data_msg));
    iovec = user + sizeof(struct vsc_scsi_data_msg) + sizeof(struct vsc_scsi_data);

    /* ��������Ƿ���Ч */
    if (unlikely(scsi_data_msg->type != VSC_MSG_TYPE_SCSI_DATA
            || scsi_data_msg->tag >= h->nr_cmds
            || scsi_data_msg->scsi_data_len > len)) {

        vsc_err("request msg error: host = %u, type = %u, tag = %u, len = %u\n",
            vsc_ctrl_get_host_no(h), scsi_data_msg->type, scsi_data_msg->tag, scsi_data_msg->scsi_data_len);
        retval = -EIO;
        goto errout;
    }

    /* ����tag����commandָ�� */
    spin_lock_bh(&h->lock);
    c = h->cmd_pool_tbl[scsi_data_msg->tag];
    if (unlikely(c->stat != CMD_STAT_READ_COMP || c->cmd_sn != scsi_data_msg->cmd_sn)) {
        spin_unlock_bh(&h->lock);
        //vsc_debug_cmd(vsc_ctrl_get_host_no(h));
        vsc_err("request msg error: host = %u, msg.sn = %u, msg.tag = %u, cmd.stat = %d, cmd.tag = %u, cmd.sn = %u\n",
                vsc_ctrl_get_host_no(h),
                scsi_data_msg->cmd_sn, scsi_data_msg->tag, c->stat, c->cmd_index, c->cmd_sn);
        c = NULL;
        retval = -EIO;
        goto errout;
    }

    /* �ж������Ƿ��Ѿ����� */
    if (unlikely(list_empty(&c->list))) { 
        spin_unlock_bh(&h->lock);
        vsc_err("request msg error: already removed host = %u, cmd.sn = %u, cmd.tag = %d, cmd.stat = %d\n",
                vsc_ctrl_get_host_no(h), 
                c->cmd_sn, c->cmd_index, c->stat);
        c = NULL;
        retval = -EIO;
        goto errout;
    }
    sc = c->scsi_cmd;

#ifdef __VSC_LATENCY_DEBUG__
    if (vsc_is_write_cmd(sc->cmnd[0])) {
        c->get_data_time = vsc_get_usec();
        h->write_stage2_total += c->get_data_time - c->get_scmd_time;
    }
    else if ((vsc_is_read_cmd(sc->cmnd[0])) {
        c->back_data_time = vsc_get_usec();
        h->read_stage2_total += c->back_data_time - c->get_scmd_time;
    }
#endif

    spin_unlock_bh(&h->lock);

    retval = vsc_xfer_data(scsi_data, mode, h, iovec, sc);
    if (unlikely(retval < 0))
        goto errout;
    totallen += retval;

    /* ��iovec���ȴ����ϲ㺯����������ת����һ��scsi cmd */
    *data_len = scsi_data->data_len;

    return totallen;
errout:
    return retval;
}

#define VSC_SCSI_BUF_HEAD_MAGIC 0x55AA33CC
#define VSC_SCSI_BUF_TAIL_MAGIC 0x11EE22DD

/* Ϊbuffer����ͷβmagicУ�飬��ǰ���ֲ��ڴ������ */
static inline void* vsc_alloc_scsi_buf(void)
{
    char *buf = mempool_alloc(scsi_buf_pool, GFP_KERNEL);
    if (unlikely(!buf)) {
        return buf;
    }

    *(__u32*)buf = VSC_SCSI_BUF_HEAD_MAGIC;
    *(__u32*)(buf+sizeof(__u32)+MAX_SCSI_DATA_AND_RSP_LENGTH) = VSC_SCSI_BUF_TAIL_MAGIC;
    return buf+sizeof(__u32);
}

static int vsc_free_scsi_buf(void *buffer)
{
    char *buf = (char*)buffer;
    __u32 head_magic = *(__u32*)(buf-sizeof(__u32));
    __u32 tail_magic = *(__u32*)(buf+MAX_SCSI_DATA_AND_RSP_LENGTH);
    
    if (unlikely(head_magic!=VSC_SCSI_BUF_HEAD_MAGIC || tail_magic!=VSC_SCSI_BUF_TAIL_MAGIC)) {
        vsc_err("fatal error, error magic 0x%x tail_magic 0x%x", head_magic, tail_magic);
        mempool_free(buf-sizeof(__u32), scsi_buf_pool);
        return -EFAULT;
    }
    
    mempool_free(buf-sizeof(__u32), scsi_buf_pool);
    return 0;
}

static ssize_t vsc_multi_scsi_cmd_data(unsigned int mode, struct vsc_ctrl_info *h,
    const char  __user *  user_ptr, int len)
{
    char *buf;
    char *temp;
    struct vsc_scsi_data_msg *scsi_data_msg;
    int scsi_data_len = 0;
    int totallen = 0;
    int index = 0;
    int ret_len = 0;
    int count = 0;

    /* buf����ΪMAX_SCSI_DATA_AND_RSP_LENGTH */
    buf = vsc_alloc_scsi_buf();
    if(unlikely(!buf)) {
        vsc_err("alloc scsi_data buffer failed.\n");
        return -ENOMEM;
    }

    /* ������������ͷ */
    if (copy_from_user(buf, user_ptr, len)) {
        vsc_err("copy scsi data msg head failed.\n");
        vsc_free_scsi_buf(buf);
        return -EFAULT;
    }

    scsi_data_msg = (struct vsc_scsi_data_msg *)buf;
    temp = buf;

    count = scsi_data_msg->reserved[0];
    if (unlikely(count == 0 || count > MAX_BATCH_SCSI_CMD_COUNT)) {
        vsc_err("too many cmd from user_space, %d.\n", count);
        vsc_free_scsi_buf(buf);
        return -EFAULT;
    }
    
    for (index = 0; index < count; index++) {
        ret_len = vsc_scsi_cmd_data(mode, h, temp, len, &scsi_data_len);
        if (unlikely(ret_len < 0)) {
            scsi_data_msg = (struct vsc_scsi_data_msg *)temp;
            vsc_err("%s cmd_data error, %d/%d, ret_len %d 1st type %d len %d reserve1 %d cmd_sn %d tag %d data_len %d host %d\n",
                mode == VSC_MODE_READ ? "Read" : "Write",
                index, count, ret_len, scsi_data_msg->type, len, scsi_data_msg->reserved[1],
                scsi_data_msg->cmd_sn, scsi_data_msg->tag, scsi_data_msg->scsi_data_len, vsc_ctrl_get_host_no(h));
            vsc_free_scsi_buf(buf);
            return -EIO;
        }
        totallen += ret_len;
        temp += SCSI_MAX_DATA_BUF_SIZE;
        len -= SCSI_MAX_DATA_BUF_SIZE;
    }
    
    return vsc_free_scsi_buf(buf);
}

static ssize_t vsc_response_multi_scsi_cmd(struct vsc_ctrl_info *h,
    const char *user, int len);

static ssize_t vsc_response_multi_data_and_rsp(unsigned int mode, struct vsc_ctrl_info *h,
        const char  __user *  user_ptr, int len)
{
    char *buf;
    char *temp;
    struct vsc_scsi_data_msg *scsi_data_msg;
    int scsi_data_len = 0;
    int totallen = 0;
    int index = 0;
    int ret_len = 0;
    int cmd_count = 0;
    int read_count = 0;
    int temp_len = 0;

    if (unlikely(len != MAX_SCSI_DATA_AND_RSP_LENGTH)) {
        vsc_err("expect_len %d actual_len %u \n", (int)MAX_SCSI_DATA_AND_RSP_LENGTH, len);
        return -EINVAL;
    }

    buf = vsc_alloc_scsi_buf();
    if(unlikely(!buf)) {
        vsc_err("alloc scsi_data buffer failed.\n");
        return -ENOMEM;
    }

    /* ������������ͷ */
    if (unlikely(copy_from_user(buf, user_ptr, len))) {
        vsc_err("copy scsi data msg head failed.\n");
        vsc_free_scsi_buf(buf);
        return -EFAULT;
    }
    scsi_data_msg = (struct vsc_scsi_data_msg *)buf;
    read_count = scsi_data_msg->reserved[0];
    cmd_count = scsi_data_msg->reserved[1];

    temp = buf;
    temp_len = len;

    if (unlikely(read_count > MAX_BATCH_SCSI_RSP_COUNT || cmd_count > MAX_BATCH_SCSI_RSP_COUNT || cmd_count == 0)) {
        vsc_err("invalid read_cnt %d or cmd_count %d.\n", read_count, cmd_count);
        vsc_free_scsi_buf(buf);
        return -EFAULT;
    }
    
    for (index = 0; index < read_count; index++) {
        ret_len = vsc_scsi_cmd_data(mode, h, temp, temp_len, &scsi_data_len);
        if (unlikely(ret_len < 0)) {
            scsi_data_msg = (struct vsc_scsi_data_msg *)temp;
            vsc_err_limit("xfer cmd_data error, %d/%d, ret_len %d 1st type %d len %d cmd_sn %d tag %d data_len %d host %d\n",
                index, read_count, ret_len, scsi_data_msg->type, temp_len,
                scsi_data_msg->cmd_sn, scsi_data_msg->tag, scsi_data_msg->scsi_data_len, vsc_ctrl_get_host_no(h));
            vsc_free_scsi_buf(buf);
            return -EIO;
        }
        totallen += ret_len;
        temp += SCSI_MAX_DATA_BUF_SIZE;
        temp_len -= SCSI_MAX_DATA_BUF_SIZE;
    }

    ret_len = vsc_response_multi_scsi_cmd(h, buf + MAX_BATCH_SCSI_RSP_COUNT * SCSI_MAX_DATA_BUF_SIZE,
        len - MAX_BATCH_SCSI_RSP_COUNT * SCSI_MAX_DATA_BUF_SIZE);
    if (unlikely(ret_len < 0)) {
        vsc_err_limit("response error reserve[0]=%d reserve[1]=%d ret_len=%d len=%d host=%d\n", read_count,
            cmd_count, ret_len, len, vsc_ctrl_get_host_no(h));
        vsc_free_scsi_buf(buf);
        return -EIO;
    }

    return vsc_free_scsi_buf(buf);
}

/**************************************************************************
 ��������  : ��ȡscsi��Ϣ
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             user_ptr              �û�̬��Ӧ����ָ��
             len                   ���ݳ���
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/
ssize_t vsc_get_msg(struct vsc_ctrl_info *h, struct file *file, char  __user *  user_ptr, int len)
{
    ssize_t retval = 0;
    unsigned int type;

    if (unlikely(!h)) {
        retval = -EFAULT;
        goto errout;
    }
   
    /* ��ȡ��Ϣ���� */
    if (unlikely(get_user(type, user_ptr))) {
        vsc_err("Request msg: copy req head data failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        retval = -EFAULT;
        goto errout;
    }

    if (likely(VSC_MSG_TYPE_SCSI_CMD == type)) {
        retval = vsc_get_scsi_cmd_msg(h, file, user_ptr, len);
    } else if (likely(VSC_MSG_TYPE_SCSI_DATA == type)) {
        retval = vsc_multi_scsi_cmd_data(VSC_MODE_READ, h, user_ptr, len);
    } else {
        retval = -EINVAL;
        goto errout;
    }

    if (unlikely(retval < 0)) {
        goto errout;
    }

    return retval;
errout:
    h->stat.read_fail_count++;
    return retval;
}

/**************************************************************************
 ��������  : ����������ȡ�Ľ���
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
 �� �� ֵ  : ��
**************************************************************************/
void vsc_interrupt_sleep_on_read(struct vsc_ctrl_info *h)
{
    if (!h) {
        return;
    }

    /* �����¼� */
    if (waitqueue_active(&h->queue_wait)) {
        h->wakeup_pid = 1;
        wake_up(&h->queue_wait);
    }

    return;
}

/**************************************************************************
 ��������  : scsi���������
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             user_ptr              �û�̬��Ӧ����ָ��
             len                   ���ݳ���
 �� �� ֵ  : ssize_t ���ݳ��ȣ�������������
**************************************************************************/
static ssize_t vsc_response_scsi_cmd_new(struct vsc_ctrl_info *h, struct vsc_scsi_rsp_msg *rsp_msg)
{
    struct vsc_cmnd_list *c = NULL;
    struct scsi_cmnd *sc = NULL;
    //struct vsc_scsi_rsp_msg rsp_msg;
    int retval = 0;
    int total_len = 0;
    int resid = 0;
    int sc_type;

    if (unlikely(!h)) {
        retval = -EFAULT;
        goto errout;
    }

    if (unlikely(rsp_msg->tag >= h->nr_cmds)) {
        vsc_err("Response cmd error: tag is invalid, host = %u, tag = %d\n", vsc_ctrl_get_host_no(h), rsp_msg->tag);
        retval = -EIO;
        goto errout;
    }

    /* ����tag����commandָ�� */
    spin_lock_bh(&h->lock);
    c = h->cmd_pool_tbl[rsp_msg->tag];
    if (unlikely(c->stat != CMD_STAT_READ_COMP || c->cmd_sn != rsp_msg->cmd_sn)) {
        spin_unlock_bh(&h->lock);

        //vsc_debug_cmd(vsc_ctrl_get_host_no(h));
        vsc_err("response cmd error: host = %u, rsp.sn = %u, rsp.tag = %d, cmd.stat = %d, cmd.tag = %d, cmd.sn = %u\n",
                vsc_ctrl_get_host_no(h),
                rsp_msg->cmd_sn, rsp_msg->tag, c->stat, c->cmd_index, c->cmd_sn);
        c = NULL;
        retval = -EIO;
        goto errout;
    }

    /* �ж������Ƿ��Ѿ����� */
    if (unlikely(list_empty(&c->list))) { 
        spin_unlock_bh(&h->lock);
        vsc_err("response cmd error: already removed host = %u, rsp.sn = %u, rsp.tag = %d, cmd.stat = %d\n",
                vsc_ctrl_get_host_no(h),
                rsp_msg->cmd_sn, rsp_msg->tag, c->stat);
        c = NULL;
        retval = -EIO;
        goto errout;
    }

    /* �����������ɾ������ */
    removeQ(c);
    /* ���ñ�־Ϊ���ڴ��� */
    c->stat = CMD_STAT_RESP;

    sc = c->scsi_cmd;
    sc_type = sc->cmnd[0];

#ifdef __VSC_LATENCY_DEBUG__
    if ((vsc_is_write_cmd(sc_type)) {
        c->back_rsp_time = vsc_get_usec();
        h->write_stage3_total += c->back_rsp_time - c->get_data_time;
    }
    else if ((vsc_is_read_cmd(sc_type)) {
        c->back_rsp_time = vsc_get_usec();
        h->read_stage3_total += c->back_rsp_time - c->back_data_time;
    }

    if ((vsc_is_readwrite_cmd(sc_type)) {
        if (c->back_rsp_time > c->start_queue_time && c->back_rsp_time - c->start_queue_time > 30000000) {
            vsc_err("too long to rsp(%llu us), host(%d) cmd_sn(%d) tag(%d) start_queue(%llu) get_scmd(%llu) rsp_time(%llu)",
                    vsc_ctrl_get_host_no(h), c->cmd_sn, c->cmd_index, c->back_rsp_time - c->start_queue_time,
                    c->start_queue_time, c->get_scmd_time, c->back_rsp_time);
        }
    }
#endif

    h->io_running--;
    spin_unlock_bh(&h->lock);

    /* ��������� */
    sc->result = (DID_OK << 16);              /* host byte */

     /* ������ */
    vsc_sense_check(c, rsp_msg->command_status);

    /* ���ｫmsg_byte��status_byte�����÷������, Ϊ�˱�֤����ʧ��2��������Ϣ */
    sc->result |= (COMMAND_COMPLETE << 8);    /* msg byte */
    sc->result |= ((rsp_msg->scsi_status & 0x7F) << 1); /* [zr] status byte set by target,
                                                                  extract by ML using status_byte() */

    /* ������Ϣ */
    if (unlikely(VSC_TRACE_RSP_SCSI_CMD & trace_switch)) {
        vsc_err("host:%u, sn:%u tag:%u  command_status = %x, scsi_status = %x, result = %x\n",
                vsc_ctrl_get_host_no(h),
                rsp_msg->cmd_sn, rsp_msg->tag, rsp_msg->command_status, rsp_msg->scsi_status, sc->result);
    }

    /* �ϱ�scsi������ */
    /* ����ʣ�����ݳ���Ϊ0 */
    scsi_set_resid(sc, resid);
    sc->scsi_done(sc);

#ifdef __VSC_LATENCY_DEBUG__
    if ((vsc_is_write_cmd(sc_type)) {
        h->write_total += vsc_get_usec() - c->start_queue_time;
    }
    else if (vsc_is_read_cmd(sc_type)) {
        h->read_total += vsc_get_usec() - c->start_queue_time;
    }
#endif

    /* �ͷ����� */
    vsc_cmd_put(c);

    return total_len;

errout:
    if (c) {
        spin_lock_bh(&h->lock);
        c->stat = CMD_STAT_READ_COMP;
        addQ(&h->cmpQ, c);
        spin_unlock_bh(&h->lock);
    }
    return retval;
}

static ssize_t vsc_response_multi_scsi_cmd(struct vsc_ctrl_info *h,
    const char *user, int len)
{
    struct vsc_scsi_rsp_msg *rsp_msg;
    int retval = 0;
    int total_len = 0;
    int index = 0;
    int cmd_count = 0;
    
    if (unlikely(!h)) {
        retval = -EFAULT;
        goto errout;
    }

    if (unlikely(len != sizeof(struct vsc_scsi_rsp_msg)*MAX_BATCH_SCSI_RSP_COUNT)) {
        vsc_err("expect_len %d actual_len %u \n",
            (int)sizeof(struct vsc_scsi_rsp_msg)*MAX_BATCH_SCSI_RSP_COUNT, len);
        retval = -EFAULT;
        goto errout;
    }

    rsp_msg = (struct vsc_scsi_rsp_msg *)user;
    cmd_count = rsp_msg->reserved[0];

    if (unlikely(cmd_count == 0 || cmd_count > MAX_BATCH_SCSI_RSP_COUNT)) {
        vsc_err("invalid cmd_count %d \n", cmd_count);
        retval = -EINVAL;
        goto errout;
    }
    
    for (index = 0; index < cmd_count; index++) {
        retval = vsc_response_scsi_cmd_new(h, &rsp_msg[index]);
        if(unlikely(retval < 0)) {
            vsc_err_limit("%d/%d response process error, len %d host %d\n", index, cmd_count, len, vsc_ctrl_get_host_no(h));
            return -EIO;
        }

        total_len += retval;
    }
    h->put_rsp_times++;
    h->put_rsp_total += cmd_count;

    return total_len;
errout:
    // TODO: do some error handle
    return retval;
}

/**************************************************************************
 ��������  : �¼���Ӧ��Ϣ
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/
static ssize_t vsc_response_event(struct vsc_ctrl_info *h, const char __user *  user_ptr, int len)
{
    struct vsc_event_list *e = NULL;
    struct vsc_scsi_event event;
    const char __user *user = user_ptr;
    unsigned total_len = 0;
    int retval = 0;
    struct vsc_scsi_msg_data *event_msg = NULL;

    if (unlikely(!h) || unlikely(!user_ptr)) {
        retval = -EFAULT;
        goto errout;
    }
   
    /* ��ȡ��Ӧͷ */
    if (copy_from_user(&event, user, sizeof(event))) {
        vsc_err("Response event: copy resp head data failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        retval = -EFAULT;
        goto errout;
    }
    user += sizeof(event);
    total_len += sizeof(event);

    if (event.tag >= h->nr_events) {
        vsc_err("response event error: tag is invalid, host = %u, tag = %d\n", 
            vsc_ctrl_get_host_no(h), event.tag);
        retval = -EIO;
        goto errout;
    }

    spin_lock_bh(&h->lock);
    e = h->event_pool_tbl[event.tag];
    if (e->stat != EVENT_LIST_STAT_READ_COMP || e->event_sn != event.event_sn) {
        spin_unlock_bh(&h->lock);
        vsc_err("response event error: host = %u, rsp.sn = %u, rsp.tag = %u, e.stat = %d, e.tag = %u, e.sn = %u\n",
                vsc_ctrl_get_host_no(h), 
                event.event_sn, event.tag, e->stat, e->event_index, e->event_sn);
        e = NULL;
        retval = -EIO;
        goto errout;
    }
    e->stat = EVENT_LIST_STAT_RESP;
    spin_unlock_bh(&h->lock);

    /* ������ݳ��Ȳ���ȷ */
    if (event.data_length > len || event.data_length >= sizeof(e->event_data)) {
        vsc_err("Response event: invalid event data_length, host = %u\n, event.data_lenth=%u, len=%d.\n", 
            vsc_ctrl_get_host_no(h), event.data_length, len);
        retval = -EIO;
        goto errout;
    }

    /* ��ȡ�¼����� */
    e->event_data_len = event.data_length;
    if (copy_from_user(e->event_data, user, event.data_length)) {
        vsc_err("Response event: copy resp data failed, host = %u\n", vsc_ctrl_get_host_no(h));
        retval = -EFAULT;
        goto errout;
    }

    /* �̶���ȡevent�¼����� */
    event_msg = (struct vsc_scsi_msg_data *)(e->event_data);
    if (e->event_callback) {
        if (event_msg->data_len > event.data_length) {
            vsc_err("Response event: event msg data_len invalid. "
                        "host=%u, type=%d, event_msg.data_len=%u, event.data_length=%u.\n", 
                    vsc_ctrl_get_host_no(h), 
                    event_msg->data_type, event_msg->data_len, event.data_length);
            retval = -EFAULT;
            goto errout;    
        }
        retval = e->event_callback(e->h, EVENT_SHOOT, e, event_msg->data_type, event_msg->data, event_msg->data_len);
        /* ���Ѵ����¼� */
        e->shoot = EVENT_SHOOT_SHOOT;
        wake_up(&e->wait);
        if (retval) {
            goto errout;
        }
    }

    /* ������Ϣ */
    if (unlikely(VSC_TRACE_RSP_EVENT & trace_switch)) {
        vsc_err("event resp: host:%u sn:%u tag:%d  len:%d  type = %x\n",
                vsc_ctrl_get_host_no(h), 
                event.event_sn, event.tag, event.data_length, event_msg->data_type);
    }

    return total_len;
errout:
    return retval;
}

/**************************************************************************
 ��������  : scsi���������
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
 �� �� ֵ  : ssize_t�� ���ݳ��ȣ�������������
**************************************************************************/
ssize_t vsc_response_msg(struct vsc_ctrl_info *h, const char __user *  user_ptr, int len)
{
    int retval = 0;
    unsigned int type;

    if (unlikely(!h)) {
        retval = -EFAULT;
        goto errout;
    }
   
    /* ��ȡ��Ϣ���� */
    if (get_user(type, user_ptr)) {
        vsc_err("Response msg: copy resp head data failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        retval = -EFAULT;
        goto errout;
    }

    if (unlikely(VSC_MSG_TYPE_EVENT == type)) {
        retval = vsc_response_event(h, user_ptr, len);
    } else if (likely(VSC_MSG_TYPE_SCSI_DATA == type)) {
        retval = vsc_response_multi_data_and_rsp(VSC_MODE_WRITE, h, user_ptr, len);
    } else {
        retval = -EINVAL;
        vsc_err("invalid msg type %d\n", type);
        goto errout;
    }

    if (unlikely(retval < 0)) {
        goto errout;
    }

    return retval;

errout:
    if (likely(h)) {
        h->stat.write_fail_count++;
    }
    return retval;
}


/**************************************************************************
 ��������  : ���ƽṹ���ͷ�
 ��    ��  : vsc_ctrl_info *h:   host���ƾ��
 �� �� ֵ  : ��
**************************************************************************/
static void inline vsc_ctrl_info_destroy(struct vsc_ctrl_info *h)
{
    int i = 0;
    struct vsc_cmnd_list *c;
    struct vsc_event_list *e;

    if (h->event_pool_tbl) {
        for (i = 0; i < h->nr_events; i++) {
            e = h->event_pool_tbl[i];
            if (e) {
                kfree(e);
                h->event_pool_tbl[i] = NULL;
            }
        }
        kfree(h->event_pool_tbl);
        h->event_pool_tbl = NULL;
    }

    if (h->event_pool_bits) {
        kfree(h->event_pool_bits);
        h->event_pool_bits = NULL;
    }

    if (h->cmd_pool_tbl) {
        for (i = 0; i < h->nr_cmds; i++) {
            c = h->cmd_pool_tbl[i];
            if (c) {
                kfree(c);
                h->cmd_pool_tbl[i] = NULL;
            }
        }
        kfree(h->cmd_pool_tbl);
        h->cmd_pool_tbl = NULL;
    }

    if (h->cmd_pool_bits) {
        kfree(h->cmd_pool_bits);
        h->cmd_pool_bits = NULL;
    }
}

/**************************************************************************
 ��������  : ���ƽṹ�ͷź���������=0ʱ�ͷ��ڴ�
 ��    ��  : 
 �� �� ֵ  : vsc_ctrl_info *h:     host���ƾ��
**************************************************************************/
void vsc_ctrl_info_put(struct vsc_ctrl_info *h)
{
    if (atomic_dec_and_test(&h->ref_cnt)) {
        vsc_ctrl_info_destroy(h);
        kfree(h);     
    }
}

/**************************************************************************
 ��������  : ���ƽṹ���ü���+1
 ��    ��  : 
 �� �� ֵ  : vsc_ctrl_info *h:     host���ƾ��
**************************************************************************/
void vsc_ctrl_info_get(struct vsc_ctrl_info *h)
{
    atomic_inc(&h->ref_cnt);
}

/**************************************************************************
 ��������  : ������ƽṹ�ڴ�
 ��    ��  : 
 �� �� ֵ  : vsc_ctrl_info *h:     host���ƾ��
**************************************************************************/
static struct vsc_ctrl_info *vsc_ctrl_info_alloc(void)
{
    struct vsc_ctrl_info *h = NULL;

    h = kzalloc(sizeof(struct vsc_ctrl_info), GFP_KERNEL);
    if (!h) {
        return NULL;
    }

    atomic_set(&h->ref_cnt, 0);
    vsc_ctrl_info_get(h);

    return h;
}

/**************************************************************************
 ��������  : ���ƽṹ���ʼ��
 ��    ��  : vsc_ctrl_info *h:     host���ƾ��
             struct Scsi_Host *sh: scsi�в��ָ��
             int nr_cmds           ������и���
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
static int inline vsc_ctrl_init(struct vsc_ctrl_info *h, struct Scsi_Host *sh, int nr_cmds, int vbs_host_id)
{
    int retval = 0;
    struct vsc_cmnd_list *c;
    struct vsc_event_list *e;
    int i = 0;

    if (!h || !sh) {
        return -EINVAL;
    }

    /*��ʼ��hash����*/
    INIT_LIST_HEAD(&h->cmpQ);
    INIT_LIST_HEAD(&h->reqQ);
    INIT_LIST_HEAD(&h->rspQ);
    INIT_LIST_HEAD(&h->event_reqQ);
    INIT_LIST_HEAD(&h->event_rspQ);
   
    /*��ʼ����*/
    spin_lock_init(&h->lock);

    /* ��ʼ��target��Ϣ */
    h->file = NULL;

    /* ��ʼ�ȴ����� */
    init_waitqueue_head(&h->queue_wait);

    h->wakeup_pid = 0;
    h->scsi_host = sh; 
    h->vbs_host_id = vbs_host_id;
    h->nr_cmds = (nr_cmds) ? nr_cmds : VSC_MAX_CMD_NUM;
    h->nr_events = VSC_DEFAULT_EVENT_NUMBER;
    h->suspend = 0;
    h->target_abnormal_time = 0;
    h->io_running = 0;
    atomic_set(&h->target_abnormal_lock, 0);
    init_timer(&h->target_abnormal_timer);
    setup_timer(&h->target_abnormal_timer, vsc_target_abnormal, (unsigned long)h);

    /* ��ʼ��������λ����Ϣ������0 */
    h->cmd_pool_bits = kzalloc(((h->nr_cmds + BITS_PER_LONG - 1) / BITS_PER_LONG) * sizeof(unsigned long), GFP_KERNEL);
    if (!h->cmd_pool_bits) {
        retval = -ENOMEM;
        vsc_err("malloc cmd memory for pool bits failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        goto err_out;
    }

    /* ��ʼ����������С */
    h->cmd_pool_tbl = kzalloc( h->nr_cmds * sizeof(*h->cmd_pool_tbl), GFP_KERNEL);
    if (!h->cmd_pool_tbl) {
        retval = -ENOMEM;
        vsc_err("malloc cmd memory for pool failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        goto err_out;
    }

    /* �����Ӧ��������� */
    for (i = 0; i < h->nr_cmds; i++) {
        c = kmalloc(sizeof(*c), GFP_KERNEL);
        if (!c) {
            retval = -ENOMEM;
            goto err_out;
        }
        h->cmd_pool_tbl[i] = c;
    }
    
    /* ��ʼ��������λ����Ϣ������0 */
    h->event_pool_bits = kzalloc(((h->nr_events + BITS_PER_LONG - 1) / BITS_PER_LONG) * sizeof(unsigned long), GFP_KERNEL);
    if (!h->event_pool_bits) {
        retval = -ENOMEM;
        vsc_err("malloc event memory for pool bits failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        goto err_out;
    }

    /* ��ʼ����������С */
    h->event_pool_tbl = kzalloc( h->nr_events * sizeof(*h->event_pool_tbl), GFP_KERNEL);
    if (!h->event_pool_tbl) {
        retval = -ENOMEM;
        vsc_err("malloc event memory for pool failed, host is %u.\n", vsc_ctrl_get_host_no(h));
        goto err_out;
    }

    /* �����Ӧ���¼������� */
    for (i = 0; i < h->nr_events; i++) {
        e = kmalloc(sizeof(*e), GFP_KERNEL);
        if (!e) {
            retval = -ENOMEM;
            goto err_out;
        }
        h->event_pool_tbl[i] = e;
    }

    return 0;

err_out:
    vsc_ctrl_info_destroy(h);

    return retval;
}

/**************************************************************************
 ��������  : ��ȡhost���
 ��    ��  : vsc_ctrl_info *h:   host���ƾ��
 �� �� ֵ  : ������host_no������ȫF
**************************************************************************/
unsigned int vsc_ctrl_get_host_no(struct vsc_ctrl_info *h)
{
    if (unlikely(!h)) {
        return -1;
    }

    if (!h->scsi_host) {
        return -1;
    }

    //return h->scsi_host->host_no;
    return h->vbs_host_id;
}

/**************************************************************************
 ��������  : ����host no���ҿ��ƿ�

             WARNNING!!!! 
             ��Ҫ���׵���vsc_ctrl_info_put��
             WARNNING!!!! 
 ��    ��  : hostno:        ���������
 �� �� ֵ  : vsc_ctrl_info *h:   host���ƾ��
**************************************************************************/
struct vsc_ctrl_info * vsc_get_ctrl_by_host( unsigned int host_no )
{
    struct vsc_host_mgr *mgr = NULL;
    struct vsc_ctrl_info *h = NULL;
    __u32 vbs_id = vsc_get_vbs_id_by_host_id(host_no);
    __u32 host_index = vsc_get_host_index_in_vbs(host_no);

    if (host_index >= MAX_HOST_NR_PER_VBS) {
        return NULL;
    }
    mutex_lock(&ctrl_info_list_lock);
    list_for_each_entry(mgr, &g_host_mgr_list, node) {
        if (mgr->vbs_id == vbs_id) {
            h = mgr->host_list[host_index];
            if (h) {
                vsc_ctrl_info_get(h);
            }
            mutex_unlock(&ctrl_info_list_lock);
            return h;
        }
    }
    mutex_unlock(&ctrl_info_list_lock);

    return NULL;
}

static int vsc_add_host_to_mgr(struct vsc_ctrl_info *h, __u32 host_id)
{
    struct vsc_host_mgr *mgr = NULL;
    __u32 vbs_id = vsc_get_vbs_id_by_host_id(host_id);
    __u32 host_index = vsc_get_host_index_in_vbs(host_id);

    if (host_index >= MAX_HOST_NR_PER_VBS) {
        vsc_err("fatal error..., host_id=%d, host_index=%d\n", host_id, host_index);
        return -1;
    }

    mutex_lock(&ctrl_info_list_lock);
    list_for_each_entry(mgr, &g_host_mgr_list, node) {
        if (mgr->vbs_id == vbs_id) {
            if (mgr->host_count >= MAX_HOST_NR_PER_VBS) {
                vsc_err("fatal error..., host_count=%d\n", mgr->host_count);
                mutex_unlock(&ctrl_info_list_lock);
                return -1;
            }

            mgr->host_list[host_index] = h;
            h->silbing_hosts = mgr;
            mgr->host_count++;
            mutex_unlock(&ctrl_info_list_lock);
            return 0;
        }
    }
    mutex_unlock(&ctrl_info_list_lock);

    /* û���ҵ���Ӧ��vbs����Ҫ��� */
    mgr = kmalloc(sizeof(struct vsc_host_mgr), GFP_KERNEL);
    if (!mgr) {
        vsc_err("fatal to alloc vbs_host_mgr\n");
        return -ENOMEM;
    }
    memset(mgr, 0, sizeof(struct vsc_host_mgr));

    mgr->vbs_id = vbs_id;
    mgr->host_list[host_index] = h;
    h->silbing_hosts = mgr;
    mgr->host_count++;
    mutex_lock(&ctrl_info_list_lock);
    list_add_tail(&mgr->node, &g_host_mgr_list);
    mutex_unlock(&ctrl_info_list_lock);
    return 0;
}

/**************************************************************************
 ��������  : ��ȡhost��Ϣ��proc�ӿ�
 ��    ��  : host_info:   ע����Ϣ
 �� �� ֵ  : ����host���ƾ��
**************************************************************************/
#if LINUX_VERSION_CODE < (KERNEL_VERSION(2, 6, 26))
int vsc_hostinfo_proc_read_old(char *page, char **start, 
    off_t off, int count, int *eof, void *data)
{
    struct vsc_ctrl_info *h = NULL;
    int sdev_count = 0;
    struct scsi_device *sdev = NULL;
    int len = 0;

    h = (struct vsc_ctrl_info *)data;
    if (!h) {
        return -EFAULT;
    }

    vsc_ctrl_info_get(h);

    /* ��ȡ�豸��Ŀ */
    shost_for_each_device(sdev, h->scsi_host) {
        sdev_count ++;
    }
    
    /* ��ӡ�����Ϣ */
    len += snprintf((page + len), (count - len), "Host No.:\t%u\n", vsc_ctrl_get_host_no(h));
    len += snprintf((page + len), (count - len), "SCSI_Host ID.:\t%u\n", h->scsi_host->host_no);
    len += snprintf((page + len), (count - len), "Max channel:\t%u\n", h->scsi_host->max_channel);
    len += snprintf((page + len), (count - len), "Max id:\t\t%u\n", h->scsi_host->max_id);
    len += snprintf((page + len), (count - len), "Max lun:\t%u\n", h->scsi_host->max_lun);
    len += snprintf((page + len), (count - len), "Max sg count: \t%u\n", h->scsi_host->sg_tablesize);
    len += snprintf((page + len), (count - len), "Max cmd count:\t%u\n", h->nr_cmds);
    len += snprintf((page + len), (count - len), "Cmd per lun:\t%u\n", h->scsi_host->cmd_per_lun);
    len += snprintf((page + len), (count - len), "Host status:\t%s\n", (h->suspend) ? "Suspend" : "Running");
    len += snprintf((page + len), (count - len), "Host blocked:\t%s\n", (h->scsi_host->host_self_blocked)? "Blocked" : "Unblock");
    len += snprintf((page + len), (count - len), "Device count:\t%d\n", sdev_count);
    len += snprintf((page + len), (count - len), "Cmd sn: \t%u (Overflow count: %u)\n", (__u32)((h->cmd_sn) & 0xFFFFFFFF), (__u32)((h->cmd_sn)>>32));
    len += snprintf((page + len), (count - len), "Event sn:\t%llu\n", h->event_sn);
    len += snprintf((page + len), (count - len), "Attatched status:\t%s\n", (h->file) ? "Attached" : "Detached");
    len += snprintf((page + len), (count - len), "Abort cmd count:\t%u\n", h->stat.abort_cmd_count);
    len += snprintf((page + len), (count - len), "Reset device count:\t%u\n", h->stat.reset_dev_count);
    len += snprintf((page + len), (count - len), "Vsc read fail count:\t%u\n", h->stat.read_fail_count);
    len += snprintf((page + len), (count - len), "Vsc write fail count:\t%u\n", h->stat.write_fail_count);
    len += snprintf((page + len), (count - len), "Host Running Cmd    :\t%u\n", h->io_running);

    len += snprintf((page + len), (count - len), "\nGet Command Times :\t%u\n", h->get_cmd_times);
    len += snprintf((page + len), (count - len), "Get Command Total :\t%u\n", h->get_cmd_total);
    len += snprintf((page + len), (count - len), "Put Response Times:\t%u\n", h->put_rsp_times);
    len += snprintf((page + len), (count - len), "Put Response Total:\t%u\n", h->put_rsp_total);

#ifdef __VSC_LATENCY_DEBUG__
    len += snprintf((page + len), (count - len), "\nWrite Cmd Count   :\t%llu\n", h->write_cmd_count);
    if (h->write_cmd_count) {
        len += snprintf((page + len), (count - len), "Write Stage1 Lat:\t%llu\n", h->write_stage1_total/h->write_cmd_count);
        len += snprintf((page + len), (count - len), "Write Stage2 Lat:\t%llu\n", h->write_stage2_total/h->write_cmd_count);
        len += snprintf((page + len), (count - len), "Write Stage3 Lat:\t%llu\n", h->write_stage3_total/h->write_cmd_count);
        len += snprintf((page + len), (count - len), "Write Total Lat :\t%llu\n", h->write_total/h->write_cmd_count);
    }
    len += snprintf((page + len), (count - len), "\nRead Cmd Count    :\t%llu\n", h->read_cmd_count);
    if (h->read_cmd_count) {
        len += snprintf((page + len), (count - len), "Read Stage1 Lat:\t%llu\n", h->read_stage1_total/h->read_cmd_count);
        len += snprintf((page + len), (count - len), "Read Stage2 Lat:\t%llu\n", h->read_stage2_total/h->read_cmd_count);
        len += snprintf((page + len), (count - len), "Read Stage3 Lat:\t%llu\n", h->read_stage3_total/h->read_cmd_count);
        len += snprintf((page + len), (count - len), "Read Total Lat :\t%llu\n", h->read_total/h->read_cmd_count);
    }
#endif

    spin_lock_bh(&h->lock);
    len += snprintf((page + len), (count - len), "\nReq Queue Count   :\t%u\n", list_size(&h->reqQ));
    len += snprintf((page + len), (count - len), "Cmp Queue Count   :\t%u\n", list_size(&h->cmpQ));
    len += snprintf((page + len), (count - len), "Rsp Queue Count   :\t%u\n", list_size(&h->rspQ));
    spin_unlock_bh(&h->lock);

    vsc_ctrl_info_put(h);
    return len;
}

int vsc_hostinfo_proc_write_old(struct file *file, const char *buffer, 
        unsigned long count, void *data)
{
    char buf[128];
    int retval = 0;
#ifdef __VSC_LATENCY_DEBUG__
    struct vsc_ctrl_info *h = NULL;
    struct vsc_host_mgr *mgr = NULL;
    int j;
#endif

    if (unlikely(!file)) {
        retval = -EFAULT;
    }
    if (count < 1) {
        return -EINVAL;
    }
    if (copy_from_user(buf, buffer, 1)) {
        vsc_err("seq write failed\n");
        retval = -EFAULT;
    }

    /* �ݲ�֧������ֵ */
    if (!strncmp(buf, "4", 1)) {
        io_per_host=4;
        io_per_host_shift=2;
        vsc_info("io_per_host change to %d, io_per_host_shift=%d\n", io_per_host, io_per_host_shift);
    }
    else if (!strncmp(buf, "2", 1)) {
        io_per_host=2;
        io_per_host_shift=1;
        vsc_info("io_per_host change to %d, io_per_host_shift=%d\n", io_per_host, io_per_host_shift);
    }
    else if (!strncmp(buf, "1", 1)) {
        io_per_host=1;
        io_per_host_shift=0;
        vsc_info("io_per_host change to %d, io_per_host_shift=%d\n", io_per_host, io_per_host_shift);
    }
    else if (!strncmp(buf, "0", 1)) {
        io_per_host=0;
        vsc_info("io_per_host change to %d\n", io_per_host);
    }
    
#ifdef __VSC_LATENCY_DEBUG__
    if (!strncmp(buf, "clear", 5)) {
        /* ���ioͳ�� */
        mutex_lock(&ctrl_info_list_lock);
        list_for_each_entry(mgr, &g_host_mgr_list, node) {
            if (mgr->host_count > MAX_HOST_NR_PER_VBS) {
                vsc_err("invalid host_count=%d", mgr->host_count);
                continue;
            }
            for (j=0;j<mgr->host_count;j++) {
                if(!mgr->host_list[j]) {
                    continue;
                }

                h = mgr->host_list[j];
                spin_lock_bh(&h->lock);
                h->get_cmd_times = 0;
                h->get_cmd_total = 0;
                h->get_cdb_times = 0;
                h->get_cdb_total = 0;
                h->put_rsp_times = 0;
                h->put_rsp_total = 0;

                h->write_cmd_count = 0;
                h->read_cmd_count = 0;

                h->write_stage1_total = 0;
                h->write_stage2_total = 0;
                h->write_stage3_total = 0;
                h->write_total = 0;

                h->read_stage1_total = 0;
                h->read_stage2_total = 0;
                h->read_stage3_total = 0;
                h->read_total = 0;
                spin_unlock_bh(&h->lock);
            }
        }
    }
    else {
        vsc_err("invalid command, %s\n", buf);
    }
#endif

    return count;
}

#else
static int vsc_hostinfo_proc_read(struct seq_file *v_pstFile, void *unused)
{
    struct vsc_ctrl_info *h = NULL;
    int sdev_count = 0;
    struct scsi_device *sdev = NULL;

    h = (struct vsc_ctrl_info *)v_pstFile->private;
    if (!h) {
        return -EFAULT;
    }

    vsc_ctrl_info_get(h);

    /* ��ȡ�豸��Ŀ */
    shost_for_each_device(sdev, h->scsi_host) {
        sdev_count ++;
    }
    
    /* ��ӡ�����Ϣ */
    seq_printf(v_pstFile, "Host No.:\t%u\n", vsc_ctrl_get_host_no(h));
    seq_printf(v_pstFile, "SCSI_Host ID.:\t%u\n", h->scsi_host->host_no);
    seq_printf(v_pstFile, "Max channel:\t%u\n", h->scsi_host->max_channel);
    seq_printf(v_pstFile, "Max id:\t\t%u\n", h->scsi_host->max_id);
#if LINUX_VERSION_CODE < (KERNEL_VERSION(3, 17, 0))
    seq_printf(v_pstFile, "Max lun:\t%u\n", h->scsi_host->max_lun);
#else
    seq_printf(v_pstFile, "Max lun:\t%llu\n", h->scsi_host->max_lun);
#endif
    seq_printf(v_pstFile, "Max sg count: \t%u\n", h->scsi_host->sg_tablesize);
    seq_printf(v_pstFile, "Max cmd count:\t%u\n", h->nr_cmds);
    seq_printf(v_pstFile, "Cmd per lun:\t%u\n", h->scsi_host->cmd_per_lun);
    seq_printf(v_pstFile, "Host status:\t%s\n", (h->suspend) ? "Suspend" : "Running");
    seq_printf(v_pstFile, "Host blocked:\t%s\n", (h->scsi_host->host_self_blocked)? "Blocked" : "Unblock");
    seq_printf(v_pstFile, "Device count:\t%d\n", sdev_count);
    seq_printf(v_pstFile, "Cmd sn: \t%u (Overflow count: %u)\n", (__u32)((h->cmd_sn) & 0xFFFFFFFF), (__u32)((h->cmd_sn)>>32));
    seq_printf(v_pstFile, "Event sn:\t%llu\n", h->event_sn);
    seq_printf(v_pstFile, "Attatched status:\t%s\n", (h->file) ? "Attached" : "Detached");
    seq_printf(v_pstFile, "Abort cmd count:\t%u\n", h->stat.abort_cmd_count);
    seq_printf(v_pstFile, "Reset device count:\t%u\n", h->stat.reset_dev_count);
    seq_printf(v_pstFile, "Vsc read fail count:\t%u\n", h->stat.read_fail_count);
    seq_printf(v_pstFile, "Vsc write fail count:\t%u\n", h->stat.write_fail_count);
    seq_printf(v_pstFile, "Host Running Cmd    :\t%u\n", h->io_running);

    seq_printf(v_pstFile, "\nGet Command Times :\t%u\n", h->get_cmd_times);
    seq_printf(v_pstFile, "Get Command Total :\t%u\n", h->get_cmd_total);
    seq_printf(v_pstFile, "Put Response Times:\t%u\n", h->put_rsp_times);
    seq_printf(v_pstFile, "Put Response Total:\t%u\n", h->put_rsp_total);

#ifdef __VSC_LATENCY_DEBUG__
    seq_printf(v_pstFile, "\nWrite Cmd Count   :\t%llu\n", h->write_cmd_count);
    if (h->write_cmd_count) {
        seq_printf(v_pstFile, "Write Stage1 Lat:\t%llu\n", h->write_stage1_total/h->write_cmd_count);
        seq_printf(v_pstFile, "Write Stage2 Lat:\t%llu\n", h->write_stage2_total/h->write_cmd_count);
        seq_printf(v_pstFile, "Write Stage3 Lat:\t%llu\n", h->write_stage3_total/h->write_cmd_count);
        seq_printf(v_pstFile, "Write Total Lat :\t%llu\n", h->write_total/h->write_cmd_count);
    }
    seq_printf(v_pstFile, "\nRead Cmd Count    :\t%llu\n", h->read_cmd_count);
    if (h->read_cmd_count) {
        seq_printf(v_pstFile, "Read Stage1 Lat:\t%llu\n", h->read_stage1_total/h->read_cmd_count);
        seq_printf(v_pstFile, "Read Stage2 Lat:\t%llu\n", h->read_stage2_total/h->read_cmd_count);
        seq_printf(v_pstFile, "Read Stage3 Lat:\t%llu\n", h->read_stage3_total/h->read_cmd_count);
        seq_printf(v_pstFile, "Read Total Lat :\t%llu\n", h->read_total/h->read_cmd_count);
    }
#endif

    spin_lock_bh(&h->lock);
    seq_printf(v_pstFile, "\nReq Queue Count   :\t%u\n", list_size(&h->reqQ));
    seq_printf(v_pstFile, "Cmp Queue Count   :\t%u\n", list_size(&h->cmpQ));
    seq_printf(v_pstFile, "Rsp Queue Count   :\t%u\n", list_size(&h->rspQ));
    spin_unlock_bh(&h->lock);

    vsc_ctrl_info_put(h);
    return 0;
}
static int vsc_seq_open_dev(struct inode *inode,struct file *file)
{
#if LINUX_VERSION_CODE < (KERNEL_VERSION(3, 10, 0))
    return single_open(file, vsc_hostinfo_proc_read, PDE(inode)->data);
#else
    return single_open(file, vsc_hostinfo_proc_read, PDE_DATA(inode));
#endif
}

static ssize_t vsc_seq_write(struct file *file, const char __user *user_ptr,
        size_t len, loff_t *pos)
{
    char buf[128];
    int retval = 0;
#ifdef __VSC_LATENCY_DEBUG__
    struct vsc_ctrl_info *h = NULL;
    struct vsc_host_mgr *mgr = NULL;
    int j;
#endif

    if (unlikely(!file)) {
        retval = -EFAULT;
        goto errout;
    }

    if (copy_from_user(buf, user_ptr, len)) {
        vsc_err("seq write failed\n");
        retval = -EFAULT;
        goto errout;
    }

    /* �ݲ�֧������ֵ */
    if (!strncmp(buf, "4", 1)) {
        io_per_host=4;
        io_per_host_shift=2;
        vsc_info("io_per_host change to %d, io_per_host_shift=%d\n", io_per_host, io_per_host_shift);
    }
    else if (!strncmp(buf, "2", 1)) {
        io_per_host=2;
        io_per_host_shift=1;
        vsc_info("io_per_host change to %d, io_per_host_shift=%d\n", io_per_host, io_per_host_shift);
    }
    else if (!strncmp(buf, "1", 1)) {
        io_per_host=1;
        io_per_host_shift=0;
        vsc_info("io_per_host change to %d, io_per_host_shift=%d\n", io_per_host, io_per_host_shift);
    }
    else if (!strncmp(buf, "0", 1)) {
        io_per_host=0;
        vsc_info("io_per_host change to %d\n", io_per_host);
    }
    
#ifdef __VSC_LATENCY_DEBUG__
    if (!strncmp(buf, "clear", 5)) {
        /* ���ioͳ�� */
        mutex_lock(&ctrl_info_list_lock);
        list_for_each_entry(mgr, &g_host_mgr_list, node) {
            if (mgr->host_count > MAX_HOST_NR_PER_VBS) {
                vsc_err("invalid host_count=%d", mgr->host_count);
                continue;
            }
            for (j=0;j<mgr->host_count;j++) {
                if(!mgr->host_list[j]) {
                    continue;
                }

                h = mgr->host_list[j];
                spin_lock_bh(&h->lock);
                h->get_cmd_times = 0;
                h->get_cmd_total = 0;
                h->get_cdb_times = 0;
                h->get_cdb_total = 0;
                h->put_rsp_times = 0;
                h->put_rsp_total = 0;

                h->write_cmd_count = 0;
                h->read_cmd_count = 0;

                h->write_stage1_total = 0;
                h->write_stage2_total = 0;
                h->write_stage3_total = 0;
                h->write_total = 0;

                h->read_stage1_total = 0;
                h->read_stage2_total = 0;
                h->read_stage3_total = 0;
                h->read_total = 0;
                spin_unlock_bh(&h->lock);
            }
        }
    }
    else {
        vsc_err("invalid command, %s\n", buf);
    }
#endif

    return len;
errout:
    return retval;
}

struct file_operations g_proc_host_vsc_ops =
{
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2, 6, 27)
    .owner = THIS_MODULE,
#endif
    .open = vsc_seq_open_dev,
    .read = seq_read,
    .write = vsc_seq_write,
    .llseek = seq_lseek,
    .release = NULL,
};
#endif

#if LINUX_VERSION_CODE < (KERNEL_VERSION(3, 17, 0))
static int vsc_user_scan(struct Scsi_Host *shost, unsigned int channel, unsigned int id, unsigned int lun)
{
    vsc_info("hostno: %d, try to rescan device: channel: %d, id: %d, lun: %d\n",
                shost->host_no, channel, id, lun);

    return 0;
}
#else
static int vsc_user_scan(struct Scsi_Host *shost, unsigned int channel, unsigned int id, unsigned long long lun)
{
    vsc_info("hostno: %d, try to rescan device: channel: %d, id: %d, lun: %llu\n",
                shost->host_no, channel, id, lun);
    return 0;
}
#endif   
 
static struct scsi_transport_template vsc_transportt =
{
    .user_scan = vsc_user_scan,
    .device_size = VSC_SCSI_DEVICE_RESERVE_SIZE,
};

struct Scsi_Host *vsc_scsi_host_lookup(unsigned int host_no)
{
    struct vsc_ctrl_info *h = NULL;

    h = vsc_get_ctrl_by_host(host_no);
    if (NULL == h || NULL == h->scsi_host)
    {
        return NULL;
    }

    vsc_ctrl_info_put(h);

    return scsi_host_get(h->scsi_host);
}

/**************************************************************************
 ��������  : ���host��ϵͳ��
 ��    ��  : host_info:   ע����Ϣ
 �� �� ֵ  : ����host���ƾ��
**************************************************************************/
struct vsc_ctrl_info *vsc_register_host( struct vsc_ioctl_cmd_add_host *host_info )
{
    struct vsc_ctrl_info *h = NULL;
    struct Scsi_Host *sh  = NULL;
    struct vsc_scsi_struct *vss = NULL;
    long scsi_add_retval = -EFAULT;
    char proc_file_name[VSC_PROC_FILE_NAME_LEN];
    struct proc_dir_entry  *proc_file = NULL;
    int err_retval = 0;
    int sys_host_id = 0;
    
    if (!host_info) {
        return ERR_PTR(-EINVAL);
    }

    if (check_host_info(host_info)) {
        vsc_err("invalid param in host_info when add host!\n");
        return ERR_PTR(-EINVAL);
    }

    /* ��ֹ����ע����ͬ��HOST���������� */
    mutex_lock(&ctrl_host_reg_lock);
    /* ���ϵͳ���Ƿ���ڶ�Ӧ��host */
    /*scsi_host_lookup�������ܲ���host no ����65535��scsi_host*/
    sh = vsc_scsi_host_lookup(host_info->host);
    if (sh) {
        sys_host_id = sh->host_no;
        scsi_host_put(sh);
        sh = NULL;
        err_retval = -EEXIST;
        
        h = vsc_get_ctrl_by_host(host_info->host);
        if (!h) {
            err_retval = -ENODEV; /* [review] �в���������û�У����ظ��û���������û��������δ���
                                        �����в�������в�һ�µĳ�������˵�����������ص�ϵͳ������߷Ƿ������� */
            vsc_err("vsc_register_host(): host %u found in ml, but info not found in driver.\n", host_info->host);
        }
        else {
            /* vbs����ʱ����sys host id�ش���vbs */
            host_info->sys_host_id = sys_host_id;
            vsc_ctrl_info_put(h);
        }
        h = NULL;
        goto err_out;
    }

    /* ����Ƿ��ж�Ӧ��host */
    h = vsc_get_ctrl_by_host(host_info->host);
    if (h) {
        vsc_ctrl_info_put(h);
        h = NULL;
        //err_retval = -EEXIST;
        err_retval = -ENODEV; 
        vsc_err("vsc_register_host(): host %u info found in driver but host not found in ml.\n", host_info->host);
        goto err_out;
    }

    /* ע��scs host����������vsc_ctrl_info���ڴ� */
    h = vsc_ctrl_info_alloc();
    if (!h) {
        vsc_err("kmalloc for vsc_ctrl_info failed, host is %u.\n", host_info->host);
        err_retval = -ENOMEM;
        goto err_out;
    }

    /* ע��scsi host����������vsc_ctrl_info���ڴ� */
    vss = vsc_scsi_if_alloc();
    if (!vss || IS_ERR(vss)) {
        vsc_err("register scsi driver template failed, host is %u.\n", host_info->host);
        err_retval = -ENOMEM;
        goto err_out;
    }
    sh = vsc_scsi_if_get_host(vss);
    vsc_scsi_if_set_priv(vss, h);
    
    /* ��ʼ��host���ƾ�� */
    if (vsc_ctrl_init(h, sh, host_info->max_nr_cmds, host_info->host)) {
        vsc_err("init ctrl info failed, host is %u.\n", host_info->host);
        err_retval = -EFAULT;
        goto err_out;
    }

    //sh->host_no = host_info->host;
    sh->io_port = 0;
    sh->n_io_port = 0;
    sh->this_id = -1;
    sh->max_channel = host_info->max_channel;
    sh->max_cmd_len = host_info->max_cmd_len;
    sh->max_lun = host_info->max_lun;
    sh->max_id = host_info->max_id;
    sh->can_queue = h->nr_cmds;
    sh->cmd_per_lun = host_info->cmd_per_lun;
    sh->shost_gendev.parent = NULL;
    sh->sg_tablesize = host_info->sg_count;
    sh->irq = 0;
    sh->unique_id = sh->irq;
    
    /* ֪ͨSCSI�в����host */
    scsi_add_retval = scsi_add_host(sh, NULL);
    if (scsi_add_retval) {
        vsc_err("add scsi host failed, host = %u, ret = %ld\n", sh->host_no, scsi_add_retval);
        err_retval = scsi_add_retval;
        goto err_out;
    }

     /* ����procĿ¼�ļ� */
    snprintf(proc_file_name, VSC_PROC_FILE_NAME_LEN, "host%d", sh->host_no);
    //snprintf(proc_file_name, VSC_PROC_FILE_NAME_LEN, "host%d", host_info->host);
#if LINUX_VERSION_CODE > (KERNEL_VERSION(2, 6, 25))   
    proc_file = proc_create_data(proc_file_name, S_IRUGO, proc_vsc_root, &g_proc_host_vsc_ops, h);
    if (!proc_file) {
        vsc_err("vsc_register_host(): create vsc root proc file error, host is %u.\n", host_info->host);
        err_retval = -ENOMEM;
        goto err_out;
    }
#else
    proc_file = create_proc_entry(proc_file_name, S_IRUGO, proc_vsc_root);
    if (!proc_file) {
        vsc_err("vsc_register_host(): create vsc root proc file error, host is %u.\n", host_info->host);
        err_retval = -ENOMEM;
        goto err_out;
    }
    proc_file->read_proc=vsc_hostinfo_proc_read_old;
    proc_file->write_proc=vsc_hostinfo_proc_write_old;
    proc_file->data=h;
#endif
    /* ��hostָ����뵽������ */
    err_retval = vsc_add_host_to_mgr(h, host_info->host);
    if (err_retval)
    {
        goto err_out;
    }
    /* ��host no�ش���vbs */
    host_info->sys_host_id = sh->host_no;
    
    mutex_unlock(&ctrl_host_reg_lock);

    return h;

err_out:
    if (!scsi_add_retval) {
        scsi_remove_host(sh);
        vsc_err("vsc_register_host(): err_out, host %u removed in ml.", host_info->host);
    }
    if (proc_file) {
        remove_proc_entry(proc_file_name, proc_vsc_root);
        proc_file = NULL;
    }
    if (h) {
        vsc_ctrl_info_put(h); 
        vsc_err("vsc_register_host(): err_out, host %u info destroied in driver.", host_info->host);
    }

    if (vss) {
        vsc_scsi_if_free(vss);
    }
    mutex_unlock(&ctrl_host_reg_lock);
    return ERR_PTR(err_retval);
}

/**************************************************************************
 ��������  : ɾ��ָ����host
 ��    ��  : h:  scsi���ƾ�� 
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
static int vsc_do_remove_host(struct vsc_ctrl_info *h, int remove_host)
{
    struct Scsi_Host *sh = NULL;
    struct vsc_scsi_struct *vss = NULL;
    char proc_file_name[VSC_PROC_FILE_NAME_LEN];

    if (unlikely(!h)) {
        vsc_err("scsi ctrl info is null.\n");
        return -EINVAL;
    }

    sh = h->scsi_host;
    if (unlikely(!sh)) {
        vsc_err("scsi host is null, ctrl info is %p, host is %u.\n", h, vsc_ctrl_get_host_no(h));
        return -EFAULT;
    }

    vss = vsc_scsi_if_get_vss(sh);
    if (unlikely(!vss)) {
        vsc_err("vss is null, ctrl info is %p, host is %u.\n", h, vsc_ctrl_get_host_no(h));
        return -EFAULT;
    }

    del_timer_sync(&h->target_abnormal_timer);

    spin_lock_bh(&h->lock);
    h->file = NULL;
    spin_unlock_bh(&h->lock);

    /* ɾ��������proc�ļ� */
    snprintf(proc_file_name, VSC_PROC_FILE_NAME_LEN, "host%d", sh->host_no);
    remove_proc_entry(proc_file_name, proc_vsc_root);

    /* �Ӷ�����ɾ������ */
    //list_del(&h->list);

    if (remove_host) {

        /* ��ֹɾ��ʱ�����������豸 */
        vsc_resume_host(h);

        /* ���������ڴ����е��¼� */
        vsc_abort_all_cmd(h);

        /* ɾ���豸ʱ������������ */
        vsc_abort_all_event(h);
        scsi_remove_host(sh);
        vsc_scsi_if_free(vss);
    } else {
        /* ж������ʱ�����½����������� */
        vsc_requeue_all_cmd(h);
    }

    /* �ͷ��������Դ */
    vsc_ctrl_info_put(h);
    
    return 0;
}

/**************************************************************************
 ��������  : ɾ��ָ����host
 ��    ��  : vsc_ctrl_info *h:   host���ƾ��
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
int vsc_remove_host(struct vsc_ctrl_info *h)
{
    int retval = 0;
    struct vsc_host_mgr *mgr;
    __u32 host_index = vsc_get_host_index_in_vbs(h->vbs_host_id);
    
    mutex_lock(&ctrl_info_list_lock);
    mgr = h->silbing_hosts;
    
    retval = vsc_do_remove_host(mgr->host_list[host_index], 1);
    mgr->host_list[host_index] = NULL;
    mgr->host_count--;

    /* ���host����host mgr���Ѿ�û��ʣ��host���ͷ�host mgr */
    if (mgr->host_count == 0)
    {
        list_del(&mgr->node);
        kfree(mgr);
    }
    mutex_unlock(&ctrl_info_list_lock);

    return retval;
}

/**************************************************************************
 ��������  : �ͷ����п��ƾ��
 ��    ��  :
 �� �� ֵ  : ��
**************************************************************************/
void vsc_remove_all_host_mgr( void ) 
{
    struct vsc_host_mgr *mgr;
    struct vsc_host_mgr *temp;
    __u32 i;

    mutex_lock(&ctrl_info_list_lock);
    list_for_each_entry_safe(mgr, temp, &g_host_mgr_list, node) {
        if (mgr->host_count > MAX_HOST_NR_PER_VBS) {
            vsc_err("invalid host_count=%d", mgr->host_count);
            continue;
        }
        for (i=0; i<mgr->host_count; i++) {
            mgr->host_list[i] = NULL;
        }
        list_del(&mgr->node);
        kfree(mgr);
    }
    mutex_unlock(&ctrl_info_list_lock);
}

int vsc_load_host_data(struct vsc_ctrl_info *h, void *data, int size)
{
    struct vsc_scsi_data_head *scsi_head = data;
    struct vsc_scsi_data_struct *scsi_data = NULL;

    /* ����ڴ�ħ���Ƿ���ȷ */
    if (scsi_head->magic != VSC_DATA_MAGIC) {
        return 0;
    }

    /* ���汾��һ�µ�����£����ݷ�ʽ��ֱ�Ӹ������� */
    if (scsi_head->ver_major == VSC_DATA_VER_MAJOR) {
        struct vsc_scsi_data_struct tmp_data;
        memset(&tmp_data, 0, sizeof(tmp_data));

        if (scsi_head->ver_minor > VSC_DATA_VER_MINOR) {

            /*  ���ԭʼ���ݰ汾�Ƚ��£����洢�����ݴ�СС�ڵ�ǰ��С������Ϊ������Ч */
            if (scsi_head->size < sizeof(struct vsc_scsi_data_struct)) {
                vsc_err("load host data failed, host data is invalid, length is invald, %lu to %lu\n",
                        scsi_head->size, sizeof(struct vsc_scsi_data_struct));
                return 0;
            }

            /* �������� */
            memcpy(&tmp_data, data, sizeof(tmp_data));
            /* ���δʹ�õ����� */
            memset(((char *)data) + sizeof(tmp_data), 0, scsi_head->size - sizeof(tmp_data));

            tmp_data.head.ver_minor = VSC_DATA_VER_MINOR;
            scsi_data = &tmp_data;
        } else if (scsi_head->ver_minor < VSC_DATA_VER_MINOR) {
            /*  ���ԭʼ���ݰ汾�ȽϾɣ����洢�����ݴ�С���ڵ�ǰ��С������Ϊ������Ч */
            if (scsi_head->size > sizeof(struct vsc_scsi_data_struct)) {
                vsc_err("load host data failed, host data is invalid, length is invald, %lu to %lu\n",
                        scsi_head->size, sizeof(struct vsc_scsi_data_struct));
                return 0;
            }

            /* �������ݣ�δ���Ʋ���Ĭ��Ϊ0*/
            memcpy(&tmp_data, data, sizeof(tmp_data));
            tmp_data.head.ver_minor = VSC_DATA_VER_MINOR;
            scsi_data = &tmp_data;
        } else {
            scsi_data = data;            
        }

        /* �������� */
        scsi_data = (struct vsc_scsi_data_struct*)scsi_head;
        spin_lock_bh(&h->lock);
        h->cmd_sn = scsi_data->cmd_sn;
        h->event_sn = scsi_data->event_sn;
        h->suspend = scsi_data->suspend;
        h->vbs_host_id = scsi_data->vbs_host_id;
        memcpy(&h->stat, &scsi_data->stat, sizeof(struct vsc_ctrl_statics));
        spin_unlock_bh(&h->lock);

    } else {
        /* ���汾�Ų�һ�µ�������������� */
        /* TODO */
    }

    return 0;
}

int vsc_load_host(struct vsc_scsi_struct *vss, void *data, int size)
{
    struct vsc_ctrl_info *h = NULL;
    struct Scsi_Host *sh  = NULL;
    char proc_file_name[VSC_PROC_FILE_NAME_LEN];
    struct proc_dir_entry  *proc_file = NULL;
    int retval = 0;

    if (!vss) {
        return -EINVAL;
    }

    sh = vsc_scsi_if_get_host(vss);
    if (!sh) {
        return -EFAULT;
    }
    mutex_lock(&ctrl_host_reg_lock);

    h = vsc_ctrl_info_alloc();
    if (!h) {
        vsc_err("kmalloc for vsc_ctrl_info failed, host is %u.\n", sh->host_no);
        retval = -ENOMEM;
        goto err_out;
    }

    if (vsc_ctrl_init(h, sh, sh->can_queue, h->vbs_host_id)) {
        vsc_err("init ctrl info failed, host is %u.\n", sh->host_no);
        retval = -EFAULT;
        goto err_out;
    }

    if (vsc_load_host_data(h, data, size)) {
        vsc_err("load host data failed.\n");
        retval = -EFAULT;
        goto err_out;
    }

    snprintf(proc_file_name, VSC_PROC_FILE_NAME_LEN, "host%d", sh->host_no);
#if LINUX_VERSION_CODE > (KERNEL_VERSION(2, 6, 25))   
    proc_file = proc_create_data(proc_file_name, S_IRUGO, proc_vsc_root, &g_proc_host_vsc_ops, h);
    if (!proc_file) {
        vsc_err("add scsi host failed, create proc file error, host is %u.\n", sh->host_no);
        retval = -ENOMEM;
        goto err_out;
    }
#else
    proc_file = create_proc_entry(proc_file_name, S_IRUGO, proc_vsc_root);
    if (!proc_file) {
        vsc_err("add scsi host failed, create proc file error, host is %u.\n", sh->host_no);
        retval = -ENOMEM;
        goto err_out;
    }
    proc_file->read_proc=vsc_hostinfo_proc_read_old;
    proc_file->write_proc=vsc_hostinfo_proc_write_old;
    proc_file->data=h;
#endif

    /* ��hostָ����뵽������ */
    vsc_add_host_to_mgr(h, h->vbs_host_id);

    mutex_unlock(&ctrl_host_reg_lock);

    vsc_scsi_if_set_priv(vss, h);    
    return 0;

err_out:
    if (proc_file) {
        remove_proc_entry(proc_file_name, proc_vsc_root);
        proc_file = NULL;
    }

    if (h) {
        vsc_ctrl_info_put(h);
    }

    mutex_unlock(&ctrl_host_reg_lock);
    return retval;
}

int vsc_unload_host(struct vsc_scsi_struct *vss, void *data, int size)
{
    struct vsc_ctrl_info *h = NULL;
    struct vsc_scsi_data_struct *scsi_data = data;
    struct vsc_host_mgr *mgr = NULL;
    __u32 host_index = MAX_HOST_NR_PER_VBS;

    if (!vss || !scsi_data)
    {
        vsc_err("NULL point. vss: %p,  scsi_data: %p.\n", vss, scsi_data);
        return 0;
    }

    h = vsc_scsi_if_get_priv(vss);
    if (!h) {
        vsc_err("unload scsi host faied\n");
        return 0;
    }
    host_index = vsc_get_host_index_in_vbs(h->vbs_host_id);

    mutex_lock(&ctrl_info_list_lock);
    mgr = h->silbing_hosts;
    spin_lock_bh(&h->lock);
    scsi_data->head.magic = VSC_DATA_MAGIC;
    scsi_data->head.ver_major = VSC_DATA_VER_MAJOR;
    scsi_data->head.ver_minor = VSC_DATA_VER_MINOR;
    scsi_data->head.size = sizeof(struct vsc_scsi_data_struct);
    scsi_data->cmd_sn = h->cmd_sn;
    scsi_data->event_sn = h->event_sn;
    scsi_data->suspend = h->suspend;
    scsi_data->vbs_host_id = h->vbs_host_id;
    memcpy(&scsi_data->stat, &h->stat, sizeof(struct vsc_ctrl_statics));
    spin_unlock_bh(&h->lock);

    vsc_do_remove_host(h, 0);
    if (NULL != mgr && host_index < MAX_HOST_NR_PER_VBS)
    {
        if (NULL != mgr->host_list[host_index])
        {
            mgr->host_list[host_index] = NULL;
            mgr->host_count--;
        }
        else
        {
            vsc_err("scsi host already unload. host_index = %u.\n", host_index);
        }

        /* ���host����host mgr���Ѿ�û��ʣ��host���ͷ�host mgr */
        if (mgr->host_count == 0)
        {
            list_del(&mgr->node);
            kfree(mgr);
        }
    }
    mutex_unlock(&ctrl_info_list_lock);

    return 0;
}

/*
 * vsc scsi�ӿ�ע��ģ��
 */ 
static struct vsc_scsi_host_operation vsc_scsi_host_op = {
    .sht                      = &vsc_driver_template,
    .stt                      = &vsc_transportt,
    .load                     = vsc_load_host,
    .unload                   = vsc_unload_host,
};

/**************************************************************************
 ��������  : vsc������ʼ��
 ��    ��  :
 �� �� ֵ  : 0�� �ɹ���������������
**************************************************************************/
static int __init vsc_init( void )
{
    int retval;
    
    printk(banner);

    switch(io_per_host){
        case 0:
            break;
        case 1:
            io_per_host_shift = 0;
            break;
        case 2:
            io_per_host_shift = 1;
            break;
        case 4:
            io_per_host_shift = 2;
            break;
        default:
            vsc_info("invalid io_per_host = %d\n", io_per_host);
            return -EINVAL;
    }
    vsc_info("io_per_host = %d io_per_host_shift = %d\n", io_per_host, io_per_host_shift);

    INIT_LIST_HEAD(&g_host_mgr_list);

    /* ��ʼ��GPL��ϵͳ���� */
    retval = vsc_sym_init();
    if (retval) {
        vsc_err("vsc_sym_init failed, ret = %d\n", retval);
        goto errout1;
    }

    /* 
       �û�̬�����κϲ������ݺ�һ�κϲ�д���ݣ�
       ��һ�ζ�scsi msg+cdb��
       �ڶ��ζ�vsc_scsi_data_msg+vsc_scsi_data_msg+iovecs�����SCSI_MAX_DATA_BUF_SIZE�ֽ�
       дrspʱ���ڴ��СΪSCSI_MAX_DATA_BUF_SIZE+sizeof(struct vsc_scsi_rsp_msg)
       ͨ��mempoolԤ���ڴ棬����rsp��Ԥ������
     */
     /* sizeof(__u32)*2: Ϊbuffer����ͷβmagicУ�飬��ǰ���ֲ��ڴ������ */
#if LINUX_VERSION_CODE > (KERNEL_VERSION(2, 6, 22))
    scsi_buf_slab = kmem_cache_create("vsc_scsi_buf",
            MAX_SCSI_DATA_AND_RSP_LENGTH+sizeof(__u32)*2, 0, 0, NULL);
    if (!scsi_buf_slab) {
        vsc_err("failed to create rsp slab");
        goto errout2;
    }
#else
    scsi_buf_slab = kmem_cache_create("vsc_scsi_buf",
            MAX_SCSI_DATA_AND_RSP_LENGTH+sizeof(__u32)*2, 0, 0, NULL, NULL);
    if (!scsi_buf_slab) {
        vsc_err("failed to create rsp slab");
        goto errout2;
    }
#endif
    /* mempool����ͨ��mempool_alloc_slab���䣬ϵͳ���䲻������ʹ��Ԥ����MIN_SCSI_CMD_RESERVED���ṹ */
    scsi_buf_pool = mempool_create(MIN_SCSI_CMD_RESERVED, mempool_alloc_slab,
            mempool_free_slab, scsi_buf_slab);
    if (!scsi_buf_pool) {
        vsc_err("mempool create failed");
        goto errout3;
    }

    retval = vsc_scsi_if_register(&vsc_scsi_host_op);
    if (retval != 0) {
        vsc_err("vsc_scsi_if_register failed, ret:%d.\n", retval);
        goto errout4;
    }

    /* ��ʼ����������ӿ� */
    retval = vsc_ioctl_init();
    if (retval) {
        vsc_err("vsc_ioctl_init failed, ret:%d.\n", retval);
        goto errout5;
    }

    return 0;

errout5:
    vsc_scsi_if_unregister();
errout4:
    if (scsi_buf_pool) {
        mempool_destroy(scsi_buf_pool);
    }
errout3:
    if (scsi_buf_slab) {
        kmem_cache_destroy(scsi_buf_slab);
    }
errout2:
    vsc_sym_exit();
errout1:

    vsc_err("Virtual storage controller driver initialize failed, ret = %d\n", retval);
    return retval;
}

/**************************************************************************
 ��������  : vsc�����˳�
 ��    ��  :
 �� �� ֵ  : ��
**************************************************************************/
static void __exit vsc_exit( void )
{
    /*�Ȱѿ����豸ɾ�������ж������Ľ���*/
    vsc_ioctl_exit();

    vsc_scsi_if_unregister();
    vsc_remove_all_host_mgr();

    if (scsi_buf_pool) {
        mempool_destroy(scsi_buf_pool);
        scsi_buf_pool = NULL;
    }
    
    if (scsi_buf_slab) {
        kmem_cache_destroy(scsi_buf_slab);
        scsi_buf_slab = NULL;
    }

    printk("Virtual storage controller driver unregistered.\n");
    return ;
}

module_init(vsc_init);
module_exit(vsc_exit);

MODULE_DESCRIPTION("Huawei Cloudstorage virtual storage controller driver. (build date : "__DATE__" "__TIME__")");
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Huawei Technologies Co., Ltd.");
#ifdef DRIVER_VER
MODULE_VERSION(DRIVER_VER);
#else
MODULE_VERSION("1.0.0");
#endif

