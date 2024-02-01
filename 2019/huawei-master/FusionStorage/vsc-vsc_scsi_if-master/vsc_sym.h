/********************************************************************
            Copyright (C) Huawei Technologies, 2012
  #���ߣ�Peng Ruilin (pengruilin@huawei.com)
  #����: vsc sym����ͷ�ļ�
********************************************************************/
#include <linux/version.h>
#include "vsc_common.h"

#ifndef __VSC_SYM_H_
#define __VSC_SYM_H_

/*symģ���ʼ*/
int vsc_sym_init(void);
/*symģ���˳�*/
int vsc_sym_exit(void);

#define vsc_device_create  device_create
#define vsc_device_destroy device_destroy
#define vsc_class_create   class_create
#define vsc_class_destroy  class_destroy

#endif

