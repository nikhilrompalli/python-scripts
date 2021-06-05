from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import urllib
import requests
import urllib2
# raw_html = open('/home/nikhilrompalli/sam/dependency-check-report.html').read()
# raw_html = open('dependency-check-report.html').read()

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
    
page_link = "http://127.0.0.1:9000/project/extension/dependencycheck/report?id=user-v2.0&qualifier=TRK"
site = requests.get(page_link, timeout=1000)
if site.status_code is 200:
    print(site.content)
content = BeautifulSoup(site.content, 'html.parser')
div = content.find_all('div')
response = requests.get(url, timeout=10)
raw_html = simple_get(page_link)
raw_html = urllib.urlopen(page_link)

page = urllib2.urlopen(page_link)
html = BeautifulSoup(page_response, 'html.parser')
div = html.find_all('div')
price_box = html.find_all('div', attrs={'class': 'global-loading-text'})
for ultag in html.find_all('h4'):
    for litag in ultag.find_all('li'):
        print litag_content.append(litag.text)










