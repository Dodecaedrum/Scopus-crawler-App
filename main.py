import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import smtplib
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty
from kivy.core.window import Window
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import numpy as np
from os import system, name
from kivy.lang import Builder
import xlrd
import openpyxl

path = os.getcwd()
options = Options()
options.add_argument("--window-size=1920,1080")

port = 465
smtp_server = "smtp.gmail.com"
sender_email = # add sender email here
receivers = # add list of recievers here
password = # add string apssword here

body = """\
This is automated message, containing Scopus data."""

msg = MIMEMultipart()
msg['Subject'] = "Scopus data"
msg['From'] = sender_email
msg['To'] = ', '.join(receivers)
msg.attach(MIMEText(body, 'plain'))

path_1 = ''


# Waiting function
def cit_overview_loading_waiting(driver):
    WebDriverWait(driver, 90).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="loadingModal"]/div/div/div')))
    WebDriverWait(driver, 90).until(
        EC.invisibility_of_element_located((By.XPATH, '//*[@id="loadingModal"]/div/div/div')))
    WebDriverWait(driver, 90).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#endYear-button .ui-selectmenu-text'), '2021'))
    WebDriverWait(driver, 90).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '#cto_details_table .secondaryLink')))
    time.sleep(3)


# Terminal clearing function
def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


# Clusters creating function
def chunks(years, lst):
    for j in range(0, len(lst), years):
        yield lst[j:j + years]


class FirstScreen(Screen):
    uni_name = ObjectProperty(None)
    years = ObjectProperty(None)

    def callback(self):
        # Passing global variables

        global path_1, path, options, port, smtp_server, sender_email, receivers, password, msg

        current_date = str(datetime.date(datetime.now())).replace('-', '')

        # Creating webdriver
        driver = webdriver.Chrome(options=options,
                                  executable_path=path.replace('/', '\\') + '\chromedriver.exe')

        # !!! ALL DATA ALWAYS SHOULD BE EXPORTED THE SAME DAY !!!
        data_api = pd.read_csv(path_1, sep=';')

        # Getting to the link for authorization
        driver.get('https://www.scopus.com/search/form.uri?display=basic#affiliation')

        # Logging in
        try:
            driver.find_element_by_xpath('//*[@id="signin_link_move"]/span').click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="bdd-email"]')))
            driver.find_element_by_xpath('//*[@id="bdd-email"]').send_keys('dc@satbayev.university')
            driver.find_element_by_xpath('//*[@id="bdd-elsPrimaryBtn"]').click()
            time.sleep(2)
            driver.find_element_by_xpath('//*[@id="bdd-password"]').send_keys('Satbayev2020*')
            driver.find_element_by_xpath('//*[@id="bdd-elsPrimaryBtn"]').click()
        except:
            pass

        # Going to institution page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#institutions-tab .button__text')))
        driver.find_element_by_css_selector('#institutions-tab .button__text').click()
        driver.find_element_by_css_selector('.has-search-icon').click()
        driver.find_element_by_css_selector('.has-search-icon').send_keys(self.uni_name.text)
        driver.find_element_by_css_selector('.has-search-icon').send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.docTitle a')))
        driver.find_element_by_css_selector('.docTitle a').click()

        # Going to all inst docs
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#rolledupCard .anchorText'))).click()
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ddmDocTitle')))

        # Trying to click more years and selecting them
        try:
            driver.find_element_by_css_selector('#viewMoreLink_PUBYEAR .btnText').click()
        except:
            pass
        year_labels = driver.find_elements_by_css_selector('#clusterAttribute_PUBYEAR .checkbox-label .btnText')
        for i in range(int(self.years.text)):
            year_labels[i].click()
        driver.find_element_by_css_selector('.limitToButton').click()

        # Changing results amount to 100
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ddmDocTitle')))
        driver.find_element_by_css_selector('#resultsPerPage-button .flexColumn').click()
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="ui-id-3"]').click()

        # Getting an comfortable url
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ddmDocTitle')))
        driver.find_element_by_css_selector('li:nth-child(10) .ico-navigate-right').click()
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ddmDocTitle')))
        comfortable_url = driver.current_url

        # Getting page amount
        page_amount = int(driver.find_element_by_css_selector('li:nth-child(10) a').text)
        parts = comfortable_url.split('offset=')
        right_parts = parts[1].split('&')
        del right_parts[0]
        print(right_parts[0])
        right_parts = '&'.join(right_parts)

        full_data = pd.DataFrame()

        # Creating urls
        new_url = parts[0] + 'offset=' + str(1) + '&' + right_parts
        driver.get(new_url)

        # Starting the main cycle
        for i in range(page_amount):

            # Selecting page's docs
            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ddmDocTitle')))
            driver.find_element_by_css_selector('.icon-after').click()
            driver.find_element_by_xpath('//*[@id="selectAllMenuItem"]/span[2]/span/ul/li[2]/label').click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ctoDocResultLink .btnText')))
            driver.find_element_by_css_selector('#ctoDocResultLink .btnText').click()

            # Loading waiting
            cit_overview_loading_waiting(driver=driver)
            time.sleep(5)

            # Year selecting
            WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#startYear-button .flexColumn')))
            driver.find_element_by_css_selector('#startYear-button .flexColumn').click()
            driver.find_element_by_xpath('//*[@id="ui-id-{}"]'.format(4+int(self.years.text))).click()

            # Doc per page amount selecting
            driver.find_element_by_css_selector('#docs_per_page-button .flexColumn').click()
            driver.find_element_by_xpath('//*[@id="ui-id-60"]').click()
            if i != page_amount-1:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#pageCheckBoxCTORow_100+ .checkbox-label')))

            # Pushing the Update button
            driver.find_element_by_css_selector('#updateOverviewButtonOn').click()

            # Loading waiting
            cit_overview_loading_waiting(driver=driver)

            # Scrapping data
            years_list = driver.find_elements_by_css_selector('.yearTotal')
            years_self = ['self_cit_'+j.text for j in years_list]
            years_noself = ['noself_cit_'+j.text for j in years_list]

            # Scrapping eids
            eids = driver.find_elements_by_xpath('//*[@id="cto_details_table"]/tr/td[2]/a')
            eids = [j.get_attribute('href').split('eid=')[-1] for j in eids]

            # Self cits scrapping
            self_cits = driver.find_elements_by_css_selector('.yearTotalCell')
            self_cits = [int(j.text) if j.text != ' ' and j.text != '' else np.nan for j in self_cits]
            self_cits = list(chunks(years=len(years_list), lst=self_cits))
            self_cits = pd.DataFrame(data=self_cits, columns=years_self)

            # Clicking self cit exclusion
            driver.find_element_by_css_selector('#excludeArticleAuthorsBox+ .checkbox-label').click()
            driver.find_element_by_css_selector('#updateOverviewButtonOn').click()

            # Loading waiting
            cit_overview_loading_waiting(driver=driver)

            # Without self cits data scrapping
            noself_cits = driver.find_elements_by_css_selector('.yearTotalCell')
            noself_cits = [int(j.text) if j.text != ' ' and j.text != '' else np.nan for j in noself_cits]
            noself_cits = list(chunks(years=len(years_list), lst=noself_cits))
            noself_cits = pd.DataFrame(data=noself_cits, columns=years_noself)

            # Appending data
            page_data = pd.concat([self_cits, noself_cits], axis=1)
            page_data['eid'] = eids
            full_data = full_data.append(page_data).reset_index(drop=True)

            # Getting back from cit overview and deselecting docs
            driver.back()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ddmDocTitle')))
            driver.find_element_by_css_selector('.icon-after').click()
            driver.find_element_by_xpath('//*[@id="selectAllMenuItem"]/span[2]/span/ul/li[2]/label').click()

            # Next page getting
            if i != page_amount - 1:
                driver.find_element_by_xpath(
                    '//*[@id="resultsFooter"]/div[2]/ul//a/span[@class="ico-navigate-right"]').click()

        driver.quit()

        # Dealing with API
        print('Joining data...')
        full_data = full_data.fillna(0)
        full_data = data_api.join(full_data.set_index('eid'), on='eid')
        print('Data joined')

        # Saving data
        print('Saving data...')
        full_data.to_excel('scopus_crawled_data_{}.xlsx'.format(current_date), index=False)
        print('Data saved')

        # Sending an email
        print('Sending email...')
        filename = 'scopus_crawled_data_{}.xlsx'.format(current_date)
        attachment = open(path.replace('/', '\\') + '\\' + filename, "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)
        s = smtplib.SMTP_SSL(smtp_server, port)
        s.ehlo()
        s.login(sender_email, password)
        text = msg.as_string()
        s.sendmail(sender_email, receivers, text)
        s.quit()
        print("Email sent, job's done")


class SecondScreen(Screen):
    def selected(self, filename):
        global path_1
        try:
            path_1 = filename[0].replace('\\', '/')
            print(path_1)
        except:
            pass


class WindowManager(ScreenManager):
    pass


class ScopusApp(App):
    def build(self):
        Builder.load_file('Scopus.kv')
        sm = ScreenManager()
        sm.add_widget(FirstScreen(name='first'))
        sm.add_widget(SecondScreen(name='second'))
        return sm


if __name__ == "__main__":
    ScopusApp().run()
