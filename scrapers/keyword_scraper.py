#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#need to install requests, pandas, lxml, xlrd and openpyxl

import requests,re,time
from lxml.etree import HTML
from lxml import html as HTMLParser
import pandas as pd

    
key = u'音乐'  #keyword: music
cookie={"Cookie":'_T_WM=79f8129787a95356116ab2e7715b968d; SUB=_2A252drqeDeRhGeRL71sU8ivEyjyIHXVVmMbWrDV6PUJbkdANLU39kW1NUyLP7S0wHskwhauI8p-KtDAr31jmUIkN; SUHB=0xnTO9mUNrlKXN; SCF=Am9vEoCU57YFDb1PBCYw0NJQiiVyWPcwlJRBX3O2jU7RE3ysLF8kiweO9pcK9Zjc1aAmgA-Al_2DISGlpQhjH98.; SSOLoginState=1534249678'}
header={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'
        } #need to update the cookie almost once a week

data = []
#scrape the first 100 pages of searching result
for page in range(100):
    page += 1
    url = "http://weibo.cn/search/mblog?keyword="+key+"&page="+str(page)+"&sort=hot"
    try:
        html = requests.get(url,cookies=cookie,headers=header,timeout=10).content
    except:
        continue
    html = HTML(html)
    
    pageData = []
    for item in html.xpath("//div[@class='c' and @id]"):
        #ID and username
        ID = item.attrib['id']
        nickName = item.xpath('div[position()=1]/a[@class="nk"]')[0].text
        print(nickName)
        content = item.xpath('div[position()=1]/span[@class="ctt"]')[0]
        #likes
        content = content.xpath('string(.)')
        zan = item.xpath('div/a[starts-with(@href,"https://weibo.cn/attitude")]')[0]
        zanPattern = re.compile(r'\[(.*?)\]')
        zanNum = re.findall(zanPattern,zan.text)[0]
        zanURL = zan.attrib['href'] 
        #reposts
        zhuan = item.xpath('div/a[starts-with(@href,"https://weibo.cn/repost")]')[0]
        zhuanPattern = zanPattern
        zhuanNum = re.findall(zhuanPattern,zhuan.text)[0]
        zhuanURL = zhuan.attrib['href'] 
        #comments
        ping = item.xpath('div/a[starts-with(@href,"https://weibo.cn/comment")]')[0]
        pingPattern = zanPattern
        pingNum = re.findall(pingPattern,ping.text)[0]
        pingURL = ping.attrib['href'] 
        #time
        shijian = item.xpath('div/span[@class="ct"]')[0].text
        pageData.append([ID,nickName,content,zanNum,zanURL,zhuanNum,zhuanURL,pingNum,pingURL,shijian])
    
    data.extend(pageData)

    
pd.DataFrame(data,columns=['id','username','content','likes','page_of_likes','reposts','page_of_reposts','comments','page_of_comments','time_source']).to_excel(u'keyword_music.xlsx',index=False)

    
