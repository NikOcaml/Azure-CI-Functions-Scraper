FROM selenium/standalone-chrome

USER root
RUN apt-get update && apt-get install python3-distutils -y && \
      wget https://bootstrap.pypa.io/get-pip.py && \
      python3 get-pip.py --user && \
      rm get-pip.py && python3 -m pip install selenium sendgrid
WORKDIR /SeleniumApp/
CMD pkill java;python3 scraper.py