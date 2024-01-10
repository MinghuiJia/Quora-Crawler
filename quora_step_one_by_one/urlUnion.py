import os

def readTxt(file_path):
    file = open(file_path, 'r')
    lines = file.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    file.close()
    return lines

def urlsUnion(urls1, urls2):
    for url in urls2:
        if (url not in urls1):
            urls1.append(url)
    return urls1

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
    for keyword in keywordsList:
        file_path_answer = "./answerType/"+str(keyword)+"_AnsweredQuestionUrls.txt"
        file_path_question = "./questionType/"+str(keyword)+"_AnsweredQuestionUrls.txt"
        file_save_dir = "./unionQuestionAnswerType/"
        aaa = os.path.exists(file_save_dir)
        file_save_path = file_save_dir+str(keyword)+"_AnsweredQuestionUrls.txt"
        if (not os.path.exists(file_save_dir)):
            os.mkdir(file_save_dir)
        answersUrls = readTxt(file_path_answer)
        questionUrls = readTxt(file_path_question)
        unionUrls = urlsUnion(questionUrls, answersUrls)
        write2Txt(file_save_path, unionUrls)
