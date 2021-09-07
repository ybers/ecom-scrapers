from typing import Optional

from httpx import Client
from sqlalchemy.orm import Session

from .core import KoveaScraper
from .crud import add_company_tree
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
    add_company_tree(
        db=db, company=company, company_data=company_data, vendor_code_gen=vendor_code_gen
    )
    company.last_generated_product_id = vendor_code_gen.last_generated_number
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
