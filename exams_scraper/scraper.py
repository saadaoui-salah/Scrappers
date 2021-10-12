# coding: utf8
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from selenium import webdriver


login_url = "https://www.examsuccess.com.au/users/sign_in"

email = 'ash.bris@gmail.com'
password = '44oaiy1p1nRs'

class Scraper():
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = False
        self.driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)

    def login(self):
        self.driver.get(login_url)
        self.driver.find_element_by_id('user_email').send_keys(email)
        self.driver.find_element_by_id('user_password').send_keys(password)
        self.driver.find_element_by_name('commit').click()
        self.driver.get('https://www.examsuccess.com.au/practice-writing-app/sample_essays/')

    def get_essays_links(self):
        links_items = self.driver.find_elements_by_xpath('//a[@class="list-group-item writing-prompt-link "]')
        self.links = []
        for link in links_items:
            data = {}
            data['name'] = link.text
            data['link'] = link.get_attribute('href')
            self.links.append(data)

    def get_questions_links(self):
        for link in self.links:
            self.driver.get(link['link'])
            questions_items = self.driver.find_elements_by_xpath('//a[@class="list-group-item essay-list-item"]')
            self.questions_links = []
            for question in questions_items:
                self.questions_links.append(question.get_attribute('href'))
        print(len(self.questions_links))
        
    def feed(self):
        self.get_essays_links()
        self.get_questions_links()

    def __join__(self, tags):
        text = '' 
        for tag in tags:
            text += tag.text + '\n'
        return text

    def get_data(self, url):
        self.driver.get(url)
        try:
            self.question_title = self.driver.find_elements_by_tag_name('h3')[0].text
        except :
            self.question_title = ''
        try:
            p_tags = self.driver.find_elements_by_xpath('//blockquote//p')
            self.question = self.__join__(p_tags)
        except :
            self.question = ''
        try:
            self.sample_title = self.driver.find_elements_by_xpath('//h1')[0].text
        except:
            self.sample_title = ''
        try:
            sample_items = self.driver.find_elements_by_xpath('//div[@class="col-md-8"]/p')
            self.sample = self.__join__(sample_items)
        except :
            self.sample = ''

    def create_pdf(self):
        for link in self.questions_links:
            self.get_data(link)


            styles = getSampleStyleSheet()
            styleN = styles['Normal']
            styleH = styles['Heading1']
            story = []

            pdf_name = f'{self.question_title}.pdf'
            doc = SimpleDocTemplate(
                pdf_name,
                pagesize=letter,
                bottomMargin=.4 * inch,
                topMargin=.6 * inch,
                rightMargin=.8 * inch,
                leftMargin=.8 * inch
            )
            P1 = Paragraph(self.question_title, styleH)
            P2 = Paragraph(self.question, styleN)
            P3 = Paragraph(self.sample_title, styleH)
            P4 = Paragraph(self.sample, styleN)
            story.append(P1)
            story.append(P2)
            story.append(P3)
            story.append(P4)
            doc.build(
                story,
            )
    

scraper = Scraper()
scraper.login()
scraper.feed()
scraper.create_pdf()