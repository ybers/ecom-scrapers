from sqlalchemy.orm import Session

from ..models.ecommerce import (
    Category, Company, Image, Product,
    ProductSpecification, Specification
)
from ..schemas.ecommerce import Company as CompanyData
from ..utils import vendor_code_generator


def add_company_tree(
        *,
        db: Session,
        company: Company,
        company_data: CompanyData,
        vendor_code_gen: vendor_code_generator
):
    # TODO: decompose this one
    for category_data in company_data.categories:
        category = Category(
            name=category_data.name, url=category_data.url, company_id=company.id
        )
        category = db.merge(category)
        for product_data in category_data.products:
            product = Product(
                name=product_data.name, url=product_data.url, company_id=company.id,
                vendor_code=product_data.vendor_code or next(vendor_code_gen),
                price=product_data.price, description=product_data.description,
            )
            category.products.append(product)
            product = db.merge(product)
            for image_data in product_data.images:
                image = Image(url=image_data.url, product=product)
                product.images.append(image)
                image = db.merge(image)
                db.add(image)
            for specification_data in product_data.specifications:
                specification = Specification(name=specification_data.name)
                relation = ProductSpecification(value=specification_data.value)
                relation.specification = specification
                product.specifications.append(specification)
            db.add(product)
        db.add(category)
        db.commit()
