from abc import ABC, abstractmethod

from httpx import Client
from lxml import html


class BaseScraper(ABC):
    NS = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    def __init__(self, session: Client):
        self._session = session

    def get_content(self, url, **params):
        page = self._session.get(url, params=params)
        content = html.fromstring(page.content)
        return content

    @abstractmethod
    def run(self):
        pass
