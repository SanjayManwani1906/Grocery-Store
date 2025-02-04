from flask import render_template, request, redirect, flash, url_for, session
from app import app, db
from application.models.models import Users, Categories, Products, Carts, Orders
from application.utils.dateutils import stringToDate


@app.route("/", methods=["GET", "POST"])
def login():
  
  if request.method == "GET":
    if "user_id" in session:
      session.pop("user_id", None)
    return render_template("login.html")
  
  if request.method == "POST":
    user_name = request.form.get("username")
    password = request.form.get("password") 
    user = Users.query.filter_by(Name=user_name).first() 
    if user == None:
      flash("User not found")
      return render_template("login.html")
    if password == user.Password :
      if user.Authorisation == "admin":
        session["admin_id"] = user.Id
        return redirect(url_for("adminHome"))
      if user.Authorisation == "customer":
        session["user_id"] = user.Id
        return redirect(url_for("userHome"))
    else:
      flash("Incorrect Username/Password")
      return render_template("login.html")
      

@app.route('/logout')
def logout():
  if "user_id" in session:
    session.pop("user_id", None)
    flash("Logged Out")
    return redirect(url_for("login"))
  else:
    flash("Already Logged Out")
    return redirect(url_for("login"))
  
@app.route('/adminlogout')
def adminLogout():
  if "admin_id" in session:
    session.pop("admin_id", None)
    flash("Logged Out")
    return redirect(url_for("login"))
  else:
    flash("Already Logged Out")
    return redirect(url_for("login"))

@app.route("/home/user", methods=["GET", "POST"])
def userHome():
  if "user_id" in session:
    user_id = session["user_id"]
    user = Users.query.filter_by(Id=user_id).first()
    categories = Categories.query.all()
    category_dict = {}
    for category in categories:
      product_list = Products.query.filter_by(CategoryId = category.Id).filter(Products.Quantity > 0).all()
      category_dict[category] = product_list
    if request.method == "GET":
        return render_template("user_home.html", category_dict=category_dict, user=user)
    if request.method == "POST":
      search_keyword = request.form['search_keyword']
      product_list = set(Products.query.filter(Products.Name.like("%"+search_keyword+"%")).all() + Products.query.filter(Products.CategoryName.like("%"+search_keyword+"%")).all())
      return render_template("search.html",products=product_list, user=user)

  else:
    return redirect(url_for("login")) 


@app.route("/home/admin", methods=["GET", "POST"])
def adminHome():
  if "admin_id" in session:
    admin_id = session["admin_id"]
    if request.method == "GET":
        all_categories = Categories.query.all()
        return render_template("admin_home.html", categories = all_categories)
  else:
    return redirect(url_for("login"))

@app.route("/category/page/<int:category_id>", methods=["GET", "POST"])
def categoryPage(category_id):
  if "admin_id" in session:
    admin_id = session["admin_id"]
    categories = Categories.query.all()
    if request.method == "GET":
        products = Products.query.filter_by(CategoryId = category_id).all()
        category = Categories.query.filter_by(Id = category_id).first()
        return render_template("category_page.html", products = products, category_id = category_id,category = category, categories=categories)
  else:
    return redirect(url_for("login"))  


@app.route("/products/page", methods=["GET", "POST"])
def productsPage():
  if "admin_id" in session:
    admin_id = session["admin_id"]

    if request.method == "GET":
        return render_template("products_page.html")
  else:
    return redirect(url_for("login"))  
  

@app.route("/cart", methods=["GET", "POST"])
def cart():
  if "user_id" in session:
    user_id = session["user_id"]
    user = Users.query.filter_by(Id=user_id).first()
    cart_items = db.session.query(Carts,Products).filter(Products.Id == Carts.ProductId).filter(Carts.UserId == user_id).all()
    
    if request.method == "GET":
        grand_total = 0
        for items in cart_items:
          grand_total += items[0].TotalAmount 
        return render_template("cart.html", cart_items=cart_items, grand_total=grand_total,user=user)
    if request.method == "POST":
      search_keyword = request.form['search_keyword']
      product_list = set(Products.query.filter(Products.Name.like("%"+search_keyword+"%")).all() + Products.query.filter(Products.CategoryName.like("%"+search_keyword+"%")).all())
      return render_template("search.html",products=product_list, user=user)
  else:
    return redirect(url_for("login"))  
  

@app.route("/product/page/<int:category_id>", methods=["GET", "POST"])
def productPage(category_id):
  if "user_id" in session:
    user_id = session["user_id"]
    user = Users.query.filter_by(Id=user_id).first()
    categories = Categories.query.all()
    product_list = Products.query.filter_by(CategoryId = category_id).filter(Products.Quantity > 0).all()
    out_of_stock_products = Products.query.filter_by(CategoryId = category_id).filter(Products.Quantity == 0).all()
    category = Categories.query.filter_by(Id = category_id).first()
    if request.method == "GET":
        return render_template("product_page.html",user=user, categories=categories,products=product_list,out_of_stock_products=out_of_stock_products,category=category,user_id=user_id)
    if request.method == "POST":
      search_keyword = request.form['search_keyword']
      product_list = set(Products.query.filter(Products.Name.like("%"+search_keyword+"%")).all() + Products.query.filter(Products.CategoryName.like("%"+search_keyword+"%")).all())
      return render_template("search.html",products=product_list, user=user)
  else:
    return redirect(url_for("login"))   
  

@app.route("/search", methods=["GET","POST"])
def search():
  if "user_id" in session:
    user_id = session["user_id"]
    user = Users.query.filter_by(Id=user_id).first()
    if request.method == "GET":
        return render_template("search.html",products=[])
    if request.method == "POST":
      search_keyword = request.form['search_keyword']

      if 'order_by' not in request.form:
        order_by = 'price'
      else:
        order_by = request.form['order_by']

      if 'order' not in request.form or request.form['order'] == 'ascending':
        order = False
      else:
        order = True
      
      # Querying
      product_list = set(Products.query.filter(Products.Name.like("%"+search_keyword+"%")).all() + Products.query.filter(Products.CategoryName.like("%"+search_keyword+"%")).all())
      
      # Sorting
      if order_by == 'expiry':
        product_list = sorted(product_list, key=lambda product: (product.ExpiryDate), reverse=order)
      else:
        product_list = sorted(product_list, key=lambda product: (product.Price), reverse=order)
      return render_template("search.html",products=product_list, user=user)
  else:
    return redirect(url_for("login"))
  
@app.route("/user/account", methods=["GET", "POST"])
def account():
  if "user_id" in session:
    user_id = session["user_id"]
    user = Users.query.filter_by(Id=user_id).first()
    order_entries = db.session.query(Orders,Products).filter(Products.Id == Orders.ProductId).filter(Orders.UserId == user_id).order_by(Orders.Id.desc()).all()
    if request.method == "GET":
        return render_template("account_info.html", order_entries=order_entries, user=user)
    if request.method == "POST":
      search_keyword = request.form['search_keyword']
      product_list = set(Products.query.filter(Products.Name.like("%"+search_keyword+"%")).all() + Products.query.filter(Products.CategoryName.like("%"+search_keyword+"%")).all())
      return render_template("search.html",products=product_list, user=user)
  else:
    return redirect(url_for("login"))  
  

@app.route("/admin/account", methods=["GET", "POST"])
def adminAccount():
  if "admin_id" in session:
    admin_id = session["admin_id"]
    order_entries = db.session.query(Orders,Products).filter(Products.Id == Orders.ProductId).all()

    if request.method == "GET":
        return render_template("admin_account.html", order_entries=order_entries)
  else:
    return redirect(url_for("login"))    
  
@app.route("/best_selling_products", methods=["GET", "POST"])
def bestSellingProducts():
  if "user_id" in session:
    user_id = session["user_id"]
    user = Users.query.filter_by(Id = user_id).first()
    products = db.session.query(Products,Orders).filter(Orders.ProductId == Products.Id).group_by(Products.Id).order_by(Orders.ProductQuantity.desc()).all()
    print(products)
    if request.method == "GET":
        return render_template("best_selling_products.html", products=products, user=user)
    if request.method == "POST":
      search_keyword = request.form['search_keyword']
      product_list = set(Products.query.filter(Products.Name.like("%"+search_keyword+"%")).all() + Products.query.filter(Products.CategoryName.like("%"+search_keyword+"%")).all())
      return render_template("search.html",products=product_list, user=user)
  else:
    return redirect(url_for("login"))

  







