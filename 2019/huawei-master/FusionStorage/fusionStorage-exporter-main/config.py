from configparser import RawConfigParser
import argparse, json

def get_args():
    parser = argparse.ArgumentParser(description="Fusion Storage options!")
    parser.add_argument("-a","--address",type=str,default='0.0.0.0',help="Exporter 启动地址")
    parser.add_argument("-p","--port",type=int,default=9099,help="Exporter 启动端口")
    parser.add_argument("-c","--config",type=str,default="./conf/config.ini",help="配置文件路径")
    args = parser.parse_args()
    return args

def get_config(config_path):
    config = RawConfigParser()
    config.read(config_path,encoding='UTF8')
    hw_host = config.get('huawei', "host")
    hw_port = config.get('huawei',"port")
    hw_username = config.get('huawei',"username")
    hw_password = config.get('huawei',"password")
    hw_h_list = config.get('huawei',"host_list")
    hw_host_list = json.loads(hw_h_list)
    return hw_host,hw_port,hw_username,hw_password,hw_host_list
