from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer,
    String, Table, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship

from .base import Base, TimeStampMixin


category_product_relation = Table(
    'product_category_relation', Base.metadata,
    Column('product_url', ForeignKey('product.url'), primary_key=True),
    Column('category_url', ForeignKey('category.url'), primary_key=True),
)


class ProductSpecification(Base):
    __tablename__ = 'product_specification'
    product_url = Column(ForeignKey('product.url'), primary_key=True)
    specification_name = Column(ForeignKey('specification.name'), primary_key=True)
    value = Column(String(127))

    product = relationship("Product", back_populates="specifications")
    specification = relationship("Specification", back_populates="products")


class Company(TimeStampMixin, Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    last_generated_product_id = Column(Integer, default=0)

    categories = relationship('Category', back_populates='owner')
    products = relationship('Product', back_populates='owner')


class Category(TimeStampMixin, Base):
    __tablename__ = 'category'
    __table_args__ = (
        UniqueConstraint('url', 'company_id'),
    )
    id = Column(Integer, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String(length=255))
    url = Column(String, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id'))

    owner = relationship(Company, back_populates='categories')
    children = relationship('Category')
    products = relationship(
        "Product", secondary=category_product_relation, backref="categories"
    )


class Product(TimeStampMixin, Base):
    __tablename__ = 'product'
    __table_args__ = (
        UniqueConstraint('url', 'company_id'),
    )
    id = Column(Integer, autoincrement=True)
    name = Column(String(length=255))
    url = Column(String, primary_key=True)
    quantity = Column(Integer, nullable=True)
    available = Column(Boolean, default=False)
    vendor_code = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey('company.id'))
    price = Column(Integer, nullable=False)
    old_price = Column(Integer)
    purchase_price = Column(Integer, default=0)
    description = Column(Text)

    owner = relationship(Company, back_populates='products')
    images = relationship('Image', back_populates='product')
    specifications = relationship("ProductSpecification", backref="product")


class Image(Base):
    __tablename__ = 'image'
    __table_args__ = (
        UniqueConstraint('url', 'product_id'),
    )
    url = Column(String, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)

    product = relationship(Product, back_populates='images')


class Specification(Base):
    __tablename__ = 'specification'
    name = Column(String, primary_key=True)

    product = relationship(Product, back_populates='specifications')
