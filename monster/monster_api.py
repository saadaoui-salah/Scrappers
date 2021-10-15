import requests
from bs4 import BeautifulSoup as BS
import json
from html.parser import HTMLParser

class MonsterScraper():
    def __init__(self, keyword, location, offset, page_size):
        self.keyword = keyword.replace(' ','+')
        self.location = location.replace(' ','+')
        self.payload = {
            "fingerprintId": "ec4d1343a1b4d333a2a09ce7df2bcaf8",
            "includeJobs": [],
            "jobAdsRequest": {"position": [1, 2, 3, 4, 5, 6, 7, 8, 9], "placement": {"component": "JSR_SPLIT_VIEW", "appName": "monster"}},
            "placement": {"component": "JSR_SPLIT_VIEW", "appName": "monster"},
            "appName": "monster",
            "component": "JSR_SPLIT_VIEW",
            "position": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "jobQuery": {
            "locations": [{"country": "us", "address": location, "radius": {"unit": "mi", "value": 20}}],
            0: {"country": "us", "address": location, "radius": {"unit": "mi", "value": 20}},
            "address": location,
            "country": "us",
            "radius": {"unit": "mi", "value": 20},"unit": "mi","value": 20,"query": keyword},
            "offset": offset,
            "pageSize": page_size,
        }
        
    def get_api_key(self):
        r = requests.get(f"https://www.monster.com/jobs/search?q={self.keyword}&where={self.location}&page=2")
        html = BS(r.text, 'html.parser')
        script = html.find_all('script', {"id":"__NEXT_DATA__"})[0]
        json_str = script.contents[0]
        return json.loads(json_str)['runtimeConfig']['api']['key']


    def call_api(self):
        api_key = self.get_api_key()
        r = requests.post(f'https://appsapi.monster.io/jobs-svx-service/v2/monster/search-jobs/samsearch/en-US?apikey={api_key}', json=self.payload )
        self.api_data = r.json()

class DescriptionParser(HTMLParser):
    def __init__(self):
        super(DescriptionParser, self).__init__(convert_charrefs=True)
        self.data = {}
        self.data['detail'] = ''
        self.list = []
        self.list_started = False
        self.is_div = False
        self.is_strong = False
    def handle_starttag(self, tag, attrs):
        if tag == 'ul':
            self.list_started = True
        if tag == 'div':
            self.is_div = True
        if tag == 'strong':
            self.is_strong = True

    def handle_endtag(self, tag):
        if tag == 'ul':
            items = list(self.data.items())
            if items[-1][-1] == True:
                self.data[items[-1][0]] = self.list
                self.list = []
                self.list_started = False
        if tag == 'div':
            self.is_div = False
        if tag == 'strong':
            self.is_strong = False


    def handle_data(self, data):
        items = list(self.data.items())
        if self.is_div:
            self.data['detail'] += data
        if items[-1][-1] == True:
            self.data[items[-1][0]] = data
        if ':' in data:
            splitted_data = data.split(':')
            if splitted_data[1] != '':
                exist = self.data.get(splitted_data[0]) 
                if exist:
                    self.data[splitted_data[0]] += splitted_data[1]
                else:
                    self.data[splitted_data[0]] = splitted_data[1]
            else:
                self.data[splitted_data[0]] = True
        if self.list_started:
            self.list.append(data)
        if self.is_strong:
            self.data[data] = True



def get_monster_data(keyword, location, offset, page_size):
    scraper = MonsterScraper(keyword, location, offset, page_size)
    scraper.call_api()
    parser = DescriptionParser()
    jobs_data = scraper.api_data
    for i, job_data in enumerate(jobs_data['jobResults']):
        parser.feed(job_data['jobPosting']['description'])
        jobs_data['jobResults'][i]['jobPosting']['description'] = parser.data
        try:
            parser.feed(job_data['jobPosting']['hiringOrganization']['description'])
            jobs_data['jobResults'][i]['jobPosting']['hiringOrganization']['description'] = parser.data
        except KeyError:
            pass
        try:
            parser.feed(job_data['normalizedJobPosting']['hiringOrganization']['description'])
            jobs_data['jobResults'][i]['normalizedJobPosting']['hiringOrganization']['description'] = parser.data
        except KeyError:
            pass
        parser.feed(job_data['normalizedJobPosting']['description'])
        jobs_data['jobResults'][i]['normalizedJobPosting']['description'] = parser.data
    return jobs_data


#### TEST
print(get_monster_data('it', 'texas', 0, 10)['jobResults'][-1]['jobPosting']['description'])
