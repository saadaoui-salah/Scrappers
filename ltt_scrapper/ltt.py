import requests
from config import FILTERS
from bs4 import BeautifulSoup


class LttrScrapper():
    def __init__(self, keyword=None, filter_id=None, scraper=True):
        if scraper:
            url = "https://www.ltt.aero/training-finder"
            params = {
                "p_p_id": "TrainingFinder_WAR_trainingfinderportlet",
                "p_p_lifecycle": 2,
                "p_p_state": "normal",
                "p_p_mode": "view",
                "p_p_cacheability": "cacheLevelPage",
                "p_p_col_id": "column-1",
                "p_p_col_pos": 2,
                "p_p_col_count": 3,
                "_TrainingFinder_WAR_trainingfinderportlet_action": "doSearch",
                "_TrainingFinder_WAR_trainingfinderportlet_sortCondition": "date",
                "_TrainingFinder_WAR_trainingfinderportlet_sortDirection": "asc",
                "_TrainingFinder_WAR_trainingfinderportlet_limit": 1,
                "_TrainingFinder_WAR_trainingfinderportlet_offset": 0,
                "_": 1632675832234
            }
            if filter_id:
                params["_TrainingFinder_WAR_trainingfinderportlet_facets"] = FILTERS[filter_id]
            if keyword:
                params["_TrainingFinder_WAR_trainingfinderportlet_text"] = keyword
            params["_TrainingFinder_WAR_trainingfinderportlet_limit"] = requests.get(url, params=params).json()["total"]
            print(f"Found {params['_TrainingFinder_WAR_trainingfinderportlet_limit']} results")
            print(f"Getting data from {url}")
            self.response = requests.get(url, params=params).json()
            self.data = []

    def get_available_data(self):
        print("Start scrapping availible data...")
        for course in self.response["courseResults"]['list']:
            course_data = {}
            course_data['courseId'] = course.get("serializable").get('courseId')
            course_data['title'] = course.get("serializable").get('title')
            print(f"\tTitle:\t{course_data['title']}")
            print(f"\tCourse ID:\t{course_data['courseId']}")
            print("\t...more")
            course_data['description'] = course.get("serializable").get('metaDescription') 
            course_data['duration'] = course.get("serializable").get('duration') 
            course_data['maxParticipants'] = str(course.get("serializable").get('maxParticipants')) 
            course_data['detailsURL'] = course.get("serializable").get("detailsURL")
            course_data["projects"] = []
            for project in course.get("serializable").get("projects").get("list"):
                new_project = {}
                new_project['startDate'] = project.get("serializable").get('formatedScheduleBegin') 
                new_project['endDate'] = project.get("serializable").get('formatedScheduleEnd') 
                new_project['city'] = project.get("serializable").get('trainingLocationCity') 
                new_project['country'] = project.get("serializable").get('trainingLocationCountry') 
                new_project['tax'] = project.get("serializable").get('vatInTotal') 
                new_project['price'] = project.get("serializable").get('unitPrice') 
                new_project['currency'] = project.get("serializable").get('currency') 
                new_project['courseLanguage'] = project.get("serializable").get('courseLanguage') 
                new_project['statusColor'] = project.get("serializable").get('statusColor') 
                course_data["projects"].append(new_project)
            self.data.append(course_data)

    def get_revision_id(self):
        tags = self.table.find_all("font",{"size":"-3", "face":"Arial", "color":"#909090"})
        for tag in tags:
            if "( Revision Id:" in tag.text:
                return tag.text.replace("( Revision Id: ","").replace(")","")

    def get_detail_description(self):
        for course in self.data :
            print(f"Getting more details from: {course['detailsURL']}")
            print(f"Details related to : {course['title']}")
            response = requests.get(course["detailsURL"])
            html  = BeautifulSoup(response.text, 'html.parser')
            try:
                self.table = html.find_all('table')[1]
            except IndexError:
                try:
                    self.table = html.find_all('table')[0]
                except IndexError:
                    return
            details = {}
            for tr in self.table.find_all('tr'):
                if len(tr.find_all('td')) == 2 :
                    all_td =  tr.find_all('td')
                    key = all_td[0].text.replace(":","").replace(" ","")
                    value = all_td[1].text
                    if key == "\xa0":
                        continue
                    details[key] = value 
            details['revision'] = self.get_revision_id()
            details['LTT-ID'] = html.find_all("p",{"class":"tf-ltt-id"})[0].span.text
            print(f"\tLTT-ID:\t{details['LTT-ID']}")
            print(f"\tRevision ID:\t{details['revision']}")
            course["details"] = details

    def feed(self):
        self.get_available_data()
        self.get_detail_description()
        return self.data

    def clean_title(self, title):
        return title.replace(" ","_").replace("[","_").replace("]","_").replace("&","_").replace("(","_").replace(")","_")


    def get_captcha_url(self, courseId, title):
        return f"https://www.ltt.aero/training-finder?p_p_id=TrainingFinder_WAR_trainingfinderportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=3&_TrainingFinder_WAR_trainingfinderportlet_action=getCaptcha&_TrainingFinder_WAR_trainingfinderportlet_action=doSearch&_TrainingFinder_WAR_trainingfinderportlet_title={self.clean_title(title)}&_TrainingFinder_WAR_trainingfinderportlet_courseId={courseId}&_TrainingFinder_WAR_trainingfinderportlet_revision=0&t=1632685508356" 
        
    def send_request(self, zip_, lastName, country, occupation, city, courseID, privacyPolicy, sendNews, firstName, places, phone, taxId, street, company, comment, captcha, salutation, email, title):
        if salutation != "Mr." and salutation != "Ms." :
            """
            salutation is a select ipnut
            """
            raise ValueError("[INCORRECT SALUTATION]: salutation should be 'Mr.' or 'Ms.'")
        if privacyPolicy:
            privacyPolicy = 'true'
        else:
            privacyPolicy = "false" 
        
        if sendNews:
            sendNews = 'true'
        else:
            sendNews = "false" 
        title = self.clean_title(title)
        request_url = f"https://www.ltt.aero/training-finder?p_p_id=TrainingFinder_WAR_trainingfinderportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=3&_TrainingFinder_WAR_trainingfinderportlet_zip={zip_}_TrainingFinder_WAR_trainingfinderportlet_lastName={lastName}&_TrainingFinder_WAR_trainingfinderportlet_country={country}&_TrainingFinder_WAR_trainingfinderportlet_occupation={occupation}&_TrainingFinder_WAR_trainingfinderportlet_city={city}&_TrainingFinder_WAR_trainingfinderportlet_privacyPolicy={privacyPolicy}&_TrainingFinder_WAR_trainingfinderportlet_sendNews={sendNews}&_TrainingFinder_WAR_trainingfinderportlet_type=INHOUSE&_TrainingFinder_WAR_trainingfinderportlet_firstName={firstName}&_TrainingFinder_WAR_trainingfinderportlet_customerType=FIRM&_TrainingFinder_WAR_trainingfinderportlet_places={places}&_TrainingFinder_WAR_trainingfinderportlet_phone={phone}&_TrainingFinder_WAR_trainingfinderportlet_taxId={taxId}&_TrainingFinder_WAR_trainingfinderportlet_street={street}&_TrainingFinder_WAR_trainingfinderportlet_action=doBooking&_TrainingFinder_WAR_trainingfinderportlet_action=doSearch&_TrainingFinder_WAR_trainingfinderportlet_company={company}&_TrainingFinder_WAR_trainingfinderportlet_comment={comment}&_TrainingFinder_WAR_trainingfinderportlet_captchaText={captcha}&_TrainingFinder_WAR_trainingfinderportlet_salutation={salutation}&_TrainingFinder_WAR_trainingfinderportlet_courseId={courseID}&_TrainingFinder_WAR_trainingfinderportlet_courseId={courseID}&_TrainingFinder_WAR_trainingfinderportlet_projectId=&_TrainingFinder_WAR_trainingfinderportlet_email={email}&_TrainingFinder_WAR_trainingfinderportlet_title={title}&_TrainingFinder_WAR_trainingfinderportlet_revision=0"
        r = requests.post(request_url)
        return r
    

def get_data(keyword=None, filter_id=None):
    scrapper = LttrScrapper(keyword, filter_id)
    print("All data scrapped:")
    print(f"\t{scrapper.feed()}")
    return scrapper.feed()

def send_request(zip_, lastName, country, occupation, city, courseID, privacyPolicy, sendNews, firstName, places, phone, taxId, street, company, comment, captcha, salutation, email, title):
    scrapper = LttrScrapper(scraper=False)
    print("Sending data to the server")
    print("Waiting for response ...")
    response = scrapper.send_request(zip_, lastName, country, occupation, city, courseID, privacyPolicy, sendNews, firstName, places, phone, taxId, street, company, comment, captcha, salutation, email, title)
    resppnse_data = response.json()
    if ['success'] == True:
        print("Data sended successfully")
        print(f"\tResponse: {resppnse_data}")
        print(f"\tStatus Code: {response.status_code}")
        return True
    print("Error accured in the server")
    print(f"\tStatus Code: {response.status_code}")
    print(f"\tResponse: {resppnse_data}")
    return False


def get_captcha_url(courseId, title):
    scrapper = LttrScrapper(scraper=False)
    scrapper.get_captcha_url(courseId, title)