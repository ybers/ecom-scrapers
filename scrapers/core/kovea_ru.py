from .base import BaseScraper
from ..schemas.ecommerce import (
    Category, Company, Image, Product, Specification
)


class Scraper(BaseScraper):

    BASE_URL = 'https://kovea.ru/'

    def __init__(self, session, company_data: Company):
        super().__init__(session)
        self._company_data = company_data
        self._session.base_url = self._company_data.url = self.BASE_URL
        self.broken_items = list()

    def collect_categories(self, url):
        content = self.get_content(url)
        for element in content.xpath('//div[@class="caption"]/a'):
            if element.attrib['href'].startswith('/catalog/'):
                url = str(self._session.base_url.join(element.attrib['href']))
                self._company_data.categories.add(Category(name=element.text, url=url))

    def _collect_products_from_categories(self):
        products = list()
        for category in self._company_data.categories:
            category_page = self.get_content(category.url)
            for product in category_page.xpath('//ul[@class="list-item"]/li'):
                vendor_code = product.xpath('.//span[@class="article v-m"]')[0].text
                name_node = product.xpath('.//span[@itemprop="name"]')[0]
                name = name_node.text
                url = str(self._session.base_url.join(name_node.getparent().attrib['href']))
                price = product.xpath('.//span[@class="price-new"]')[0].text.replace(' ', '')
                product = Product(
                    name=name, price=price, url=url, vendor_code=vendor_code,
                )
                products.append(product)
        return products

    def collect_products_data(self):
        products = self._collect_products_from_categories()
        for product in products:
            product_page = self.get_content(product.url)
            if description_section := product_page.xpath('//div[@class="text-block"]'):
                product.description = description_section[0].text_content().strip()

            if pictures := product_page.xpath('//a[@class="fancybox main-img img-center"]'):
                for picture in pictures:
                    picture_url = str(self._session.base_url.join(picture.attrib['href']))
                    product_image = Image(url=picture_url)
                    product.images.append(product_image)

            if specifications_title := product_page.xpath('//div[@class="caption" and text () = "Характеристики"]'):
                table = specifications_title[0].getparent().getnext()
                for row in table.getchildren():
                    name, value = map(lambda x: x.text.removesuffix(':'), row.getchildren())
                    specification = Specification(name=name, value=value)
                    product.specifications.append(specification)

    def run(self):
        self.collect_categories('catalog')
        self.collect_products_data()
