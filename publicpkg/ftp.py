#!/usr/bin/env python
# -*- coding:utf-8 -*-

# -*- encoding: utf-8 -*-
# @Time    : 2018/2/5 18:29
# @Author  : mike.liu
# @File    : ftp.py
import configparser
import os
from ftplib import FTP
from publicpkg.mylogger import logger


class MyFTP:
    def __init__(self,ftp_conf):
        '''ftp服务器主机IP，端口等配置'''
        config = configparser.ConfigParser()
        config.read(ftp_conf,encoding='utf-8')

        self.ftp_host = config.get('FTP','ftp_host')
        self.ftp_port = int(config.get('FTP','ftp_port'))
        self.ftp_user = config.get('FTP','ftp_user')
        self.ftp_passwd = config.get('FTP','ftp_passwd')
        self.ftp = FTP()



    def get_ftp_host(self):
        return self.ftp_host

    def get_ftp_port(self):
        return self.ftp_port

    def get_ftp_user(self):
        return self.ftp_user

    def get_ftp_passwd(self):
        return self.ftp_passwd

    #连接到ftp服务器
    def connect(self):
        logger.info('is connecting to ftp server %s on %s' % (self.ftp_host, self.ftp_port))
        self.ftp.connect(self.ftp_host,self.ftp_port)

    #登录到ftp服务器
    def login(self):
        logger.info('ready to login ftp server')
        self.ftp.login(self.ftp_user,self.ftp_passwd)
        logger.info('login ftp server successfully')

    # 友好的关闭连接
    def quit(self):
        try:
            self.ftp.quit()
            logger.info('close ftp connection successfully')
        except Exception as e:
            logger.info('关闭ftp连接失败%s' %e)

    #上传文件
    def upload_folder(self,local_path='D:/python/webautotest/screentshot/',remote_path='/home/testftp'):
        if not os.path.isdir(local_path):
            logger.error('出错了，请选择要上传的文件夹')
            return
        local_path = local_path.strip()  # 以防万一，去除首尾空格
        local_path = local_path.rstrip('/')  # 去除右部 /
        local_path = local_path.rstrip('\\') # 去除右部 \\
        remote_path = remote_path.strip()
        remote_path = remote_path.rstrip('/')
        remote_path = remote_path.rstrip('\\')

        self.ftp.cwd(remote_path)

        last_dir = os.path.basename(local_path)
        remote_path = os.path.join(remote_path,last_dir)
        remote_path = remote_path.replace('\\','/') # 转为linux标准路径
        # 如果ftp服务器上不存在该路径,则创建对应路径下的目录
        try:
            self.ftp.mkd(last_dir)
        except:
            logger.warn('dir: %s already exists' % last_dir)
            pass

        sub_items = os.listdir(local_path)
        for sub_item in sub_items:
            sub_item_path = os.path.join(local_path,sub_item)
            pass

        sub_items = os.listdir(local_path)
        for sub_item in sub_items:
            sub_item_path = os.path.join(local_path,sub_item)
            if os.path.isdir(sub_item_path): #如果子项目为目录
                self.upload_folder(sub_item_path,remote_path)
            else:
                self.upload_file(sub_item_path,remote_path)

    #上传文件
    def upload_file(self,src_file_path,remote_file_name):
        try:  #如果文件不存在，调用file.size(filename)会报错
            if self.ftp.size(remote_file_name)!= None:
                pass
        except Exception as e:
            pass

        with open(src_file_path,'rb') as file_handler:
            self.ftp.storbinary('STOR %s' %remote_file_name,file_handler)
            logger.info('文件：%s 已经上传到ftp' % src_file_path)

    #下载目录
    def download_dir(self,local_path,remote_path):
        if os.path.isfile(local_path):
            logger.error('出错了，请选择文件保存位置')
            return
        local_path = local_path.strip() # 以防万一，去除首尾空格
        remote_path = remote_path.strip()
        remote_path = remote_path.rstrip('/')
        remote_path = remote_path.rstrip('\\')

        last_dir = os.path.basename(remote_path)
        local_path = os.path.join(local_path,last_dir)
        local_path = local_path.replace('/', '\\') # 转为Windows标准路径
        # 如果本地客户端不存在该路径,则创建对应路径下的目录
        if not os.path.isdir(local_path):
            os.mkdir(local_path)

        sub_items = self.ftp.nlst(remote_path)
        for sub_item in sub_items:
            try:
                self.ftp.cwd(sub_item)  #如果子项目为目录
                self.download_dir(local_path,sub_item)
            except Exception: #非目录
                self.download_file(local_path,sub_item)

    def download_file(self,local_path,remote_file_path):
        last_file_name = os.path.split(remote_file_path)[1]
        local_file_path = os.path.join(local_path,last_file_name)
        if os.path.isdir(local_file_path):
            logger.error('请选择文件保存目录路径')
            return

        if os.path.isfile(local_file_path):
            local_file_path = local_file_path.replace('\\','/')
            logger.error('文件:%s 已存在' %local_file_path)
            return

        with open(local_file_path,'wb') as file_handle:
            self.ftp.retrbinary('RETR %s' % remote_file_path,file_handle.write)







