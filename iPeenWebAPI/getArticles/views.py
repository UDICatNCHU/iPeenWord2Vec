from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from TopCosineSimilarity.TopCosineSimilarity import GetTopResult
# Create your views here.

def get(request):
    obj = GetTopResult('./TopCosineSimilarity/med250.model.bin', 'mongodb://140.120.13.244:7777/')
    termStr = request.GET['term']
    num = request.GET['num']
    termList = termStr.split()
    print(termList)
    returnList = obj.getArticle(termList, int(num)) # 回傳[文章資訊dict, ... , 文章資訊dict]
    
    showList = list()
    for item in returnList:
        innerList = list()
        innerList.append(item['Content'])
        innerList.append(item['Top20'])
        showList.append(innerList)

    # print(showList)
    context = {'showList': showList}
    return render(request, 'getArticles/index.html', context)