from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ReferenceField, ListField, EmbeddedDocument, EmbeddedDocumentField, BooleanField
from flask_login import UserMixin
from datetime import *


class Position(EmbeddedDocument):
    name = StringField(required=True, unique=True, max_length=20)
    color = StringField(required=True)
    fontweight = StringField(required=True)
    backgroundcolor = StringField(required=True)
    description = StringField(required=True)

    meta = {'strict': False}

class User(UserMixin, Document):
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(required=True, default='user')
    is_admin = BooleanField(default=False)
    verification_code = StringField()

    nickname = StringField(unique=True)
    first_name = StringField(max_length=50, required=True)
    last_name = StringField(max_length=50, required=True)
    country = StringField()
    positions = ListField(EmbeddedDocumentField(Position), required=True)
    user_description = StringField()
    profile_image_url = StringField()  

    def get_id(self):
        return self.email

    meta = {'collection': 'user'}

class Product(Document):
    name = StringField(required=True, unique=True)
    category = StringField(required=True)
    product_type = StringField(required=True)
    date_added = DateTimeField(default=lambda: datetime.now(timezone.utc).replace(second=0, microsecond=0))
    value = IntField(required=True)
    price = FloatField(required=True)
    meta = {'collection': 'product'}

class OrderItem(EmbeddedDocument):
    product = ReferenceField(Product, required=True)
    product_name = StringField(required=True)
    quantity = IntField(required=True)
    total_price = FloatField(required=True)
    meta = {'strict': False}

class Order(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    date_added = DateTimeField(default=lambda: datetime.now(timezone.utc).replace(second=0, microsecond=0))
    pesel = StringField(required=True)
    contact = StringField(required=True)
    address = StringField(required=True)
    order_items = ListField(EmbeddedDocumentField(OrderItem), required=True)
    total_order_price = FloatField(required=True)
    discount = FloatField(default=0)

    #CODE !ONLY! FOR CUSTOMIZATION
    dot = StringField(default="rgba(0, 0, 0, 0)")
    description = StringField()
    meta = {'collection': 'order'}



