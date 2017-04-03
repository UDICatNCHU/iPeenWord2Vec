import requests, json, sys, time
from bs4 import BeautifulSoup


class ipeenCrawler(object):
    """
    ipeenCrawler類別可將愛評網上所有有關美食的分享文依照不同種類(共15種)爬蟲並寫檔
    此類別需初始化成員typeNumber為餐廳種類代號
    """
    def __init__(self, typeNumber):
        self.baseUrl = 'http://www.ipeen.com.tw'
        # typeIndexDict存放每種餐廳類別的相關資訊，共15個種類
        self.typeIndexDict = {27:[1500, 'ChineseCuisine.txt'], 2:[500, 'JapaneseCuisine.txt'], 4:[150, 'AsianCuisine.txt'], 25:[500, 'WesternCuisine.txt'], 19:[200, 'Barbecue.txt'], 21:[400, 'Hotpot.txt'], 17:[1000, 'Cafe.txt'], 6:[50, 'Vegetarian.txt'], 9:[70, 'FastFood.txt'], 23:[150, 'ThemeRestaurant.txt'], 126:[150, 'Breakfast.txt'], 127:[15, 'Buffet.txt'], 8:[1000, 'Snack.txt'], 15:[300, 'SweetSoup.txt'], 7:[300, 'Bake.txt']}
        self.typeNumber = typeNumber


    def getTypeUrl(self):
        """
        功能: loops over 每種type
        輸出: 看typeIndexDict有幾個element就呼叫幾次soupProcess_Type，
              每次都丟一個「type網頁」給soupProcess_Type
        """
        typeUrlHead = 'http://www.ipeen.com.tw/search/taiwan/000/1-0-'
        typeUrlTail = '-0/?p='

        print('<===開始處理' + self.typeIndexDict[self.typeNumber][1] + '===>')

        for p in range(1, self.typeIndexDict[self.typeNumber][0]):
            print('==========正在處理第' + str(p) + '頁的所有餐廳==========')
            time.sleep(4)
            res = requests.get(typeUrlHead + str(self.typeNumber) + typeUrlTail + str(p))
            self.soupProcess_Type(res.text)


    def soupProcess_Type(self, resStr):
        """
        輸入: type的一頁網頁原始碼(一頁會有15家餐廳)
        輸出: 得到一個15家餐廳的list，並根據List內容呼叫15次getSharePage
        """
        restaurantList = list()
        soup = BeautifulSoup(resStr, 'html.parser')
        tagList = soup.select('.name > a')
        del tagList[0] # 刪除第一個隨機顯示的餐廳
        for item in tagList:
            restaurantList.append(self.baseUrl + item['href'])

        count = 0
        for restaurant in restaurantList: # restaurant是餐廳的網址
            count += 1
            print('===已送出該頁第' + str(count) + '家餐廳的連結給getSharePage函式===')
            self.getSharePage(restaurant)


    def getSharePage(self, restaurantUrl):
        """
        輸入: 一家餐廳的網址
        輸出: 一個餐廳的所有分享文網址串成一個List
        """
        # 找到該餐廳的「分享文」按鈕的url
        time.sleep(4)
        res = requests.get(restaurantUrl)
        soup = BeautifulSoup(res.text, 'html.parser')
        returnList = soup.select('#shop-header > nav > ul > li:nth-of-type(3) > a')

        # query該餐廳的「分享文」按鈕的url
        if len(returnList) == 0 : pass
        time.sleep(4)
        resShare = requests.get(self.baseUrl + returnList[0]['href'])
        shareSoup = BeautifulSoup(resShare.text, 'html.parser')

        shareLinkList = list()
        nextPageForCheck = list()

        # 如果有分享文，把它們的連結串進shareLinkList
        articleList = shareSoup.select('#comments > div.row > div > section > article > div > div.text > h2 > a')
        if len(articleList) != 0:
            for tag in articleList: # 如果沒有分享文，會沒有article標籤，shareLinkList會是空串列
                shareLinkList.append(self.baseUrl + tag['href'])

        
        # 找到「第一頁」的「下一頁」按鈕
        nextPageButtonList = shareSoup.select('#comments > div.row > div > section > div.page-block > a[data-label="下一頁"]')

        # 如果有「下一頁」按鈕
        if len(nextPageButtonList) != 0:
            pageCount = 1
            while True:
                # 檢查用，存「下一頁」按鈕的連結
                nextPageForCheck.append(self.baseUrl + nextPageButtonList[0]['href'])
                # query下一頁按鈕
                time.sleep(4)
                nextPageResponse = requests.get(self.baseUrl + nextPageButtonList[0]['href'])
                nextPageSoup = BeautifulSoup(nextPageResponse.text, 'html.parser')
                # 把下一頁的分享文的url放進list
                for url in nextPageSoup.select('#comments > div.row > div > section > article > div > div.text > h2 > a'):
                    shareLinkList.append(self.baseUrl + url['href'])
                #再找到它的下一頁按鈕
                nextPageButtonList = nextPageSoup.select('#comments > div.row > div > section > div.page-block > a[data-label="下一頁"]')

                print('已經爬完第' + str(pageCount) + '頁的分享文的網址')
                pageCount += 1

                if len(nextPageButtonList) == 0: break
        
        print('v v v v v 這家餐廳的所有分享文的連結如下 v v v v v')
        for item in shareLinkList: print(item)
        self.soupProcess_Share(shareLinkList) # 有可能傳空list出去


    def soupProcess_Share(self, sharePageList):
        """
        功能: 得到每篇分享文內容並寫檔
        輸入: 一家餐廳的所有分享文的網址List
        輸出: 一篇分享文為一行寫檔
        """
        if len(sharePageList) == 0:
            pass

        with open('./result/' + self.typeIndexDict[self.typeNumber][1], 'a') as file:
            count = 1
            for item in sharePageList:
                time.sleep(4)
                res = requests.get(item)
                soup = BeautifulSoup(res.text, 'html.parser')

                writeStr = ''
                
                for tag in soup.find_all('div', class_ = 'description'):
                    writeStr += tag.text

                writeStr = writeStr.replace('\n', '')
                writeStr = writeStr.replace('\t', '')
                writeStr = writeStr.replace(' ', '')
                file.write(writeStr + '\n')
                print('該餐廳第' + str(count) + '篇分享文已寫檔完畢')
                count += 1


    def main(self):
        self.getTypeUrl()
        print('>>>>>>> 全部文章都已經爬完 <<<<<<<')



if __name__ == '__main__':
    ipeenObj = ipeenCrawler(int(sys.argv[1]))
    ipeenObj.main()
