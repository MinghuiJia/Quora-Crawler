import os

def readTxt(file_path):
    file = open(file_path, 'r')
    lines = file.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    file.close()
    return lines

def noProcessUrls(processedUrls, allUrls):
    leftUrls = []
    for i in range(len(allUrls)):
        if (allUrls[i] not in processedUrls):
            leftUrls.append(allUrls[i])
    return leftUrls

def write2Txt(file_path, urls):
    file = open(file_path, 'w')
    for i in range(len(urls)):
        file.write(urls[i]+"\n")
    file.close()

if __name__ == "__main__":
    keywordsList = [
        'china energy conservation',  # 全部搜集完了/question
        # 'energy conservation',
        'china double carbon plan',     #全部搜集完了/question(无问题)
        # 'double carbon plan',
        'china carbon peak',    # 全部搜集完了/question-answer
        # 'carbon peak',
        'china new energy',     # 全部搜集完了/question
        'china technology', # 全部搜集完了/answer
        'china carbon neutrality',  # 全部搜集完了/question-answer
    ]
    alreadyProcessUrls = []

    file_save_dir = "./noProcess/"
    if (not os.path.exists(file_save_dir)):
        os.mkdir(file_save_dir)

    for keyword in keywordsList:
        file_path_already_process = "./alreadyProcess/"+str(keyword)+"_AnsweredQuestionUrls.txt"
        answersUrls_process = readTxt(file_path_already_process)
        alreadyProcessUrls += answersUrls_process

    for keyword in keywordsList:
        file_save_path = file_save_dir + str(keyword) + "_AnsweredQuestionUrls.txt"

        file_path_answer = "./unionQuestionAnswerType/" + str(keyword) + "_AnsweredQuestionUrls.txt"
        answersUrls = readTxt(file_path_answer)
        leftUrls = noProcessUrls(alreadyProcessUrls,answersUrls)

        write2Txt(file_save_path, leftUrls)
        print(keyword, " has ", len(answersUrls), " urls, and ", len(leftUrls), "urls without process...")
    aaa = 10
