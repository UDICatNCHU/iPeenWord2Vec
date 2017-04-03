import numpy as np
from gensim import models
import operator
from bson.objectid import ObjectId


class GetTopResult(object):
    """
    
    """
    def __init__(self, modelPath, uri):
        from pymongo import MongoClient
        self.client = MongoClient(uri)
        self.db = self.client['iPeen']
        self.coll = self.db['ipeenArticleInfo']
        self.modelPath = modelPath


    def getArticle(self, inputTermList, topNum):
        model = models.KeyedVectors.load_word2vec_format(self.modelPath, binary=True)
        uninitialized = True
        for item in inputTermList:
            try:
                if uninitialized:
                    sumVec = model[item]
                    uninitialized = False
                else:
                    sumVec += model[item]
            except:
                continue
        # 至此已經得到使用者Query的所有Term的加總向量，為sumVec

        # self.getMostSimilar(sumVec, topNum)
        idList = self.getMostSimilar(sumVec, topNum)
        resultList = list()
        for item in idList:
            resultArticle = self.coll.find({"_id": ObjectId(item)}, {'Vector': False, 'ID': False})
            # print(type(resultArticle[0])) # <class 'dict'>
            resultList.append(resultArticle[0])
        
        return resultList


    def getMostSimilar(self, queryVec, num):
        allVectors = self.coll.find({}, {'Vector':True, '_id':True})
        # topCosineSimilarity = 0.0
        vecDict = dict()
        for vector in allVectors:
            array = np.array(vector['Vector']) # 資料庫裡的Vector欄位，當初是以.tolist()存進json，則拿出來要這樣復原
            cosineSimilarity = np.dot(queryVec, array)/(np.linalg.norm(queryVec) * np.linalg.norm(array))
            vecDict[vector['_id']] = cosineSimilarity
        
        sorted_vecDict = sorted(vecDict.items(), key=operator.itemgetter(1), reverse=True)
        objectIDList = list()
        for item in sorted_vecDict[0:num]:
            objectIDList.append(item[0])

        return objectIDList # 回傳[58d8e3850383b11732f87a0d, 58d8e3860383b11732f87c76]



    def testMongo(self):
        result = self.coll.find({}, {'Vector':1, 'ID':True, '_id':False})
        for item in result:
            array = np.array(item['Vector'])
            print(item)


    def main(self):
        self.testMongo()



if __name__ == '__main__':
    import sys
    queryList = list()
    for item in sys.argv:
        if item == sys.argv[0]: continue
        queryList.append(item)

    obj = GetTopResult('./med250.model.bin', 'mongodb://140.120.13.244:7777/')
    # for item in obj.getArticle(queryList, 10):
    #     print(item)
    print(obj.getArticle(queryList, 2))


