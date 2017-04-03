# iPeenWord2Vec
iPeenWord2Vec is a project intends to see the efficiency of word2vec techniques applied to the interest-detect-article-recommendation circumstances with the source articles from iPeen ([愛評網](http://www.ipeen.com.tw/)).
This project includes the following sections:
1) Crawler codes which are able to get all the articles, specifically about food and restaurants, on iPeen website and write into text files according to different types of cuisine for further analysis.

2) A web API for querying articles. For each query, the codes calculate the sum vector (for this project we use a 250 dimension word2vec trained model) of the query terms, and find the top-k cosine similarity articles that might match the user's interests.

3) A class to store approximately 150,000 articles into MongoDB, simultaneously find the top 20 keywords for each article with TF-IDF, for those 20 keywords we calculate the sum vector which is supposed to represent the position of the article in word2vec vector space.

## Prerequisities
- numpy
- gensim
- jieba
- pymongo
- requests
- beautifulsoup

## Run
### ipeenCrawler class
ipeenCrawler class needs to be initialized with __a number__ that stands for one certain type of restaurant as below:

| #   |  Type                                         |
| --- | --------------------------------------------- |
| 27  |  中式料理                                      |
| 2   |  日式料理                                      |
| 4   |  亞洲料理（韓式料理、泰式料理、越南料理等等）        |
| 25  |  異國料理（法式料理、美式料理、義式料理、德式料理等等）|
| 19  |  燒烤類                                        |
| 21  |  火鍋類                                        |
| 17  |  咖啡、簡餐、茶                                 |
| 6   |  素食                                         |
| 9   |  速食料理                                      |
| 23  |  主題特色餐廳（桌遊主題餐廳、親子餐廳、酒吧等等）     |
| 126 |  早餐                                          |
| 127 |  buffet自助餐                                  |
| 8   |  小吃                                          |
| 15  |  冰品、飲料、甜湯                                |
| 7   |   烘陪、甜食、零食                               |

#### getTypeUrl function
__args__: none
__return__: none
getTypeUrl will create a text file, with a article per line.
#### Example
```python
obj = ipeenCrawler(27) # 中式料理
obj.getTypeUrl() # the result text file will be stored in './result/'

```

### exportToMongo class
exportToMongo class has 3 constructors need to be initialized: __text file file path__, __word2vec model file path__ and __mongoDB uri__.

#### insertDB functiomn
__args__: none
__return__: none
insertDB function find the top20 keywords for each article with TF-IDF, and stores article content, top20 keywords, sum vector of top20 etc into mongoDB as a document.

#### Example
```python
obj = exportToMongo(text file path, model path, uri)
obj.insertDB() # it takes around 40 minutes
```

### GetTopResult class
GetTopResult class cooperates with the django views. This class needs to be initialized with __word2vec model path__ and __mongoDB uri__.

#### getArticle funstion
__args__:
1. a list which contains the query terms from user
2. an integer which assigns the return number of articles.

__return__:
A dictionary which stores the information of the article contents along with its top20 keywords.

#### Example
```python
obj = GetTopResult(model path, uri)
obj.getArticle(queryList, 50)
```

## Built With
python3.4

## Contributors
[Shane Yu](https://github.com/theshaneyu)