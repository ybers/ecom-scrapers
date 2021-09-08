from typing import Union

from .kovea_ru import Scraper as KoveaScraper

Scraper = Union[KoveaScraper]

__all__ = (
    Scraper,
    KoveaScraper,
)
