from app import db

class Users(db.Model):
  __tablename__ = "Users"
  Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  Name = db.Column(db.String, nullable=False, unique=True)
  Password = db.Column(db.String, nullable=False)
  Authorisation = db.Column(db.String, nullable=False)

class Categories(db.Model):
  __tablename__ = "Categories"
  Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  Name = db.Column(db.String, nullable=False, unique=True)
  AdminId = db.Column(db.Integer,db.ForeignKey("Users.Id"),nullable=False)
  Image = db.Column(db.String)

class Products(db.Model):
  __tablename__ = "Products"
  Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  Name = db.Column(db.String, nullable=False)
  CategoryId = db.Column(db.Integer,db.ForeignKey("Categories.Id"),nullable=False)
  CategoryName = db.Column(db.Integer,db.ForeignKey("Categories.Name"),nullable=False)
  Price = db.Column(db.Integer, nullable=False)
  Quantity = db.Column(db.Integer,nullable=False)
  Units = db.Column(db.String,nullable=False)
  ExpiryDate = db.Column(db.DateTime, nullable=False)
  Image = db.Column(db.String)


class Carts(db.Model):
  __tablename__ = "Carts"
  UserId = db.Column(db.Integer,db.ForeignKey("Users.Id"), primary_key=True, nullable=False)
  ProductId = db.Column(db.Integer,db.ForeignKey("Products.Id"), primary_key=True, nullable=False)
  ProductQuantity = db.Column(db.Integer,db.ForeignKey("Products.Quantity"), nullable=False)
  TotalAmount = db.Column(db.Integer, nullable=False)

class Orders(db.Model):
  __tablename__ = "Orders"
  Id = db.Column(db.Integer, primary_key=True, nullable=False)
  UserId = db.Column(db.Integer,db.ForeignKey("Users.Id"), nullable=False)
  ProductId = db.Column(db.Integer,db.ForeignKey("Products.Id"), nullable=False)
  ProductQuantity = db.Column(db.Integer,db.ForeignKey("Products.Quantity"), nullable=False)
  TotalAmount = db.Column(db.Integer, nullable=False)
  Address = db.Column(db.String,nullable=False)
  PaymentMethod = db.Column(db.String,nullable=False)