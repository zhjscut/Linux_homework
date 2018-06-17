#!/usr/bin/python 
# -*- coding: utf-8 -*-

from flask import Flask, request
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


def get_music_path(keyword):
    url = "http://songsearch.kugou.com/song_search_v2?callback=jQuery1124006980366032059648_1518578518932&keyword="+str(keyword)+"&page=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filter=0&_=1518578518934"
    content = requests.get(url)
    if re.findall('"FileHash":"(.*?)"',content.text) == []:
        music_path = '没有搜索到对应的歌曲'
        songname = '无'
#         message_answer = '没有搜索到对应的歌曲'
#         result_tts = client.synthesis(message_answer, 'zh', 1, {'vol': 5, 'per': 0})
#         with open(filename_answer, 'wb') as f:
#             f.write(result_tts)
    else:
        filehash = re.findall('"FileHash":"(.*?)"',content.text)[0]
        songname = re.findall('"SongName":"(.*?)"',content.text)[0].replace("<\\/em>","").replace("<em>","") #即将播放的歌曲名
        hash_url = "http://www.kugou.com/yy/index.php?r=play/getdata&hash="+filehash
        hash_content = requests.get(hash_url)
        play_url = re.findall('"play_url":"(.*?)"',hash_content.text)
        play_url = ' '.join(play_url)
        real_download_url = play_url.replace("\\","")
        music_path = real_download_url
#         print("客官，请稍等一下，好音乐马上呈上！")
        # with open(songname+".mp3","wb")as fp:
#         with open(filename_music,"wb")as fp:
#             fp.write(requests.get(real_download_url).content)
#         print('下载完成，敬请收听！')
#         play(filename_music)
    return music_path, songname



# For a given file, return whether it's an allowed type or not
def allowed_file(filename):  
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()     
    
APP_ID = '11169887'
API_KEY = 'TQypLIsDnr4XwzfyKGLqMsfD'
SECRET_KEY = 'bc5efee36b796c2b467dba12c2a080b0'    
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY) 

    
    
    
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif', 'mp3'])
# url的格式为：数据库的协议：//用户名：密码@ip地址：端口号（默认可以不写）/数据库名
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mysql@localhost/first_flask"
# 动态追踪数据库的修改. 性能不好. 且未来版本中会移除. 目前只是为了解决控制台的提示才写的
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# 创建数据库的操作对象
db = SQLAlchemy(app)

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    # 给Role类创建一个user属性，关联users表
    # backref是反向的给User类创建一个role属性，关联roles表。这是flask特殊的属性    
    users = db.relationship('User', backref="role")
    # 相当于__str__方法。
    def __repr__(self):
        return "Role: %s %s" % (self.id,self.name)

class User(db.Model):
    # 给表重新定义一个名称，默认名称是类名的小写，比如该类默认的表名是user。
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(16))
    # 创建一个外键，和django不一样。flask需要指定具体的字段创建外键，不能根据类名创建外键    
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    
    def __repr(self):
        return "User: %s %s %s %s" % (self.id, self.name, self.password, self.role_id)
    
@app.route('/', methods =['GET','POST'])
def hello_world():

    return "Hello World!"


@app.route('/receive', methods=['GET','POST'])
def receive():

    postdata = request.values.get('clickdata')

    print(json.loads(postdata))  # 注意这里哈

    #postdata = json.loads(postdata)  # 注意这里哈，变回DICT格式，亲切ing

    return "46575"

@app.route('/music', methods=['GET','POST'])
def listen_music():
    try:
        upload_file = request.files['file']
        print('收到录音文件')
        if upload_file and allowed_file(upload_file.filename):
            filename = 'from_music.mp3'
            save_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            print(save_filename)
            upload_file.save(save_filename)
            output_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'decoded.wav') #各个模块做转码得到的文件可以放在同一个文件上
            if os.path.exists(output_filename): #ffmpy.FFmpeg对象用于音视频转码，如果输出文件名已存在，那么run()方法将报错，因此run之前应先检查输出文件是否存在，若存在应先移除
                os.remove(output_filename)
            from ffmpy import FFmpeg
            ff = FFmpeg(
               inputs={save_filename: None},
               outputs={output_filename: None}
            )
            ff.run()
            #语音转文字
            result_stt = client.asr(get_file_content(output_filename), 'wav', 8000, {'dev_pid': '1537'})
            if result_stt['err_msg'] != 'success.':
                music_name = '没有识别到内容' 
                music_path = ''
            else:
                music_name_request = result_stt['result'][0].replace('，','') #str类型即可
                print(music_name_request)
                music_path, music_name = get_music_path(music_name_request) #music_path是json格式的音频url，可以直接返回
    except: #可能是手动输入的请求数据        
        music_name_request = json.loads( request.values.get('music_name') )
        music_path, music_name = get_music_path(music_name_request)
#         postdata = json.loads(postdata)  # 注意这里哈，变回DICT格式，亲切ing
    finally: 
        result = {'music_path': music_path, 'music_name': music_name}
        print(result)
        print(json.dumps(result))
        return json.dumps(result)


@app.route('/file', methods=['GET','POST'])
def collect_file():
    upload_file = request.files['file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
#         upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        return 'hello, '+request.form.get('name', 'little apple')+'. success'
    else:
        return 'hello, '+request.form.get('name', 'little apple')+'. failed'
    
    file = request.get_data()
    file = request.files['file']
    print(file)

    return 'done.'

@app.route('/upload', methods=['POST'])
def upload():  
    upload_file = request.files['file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
#         upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        return 'hello, '+request.form.get('name', 'little apple')+'. success'
    else:
        return 'hello, '+request.form.get('name', 'little apple')+'. failed'

    
if __name__ == '__main__':
    # 删除所有的表
    db.drop_all()
    # 创建表
    db.create_all()
    
    rol = Role(name = "admin")
    # 先将rol对象添加到会话中，可以回滚
    db.session.add(rol)
    
    ro2 = Role()
    ro2.name = 'user'
    db.session.add(ro2)
    # 最后插入完数据一定要提交
    db.session.commit()
    
    us1 = User(name='wang', email='wang@163.com', password='123456', role_id=rol.id)
    us2 = User(name='zhang', email='zhang@189.com', password='201512', role_id=ro2.id)
    us3 = User(name='chen', email='chen@126.com', password='987654', role_id=ro2.id)
    us4 = User(name='zhou', email='zhou@163.com', password='456789', role_id=ro1.id)
    us5 = User(name='tang', email='tang@itheima.com', password='158104', role_id=ro2.id)
    us6 = User(name='wu', email='wu@gmail.com', password='5623514', role_id=ro2.id)
    us7 = User(name='qian', email='qian@gmail.com', password='1543567', role_id=ro1.id)
    us8 = User(name='liu', email='liu@itheima.com', password='867322', role_id=ro1.id)
    us9 = User(name='li', email='li@163.com', password='4526342', role_id=ro2.id)
    us10 = User(name='sun', email='sun@163.com', password='235523', role_id=ro2.id)
    db.session.add_all([us1, us2, us3, us4, us5, us6, us7, us8, us9, us10])
    db.session.commit()
    
    
    
    
    app.run(host='0.0.0.0', port=6007, debug=True) #6007端口，浏览器要访问1115端口