import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; Anki)"
HEADERS = {"User-Agent": USER_AGENT}


def make_request(url: str) -> requests.Response:
    res = requests.get(url, headers=HEADERS)
    return res


def get_soup(url: str) -> BeautifulSoup:
    res = make_request(url)
    soup = BeautifulSoup(res.content, "html.parser")
    return soup
