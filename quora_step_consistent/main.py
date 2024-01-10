import time
from getQuestionsURL import getQuestionsUrlsByKeywords

# # chromedirver模拟操作浏览器
# chromedriver = "chromedriver"
# os.environ["webdriver.chrome.driver"] = chromedriver
# browser = webdriver.Chrome()

# 出bug的网址，因为这个帖子被分到了other函数中，里面没有all related answer的按钮
# https://www.quora.com/Is-global-warming-really-imminent-Why-do-many-countries-including-the-United-States-and-China-all-propose-the-goal-of-carbon-neutrality  question start crawler...

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

