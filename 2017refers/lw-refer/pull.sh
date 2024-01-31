#!/bin/bash

cd /lonwey/yanghao/cc_supervisor/cc
git reset --hard
# /lonwey/yanghao/cc/pull.exp
chmod 777 pull.exp
./pull.exp

# cd /lonwey/yanghao/cc_sv_119/cc
# git reset --hard
# # /lonwey/yanghao/cc/pull.exp
# chmod 777 pull.exp
# ./pull.exp
# #cd ..
# #cp config_119.py cc/config.py
# cp config_119.py config.py

supervisorctl reload
