from datetime import datetime
from typing import Optional, Union
from zoneinfo import ZoneInfo
from lxml import etree


class OutputXML:
    
    def __init__(self, *, filename):
        self._root = etree.Element('yml_catalog', attrib={'date': str(datetime.now(tz=ZoneInfo('Europe/Moscow')))})
        shop = etree.SubElement(self._root, 'shop')
        self._categories = etree.SubElement(shop, 'categories')
        self._offers = etree.SubElement(shop, 'offers')
        self._filename = filename

    def save(self):
        self.result.write(self._filename, encoding='utf-8', xml_declaration=True, pretty_print=True)
    
    @property
    def result(self):
        return self._root.getroottree()

    def add_category(self, name: str, id_: int, parent_id: Optional[int] = None):
        attrib = {'id': str(id_)}
        if parent_id:
            attrib['parentId'] = parent_id
        category = etree.SubElement(self._categories, 'category', attrib=attrib)
        category.text = name

    def add_offer(
            self, *,
            name: str,
            price: int,
            category: int,
            vendor_code: str,
            description: Optional[str] = None,
            pictures: Optional[list[str]] = None,
            characteristics: Optional[dict[str, Union[int, str]]] = None,
    ):
        offer = etree.SubElement(self._offers, 'offer')

        offers_map = {
            'name': name, 'price': str(price),
            'categoryId': str(category), 'vendorCode': vendor_code
        }
        if description:
            offers_map['description'] = description

        for name, text in offers_map.items():
            node = etree.SubElement(offer, name)
            node.text = text

        if pictures:
            for picture in pictures:
                picture_node = etree.SubElement(offer, 'picture')
                picture_node.text = picture
        if characteristics:
            for name, value in characteristics.items():
                characteristics_node = etree.SubElement(offer, 'param', attrib={'name': name})
                characteristics_node.text = value
