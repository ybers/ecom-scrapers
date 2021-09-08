from sqlalchemy.orm import Session

from ..models.ecommerce import (
    Category, Company, Image, Product,
    ProductSpecification, Specification
)
from ..schemas.ecommerce import Company as CompanyData
from ..utils import vendor_code_generator


def add_image(db, image_data, product):
    image = Image(url=image_data.url, product=product)
    product.images.append(image)
    image = db.merge(image)
    db.add(image)


def add_specification(db, specification_data, product):
    specification = Specification(name=specification_data.name)
    relation = ProductSpecification(value=specification_data.value)
    relation.specification = specification
    product.specifications.append(specification)
    db.add_all([specification, relation])


def add_product(db, product_data, category, **kwargs):
    vendor_code_gen = kwargs.pop('vendor_code_gen')
    product = Product(
        name=product_data.name, url=product_data.url, owner=category.owner,
        vendor_code=product_data.vendor_code or next(vendor_code_gen),
        price=product_data.price, description=product_data.description,
    )
    category.products.append(product)
    product = db.merge(product)
    for image_data in product_data.images:
        add_image(db, image_data, product)
    for specification_data in product_data.specifications:
        add_specification(db, specification_data, product)


def add_category(db, category_data, company, **kwargs):
    category = Category(
        name=category_data.name, url=category_data.url, owner=company
    )
    category = db.merge(category)
    for product_data in category_data.products:
        add_product(db, product_data, category, **kwargs)
    db.commit()


def add_company_tree(
        *,
        db: Session,
        company: Company,
        company_data: CompanyData,
        vendor_code_gen: vendor_code_generator
):
    for category_data in company_data.categories:
        add_category(db, category_data, company, vendor_code_gen=vendor_code_gen)
