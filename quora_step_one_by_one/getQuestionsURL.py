from bs4 import BeautifulSoup
import urllib.parse
import time
import os
import random

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

def mouseMoveRandom(browser):
    actions = ActionChains(browser)
    actions.move_by_offset(random.random()*200, random.random()*300)
    time.sleep(random.randint(1, 5))
    actions.key_down(random.randint(2,5))
    time.sleep(random.randint(1, 3))
    actions.key_up(random.randint(2,5))
    time.sleep(random.randint(1, 3))

def getCurrentPageQuestions(browser, already_exist_urls, answered_urls, answered_file):
    # 使用bs4解析页面信息
    html_source = browser.page_source
    soup = BeautifulSoup(html_source, 'html.parser')

    # 寻找所有的问题帖子，并搜集问题的href链接
    raw_main_content = soup.find_all('div', attrs={'id': 'mainContent'})[0]
    # 获取有回答的帖子的所有元素
    answereds = raw_main_content.find_all('div', attrs={'class': 'q-box qu-borderBottom qu-p--medium qu-pb--tiny'})

    # 随机操作
    # mouseMoveRandom(browser)

    # 循环解析每个answered question的card
    for each in answereds:
        divEle = each
        divEle2 = divEle.find('span', attrs={'class': 'q-text qu-dynamicFontSize--regular qu-color--blue_dark qu-bold'})
        aEle = divEle2 and divEle2.find('a')
        href = aEle and aEle['href']

        # 可能没有找到对应的元素，就直接过滤
        # 需要判断这个url是否已经存在当前的txt中
        if (href and (href not in already_exist_urls)):
            if (href not in answered_urls):
                answered_urls.append(href)
                already_exist_urls.append(href)
                print("get answered question url: ", href)

                # 随机操作
                # mouseMoveRandom(browser)

                # 获取到一个新的url就写入到文本
                write2txt2(href, answered_file)

    # 随机操作
    # mouseMoveRandom(browser)

def crawlKeywordsHierarchy(browser, keywords, already_exist_urls, answered_file):
    print("In crawlKeywordsHierarchy() keywords: ", keywords, "...")

    # Starting node link
    # 根据关键词搜索相关的帖子
    url = 'http://www.quora.com/search?q=' + urllib.parse.quote(keywords) + '&type=question'
    # url = 'http://www.quora.com/search?q=' + urllib.parse.quote(keywords) + '&type=answer'

    browser.get(url)

    # 随机操作
    # mouseMoveRandom(browser)

    # 存储有回答的帖子
    answered_urls = []

    # # Fetch /about page
    src_updated = browser.page_source
    src = ""
    same_page_count = 0
    while True:
        # 先滚动到底部
        src = src_updated
        browser.execute_script("window.scrollBy(0, 300);")
        time.sleep(5)
        # browser.implicitly_wait(5)
        src_updated = browser.page_source

        # 随机操作
        # mouseMoveRandom(browser)

        if (src == src_updated):
            same_page_count += 1
        if (same_page_count > 100):
            same_page_count = 0
            browser.execute_script("window.scrollBy(0, -50);")
            time.sleep(5)
            # browser.implicitly_wait(5)
            src_updated = browser.page_source

        # 每次页面滚动之后，都进行解析页面，获取当前页面的问题url
        getCurrentPageQuestions(browser, already_exist_urls, answered_urls, answered_file)

        try:
            # 寻找问题加载完成时的“没有更多了”按钮，结束滚动加载（需要找No answer yet对应card的selector）
            noAnsweredsCard = browser.find_elements_by_css_selector('#mainContent div[class="q-box qu-borderBottom qu-p--medium"]')
            # 选择最后一个元素
            more_button = noAnsweredsCard[-1]
            # 这个元素出现表示没有相关问题了
            if more_button.text == "We couldn't find any more results for '" + keywords + "'.":
                print("normal break")
                break
            # 这个元素出现表示爬虫被检测到，或网络不好
            elif more_button.text == "We couldn't find any results for '" + keywords + "'.":
                print("spider is detected...")
                time.sleep(60)
                # # 这里可以解开，就会循环继续重新刷新页面。不解开就结束该关键词的查询
                # # 这里可以优化，例如几次重新刷新查询后就不再继续收集该关键词的问题
                # browser.get(url)
                break
        except Exception as e:
            # print(e)
            continue

        continue

    return answered_urls

def write2txt2(url, file):
    file.write(url+"\n")
    file.flush()
    print("write ", url, " to file ")

def readTxt(file, already_exist_urls):
    file.seek(0)
    lines = file.readlines()
    if (len(lines)):
        for line in lines:
            already_exist_urls.append(line.strip())

def getQuestionsUrlsByKeywords(keywords):
    # chromedirver模拟操作浏览器
    chromedriver = "chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    browser = webdriver.Chrome()

    # 用于记录问题的文本
    answered_file_path = '.\\'+keywords+'_AnsweredQuestionUrls.txt'
    # txt中已经存在的urls
    already_exist_urls = []

    # 记录问题的txt文本存在则直接读取内容，不存在则会创建
    answered_file = open(answered_file_path, 'a+')

    # 读取已经收集到的问题url
    readTxt(answered_file, already_exist_urls)

    # 这里返回的answered_urls是每次程序运行后追加到txt中的新url，暂时没有用处
    answered_urls = crawlKeywordsHierarchy(browser, keywords, already_exist_urls, answered_file)

    answered_file.close()

    browser.quit()

if __name__ == "__main__":
    keywordsList = [
        'china carbon neutrality',
        'china energy conservation',
        'china double carbon plan',
        'china carbon peak',
        'china new energy',
        'china technology',
    ]
    # 问题收集
    for keyword in keywordsList:
        print("search keyword ", keyword)
        print("start get keyword-related questions")
        getQuestionsUrlsByKeywords(keyword)
        time.sleep(60)
