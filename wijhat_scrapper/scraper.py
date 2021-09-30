import requests
from bs4 import BeautifulSoup as BS
import csv

CATEGORIES = {
    4:'الرياضة',
    5:'العراق',
    6:'الوطن العربي و العالم',
    7:'آراء و افكار',
    8:'اقتصاد',
    9:'تقنيات و علوم',
    11:'أدب',
    10:'نوافذ',
    21:'كاريكاتير',
    22:'ملفات',
    23:'بيانات',
}

class ArticleInfocrapper():
    def __init__(self, link):
        response = requests.get(f"https://wijhat.info/{link}")
        self.html = BS(response.text, "html.parser")
        self.info = {}
    
    def get_title(self):
        self.info['title'] = self.html.find_all('h1', {'class': 'title'})[0].text 
        print(f"Title: {self.info['title'][0:15]}...")
        return self.info['title']

    def get_date(self):
        self.info['date'] = self.html.find_all('time')[0].text 
        print(f"Date: {self.info['date']}")
        return self.info['date']

    def get_content(self):
        content = ''
        body = self.html.find_all("div", {"itemprop":"articleBody"})[0]
        spans = body.find_all("span") 
        for span in spans:
            content += f"{span.text}\n"
        self.info['content'] = content
        print(f"Content: {content[0:30]}...")
        return self.info['content']
    
    def get_image(self):
        self.info['image'] = self.html.find_all("img", { "itemprop" : "image" })[0].attrs['src']
        return self.info['image']

    def feed(self):
        self.get_title()
        self.get_date()
        self.get_content()
        self.get_image()


class ArticlesScrapper:
    def __init__(self, cat_id):
        response   = requests.get(f"https://wijhat.info/cat.php?id={cat_id}")
        self.html  = BS(response.text, "html.parser") 
        self.links = []

    def get_articles_links(self):
        content = self.html.find_all("div",{ "id": "main-column" })[0]
        tags = content.find_all("a")
        for tag in tags:
            self.links.append(tag.attrs["href"])

    def feed(self):
        self.get_articles_links()


def get_data():
    articles = {}
    for id, cat in CATEGORIES.items():
        article = ArticlesScrapper(id)
        data = []
        article.feed()
        for link in article.links:
            info = ArticleInfocrapper(link)
            info.feed()
            data.append(info.info)
        articles[cat] = data
    return articles

def create_csv():
    articles = get_data()
    headers = ['title', 'date', 'content', 'image']
    for article, data in articles.items():
        with open(f'{article}.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

create_csv()