
---

## About (Summary)

This is a webscraper for freelance.de running on a serverless Azure architecture written in python using Selenium and sendgrid. It is intended to be run in a Docker container on Azure Container Instances and orchestrated via an Azure Function. The scraper simply opens freelance.de, logs in, executes a search for the predefined search terms, parses & appends the new results (which can span multiple pages) and lastly sends an email of the new relevant job if appropriate.


The parsing basically consists of a relevancy evaluation at one's will so that a subset of highly appropriate new results (job postings) are subsequently sent via email to the recipient. Executiion (8 times a day from Monday till Friday) is less than 5€/month, only possible due to the serverless nature. Of that, more than 90% are storage costs (due to minimum quota). In detail, the cloud architecture looks like following.

---

## Architecture
<p align="center">
<img src="Scraper.svg">
</p>

1. A cronjob triggerred Azure Function orchestrates the whole ordeal by starting the container instance via Powershell *(IaC)*
2. The container is created with a mounted Fileshare to enable persistence of data 
3. The Container Instance scrapes freelance.de in aforementioned manner, appending the new jobs to results.csv and updating the watermark.
4. If applicable, an email with a set of newly found relevant jobs gets sent to the recipient using sendgrid API.
5. The Function stops the container instance

---

## How to deploy

### Requirements
- Powershell with the Azure Powershell module is needed to perform the rbac assignment
- An Azure File Share
- An Azure Function which uses Powershell

### Function App Deployment

1. Enter your data into `assign-rbac.ps1` and `run.ps1`
2. Run `assign-rbac.ps1`
3. Replace `requirements.psd1` as well as `run.ps1` of your Azure Function with the files from this function folder
4. Done!

### Script & Storage Configuration
1. Enter your data into `config.json`
2. Upload `scraper.py` and `config.json` to the File Share
3. Done!

That's it! The container instance uses an image based on the dockerfile in this directory and it should automatically access `scraper.py` and `config.py`. The function can be of any kind, not only time triggerred.

---

## ToDo:
- Easier search term change
- Visualization
- Better E-Mail Template