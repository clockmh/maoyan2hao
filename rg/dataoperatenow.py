# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 22:48:28 2018

@author: lenovo
"""

from flask import Flask,make_response,send_file
from flask import render_template
from flask import request
from flask import url_for
from PIL import Image
from flask import Response
from selenium import webdriver
from io import BytesIO

import base64
import json
import os
import sys
import pandas as pd
import numpy as np
import math
import copy
import matplotlib.pyplot as plt
import time
import subprocess
import sys

choice_year = ''
choice_season = ''
choice_month = ''
spider = ''
choice_years = []
flag = 1
choice_top = 0
choice_url = ''
choice_id = ''
cur_data = []
choice_pic = []
host_name = '游客'
choice_num = 0
child = None
flag_pachong = '0'

app = Flask(__name__)
def Response_headers(content):
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def dataInputMovies():
    path_base = os.path.dirname(os.path.realpath(__file__))
    data_movies_1 = pd.read_csv(path_base + '\\movies\\2015.csv')
    data_movies_2 = pd.read_csv(path_base + '\\movies\\2016.csv')#,encoding = 'gbk')
    data_movies_3 = pd.read_csv(path_base + '\\movies\\2017.csv')
    data_movies_4 = pd.read_csv(path_base + '\\movies\\2018.csv')
    data_movies = pd.concat([data_movies_1,data_movies_2,data_movies_3,data_movies_4]).reset_index(drop = True)
    #data_movies = data_movies.dropna()    
    return data_movies

def dataInputActorsex():
    path_base = os.path.dirname(os.path.realpath(__file__))
    data_actorsex = pd.read_csv(path_base + '\\movies\\gender.csv',encoding = 'gbk')
    return data_actorsex.set_index('name')

def getX_y(x_y,pie):
    datas = {"data":[]}
    num_sum = 0
    for i in x_y:
        if i[0] == 0:
            continue
        num_sum = num_sum + i[0]
        new = {"name":i[1],"num":i[0]}
        datas["data"].append(new)
        
    if pie:
        for j in datas["data"]:
            j["num"] = j["num"] / num_sum
            content = json.dumps(datas)
            resp = Response_headers(content)
            return resp
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp
    
def dataPre(datas):
    num_ch = {'十':1,'百':2,'千':3,'万':4,'亿':8,'美':math.log(7,10),'元':0}
    num_bof = []
    iloc = -1
    for i in datas.keys():
        iloc = iloc+1
        if i == 'title':
            datas[i].fillna('')
            continue
        if i == 'boxoffice':
            datas[i] = datas[i].fillna('0元')
            for j in range(len(datas[i])):
                k = 0
                while ord(datas[i][j][k])<58:
                    k = k + 1
                try:
                    num_base = float(datas[i][j][0:k])
                except ValueError:
                    num_bof.append(0)
                    continue
                for l in datas[i][j][k:]:
                    num_base = num_base*(10**num_ch[l])
                num_bof.append(num_base)
            datas['bof'] = num_bof
            continue
        datas[i] = datas[i].fillna('')
        for j in range(len(datas[i])):
            datas.iat[j,iloc] = datas[i][j].split(',')
            for k in range(len(datas[i][j])):
                datas[i][j][k] = datas[i][j][k].strip()

def sexSearch(name,data_actorsex):
    name = '[\''+name+'\']'
    try:
        return data_actorsex['sex'].loc[name][2]
    except:
        return False
    
def timeJudge(time):
    month_day = {'01':31,'02':29,'03':31,'04':30,'05':31,'06':30,'07':31,'08':31,'09':30,'10':31,'11':30,'12':31}
    year_null = '0000'
    md_null = '00'
    length = len(time)
    if (length > 3)|(length == 0):
        return [year_null,md_null,md_null]
    try:
        date = int(time[0])
        if (date > 2018) | (date < 1800):
            return [year_null,md_null,md_null]
    except:
        return [year_null,md_null,md_null]
    try:
        date = int(time[1])
        if (date <= 0)|(date > 12):
            return [copy.copy(time[0]),md_null,md_null]
        elif len(time[1]) == 1:
            time[1] = '0'+time[1]
    except:
        return [copy.copy(time[0]),md_null,md_null]
    try:
        date = int(time[2])
        if (date <= 0)|(date >= month_day[time[1]]):
            return [copy.copy(time[0]),copy.copy(time[1]),md_null]
        else:
            return [copy.copy(time[0]),copy.copy(time[1]),copy.copy(time[2])]
    except:
        return [copy.copy(time[0]),copy.copy(time[1]),md_null]

def timeIndexSetup(datas):
    time_all = []
    for i in range(len(datas['time'])):
        time = timeJudge(datas['time'][i])
        datas['time'][i].clear()
        datas['time'][i].extend(time)
        time_all.append(time[0]+time[1]+time[2])
    datas['time_all'] = time_all
    datas = datas.sort_values(by = 'time_all').reset_index(drop = True)
    index_time = pd.DataFrame({})
    year = []
    data_time = datas['time']
    data_last = []
    month_last = None
    for i in range(len(data_time)):
        if data_time[i][0] not in year:
            year.append(data_time[i][0])
            list_none = []
            for j in range(13):
                list_none.append([])
            index_time[data_time[i][0]] = list_none
            month_last = None
        if month_last != data_time[i][1]:
            index_time[data_time[i][0]].iloc[int(data_time[i][1])].append(i)
            month_last = data_time[i][1]
            data_last.append(i)
            data_last = index_time[data_time[i][0]].iloc[int(data_time[i][1])]
    data_last.append(i+1)
    return [datas,index_time]

def getMovies(index_time,data_movies,year_begin='2015',month_begin='00',year_end='2018',month_end='12'):
    if year_begin > year_end:
        return False
    if (year_begin == year_end)&(month_begin > month_end):
        return False
    movies_get = data_movies.iloc[index_time[str(year_begin)][int(month_begin)][0]:index_time[str(year_end)][int(month_end)][1]].copy().reset_index(drop = True)
    return movies_get

def bofAlu(movies):
    return movies('bof').sum()


def statisticsAluNew(movies,x,x_y = {},count = 0):
    length = len(x)
    if length == 0:
        return movies['bof'].sum()
    for i in range(len(movies)):
        recursionAlu(movies,x,x_y,count,i)
                    
def recursionAlu(movies,x,x_y,count,i):
    length = len(x)
    if length == 1:
        for j in movies[x[0]][i]:
            if j == '':
                continue
            if j not in x_y.keys():
                x_y.update({j:0})
            x_y[j] = x_y[j] + 1*count + (1 - count)*movies['bof'][i]
    else:
        for j in movies[x[0]][i]:
            if j == '':
                continue
            if j not in x_y.keys():
                x_y.update({j:{}})
            recursionAlu(movies,x[1:],x_y[j],count,i) 

def findTop(type_num,top,sex = None,data_actorsex = []):

    i = 0
    found = 0
    length = len(type_num.keys())
    list_top = []
    type_num = zip(type_num.values(),type_num.keys())
    if top<=0:
        return type_num
    type_num = sorted(type_num,reverse = True)
    if sex == None:
        return type_num[0:top]
    else:
        if len(data_actorsex) == 0:
            return False
        else:
            while((found < top) & (length > i)):
                if sexSearch(type_num[i][1],data_actorsex) == sex:
                    list_top.append(type_num[i])
                    found = found+1 
                i = i + 1
            return list_top   

def quarterChange(quarter,month):
    if (quarter < 1)|(quarter > 4):
        return [month,month]
    else:
        return [quarter*3 - 2,quarter*3 ]

def bofChange(bof):
    num_china = {0:'',1:'十',2:'百',3:'千',4:'万',8:'亿'}
    if len(bof) == 0:
        return False
    bof_china = []
    for i in bof:
        if i == 0:
            bof_china.append(0)
            continue
        bof_chinawd = ''
        stage = math.log(i,10)
        stage = int(stage)
        num = round(i/(10**stage),2)
        if stage <4:
            bof_chinawd = i
            bof_china.append(bof_chinawd)
            continue
        if stage > 12:
            bof_chinawd = '万亿'+bof_chinawd
            num = round(i/(10**12),2)
            bof_chinawd = str(num)+bof_chinawd
            bof_china.append(bof_chinawd)
            continue
        if stage >= 8:
            bof_chinawd = num_china[8] + bof_chinawd
            stage = stage - 8
        if stage >= 4:
            bof_chinawd = num_china[4] + bof_chinawd
            stage = stage - 4
        bof_chinawd = num_china[stage] + bof_chinawd
        bof_chinawd = str(num) + bof_chinawd
        bof_china.append(bof_chinawd)
    return bof_china

def outMovies(data_movies,index_time,pie = True):
    year_dict={'1':'2015','2':'2016','3':'2017','4':'2018'}
    global choice_year
    global choice_season
    global choice_month
    if not choice_year == '':
        year = year_dict[choice_year]
    if choice_season == '':
        month_begin = 0
        month_end = 12
    else:
        quarter = int(choice_season)
        month = int(choice_month)
        if pie:
            month_q = quarterChange(quarter,month)
            month_begin = month_q[0]
            month_end = month_q[1]
        else:
            month_begin = month
            month_end = month
    '''
    if (month>=month_begin)&(month<=month_end):
        month_begin = month
        month_end = month
    if month_end == 0:
        month_end = 12
    '''
    movies_get = getMovies(index_time,data_movies,year,month_begin,year,month_end)
    return movies_get


def currency(data_movies,index_time,x = [],count = 0,top = 0,sex = None,data_actorsex = [],pie = False):
    movies_get = outMovies(data_movies,index_time,pie)
    x_y = {}
    statisticsAluNew(movies_get,x,x_y,count)
    x_y = findTop(x_y,top,sex,data_actorsex)
    x_y = getX_y(x_y,pie)
    return x_y

def clearup():
    global choice_year
    global choice_season
    global choice_month
    global choice_top
    global spider
    global choice_years
    choice_year = ''
    choice_season = ''
    choice_month = ''
    spider = ''
    choice_top = 0
    choice_years = []
    '''
    for i in choice_years:
        choice_years.remove(i)
    '''


def pdfCreate(filepath,pdfname):
    file_list = os.listdir(filepath)#'D:\\img')
    pic_name = []
    im_list = []
    for x in file_list:
        if "jpg" in x or 'png' in x or 'jpeg' in x:
            pic_name.append(x)

    pic_name.sort()
    if len(pic_name) == 0:
        return True
    new_pic = []

    for x in pic_name:
        if "jpg" in x:
            new_pic.append(x)

    for x in pic_name:
        if "png" in x:
            new_pic.append(x)

    print("hec", new_pic)
    
    
    im1 = Image.open(filepath + '\\' +new_pic[0])
    x,y = im1.size
    if im1.mode == "RGBA":
        p = Image.new('RGBA', im1.size, (255,255,255))
        p.paste(im1, (0, 0, x, y), im1)
        im1 = p.convert('RGB')
        
        
    new_pic.pop(0)
    
    for i in new_pic:
        img = Image.open(filepath + '\\' + i)
        # im_list.append(Image.open(i))
        x,y = img.size
        if img.mode == "RGBA":
            p = Image.new('RGBA',img.size,(255,255,255))
            p.paste(img,(0,0,x,y),img)
            img = p.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)
    im1.save(pdfname, "PDF", resolution=100.0, save_all=True, append_images=im_list)
    return False

def pachong_dis(year):
    global child
    global flag_pachong
    flag_pachong = '1'
    basepath = os.getcwd()
    f = open("pachon_2015.bat","w")
    f.write('cd ' + basepath + '\\maoyan3\\maoyan\\maoyan\n' + 'python ' + 'main.py ' + year)
    f.close()   
    child = subprocess.Popen('pachon.bat')
    child.wait()
    flag_pachong = '0'

data_movies = dataInputMovies()
data_actorsex = dataInputActorsex()
dataPre(data_movies)
data_index_time = timeIndexSetup(data_movies)
data_movies = data_index_time[0]
index_time = data_index_time[1]

@app.route('/')
def home():
    return 'Hello world'

@app.route('/pachongflag',methods = ['POST','GET'])
def pachongflag():
    datas = {"data":[]}
    if request.method == 'GET':
        print('@@@@@@@@@@@@@@@@@@@@@@@')
        datas['data'].append({'name':flag_pachong})
        content = json.dumps(datas)
        resp = Response_headers(content)
        return resp 

@app.route('/hostname',methods = ['POST','GET'])
def hostname():
    global host_name
    data = request.get_json(force=True)
    host_name = data['name']
    print(host_name)

@app.route('/download_file',methods = ['POST','GET'])
def download_file():
    basepath = os.getcwd()
    filename = basepath + '\\users\\' + host_name + '\\img_valid.pdf' 
    response = make_response(send_file(filename))
    response.headers["Content-Disposition"] = "attachment; filename=" + filename + ";"
    return response

@app.route('/receive_data', methods=['POST', 'GET'])
def receive_data():
    global choice_year
    global choice_season
    global choice_month
    global cur_data
    clearup()
    cur_data = []
    data = request.get_json(force=True)  # 获取json数据
    choice_year = data['year']
    choice_season = data['season']
    choice_month = data['month']
    cur_data.append(choice_year)
    cur_data.append(choice_season)
    cur_data.append(choice_month)
    
@app.route('/receive_spider',methods = ['POST' , 'GET'])
def receiveSpider():
    global spider
    global flag
    clearup()
    print(1)
    flag = 1
    data = request.get_json(force=True)
    spider = data['year']
    print(spider)
    spider = str(int(spider) + 2014)
    print(spider)
    pachong_dis(spider)

    
@app.route('/receive_top',methods = ['POST','GET'])
def receiveTop():
    global choice_top
    global choice_year
    global cur_data
    clearup()
    cur_data = []
    data = request.get_json(force=True)
    choice_year = data['year']
    choice_top = data['rank']
    cur_data.append(choice_year)
    cur_data.append(choice_top)
    print(choice_top,choice_year)

@app.route('/receive_mtop',methods = ['POST','GET'])
def receivemTop():
    global choice_top
    global choice_year
    global cur_data
    clearup()
    cur_data = []
    data = request.get_json(force=True)
    choice_year = data['year']
    choice_top = data['rank']
    cur_data.append(choice_year)
    cur_data.append(choice_top)
    print(choice_top,choice_year)

@app.route('/receive_years',methods = ['POST','GET'])
def receiveYears():
    clearup()
    global choice_years
    global cur_data
    cur_data = []
    data = request.get_json(force = True)
    choice_years.append(data['year1'])
    choice_years.append(data['year2'])
    choice_years.append(data['year3'])
    cur_data = choice_years
    
@app.route('/echars',methods = ['GET','POST'])
def typePersent_qua():
    if request.method == 'GET':
        resp = currency(data_movies,index_time,['type'],pie = True)
        return resp

@app.route('/month',methods = ['GET','POST'])
def typePersent_mon():
    if request.method == 'GET':
        resp = currency(data_movies,index_time,['type'],pie = False)
        return resp
    
@app.route('/actor_man',methods = ['GET','POST'])
def actorTopMan():
    global choice_top
    if request.method == 'GET':
        top = int(choice_top)
        resp = currency(data_movies,index_time,['actors'],1,top,'男',data_actorsex)
        # child.terminate()
        return resp

@app.route('/actor_woman',methods = ['GET','POST'])
def actorTopWoman():
    global choice_top
    if request.method == 'GET':
        top = int(choice_top)
        resp = currency(data_movies,index_time,['actors'],1,top,'女',data_actorsex)
        return resp
#@app.route('',method = ['GET','POST'])

@app.route('/year_bof',methods = ['GET','POST'])
def bofYearChange():
    if request.method == 'GET':
        global choice_years
        years = []
        year_dict={'1':'2015','2':'2016','3':'2017','4':'2018'}
        for k in choice_years:
            years.append(year_dict[k])
        datas = {"data":[]}
        for i in range(4):
            bof = []
            for j in years:
                print(j)
                month = quarterChange(i + 1,0)
                movies_get = getMovies(index_time,data_movies,j,month[0],j,month[1])
                bof.append(statisticsAluNew(movies_get,[]))
            print(bof)  
            datas["data"].append({"name":i,"num":bof})
        content = json.dumps(datas)
        resp = Response_headers(content)
        return resp

@app.route('/receive_url',methods = ['GET','POST'])
def receive_url():
    global choice_url
    global choice_id
    data = request.get_json(force=True)
    choice_url = data['url']
    choice_id = data['id']
    print(choice_url)
    print(choice_id)
    shot()

def shot():
    global choice_id
    global choice_url
    basepath = os.getcwd()
    driver = webdriver.PhantomJS(executable_path=basepath + "\\phantomjs-2.1.1-windows\\bin\\phantomjs")
    url = choice_url.split(',')
    choice_url = url[0]
    count = int(url[1])
    driver.get(r"http://127.0.0.1:5000/"+choice_url)
    driver.maximize_window()
    for i in range(count):
        webelement = driver.find_element_by_id('s'+str(i+1))
        webelement.find_element_by_xpath("//option[@value='"+cur_data[i]+"']").click()
        time.sleep(1)
    time.sleep(1)
    driver.find_element_by_id('btn').click()
    time.sleep(1)
    driver.save_screenshot("baidu.png")
    #imgelement = driver.find_element_by_xpath(".//*[@id='u_sp']")
    print(choice_id)
    imgelement = driver.find_element_by_id(choice_id)
    locations = imgelement.location
    sizes = imgelement.size
    rangle = (int(locations['x']),int(locations['y']),int(locations['x'] + sizes['width']),int(locations['y'] + sizes['height']))
    img = Image.open("baidu.png")
    jpg = img.crop(rangle)
    jpg.save(basepath + "\\baidu1.png")
    
@app.route('/receive_pic',methods = ['GET','POST'])
def receive_pic():
    global choice_pic
    data = request.get_json(force=True)
    choice_pic = []
    #print(len(data['pic'].split(',')))
    choice_pic.append(data['pic'].split(',')[1].replace(' ','+'))
    if 'pic1' in data.keys():
        #print('#########################################')
        choice_pic.append(data['pic1'].split(',')[1].replace(' ','+'))
        print('pic1')
    '''
    binary_img_data = base64.b64decode(choice_pic.encode('utf-8'))

    #file_like = BytesIO(binary_img_data)
    file = open('baidu.png',"wb")
    file.write(binary_img_data)
    file.close()
    # binary_img_data = base64.b64decode(choice_pic)
    # file_like = BytesIO(binary_img_data)
    # image = Image.open(file_like)
    # image.show()
    # print('finish==========================================')
    '''
    return None

@app.route('/receive_picnum',methods = ['GET','POST'])
def receive_picnum():
    global choice_num
    data = request.get_json(force=True)
    choice_num = int(data['picnum'])

@app.route('/tolist',methods = ['GET','POST'])
def to_list():
    global choice_pic
    global host_name
    global choice_num
    flag = True
    datas = {"data":[]}
    if host_name == '游客':
        datas['data'].append({'name':0})
        content = json.dumps(datas)
        resp = Response_headers(content)
        return resp
    binary_img_data = base64.b64decode(choice_pic[choice_num])
    basepath = os.getcwd()
    dirs = os.listdir(basepath + '\\users')
    for dir0 in dirs:
        if str(host_name) == str(dir0):
            flag = False
    if flag:
        os.makedirs(basepath + '\\' + 'users' + '\\' + host_name + '\\')
    timenow = time.strftime('%Y.%m.%d %H:%M:%S ',time.localtime(time.time())).replace(' ','_').replace('.','_').replace(':','_')
    #file = open(basepath+'\\'+'users\\'+host_name+'\\'+timenow+'.txt',"w")
    file = open(basepath+'\\'+'users\\'+host_name+'\\'+timenow+'.png',"wb")
    file.write(binary_img_data)
    #file.write(choice_pic[choice_num])
    file.close()
    datas['data'].append({'name':1})
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

@app.route('/listprint',methods = ['GET','POST'])
def listPrint():
    datas = {"data":[]}
    '''pri
    if host_name == '游客':
        datas['data'].append({'name':0})
        content = json.dumps(datas)
        resp = Response_headers(content)
        return resp
    '''
    flag = True
    '''
    data = request.get_json(force=True)
    print(data['picnum'])
    '''
    basepath = os.getcwd()
    file_list = os.listdir(basepath + '\\users')
    for x in file_list:
        if str(x) == str(host_name):
            flag = False
    if flag:
        datas['data'].append({'name':0})
        content = json.dumps(datas)
        resp = Response_headers(content)
        print('no such person')
        return resp
    imgpath = os.path.join(basepath,'users\\'+host_name)
    pdfpath = os.path.join(basepath,'users\\'+host_name+'\\img_valid.pdf')
    flag = pdfCreate(imgpath,pdfpath)
    if flag:
        datas['data'].append({'name':0})
        content = json.dumps(datas)
        resp = Response_headers(content)
        return resp
    file_list = os.listdir(imgpath)
    for x in file_list:
        if "jpg" in x or 'png' in x or 'jpeg' in x:
            os.remove(basepath + '\\users\\' + host_name + '\\' + x)
            print('remove')
    datas['data'].append({'name':1})
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp
'''
@app.route('/listprint',methods = ['GET','POST'])
def listprint():
    data = request.get_json(force=True)
    print(data['picnum'])

@app.route('/list_get1',methods = ['GET','POST','OPTION'])
def list_get1():
    datas = {"data":[]}
    print (request.method)
    if request.method == 'GET':
        datas['data'].append({'name':0})
        content = json.dumps(datas)
        resp = Response_headers(content)
        print('no such person')
        return resp
'''

@app.route('/moviestop',methods = ['GET','POST'])
def moviesTop():
    print('yes')
    year_dict={'1':'2015','2':'2016','3':'2017','4':'2018'}
    global choice_year
    global choice_top
    year = year_dict[choice_year]
    datas = {'data':[]}
    if request.method == 'GET':
        top = int(choice_top)
        movies_get = getMovies(index_time,data_movies,year,0,year,12)
        movies_get = movies_get.sort_values(by = 'bof',ascending = False).reset_index(drop = True)
        movies = movies_get.iloc[0:top,:]
        for i in range(top):
            new = {'name':movies['title'][i],'num':movies['bof'][i]}
            datas['data'].append(new)
        content = json.dumps(datas)
        resp = Response_headers(content)
        return resp

        #resp = currency(data_movies,index_time,['title'],0,top)
        return resp

@app.route('/spider',methods = ['GET','POST'])
def dataUpdata():
    global flag
    basepath = os.getcwd()
    exe = basepath + '\\pachon.bat'
    os.system(exe)
    flag = 0

@app.route('/finish',methods = ['GET','POST'])
def finish():
    global flag
    return flag

@app.errorhandler(403)
def page_not_found(error):
    content = json.dumps({"error_code": "403"})
    resp = Response_headers(content)
    return resp


@app.errorhandler(404)
def page_not_found(error):
    content = json.dumps({"error_code": "404"})
    resp = Response_headers(content)
    return resp


@app.errorhandler(400)
def page_not_found(error):
    content = json.dumps({"error_code": "400"})
    resp = Response_headers(content)
    return resp


@app.errorhandler(410)
def page_not_found(error):
    content = json.dumps({"error_code": "410"})
    resp = Response_headers(content)
    return resp


@app.errorhandler(500)
def page_not_found(error):
    content = json.dumps({"error_code": "500"})
    resp = Response_headers(content)
    return resp

if __name__ == '__main__':
    app.run(debug=True, port=8080)