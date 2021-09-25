import requests
from config import FILTERS
from bs4 import BeautifulSoup


class LttrScrapper():
    def __init__(self, keyword, filter_id=None, limit=20, offset=0):
        url = f"https://www.ltt.aero/training-finder?p_p_id=TrainingFinder_WAR_trainingfinderportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=3&_TrainingFinder_WAR_trainingfinderportlet_action=doSearch&_TrainingFinder_WAR_trainingfinderportlet_text={keyword}&_TrainingFinder_WAR_trainingfinderportlet_sortCondition=none&_TrainingFinder_WAR_trainingfinderportlet_sortDirection=asc&_TrainingFinder_WAR_trainingfinderportlet_limit={limit}&_TrainingFinder_WAR_trainingfinderportlet_offset={offset}&_=1632501838967"
        if filter_id:
            url = f"https://www.ltt.aero/training-finder?p_p_id=TrainingFinder_WAR_trainingfinderportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=3&_TrainingFinder_WAR_trainingfinderportlet_action=doSearch&_TrainingFinder_WAR_trainingfinderportlet_text={keyword}&_TrainingFinder_WAR_trainingfinderportlet_sortCondition=none&_TrainingFinder_WAR_trainingfinderportlet_sortDirection=asc&_TrainingFinder_WAR_trainingfinderportlet_limit={limit}&_TrainingFinder_WAR_trainingfinderportlet_offset={offset}&_TrainingFinder_WAR_trainingfinderportlet_facets={FILTERS[filter_id]}&_=1632501838967"
        self.response = requests.get(url).json()
        self.data = []

    def get_available_data(self):
        for course in self.response["courseResults"]['list']:
            course_data = {}
            course_data['courseId'] = course.get("serializable").get('courseId') 
            course_data['title'] = course.get("serializable").get('title') 
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
            break

    def get_detail_description(self):
        for course in self.data :
            response = requests.get(course["detailsURL"])
            html  = BeautifulSoup(response.text, 'html.parser')
            table = html.find_all('table')[1]
            details = {}
            for tr in table.find_all('tr'):
                if len(tr.find_all('td')) == 2 :
                    all_td =  tr.find_all('td')
                    key = all_td[0].text.replace(":","").replace(" ","")
                    value = all_td[1].text
                    if key == "\xa0":
                        continue
                    details[key] = value 
            try:
                details['revision'] = table.find("font", string="Revision Id").text.replace("( Revision Id: ","").replace(")","")
            except Exception:
                pass
            details['LTT-ID'] =  html.find_all("font", string="LTT-ID")[0].span.text
            print(details['revision'])
            print(details['LTT-ID'])


    def send_request(zip_, lastName, country, occupation, city, privacyPolicy, sendNews, firstName, places, phone, taxId, street, company, comment, captcha, salutation, courseId, projectId, email, title):
        if salutation != "Mr." or salutation != "Ms." :
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
        request_url = f"https://www.ltt.aero/training-finder?p_p_id=TrainingFinder_WAR_trainingfinderportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=3&_TrainingFinder_WAR_trainingfinderportlet_zip={zip_}&_TrainingFinder_WAR_trainingfinderportlet_lastName={lastName}&_TrainingFinder_WAR_trainingfinderportlet_country={country}&_TrainingFinder_WAR_trainingfinderportlet_occupation={occupation}&_TrainingFinder_WAR_trainingfinderportlet_city={city}&_TrainingFinder_WAR_trainingfinderportlet_privacyPolicy={privacyPolicy}&_TrainingFinder_WAR_trainingfinderportlet_sendNews={sendNews}&_TrainingFinder_WAR_trainingfinderportlet_type=PARTICIPANT&_TrainingFinder_WAR_trainingfinderportlet_firstName={firstName}&_TrainingFinder_WAR_trainingfinderportlet_customerType=FIRM&_TrainingFinder_WAR_trainingfinderportlet_places={places}&_TrainingFinder_WAR_trainingfinderportlet_phone={phone}&_TrainingFinder_WAR_trainingfinderportlet_taxId={taxId}&_TrainingFinder_WAR_trainingfinderportlet_street={street}&_TrainingFinder_WAR_trainingfinderportlet_action=doBooking&_TrainingFinder_WAR_trainingfinderportlet_action=doSearch&_TrainingFinder_WAR_trainingfinderportlet_company={company}&_TrainingFinder_WAR_trainingfinderportlet_comment={comment}&_TrainingFinder_WAR_trainingfinderportlet_captchaText={captcha}&_TrainingFinder_WAR_trainingfinderportlet_salutation={salutation}&_TrainingFinder_WAR_trainingfinderportlet_courseId={courseId}&_TrainingFinder_WAR_trainingfinderportlet_projectId={projectId}&_TrainingFinder_WAR_trainingfinderportlet_email={email}&_TrainingFinder_WAR_trainingfinderportlet_title={title}&_TrainingFinder_WAR_trainingfinderportlet_revision=1"
        requests.post(request_url)


scrapper = LttrScrapper("c")
scrapper.get_available_data()
scrapper.get_detail_description()