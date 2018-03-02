#!/usr/bin/env python
# -*- encoding: GBK -*-
# @Time    : 2018/2/7 17:45
# @Author  : mike.liu
# @File    : sendmail.py
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
        config.read(mail_config_file)

        self.login_user = config.get('SMTP','login_user')
        self.login_pwd = config.get('SMTP','login_pwd')
        self.from_addr = config.get('SMTP','from_addr')
        self.to_addrs = config.get('SMTP','to_addrs')
        self.host = config.get('SMTP','host')
        self.port = config.get('SMTP','port')
        self.encrypt = config.get('SMTP','encrypt')
        if int(self.encrypt) ==1:
            self.smtp = smtplib.SMTP_SSL()
        else:
            self.smtp = smtplib.SMTP()

    # 连接到服务器
    def connect(self):
        self.smtp.connect(self.host,self.port)

    #登录邮件服务器
    def login(self):
        try:
            self.smtp.login(self.login_user,self.login_pwd)
        except Exception as e:
            print('%s' %e)

    #发送邮件
    def send_mail(self,mail_subject,mail_content,attachment_path_set):
         # 构造MIMEMultipart对象做为根容器
        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = ','.join(eval(self.to_addrs))
         # 注意，这里的msg['To']只能为逗号分隔的字符串，形如 'sdxx@163.com', 'xdflda@126.com'
        msg['Subject'] = mail_subject

        #添加邮件内容
        content = MIMEText(mail_content,_charset='gbk')
         # 说明，这里_charset必须为gbk，和# -*- coding:GBK -*- 保持一直，否则邮件内容乱码

        msg.attach(content)

        for attachmet_path in attachment_path_set:
            if os.path.isfile(attachmet_path): #如果附件存在
                type,coding = mimetypes.guess_type(attachmet_path)
                if type == None:
                    type = 'application/octet-stream'

                major_type,minor_type = type.split('/',1)
                with open(attachmet_path,'r',encoding='GB2312') as file:
                    if major_type == 'text':
                        attachmet = MIMEText(file.read(),_subtype=minor_type,_charset='GB2312')
                    elif major_type == 'image':
                        attachmet = MIMEImage(file.read(),_subtype=minor_type)
                    elif major_type == 'application':
                        attachmet = MIMEApplication(file.read(),_subtype=minor_type)
                    elif major_type == 'audio':
                        attachmet = MIMEAudio(file.read(),_subtype=minor_type)

                #修改附件名称
                attachment_name = os.path.basename(attachmet_path)
                attachmet.add_header('Content-Disposition', 'attachment', filename = ('gbk', '', attachment_name))
                #说明：这里的('gbk', '', attachment_name)解决了附件为中文名称时，显示不对的问题

                msg.attach(attachmet)

        # 得到格式化后的完整文本
        full_text = msg.as_string()

        #发送邮件
        self.smtp.sendmail(self.from_addr,eval(self.to_addrs),full_text)

    #退出
    def quit(self):
        self.smtp.quit()


