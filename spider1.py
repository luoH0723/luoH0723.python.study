#Author:LH
#-*- codeing = utf-8 -*-
# @Time : 2020/5/2 15:46
# @Author: lh
# @Site : 
# @File : spider.py
# @Software: PyCharm

'''
爬取豆瓣top250
'''

from bs4 import BeautifulSoup #网页解析，获取数据
import re #正则表达式，进行文字匹配
# 推荐requests
import urllib.request,urllib.error  #制定URL获取网页数据
import requests  #制定Url获取网页数据
import  xlwt   #进行excel操作
import sqlite3  #进行SQLLite数据库操作
import pymysql
import time



def main():
    # 测试输出
    # print("hello")
    #1.爬取网页
    elementUrl="https://movie.douban.com/top250?start="
    dataList = getData(elementUrl)

    #2.解析数据
    # askUrl(elementUrl)
    #3.保存数据到excel
    # savepath = ".\\豆瓣电影Top250.xls"
    # saveDataExcel(dataList,savepath)
    #4.保存数据到mysql
    saveDataMysql(dataList)

#影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')     #创建正则表达式对象，表示规则（字符串的模式）
#影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)   #re.S 让换行符包含在字符中
#影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#找到评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#找到概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
#找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

#爬取网页
def getData(elementUrl):

    #1.空数据
    dataList = []

    for i in range(0,10): #调用获取信息的函数10次
        url = elementUrl + str(i*25)
        html = askUrl(url)
        #2.逐一解析数据
        #使用html解析器
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"): #查找符合条件的字符串，形成列表 下划线表示这是属性值
            # print(item)
            # break
            data = [] #保存一部电影的所有信息
            item = str(item)

            # 找到符合规则的部分
            # 获取详情链接规则
            link = re.findall(findLink,item)[0]  #使用re库通过正则表达式查找指定的字符串
            data.append(link)
            imgSrc = re.findall(findImgSrc,item)[0]
            data.append(imgSrc)
            titles = re.findall(findTitle,item)
            if len(titles) == 2:
                ctitle = titles[0]       #添加中文名
                data.append(ctitle)
                otitle = titles[1].replace("/","")  #替换斜杠
                data.append(otitle)     #添加外文名
            else:
                data.append(titles[0])
                data.append(" ")         #外文名留空
            rating = re.findall(findRating,item)[0]
            data.append(rating)
            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum)
            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq = inq[0].replace("。","")  #去掉句号
                data.append(inq)
            else:
                data.append(" ")

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)   #去掉<br/>
            bd = re.sub('/'," ",bd)  #替换/
            data.append(bd.strip())   #去掉空格

            dataList.append(data)       #把处理好的一部电影信息存到dataList

    # print(dataList)
    return dataList

#保存数据到excel
def saveDataExcel(datalist,dppath):
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)  # 创建book对象
    sheet = book.add_sheet('豆瓣电影Top250',cell_overwrite_ok=True)  # 创建工作表
    col = ("电影详情链接","图片链接","影片中文名","影片外文名","评分","评价数","影片概况","相关信息")
    for i in range(0,8):
        sheet.write(0,i, col[i])  # 写入数据，第一个参数“行”，第二个参数“列，第三个参数为内容
    for i in range(0,250):
        print("第%d条"%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])  #存入数据
    book.save(dppath)  # 保存数据表
    print("save....")

#保存数据到mysql
def saveDataMysql(datalist):
    #建立数据库连接
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='db_python_crawler',
        charset='utf8'
    )
    cursor=conn.cursor()
    print("连接成功")
    sql='''insert into t_douban(link, imgsrc, ctitle,otitle, rating, judge, inq, bd) values (%s, %s, %s, %s, %s, %s, %s, %s)'''
    for i in range(0,250):
        data = datalist[i]
        cursor.execute(sql,[data[0], data[1], data[2], data[3], data[4], data[5], data[6],data[7]])
        conn.commit()
    cursor.close()
    conn.close()

    print("success")

#得到制定一个uel的网页内容
def askUrl(url):
    # 伪装google浏览器
    head = {
        # 模拟浏览器头部
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }
    resp=requests.get(url,headers=head,timeout=5)
    html=""
    try:
        html = resp.content.decode("utf-8")
        # print(html)
    except BaseException as e:
        print("存在异常")

    return html
# main()

# 主函数  入口设置
if __name__ == "__main__":   #当前程序执行时
# 调用函数
    start=time.time()
    main()
    end=time.time()
    print("总耗时:%s"%(end-start))
