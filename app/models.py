from app import db, bcrypt, app
import jwt, datetime
from sqlalchemy.dialects.postgresql import JSON


class Account():

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=160),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

class User(db.Model, Account):

    __tablename__ = "User"

    u_id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    purchases = db.relationship("Purchases", backref="User", lazy=False)
    addresses = db.relationship("ShippingInfo", backref="User", lazy=False)

    def __init__(self, name, username, email, password):
        self.name = name,
        self.username = username,
        self.email = email,
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def to_dict(self):
        return {
            "name":self.name,
            "username": self.username,
            "email" : self.email,
            "purchases":self.purchases,
            "addresses": [{
                "id": ad.id,
                "address": ad.address,
                "city": ad.city,
                "state": ad.state,
                "country": ad.country,
                "postal_code": ad.postal_code,
                "phone": ad.phone
            } for ad in self.addresses]
        }


class Admin(db.Model, Account):

    __tablename__ = "Admin"

    a_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, name, email, password):
        self.name = name,
        self.email = email,
        self.password =  bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

class Products(db.Model):

    __tablename__ = "Products"

    p_id = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    accessory = db.Column(db.Boolean, nullable=False)

    def __init__(self, p_name, price, accessory):
        self.p_name = p_name
        self.price = price
        self.accessory = accessory


class Purchases(db.Model):

    __tablename__ = "Purchases"

    pu_id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey("User.u_id"), nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey("Products.p_id"), nullable=False )
    date = db.Column(db.DateTime, nullable=False)


class ShippingInfo(db.Model):

    __tablename__ = "ShippingInfo"
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey("User.u_id"), nullable=False)
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    postal_code = db.Column(db.String, nullable=False)
    phone = db.Column(db.CHAR(10), nullable=False)

    def __init__(self, u_id, address, city, state, country, postal_code, phone):
        self.u_id = u_id
        self.address = address,
        self.city = city,
        self.state = state,
        self.country = country,
        self.postal_code = postal_code,
        self.phone = phone

    def __repr__(self):
        return {
            "address" : self.address,
            "city" : self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "phone": self.phone
        }


class Wishlist(db.Model):

    __tablename__ = "Wishlist"
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey("User.u_id"), nullable=False)
    p_id = db.Column(db.Integer, db.ForeignKey("Products.p_id"), nullable=False)


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)