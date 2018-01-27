# file upload 

tornado自带的文件上传功能：  
首先是阻塞，   
其次是不支持大文件，超过100M的文件就无能为力。   


## 本项目
本项目是本人结合stackoverflow上面别人的回答，综合实现的。   
支持大文件传输：   

在config.py里面设置
```python
MAX_BUFFER_SIZE = 4 * 1024**3 # 4GB
```

screenshot文件夹 是本程序运行的结果展示。