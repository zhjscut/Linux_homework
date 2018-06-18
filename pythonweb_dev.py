#!/usr/bin/python 
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import urllib
import json
import re
import base64
from werkzeug.utils import secure_filename  
import os
from ffmpy import FFmpeg
from aip import AipSpeech
import sys
from flask_sqlalchemy import SQLAlchemy


from flask import Flask, request, send_from_directory, url_for
import random
import my_email
import pymysql
import time


app = Flask(__name__)

@app.route('/send_captcha', methods =['POST'])
def send_captcha():
    # 点击发送验证码按钮后来到这里，向指定邮箱发送验证码
    json_data = request.get_json()
    email = json_data['email']
    #生成6位数字验证码
    captcha = '' 
    for i in range(0, 6): 
        captcha += str(random.randint(0, 9)) #random.randint用于生成一个指定范围内的整数。其中参数a是下限，参数b是上限，生成的随机数n: a <= n <= b
    message = 'From:轻风聊天室\n    您的验证码为' + captcha + '，请收好~'
    my_email.send_email(message, [email])
#     为了后面判断验证码正确与否，要将验证码与对应的邮箱写入一个数据库表email_captcha
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Linux_homework', charset='utf8')
    with connection.cursor() as cursor:
        sql = "select * from email_captcha where email = %s"
        effect_rows = cursor.execute(sql, (email))
        if effect_rows != 0:
            print('该邮箱已请求过验证码，现重新发送')
            sql = "update email_captcha set captcha= %s where email= %s"
            cursor.execute(sql, (captcha, email))            
        else:
            print('该邮箱未请求过验证码，第一次发送')
            sql = "INSERT INTO email_captcha (email, captcha) VALUES (%s, %s)"
            cursor.execute(sql, (email, captcha))
        print(sql)
        print('done')
    connection.commit()
    connection.close()
#     return 'Captcha sent.'
    Result = {'status_code': 'success'}
    return json.dumps(Result)

@app.route('/register', methods =['POST'])
def register():
    # 点击“注册”按钮来到这里
    json_data = request.get_json()
    email = json_data['email']
    username = json_data['username']
    password = json_data['password'] #判断密码与确认密码是否一致放到前端，使得这里收到的必定是一致的
    captcha = json_data['captcha']
    print(email, username, password, captcha)
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Linux_homework', charset='utf8')
    with connection.cursor() as cursor:
        sql = "select * from users where email = %s"
        effect_rows = cursor.execute(sql, (email))
        if effect_rows != 0:
            print('该邮箱已注册过！')
            status_code = 1
        else:
            print('注册新账户')
            sql = "select captcha from email_captcha where email= %s"
            cursor.execute(sql, (email))
            
            result = cursor.fetchone() #tuple类型，每个元素代表一个字段值
            if result is None:
#                 status_code = 3 #没有请求验证码，却点了注册
                Result = {'status_code': 'others error'}
            elif result[0] != captcha: #验证码不一致
#                 status_code = 2
                Result = {'status_code': 'wrong_captcha'}
            else: #验证码一致
                sql = "insert into users (email, username, password) values ( %s, %s, %s);"
                cursor.execute(sql, (email, username, password))
#                 status_code = 0                
                Result = {'status_code': 'success'}
    connection.commit()
    connection.close()    
#     if status_code == 0: #为了在return之前提交并关闭连接，return语句不能直接插在各个if分支中
#         return 'success' #如果前端收到'success'，则在
#     elif status_code == 1:
#         return 'existed'
#     elif status_code == 2:
#         return 'wrong_captcha'
#     else:
#         return 'others error'

    # 验证邮箱是否已被注册，可以考虑通过select判断条目数是否为0来验证，为0则未注册
      # 若已注册，返回status_code = 'existed'
    # 若未注册，则判断验证码与服务器发送出去的验证码是否一致
      # 若不一致，返回status_code = 'wrong_captcha'
    # 若一致，则在users数据库表中创建一个新条目
    return json.dumps(Result)
    
@app.route('/login', methods =['POST'])
def login():
    # 点击登录按钮之后来到这里
    json_data = request.get_json()
    email = json_data['email']
    password = json_data['password']
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Linux_homework', charset='utf8')
    with connection.cursor() as cursor:
        sql = "select password from users where email = %s"
        cursor.execute(sql, (email))
        result = cursor.fetchone() #tuple类型，每个元素代表一个字段值
        if result is None:
#             status_code = 1 #该邮箱尚未注册
            Result = {'status_code': 'notexist'}
        elif result[0] != password: #密码错误
            Result = {'status_code': 'wrong_password'}
#             status_code = 2
        else: #密码正确
            Result = {'status_code': 'welcome'}
#             status_code = 0                
    connection.commit()
    connection.close()    
#     if status_code == 0: #为了在return之前提交并关闭连接，return语句不能直接插在各个if分支中
#         return 'welcome!' #如果前端收到'success'，则在
#     elif status_code == 1:
#         return 'notexist'
#     elif status_code == 2:
#         return 'wrong_password'
#     else:
#         return 'others error'
    return json.dumps(Result)

@app.route('/query_history', methods =['POST'])
def query_history():
    json_data = request.get_json()
    email = json_data['email']    
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Linux_homework', charset='utf8')
    with connection.cursor() as cursor:
        sql = "select room_number from user_room_history where email = %s order by visit_time desc;"
        cursor.execute(sql, (email))
        result = cursor.fetchall() #tuple类型，每个元素代表一个字段值。只查询一个字段值时，仍会返回一个tuple，如 (('1234',), ('5678',), ('2468',))
        if result is None: #该用户尚未有过历史数据
            history = []
            Result = {'history': history}
        else:
            result0 = []
            for i in range(0, len(result)):
                result0.append(result[i][0])
            history = ', '.join(result0)
            Result = {'history': history}
    connection.commit()
    connection.close()    
    
    return json.dumps(Result)

@app.route('/if_exist', methods =['POST'])
def if_exist():
    json_data = request.get_json()
    room_number = json_data['room_number']
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Linux_homework', charset='utf8')
    with connection.cursor() as cursor:
        sql = "select * from user_room_active where room_number = %s"
        effected_row = cursor.execute(sql, (room_number))
        if effected_row == 0: #该房间是空的，没人（不存在该房间）
            Result = {'if_exist': 'false'}
        else:
            Result = {'if_exist': 'true'}
    connection.commit()
    connection.close()     
    
    return json.dumps(Result)

@app.route('/new_visiter', methods =['POST'])
def new_visiter():
    # 突然想到一个问题，如果外人不走小程序，而是直接找到这个网址并对它进行POST访问不停地插数据的话，数据库就会被入侵者改变
    json_data = request.get_json()
    room_number = json_data['room_number']
    email = json_data['email']
    visit_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Linux_homework', charset='utf8')
    with connection.cursor() as cursor:
        sql = "insert into user_room_active (email, room_number, visit_time) values (%s, %s, %s);" #不管该房间是否有人，对应的都是相同的插入语句
        cursor.execute(sql, (email, room_number, visit_time))
        update_user_history(email, room_number, connection)
        Result = {'status_code': 'success'}
    connection.commit()
    connection.close() 
    
    return json.dumps(Result)

def update_user_history(email, room_number, connection):
    # 如果嵌套建立两次连接，可能会出问题，所以采用传参的方式把connection传进来
    with connection.cursor() as cursor:
        sql = "select * from user_room_history where email = %s"
        effected_row = cursor.execute(sql, (email))
        visit_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        if effected_row == 0: #该用户尚未有过历史数据插入一条新数据
            sql = 'insert into user_room_history (email, room_number, visit_time) values (%s, %s, %s);'
            cursor.execute(sql, (email, room_number, visit_time))
            Result = {'statue_code': 'success'}
        elif effected_row < 3: #记录未满3条，插入新数据，如果该房间号已在数据表中，则不插入新行而是更新原有行
            sql = "select * from user_room_history where email = %s and room_number = %s"
            effected_row1 = cursor.execute(sql, (email, room_number))
            if effected_row1 == 0: 
                sql = 'insert into user_room_history (email, room_number, visit_time) values (%s, %s, %s);'
                cursor.execute(sql, (email, room_number, visit_time))   
            else:
                sql = 'update user_room_history set visit_time= %s where email= %s and room_number= %s ;'
                cursor.execute(sql, (visit_time, email, room_number))                    
        else: #历史数据超过3条，替换掉时间最久远的那条记录或更新原有行 
            sql = "select * from user_room_history where email = %s and room_number = %s"
            effected_row1 = cursor.execute(sql, (email, room_number))
            if effected_row1 == 0: #替换记录
                sql = 'select min(visit_time) from user_room_history where email = %s;'
                cursor.execute(sql, (email))   
                old_time = cursor.fetchone()[0]
                sql = 'update user_room_history set visit_time= %s, room_number= %s where email= %s and visit_time= %s;'                
                cursor.execute(sql, (visit_time, room_number, email, old_time))   
            else: #更新原有行
                sql = 'update user_room_history set visit_time= %s where email= %s and room_number= %s;'
                cursor.execute(sql, (visit_time, email, room_number))    
        sql = "select room_number, visit_time from user_room_history where email = %s"
        cursor.execute(sql, (email))
#         print(cursor.fetchall())
 
    return 0

app.run(host='0.0.0.0', port=6007, debug=True) #6007端口，浏览器要访问1115端口
