from gensim import models
import numpy as np
import jieba.analyse
import re


class exportToMongo(object):
    """
    exportToMongo類別用於計算每篇文章top20關鍵字，並計算它們的向量和，再將文章內容、前20關鍵字與向量加總放入MongoDB
    需初始化成員filePath為文檔路徑，modelPath為word2vec訓練之model路徑，uri為MongoDB主機之uri
    """
    def __init__(self, filePath, modelPath, uri):
        from pymongo import MongoClient
        self.file = open(filePath, 'r')
        self.modelPath = modelPath
        self.stopwords = {'我們', '他們', '這裡', '真的', '這次', '其實', '非常', '這麼', '什麼', '可以', '不過', '雖然', '還是', '還有', '沒有', '不會', '有點', '這道', '這個', '這是', '裡面', '時候', '因為', '一整', '整個', '相當', '應該', '還蠻'}
        self.client = MongoClient(uri)
        self.db = self.client['iPeen']
        self.coll = self.db['ipeenArticleInfo']
        

    def insertDB(self):
        bigList = self.tfidfProcess()
        print('===已計算完所有文章的Top20關鍵字，開始計算每篇文章關鍵字的向量加總與輸入資料庫===')
        self.getSumVectorsAndInsertDB(bigList)


    def tfidfProcess(self):
        """
        輸入：整個文檔
        輸出：用來放所有文章關鍵字的list，長度為15萬（有15萬篇文章），每個entry為一個長度為20的list存放20個關鍵字
        """
        printCount = 0
        returnList = list() # 用來放所有文章的關鍵字
        for article in self.file.readlines(): # loops over 一篇一篇的文章
            kwList = list()
            articleResultList = jieba.analyse.extract_tags(article, topK=30, withWeight=True, allowPOS=())
            for item in articleResultList: # 一個item是 ('冰淇淋', 0.3858822943471564)
                if len(kwList) < 20:
                    if item[0] in self.stopwords: # 如果斷詞是stopword，則不放進returnList
                        continue
                    string = re.match(u"[\u4e00-\u9fa5]+", item[0])
                    if string:
                        kwList.append(item[0])
                    else: # 如果斷詞不含中文字，則不放進returnList
                        continue
                else:
                    break
            returnList.append(kwList)

            printCount += 1
            if printCount % 1000 == 0: print('已經計算完前' + str(printCount) + '篇文章的Top20關鍵字')

        return returnList


    def getSumVectorsAndInsertDB(self, bigList):
        model = models.KeyedVectors.load_word2vec_format(self.modelPath, binary=True)
        index = 0
        insertList = list()
        self.file.seek(0)
        articleList = self.file.readlines()

        forPrinting = 0
        for kwList in bigList:
            oneArticleInfoDict = dict()
            for kw in kwList: # 初始化向量用
                try:
                    sumVec = np.zeros_like(model[kw]) # 初始化一個250維向量
                    break
                except:
                    continue

            for item in kwList:
                try:
                    sumVec += model[item]
                except:
                    continue
            print(type(sumVec)) # <class 'numpy.ndarray'>
            oneArticleInfoDict['ID'] = index+1
            oneArticleInfoDict['Content'] = articleList[index]
            oneArticleInfoDict['Top20'] = kwList
            oneArticleInfoDict['Vector'] = sumVec.tolist()
            index += 1
            state = self.coll.insert(oneArticleInfoDict)
            
            forPrinting += 1
            if forPrinting % 1000 == 0: print('已經塞完' + str(forPrinting) + '篇文章進資料庫')


    def main(self):
        self.insertDB()
        print('>>> 已經將所有文章資訊都輸入至MongoDB <<<')
        # self.getSumVectorsAndInsertDB([['冰淇淋', '燒肉']])




if __name__ == '__main__':
    obj = exportToMongo('./AllArticles.txt', './med250.model.bin', 'mongodb://140.120.13.244:7777/')
    obj.main()