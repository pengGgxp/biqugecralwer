import os
import sys
from io import StringIO

from selenium import webdriver
from time import sleep
from selenium.common import exceptions
import atexit
import re


def load_prograss(filename, url_old):
    # 读取tmp文件中的进度
    try:
        with open('tmp/tmp_' + filename + '.txt', 'r', encoding='utf-8') as tmp:
            url = tmp.readline()
        tmp.close()
        print('url已定义为：' + url)
        if url != '':
            if url != url_old:
                return url
            else:
                print(
                    f'已保存进度中的链接和输入的链接冲突，请检查是否已经下载完成！\t，如果仍要使用进度中的链接，请将"output/{filename}.txt"文件删除后重试')
        else:
            print(f'正常读取进度失败，请尝试删除"output/{filename}.txt"文件删除后重试')
    except:
        print(f'正常读取进度失败，请尝试删除"output/{filename}.txt"文件删除后重试')


def browser_process(driver, url):
    driver.get(url)
    # sleep(1)
    start_url = driver.current_url
    print('已正常进入:' + start_url)
    return driver


def create_file_and_write_novelname(driver, url):
    # sleep(1)
    print('正在获取文件名')
    sleep(0.5)
    filename = driver.find_element_by_xpath('//*[@id="info"]/h1').text  # 文件名
    if not os.path.exists('output/' + filename + '.txt'):
        with open('output/' + filename + '.txt', 'w', encoding='utf-8') as file:
            file.write(filename + '\n\n')
        return url, filename + '.txt'
    else:
        print('发现已保存的进度，即将获取...')
        url2 = load_prograss(filename, url)
        return url2, filename + '.txt'


def iselement(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except exceptions.NoSuchElementException:
        return False




def isrepeat(filename, title, List):
    if List != []:
        with open('output/' + filename, 'r+', encoding='utf-8') as file:  #
            lines = file.readlines()
            for i in lines:
                if re.match(title, i) is not None:
                    return True
            List.clear()
            return False
    else:
        List.clear()
        return False



def crawl_conten(driver, filename, start):
    # 爬取内容
    if iselement(driver, '//*[@id="list"]/dl/dd[1]/a'):
        driver.find_element_by_xpath('//*[@id="list"]/dl/dd[1]/a').click()  # 点击第一章
        sleep(0.5)

    title = driver.find_element_by_xpath('//*[@id="content_read"]/div/div[2]/h1').text
    content = driver.find_element_by_xpath('//*[@id="content"]').text
    with open('output/' + filename, 'a+', encoding='utf-8') as file:  # 存储文本
        file.write(title + '\n')
        file.write('\n')
        file.write(content + '\n\n')
    # 存储进度
    with open('tmp/tmp_' + filename, 'w+', encoding='utf-8') as tmp:
        tmp.write(driver.find_element_by_xpath('//*[@id="content_read"]/div/div[6]/a[3]').get_attribute('href'))
    tmp.close()



def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=r'chromedriver-win64/chromedriver.exe', chrome_options=options)
    return driver


# if __name__ == '__main__':
    # # 读取文件
    # with open('pro.txt', 'r', encoding='utf-8') as file:
    #     for i in file.readlines():
    #         i = i.replace('\n', '')
    #         i = i.replace('\r', '')
    #         url = i
    #         main()
