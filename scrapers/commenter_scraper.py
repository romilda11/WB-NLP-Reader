#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#need to install requests, pandas, lxml, xlrd and openpyxl

import requests,re,time
from lxml.etree import HTML
from lxml import html as HTMLParser
import pandas as pd

pinglunData = pd.read_excel(u'comments.xlsx')
ids = pinglunData[['id','username']].as_matrix()

cookie={"Cookie":'_T_WM=b1db7889599da63dc87fadde22b7cb4c; SCF=Asv3hbe-S5m9PHpT26jLjWv4rujgKU4lLC7H1-_BvkqgrabonvgwpFYfV1vfMLaIlo2v5SsMlCBnnPZUwOuSs4w.; SUB=_2A252atYVDeRhGeRL71sU8ivEyjyIHXVVlPpdrDV6PUJbkdAKLUjckW1NUyLP7QCwHjvLp6KEYNQbsQoHXy2sWF4G; SUHB=0M2UDKgBSBrLWc'}
header={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'
        } #need to update the cookie almost once a week

data = []
for i,nickName in ids[:5]:
    numID = i
    time.sleep(4)  #to prevent the scraper getting blocked by weibo
    url = "https://weibo.cn" + i + '/info'  #get access to profile pages from username
    url = url.replace('/u','')
    print(url)
    try:
        html_ = requests.get(url,cookies=cookie,headers=header,timeout=10)
        
    except:
        continue
    html = HTML(html_.content)
    
    #find the div block containing user information
    targetDiv = ''
    divs = html.xpath('//div[@class="c"]')
    for div in divs:
        if '昵称' in div.xpath('string(.)'):
            targetDiv = div
            break
    
    if targetDiv == '':
        continue
    
    infoText = HTMLParser.tostring(targetDiv,encoding='utf-8').decode('utf-8')
    delPattern = re.compile(r'(<a .*?>)')
    for del_item in re.findall(delPattern,infoText):
        infoText = infoText.replace(del_item,'')
    delPattern = re.compile(r'(</a>)')
    for del_item in re.findall(delPattern,infoText):
        infoText = infoText.replace(del_item,'')
    delPattern = re.compile('更多&gt;&gt;')
    for del_item in re.findall(delPattern,infoText):
        infoText = infoText.replace(del_item,'')

    infoPattern = re.compile(r'>(.*?)<')
    infoTextList = re.findall(infoPattern,infoText)
    infoTextList = [n for n in infoTextList if n != '']

    
    iDict = {}
    for t in infoTextList:
        t = t.replace('\\xa0','')
        #username, location, gender, date_of_birth, introduction, tags
        for label in ['昵称','地区','性别','生日','简介','标签']:
            if label in t:
                iDict[label] = t.strip(label).strip(':') if t.strip(label).strip(':') != '' else ''
                
                
    htmlText = html_.text
    dengjiPattern = re.compile('会员等级：(.*?)&')
    try:
        dengji = re.findall(dengjiPattern,htmlText)[0]
    except:
        dengji = u'未开通'
    iDict['会员等级'] = dengji
    
    
    url = url.replace('/info','/profile')
    try:
        htmlText = requests.get(url,cookies=cookie,headers=header,timeout=10).text
    except:
        continue
    try:
        weiboNumPattern = re.compile('微博\[(.*?)\]')
        weiboNum = re.findall(weiboNumPattern,htmlText)[0]
        guanzhuNumPattern = re.compile('关注\[(.*?)\]')
        guanzhuNum = re.findall(guanzhuNumPattern,htmlText)[0]
        fensiNumPattern = re.compile("粉丝\[(.*?)\]")
        fensiNum = re.findall(fensiNumPattern,htmlText)[0]
    except:
        print(u'++++++++++++++++blocked, wait for a while++++++++++++++++')
        time.sleep(200)
        weiboNum = 0
        guanzhuNum = 0
        fensiNum = 0
    iDict['微博数量'] = weiboNum
    iDict['关注数量'] = guanzhuNum
    iDict['粉丝数量'] = fensiNum
    iDict['ID'] = numID
    data.append(iDict)
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

columns = ['ID','username','location','gender','dob','introduction','tags','level','weibos','following','followers']
newData = []
for i in data:
    lineData = []
    for c in columns:
        lineData.append(i.get(c,''))
    newData.append(lineData)

pd.DataFrame(newData,columns=columns).to_excel(u'commenters.xlsx',index=False)
    
