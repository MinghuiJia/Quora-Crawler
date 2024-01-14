import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# import pymysql

def readTxt(file, already_exist_urls):
    file.seek(0)
    lines = file.readlines()
    if (len(lines)):
        for line in lines:
            already_exist_urls.append(line.strip())

# 登录之后展开按钮是more按钮需要通过这个查询，而没登录是Continue Reading按钮
def getFirstContinueButton(clickName, browser):
    time.sleep(5)
    # 这是登录之后查询的selector语句
    # allClickEles = browser.find_elements_by_class_name('.qt_read_more')
    allClickEles = browser.find_elements_by_css_selector('.puppeteer_test_read_more_button')
    for each in allClickEles:
        if (clickName in each.text):
            return each
        elif (clickName == each.text):
            return each
    return None

def getAllRelatedOrAnswersButton(clickName, browser):
    time.sleep(5)
    menuClickEles = browser.find_elements_by_css_selector('#mainContent>div:nth-child(2) .q-click-wrapper')
    for each in menuClickEles:
        if (clickName in each.text):
            return each
        elif (clickName == each.text):
            return each
    return None

def getProfileInfo(href, browser):
    time.sleep(5)
    browser.get(href)

    # 寻找profile中的信息
    time.sleep(5)
    # 基本信息
    baseInfos = browser.find_elements_by_css_selector('#mainContent>div:nth-child(1)>div:nth-child(1)>div:nth-child(2)>div')
    # 全部注册时的信息
    allInfos = browser.find_elements_by_css_selector('#mainContent~div>div>div:nth-child(1)>div[class*="q-text"]>div[class*="q-text"]')

    infoList = []
    for info in allInfos:
        contentEle = info.find_elements_by_css_selector('.q-text .qu-truncateLines--2>span')
        grayInfoText = ""
        if (len(contentEle) == 2):
            grayInfoText = contentEle[1].text
        baseInfoText = contentEle[0].text
        infoList.append([baseInfoText, grayInfoText])

    infoList.append([baseInfos[0].text, ""])    # name
    infoList.append([baseInfos[1].text, ""])    # describle
    infoList.append([baseInfos[-2].text, ""])   # followers
    return infoList

# def insertData2Mysql(sql, param):
#     # 存储到数据库
#     # 连接数据库
#     conn = pymysql.connect(host='localhost', port=3306,
#                            user='root', password='JMHjmh1998',
#                            database='crawlerdb')
#
#     # 使用 cursor() 方法创建一个游标对象 cursor
#     cursor = conn.cursor()
#
#     try:
#         cursor.execute(sql, param)
#         conn.commit()
#     except Exception as e:
#         print(e)
#         conn.rollback()
#     finally:
#         conn.close()

def extractPageInfo(browser, url, keyword, func):
    # 将所有的帖子都展开，点击所有more或者continue reading按钮
    while True:
        try:
            time.sleep(5)
            # 先获取第一个可以点击的按钮
            clickEle = getFirstContinueButton('Continue Reading', browser)
            # 点击按钮，页面会更新（所以每次需要重新find按钮）
            if (clickEle): browser.execute_script("arguments[0].click();", clickEle)

            # 移动到按钮的位置
            clickEle2 = getFirstContinueButton('Continue Reading', browser)
            if (clickEle2): browser.execute_script("arguments[0].scrollIntoView()", clickEle2)

            time.sleep(5)

            if (not clickEle2 and not clickEle):
                break
        except:
            continue

    # 使用bs4解析页面信息
    html_source = browser.page_source
    soup = BeautifulSoup(html_source, 'html.parser')

    # 可能出现访问页面出错502. Bad Gateway. Quora is temporarily unavailable. Please wait a few minutes and try again.
    questionNameEle = None
    answereds = None
    try:
        # 寻找所有的问题帖子，并搜集问题的href链接
        raw_main_content = soup.find_all('div', attrs={'id': 'mainContent'})[0]
        # 获取问题
        questionNameEle = raw_main_content.find('div', attrs={'class': 'puppeteer_test_question_title'})
        # 获取有回答的帖子的所有元素
        # answereds = raw_main_content.find_all('div', attrs={'class': re.compile("dom_annotate_question_answer_item_\d+")})
        answereds = raw_main_content.select('#mainContent div[class*="dom_annotate_question_answer_item"]')
    except (Exception, BaseException) as e:
        print(e)
        time.sleep(300)

        # 如果出现任何意外就重新开始解析这个问题的帖子
        func(browser, url, keyword)

        return

    questionName = questionNameEle.text
    print("collected ", len(answereds), " answer list-item")
    print("question name: ", questionName)

    # 解析每个回答的信息列表
    upvoteCounts = []
    downvoteCounts = []
    shareCounts = []
    commentCounts = []
    contents = []
    profiles = []

    # 记录解析到第几个回答
    processCount = 1
    # 打开profile页面，用于后续解析个人信息
    chrome_options = Options()
    # chrome_options.add_argument('--no-sandbox') #禁用sandbox，让Chrome在root权限下跑
    # chrome_options.add_argument('--disable-dev-shm-usage')
    browserProfile = webdriver.Chrome(chrome_options=chrome_options)

    for answered in answereds:
        try:
            print("processing answer ", processCount, ' start...')

            # 解析出profile的链接，打开去获取用户信息
            info1 = answered.find('div', attrs={'class': 'q-click-wrapper'})
            # 存在部分情况，像china world leader，回答问题的是 answered by，就没有spacing_log_answer_header，直接找a标签看看
            aHeadEle = None
            if (info1.find('div', attrs={'class': 'spacing_log_answer_header'})):
                aHeadEle = info1.find('div', attrs={'class': 'spacing_log_answer_header'}).find('a', attrs={
                    'class': 'qu-cursor--pointer'})
            else:
                aHeadEle = info1.find_all('a', attrs={'class': 'qu-cursor--pointer'})[2]
            profileHref = aHeadEle['href']

            # 打开个人主页解析个人信息，得到返回的信息列表
            profileList = getProfileInfo(profileHref, browserProfile)

            # 获取帖子回答的文本内容
            content = info1.find('div', attrs={'class': 'spacing_log_answer_content'})
            text = content.find('div', attrs={'class': 'q-text'})
            temp_content = text.text

            # 获取支持、反对、分享、评论数
            info2 = answered.find('div', attrs={'class': 'qu-zIndex--action_bar'})
            allButtons = info2 and info2.find_all('button', attrs={'aria-label': re.compile(".")})
            upvoteButtonEle = None
            downvoteButtonEle = None
            shareButtonEle = None
            commentButtonEle = None
            if (allButtons):
                if (len(allButtons) >= 1): upvoteButtonEle = allButtons and allButtons[0]
                if (len(allButtons) >= 2): downvoteButtonEle = allButtons and allButtons[1]
                if (len(allButtons) >= 3): shareButtonEle = allButtons and allButtons[2]
                if (len(allButtons) >= 4): commentButtonEle = allButtons and allButtons[3]
            upvoteCount = upvoteButtonEle and upvoteButtonEle['aria-label']
            downvoteCount = downvoteButtonEle and downvoteButtonEle['aria-label']
            shareCount = shareButtonEle and shareButtonEle['aria-label']
            commentCount = commentButtonEle and commentButtonEle['aria-label']

            # 所有信息解析完再对数据进行存储操作（防止某个解析崩掉信息不全，如果有信息没解析全，这条信息不会被记录）
            # 获取支持、反对、分享、评论数信息
            upvoteCounts.append(upvoteCount)
            downvoteCounts.append(downvoteCount)
            shareCounts.append(shareCount)
            commentCounts.append(commentCount)
            # 回答人基本信息
            profiles.append(profileList)
            # 回答文本
            contents.append(temp_content)

            # 数据预处理组织成存储到Mysql的形式
            otherinfo = ""
            for k in range(len(profileList)):
                otherinfo += (",".join(profileList[k]) + ";")
            upvoteCountNew = ""
            if (upvoteCount == "Upvote" or upvoteCount == None):
                upvoteCountNew = "0"
            else:
                upvoteCountNew = upvoteCount.split(" ")[0]
            commentCountNew = ""
            if (commentCount == "Comment" or commentCount == None):
                commentCountNew = "0"
            else:
                commentCountNew = commentCount.split(" ")[0]
            param = (
                questionName,
                profileList[-3][0],
                profileList[-1][0].split("\n")[0].split(" ")[0],
                profileList[-2][0],
                otherinfo,
                upvoteCountNew,
                commentCountNew,
                temp_content,
                keyword
            )

            # # 数据存储到数据库
            # sql = '''
            #         INSERT INTO quora_answers_questions(question_name,author_name,author_followers,author_describle,author_otherinfo,answer_upvotes,answer_comment_count,answer_content,keyword) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            #         '''
            # insertData2Mysql(sql, param)

        except (Exception, BaseException) as e:
            print(e)
        finally:
            print("processing answer ", processCount, ' finished...')
            processCount += 1

    # 清除浏览器缓存
    browser.delete_all_cookies()
    # 关闭当前页面
    browserProfile.quit()
    print(upvoteCounts)
    print(contents)
    print("upvoteCounts length: ", len(upvoteCounts), " contents length: ", len(contents))

# 获取一个问题下的所有回答
def getNormalAnsweredInfo(browser, url, keyword):
    browser.get(url)

    # 先切换从All related到Answers menu
    # 点击All related 按钮
    relatedEle = getAllRelatedOrAnswersButton('All related', browser)
    time.sleep(5)
    # 可能会存在问题的帖子里面没有这个按钮
    if (relatedEle): browser.execute_script("arguments[0].click();", relatedEle)

    # 点击Answers按钮
    answersEle = getAllRelatedOrAnswersButton('Answer', browser)
    time.sleep(5)
    # 可能会存在问题的帖子里面没有这个按钮
    if (answersEle): browser.execute_script("arguments[0].click();", answersEle)

    # 所有文本展开后，解析所有的回答card
    extractPageInfo(browser, url, keyword, getNormalAnsweredInfo)

# 与normal对比，没有comment的button，也不需要先进行选择answers
def getOtherFormatAnsweredInfo(browser, url, keyword):
    browser.get(url)

    # 所有文本展开后，解析所有的回答card
    extractPageInfo(browser, url, keyword, getOtherFormatAnsweredInfo)

def getAnsweredInfo(answered_file_path):
    # chromedirver模拟操作浏览器
    chromedriver = "chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    chrome_options = Options()
    # chrome_options.add_argument('--no-sandbox')  # 禁用sandbox，让Chrome在root权限下跑
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # 解析回答时不让图片加载，减少浏览器内存占用（回答过多可能导致浏览器内存不足）
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    browser = webdriver.Chrome(chrome_options=chrome_options)

    # 记录问题的txt文本存在则直接读取内容，不存在则会创建
    answered_file = open(answered_file_path, 'a+')

    # txt中已经存在的urls
    already_exist_urls = []
    # 读取已经收集到的问题url
    readTxt(answered_file, already_exist_urls)

    # 根据记录所有问题的url txt文件名，解析有关问题获取时所用的关键词
    keyword = answered_file_path.split("\\")[-1].split("_")[0]

    for url in already_exist_urls:
        temp = url.split("/")[2]
        print(url, " question start crawler...")
        if (temp == 'www.quora.com'):
            # 正常的问答帖子
            getNormalAnsweredInfo(browser, url, keyword)
        else:
            # 其他类型
            getOtherFormatAnsweredInfo(browser, url, keyword)
        time.sleep(60)

    browser.quit()

if __name__ == "__main__":
    keywordsList = [
        'china carbon neutrality',  # 全部搜集完了/question-answer
        'china carbon peak',  # 全部搜集完了/question-answer
        'china double carbon plan',  # 全部搜集完了/question(无问题)
        'china energy conservation',  # 全部搜集完了/question
        'china new energy',  # 全部搜集完了/question
        'china technology',  # 全部搜集完了/answer
    ]
    # 问题收集
    for keyword in keywordsList:
        # 回答获取
        # 目前前两个url还存在各漏掉1个回答，找找bug
        print(keyword, " txt start analysis...")
        getAnsweredInfo('.\\noProcess\\' + keyword + '_AnsweredQuestionUrls.txt')


# from selenium.webdriver.common.keys import Keys
# body = browser.find_element_by_tag_name('body')
# body.send_keys(Keys.UP)
# body.send_keys(Keys.DOWN)
# browser.execute_script("window.scrollTo(0, 0);")
# browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# browser.implicitly_wait(30)