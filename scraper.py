import csv
from datetime import datetime as dt, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import json
import os
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

config=json.load(open("config.json"))

current_csv=config["csv_path"].format(dt.now().strftime('%b'))
current_wm=config["watermark_path"]
sendgrid_api_key=config["sendgrid_api_key"]
fl_acc=config["acc"]
search_term=config["search_term"]

dt_web_format="%d.%m.%Y %H:%M"
dt_csv_format="%Y-%m-%d %H:%M:%S"
cols=["Id", "Title", "Company", "Data_count", "Engineer_count", "Azure_count", "Spark_count", "Url", "Timestamp"]
def cookie_ok(driver):
    try:
        sleep(2)
        driver.find_element(by=By.CSS_SELECTOR, value="#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
    except:
        pass
    return

def check_watermark():
    if not os.path.isfile(current_csv):
        with open(current_csv, 'a', newline="") as f:
            csv.writer(f).writerows([cols])
    try:
        watermark=json.load(open(current_wm))
        watermark["last_job"]=dt.strptime(watermark["last_job"], dt_web_format)
        watermark["last_email"]=dt.strptime(watermark["last_email"], dt_web_format)
    except:
        watermark={}
        watermark["last_job"]=dt.now()-timedelta(hours=100)#52
        watermark["last_email"]=dt.now()-timedelta(hours=100)#52
    return watermark

def logging_in(driver):
    driver.find_element(by=By.CSS_SELECTOR, value="li#top-nav_login > a").click()
    sleep(2)
    user = driver.find_element(by=By.CSS_SELECTOR, value="#username")
    pw = driver.find_element(by=By.CSS_SELECTOR, value="#password")
    sleep(1)
    user.send_keys(fl_acc["name"])
    sleep(1)
    pw.send_keys(fl_acc["pw"])
    sleep(5)
    driver.find_element(by=By.CSS_SELECTOR, value="#login").click()

def search(driver):
    sleep(2)
    search=driver.find_element(by=By.CSS_SELECTOR, value="input#search-text")
    search.send_keys(f'{search_term}\n')
    sleep(3)
    driver.find_element(by=By.CSS_SELECTOR, value="button[title='Sortieren nach Relevanz']").click()
    driver.find_element(by=By.CSS_SELECTOR, value="div#filter8 li[data-original-index='1']").click()
    sleep(1)
    project_list=driver.find_elements(by=By.CSS_SELECTOR, value="div.project-list > div")
    return project_list

def parse_projects(project_list, watermark):
    no_break=True
    projects=[]
    email_projects=[]
    for project in project_list:
        time=dt.strptime(project.find_elements(by=By.CSS_SELECTOR, value="ul.icon-list > li")[-1].text, dt_web_format)
        if time <= watermark["last_job"]:
            no_break=False
            break
        id=project.get_attribute("id")[10:]
        anchor=project.find_element(by=By.CSS_SELECTOR, value=f"a#project_link_{id}")
        url=anchor.get_attribute("href")
        title=anchor.text
        comp=project.find_element(by=By.CSS_SELECTOR, value="span.company-name").text
        kw_counts=re.findall(r'\b\d+\b', \
        project.find_element(by=By.CSS_SELECTOR, value=f"div#word_matches_{id}").text)
        row=[id, title, comp, kw_counts, url, time]
        projects.append(row)
        #Your condition for email worthy jobs based on e.g. keyword occurences
        if (kw_counts):
            email_projects.append(row)
    return projects, email_projects, no_break

def next_page(driver, no_break, watermark, projects, email_projects):
    i=1
    projects_next=[]
    email_projects_next=[]
    while no_break and i < 4:
        driver.find_element(by=By.CSS_SELECTOR, value="a[aria-label='Next']").click()
        sleep(1)
        project_list_next=driver.find_elements(by=By.CSS_SELECTOR, value="div.project-list > div")
        project, email, no_break=parse_projects(project_list_next, watermark)
        projects_next=projects_next+project
        email_projects_next=email_projects_next+email
        i+=1
    return projects+projects_next, email_projects+email_projects_next
def send_mail(email_projects, watermark):
    if email_projects==[]:
        return
    watermark["last_email"]=dt.strftime(email_projects[0][-1], dt_web_format)
    email_body=""
    for row in email_projects:
        email_body=email_body+f'<h1><a href={row[-2]}>{row[1]}</a>\n</h1><h3>{row[2]}</h3>    Azure: {row[-4]}   Spark: {row[-3]} \n'
    message = Mail(
        from_email=config["from_email"],
        to_emails=config["to_email"],
        subject='New Jobs',
        html_content=email_body)
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
    except:
        pass

def serialize(projects, watermark):
    if projects!=[]:
        with open(current_wm, 'w', newline="") as c_wm:
            json.dump({"last_job": dt.strftime(projects[0][-1], dt_web_format),
                "last_email": watermark["last_email"], "last_run": dt.strftime(dt.now(), dt_web_format)}, c_wm)
        with open(current_csv, newline='') as c_csv:
            curr_csv_list=list(csv.reader(c_csv))[1:]
        with open(current_csv, "w", newline='') as c_csv:
            csv.writer(c_csv).writerows([cols]+projects+curr_csv_list)
    else:
        with open(current_wm, 'w', newline="") as c_wm:
            json.dump({"last_job": dt.strftime(watermark["last_job"], dt_web_format),
            "last_email": dt.strftime(watermark["last_email"], dt_web_format), "last_run": dt.strftime(dt.now(), dt_web_format)}, c_wm)
container_chrome_options = webdriver.ChromeOptions()
container_chrome_options.add_argument('--no-sandbox')
container_chrome_options.add_argument('--headless')
container_chrome_options.add_argument('--disable-gpu')
container_chrome_options.add_argument('--disable-dev-shm-usage')
container_chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=container_chrome_options)
driver.get("https://www.freelance.de/")
watermark=check_watermark()
cookie_ok(driver)
logging_in(driver)
project_list=search(driver)
projects, email_projects, no_break=parse_projects(project_list, watermark)
projects, email_projects=next_page(driver, no_break, watermark, projects, email_projects)
send_mail(email_projects, watermark)
serialize(projects, watermark)
