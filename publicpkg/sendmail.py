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

    # ���ӵ�������
    def connect(self):
        self.smtp.connect(self.host,self.port)

    #��¼�ʼ�������
    def login(self):
        try:
            self.smtp.login(self.login_user,self.login_pwd)
        except Exception as e:
            print('%s' %e)

    #�����ʼ�
    def send_mail(self,mail_subject,mail_content,attachment_path_set):
         # ����MIMEMultipart������Ϊ������
        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = ','.join(eval(self.to_addrs))
         # ע�⣬�����msg['To']ֻ��Ϊ���ŷָ����ַ��������� 'sdxx@163.com', 'xdflda@126.com'
        msg['Subject'] = mail_subject

        #����ʼ�����
        content = MIMEText(mail_content,_charset='gbk')
         # ˵��������_charset����Ϊgbk����# -*- coding:GBK -*- ����һֱ�������ʼ���������

        msg.attach(content)

        for attachmet_path in attachment_path_set:
            if os.path.isfile(attachmet_path): #�����������
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

                #�޸ĸ�������
                attachment_name = os.path.basename(attachmet_path)
                attachmet.add_header('Content-Disposition', 'attachment', filename = ('gbk', '', attachment_name))
                #˵���������('gbk', '', attachment_name)����˸���Ϊ��������ʱ����ʾ���Ե�����

                msg.attach(attachmet)

        # �õ���ʽ����������ı�
        full_text = msg.as_string()

        #�����ʼ�
        self.smtp.sendmail(self.from_addr,eval(self.to_addrs),full_text)

    #�˳�
    def quit(self):
        self.smtp.quit()


