import _io
import asyncio
import datetime
import os
import threading
import time
import shutil
from io import StringIO
from time import sleep

import requests
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QProcess, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import main
from qtgui import Ui_MainWindow
import multiprocessing
import sys


def exceptOutConfig(exceptype, value, tb):
    print('错误信息：')
    print('Type:', exceptype)
    print('Value:', value)
    print('Traceback:', tb)




class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))


class showurls(QtCore.QObject):
    urlshow = QtCore.pyqtSignal(list)

    urlshow2 = QtCore.pyqtSignal(list)

    def showurl(self, listtxt):
        self.urlshow.emit(list(listtxt))

    def select_firsturl(self, listt):
        self.urlshow2.emit(list(listt))


class crawlers(QtCore.QObject):
    flag = QtCore.pyqtSignal(bool)
    def emit_flag(self, value):
        self.flag.emit(value)

class kaishijieshu(QtCore.QObject):
    shijian = QtCore.pyqtSignal(float)
    def start(self, T1):
        self.shijian.emit(T1)


# class dataholder(QtCore.QObject):
#     data_change = QtCore.pyqtSignal(str)
#     def __init__(self):
#         super().__init__()
#         self._data = ''
#
#
#     @property
#     def data(self):
#         return self._data
#
#     @data.setter
#     def data(self, value):
#         self._data = value
#         self.data_change.emit(str(value))


# class start(QtCore.QObject):
#     starturl = QtCore.pyqtSignal(str)
#
#     def starttherd(self, url):
#         self.starturl.emit(str(url))

# def run_selenium_crawler():
#     selenium_crawler()




class CrawlerThread(QThread):
    finished = QtCore.pyqtSignal()  # 创建一个信号，用来通知主线程任务完成


    def __init__(self, url, _stop):
        super().__init__()
        self.url = url
        self._stop = True

    def run(self):
        #run_selenium_crawler(self.url)  # 在这里执行你的爬虫任务
        if not os.path.exists('chromedriver-win64/chromedriver.exe'):
            print('找不到谷歌开发浏览器模块，正在下载...')
            file = requests.get('https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/win64/chromedriver-win64.zip')
            open('chromedriver-win64.zip', 'wb').write(file.content)
            print('下载完成，正在解压')
            shutil.unpack_archive(filename='chromedriver-win64.zip', format='zip')
            os.unlink('chromedriver-win64.zip')
            print('解压完成，正在启动程序')
            print('如果启动失败，请检查是否已经安装谷歌浏览器')


        try:

            self.driver = main.main()

            List = [1]

            # 进行爬取

            driver = main.browser_process(self.driver, self.url)
            url_new, filename = main.create_file_and_write_novelname(driver, self.url)
            driver = main.browser_process(driver, url_new)


            num = 0
            while self._stop:
                num += 1
                print(f'正在获取-第{num}个链接')
                if main.iselement(driver, '//*[@id="content_read"]/div/div[2]/h1'):
                    title = driver.find_element_by_xpath('//*[@id="content_read"]/div/div[2]/h1').text  # 获取标题
                    if main.isrepeat(filename, title, List):
                        print('重复章节，跳过!')
                        if main.iselement(driver, '//*[@id="content_read"]/div/div[3]/a[3]'):
                            driver.find_element_by_xpath('//*[@id="content_read"]/div/div[3]/a[3]').click()
                        else:
                            driver.refresh()
                        continue
                    else:
                        main.crawl_conten(driver, filename)
                        # 点击下一章
                        if main.iselement(driver, '//*[@id="content_read"]/div/div[3]/a[3]'):
                            if self.url != driver.find_element_by_xpath(
                                    '//*[@id="content_read"]/div/div[3]/a[3]').get_attribute('href'):
                                driver.find_element_by_xpath('//*[@id="content_read"]/div/div[3]/a[3]').click()
                            else:
                                print(f'output/{filename}获取完毕')
                                break
                        else:
                            driver.refresh()
                            if main.iselement(driver, '//*[@id="content_read"]/div/div[3]/a[3]'):
                                if self.url != driver.find_element_by_xpath(
                                        '//*[@id="content_read"]/div/div[3]/a[3]').get_attribute('href'):
                                    driver.find_element_by_xpath('//*[@id="content_read"]/div/div[3]/a[3]').click()
                                else:
                                    print(f'output/{filename}获取完毕')
                                    break
                else:
                    driver.find_element_by_xpath('//*[@id="list"]/dl/dd[1]/a').click()  # 点击第一章
            # close
            #driver.quit()

            self.finished.emit()  # 发射任务完成的信号
        except:
            self.finished.emit()
    def stop(self):
        self._stop = False



class Outoutwritten(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Outoutwritten, self).__init__()
        self.setupUi(self)

        icon = QIcon("favicon.ico")  # 替换为你的图标文件路径
        self.setWindowIcon(icon)

        sys.stdout = EmittingStr(textWritten=self.outputtxt)
        # sys.stdout.textWritten.connect(self.outputtxt)
        sys.stderr = EmittingStr(textWritten=self.outputtxt)
        # sys.stderr.textWritten.connect(self.outputtxt)

        # 读取pro.txt  显示其中的链接
        self.showurl = showurls()
        self.showurl.urlshow.connect(self.printtxt)
        self.showurl.urlshow2.connect(self.selecturl_first)
        if not os.path.exists('pro.txt'):
            with open('pro.txt', 'w', encoding='utf-8') as file:
                file.write('请在此放入链接，一行一个\n')
                file.write('https://www.beqege.com/65507/\n')
                file.write('https://www.beqege.com/65507/\n')

        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        if not os.path.exists('output'):
            os.mkdir('output')
        with open('pro.txt', 'r+', encoding='utf-8') as file:
            listtxt = file.readlines()
            self.showurl.showurl(listtxt)
            self.showurl.select_firsturl(listtxt)

        # 绑定自动存储
        self.pendin_urls.textChanged.connect(self.save_pro)
        # 绑定自动获取连接
        self.saveurl.clicked.connect(self.selecturl)

        # 绑定开始处理函数
        self.submit.clicked.connect(self.start_task)
        #stop
        self.stop.clicked.connect(self.stop_task)

        self.crawler_thread = CrawlerThread(None, None)  # 创建一个 CrawlerThread 的实例
        self.crawler_thread.finished.connect(self.on_crawler_finished)  # 将任务完成的信号连接到槽函数

        # 计时绑定
    #     self.starttime = kaishijieshu(shijian=self.yunxingshijian)
    #     #self.starttime.shijian.connect(self.yunxingshijian)
    #     self.starttime.start(time.clock())
    #
    #
    # def yunxingshijian(self, T1):
    #     while True:
    #         T2 = time.clock()
    #         self.time = T2 - T1
    #         time.sleep(1)
    #         print('程序运行时间: '+ self.time + 's')


    def start_task(self):
        url = self.select_url.currentText()
        self.crawler_thread.url = url
        try:
            self.crawler_thread.start()
        except NoSuchElementException:
            self.crawler_thread.stop()
            self.crawler_thread.start()

    def stop_task(self):
        print('正在停止任务...')
        self.crawler_thread.stop()

    def on_crawler_finished(self):
        self.crawler_thread._stop = True
        self.crawler_thread.driver.quit()
        print("爬虫任务结束")  # 这里可以添加任务完成后的操作

    # def starttimer(self, flag):
    #     if flag:
    #         T1 = time.time()
    #         starttime = datetime.datetime.utcnow()
    #         print('开始时间：' + starttime.strftime("%Y-%m-%d %H:%M:%S"))
    #     while flag:
    #         print('正在爬取\\\\', end='\r')
    #         print('正在爬取--', end='\r')
    #         print('正在爬取//', end='\r')
    #         print('正在爬取--', end='\r')
    #     T2 = time.time()
    #     endtime = datetime.datetime.utcnow()
    #     print('结束时间：' + endtime.strftime("%Y-%m-%d %H:%M:%S"))
    #     print(f"总共耗时{T2 - T1}")




    def selecturl_first(self, listt):
        for i in range(len(listt)):
            if listt[0] != '\n':
                listt.append(listt[0].rstrip('\n'))
            listt.pop(0)
        self.select_url.addItems(listt)


    def selecturl(self):
        self.select_url.clear()
        with open('pro.txt', 'r+', encoding='utf-8') as file:
            listt = file.readlines()
            for i in range(len(listt)):
                if listt[0] != '\n':
                    listt.append(listt[0].rstrip('\n'))
                listt.pop(0)
            self.select_url.addItems(listt)


    def save_pro(self):
        self.urls = self.pendin_urls.toPlainText()
        with open('pro.txt', 'w+', encoding='utf-8') as file:
            file.write(self.urls)


        # 展示pro.txt链接 槽函数


    def printtxt(self, listtxt):
        for i in listtxt:
            self.pendin_urls.append(i)


    def outputtxt(self, text):
        cursor = self.log_txt.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.log_txt.setTextCursor(cursor)
        self.log_txt.ensureCursorVisible()


if __name__ == '__main__':
    sys.excepthook = exceptOutConfig
    app = QApplication(sys.argv)
    # 设置应用程序图标
    app.setWindowIcon(QIcon("favicon.ico"))  # 替换为你的图标文件路径
    win = Outoutwritten()
    win.show()
    sys.exit(app.exec_())
