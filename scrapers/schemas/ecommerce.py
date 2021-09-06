from dataclasses import dataclass, field

"""
Simple version of database structure

Company
    |
    |--> Categories
            |
            |--> Products
                    |
                    |--> Images
                    |
                    |--> Characteristics --> Characteristic's values
"""


@dataclass
class Company:
    name: str
    url: str = field(init=False)
    categories: set['Category'] = field(default_factory=set)


@dataclass(eq=False)
class Category:
    name: str
    url: str
    parent: 'Category' = None
    products: list['Product'] = field(default_factory=list)

    def __eq__(self, other: 'Category'):
        if self.url == other.url:
            return True
        return False
    
    def __hash__(self):
        return hash(self.url)


@dataclass
class Product:
    name: str
    price: int
    url: str
    description: str = None
    old_price: int = None
    purchase_price: int = None
    vendor_code: str = None
    images: list['Image'] = field(default_factory=list)
    specifications: list['Specification'] = field(default_factory=list)


@dataclass
class Image:
    url: str


@dataclass
class Specification:
    name: str
    value: str
