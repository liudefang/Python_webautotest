#!/usr/bin/env python

# -*- encoding: utf-8 -*-
# @Time    : 2018/2/6 19:33
# @Author  : mike.liu
# @File    : mail.py
import configparser
import mimetypes
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MyMail:
    def __init__(self,mail_config_file):
        config = configparser.ConfigParser()
        config.read(mail_config_file,encoding = 'utf-8')

        self.smtp = smtplib.SMTP()
        self.login_user = config.get('SMTP','login_user')
        self.login_pwd = config.get('SMTP','login_pwd')
        self.from_addr = config.get('SMTP','from_addr')
        self.to_addrs = config.get('SMTP' ,'to_addrs')
        self.host = config.get('SMTP','host')
        self.prot = config.get('SMTP','port')

    #连接到服务器
    def connect(self):
        self.smtp.connect(self.host,self.port)

    #登录邮件服务器
    def login(self):
        try:
            self.smtp.login(self.login_user,self.login_pwd)
        except Exception as e:
            print('%s' % e)

    #发送邮件
    def send_mail(self,mail_subject,mail_content,attachment_path_set):
        #构造MIMEMultipart对象做为根容器
        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = ','.join(eval(self.to_addrs))
        msg['Subject'] = mail_subject

        #添加邮件内容
        content = MIMEText(mail_content,_charset='gbk')
        msg.attach(content)

        for attachment_path in attachment_path_set:
            if os.path.isfile(attachment_path): # 如果附件存在
                type,coding = mimetypes.guess_type(attachment_path)
                if type == None:
                    type = 'application/octet-stream'

                major_type,minor_type = type.split('/',1)
                with open(attachment_path,'rb') as file:
                    if major_type == 'text':
                        attachment = MIMEText(file.read(),_subtype=minor_type)
                    elif major_type == 'image':
                        attachment = MIMEImage(file.read(),_subtype=minor_type)
                    elif major_type == 'application':
                        attachment = MIMEApplication(file.read(),_subtype=minor_type)
                    elif major_type == 'audio':
                        attachment = MIMEAudio(file.read(),_subtype=minor_type)

                #修改附件名称
                attachment_name = os.path.basename(attachment_path)
                attachment.add_header('Content-Disposition','attachment',filename = ('gbk','',attachment_name))

                msg.attach(attachment)

        #得到格式化后的完整文本
        full_text = msg.as_string()

        #发送邮件
        self.smtp.sendmail(self.from_addr,eval(self.to_addrs),full_text)

    #退出
    def quit(self):
        self.smtp.quit()




