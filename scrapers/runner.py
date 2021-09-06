from typing import Optional

from httpx import Client
from sqlalchemy.orm import Session

from .core import KoveaScraper
from .models import base, ecommerce
from .schemas.ecommerce import Company
from .utils import vendor_code_generator


COMPANIES = {
    'Kovea': KoveaScraper,
}


def scrape(session: Client, companies: dict) -> Company:
    for name, scraper_obj in companies.items():
        company_data = Company(name=name)
        scraper = scraper_obj(session, company_data)
        scraper.run()
        return company_data


def db_worker(db: Session, company_data: Company):
    engine = db.get_bind()
    base.Base.metadata.create_all(bind=engine)
    company = ecommerce.Company(name=company_data.name, url=company_data.url)
    company = db.merge(company)
    db.add(company)
    db.commit()
    vendor_code_gen = vendor_code_generator('YB', company.last_generated_product_id)
    for category_data in company_data.categories:
        category = ecommerce.Category(
            name=category_data.name, url=category_data.url, company_id=company.id
        )
        category = db.merge(category)
        for product_data in category_data.products:
            product = ecommerce.Product(
                name=product_data.name, url=product_data.url, company_id=company.id,
                vendor_code=product_data.vendor_code or next(vendor_code_gen),
                price=product_data.price, description=product_data.description,
            )
            category.products.append(product)
            product = db.merge(product)
            for image_data in product_data.images:
                image = ecommerce.Image(url=image_data.url, product=product)
                product.images.append(image)
                image = db.merge(image)
                db.add(image)
            for specification_data in product_data.specifications:
                specification = ecommerce.Specification(name=specification_data.name)
                relation = ecommerce.ProductSpecification(value=specification_data.value)
                relation.specification = specification
                product.specifications.append(specification)
            db.add(product)
        db.add(category)
        db.commit()


def main(*, db: Session, session: Client, company_names: Optional[list[str]] = None):
    if company_names:
        try:
            company_names = {name: COMPANIES[name] for name in company_names}
        except KeyError as ex:
            possible_company_names = ', '.join(COMPANIES)
            raise KeyError('Possible company names are: %s. You passed %s' % (possible_company_names, ex))
    else:
        company_names = COMPANIES
    data = scrape(session, company_names)
    db_worker(db, data)
