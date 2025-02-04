from flask import render_template, request, redirect, flash, url_for, session
from app import app, db, current_dir
from application.models.models import Users, Categories, Products, Carts, Orders
from application.utils.dateutils import stringToDate
from application.utils.imageutils import imageUpload, imageDelete

@app.route("/create/user", methods=["GET", "POST"])
def createUser():
  
  if request.method == "GET":
    return render_template("create_user.html")
  
  if request.method == "POST":
    # Fetching form data
    user_name = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('c_password')

    # Checking if username already taken
    existing_users = Users.query.filter_by(Name=user_name).all()
    if len(existing_users) > 0 :
      flash("User-name already taken. Please try again with a different name.")
      return render_template("create_user.html")
    
    # Creating new account
    if password == confirm_password:
      user = Users(Name = user_name, Password = password, Authorisation="customer")
      db.session.add(user)
      db.session.commit()
      session["user_id"] = user.Id
      return redirect(url_for("userHome")) 
    
@app.route("/create/category", methods=["GET", "POST"])
def createCategory():
  if "admin_id" in session:
    admin_id = session["admin_id"]
    if request.method == "GET":
        return render_template("create_category.html") 
    
    if request.method == "POST":
      # Fetching form data
      category_name = request.form.get('category_name')
      category_image = request.files.get('category_image')

      # Checking if category exists
      existing_category = Categories.query.filter_by(Name = category_name).first()
      if existing_category != None:
        flash("This category already exists")
        return redirect('/category/page/' + str(existing_category.Id))
      
      # Creating category 
      category = Categories(Name=category_name, AdminId=admin_id)
      db.session.add(category)
      db.session.commit()

      # Uploading Image 
      imageUpload(current_dir+"/static/categories", category_image, category.Id)
      category.Image = "/static/categories/"+str(category.Id)+".jpg"
      db.session.add(category)
      db.session.commit()

      return redirect("/home/admin")
  else:
    return redirect(url_for("login"))  
  
@app.route("/edit/category/<int:category_id>", methods=["GET", "POST"])
def editCategory(category_id):

  if "admin_id" in session:
    admin_id = session["admin_id"]
    category = Categories.query.filter_by(Id = category_id).first()

    if request.method == "GET":
        return render_template("edit_category.html",category=category)
    
    if request.method == "POST":
      # Fetching form data
      category_name = request.form.get('category_name')
      category_image = request.files.get('category_image')

      # Editing Category
      category.Name = category_name
      db.session.add(category)
      db.session.commit()

      try:
        imageUpload(current_dir+"/static/categories", category_image, category.Id)
      except:
        pass  

      # Editing Products under Category
      products = Products.query.filter_by(CategoryId = category_id).all()
      for product in products:
          product.CategoryName = category_name
          db.session.add(product)
          db.session.commit()

      return redirect('/home/admin')
  else:
    return redirect(url_for("login")) 
  
@app.route("/delete/category/<int:category_id>", methods=["GET", "POST"])
def deleteCategory(category_id):
  if "admin_id" in session:
    admin_id = session["admin_id"]
    category = Categories.query.filter_by(Id = category_id).first()

    if request.method == "GET":
        # Deleting category products and cart entries
        products = Products.query.filter_by(CategoryId = category_id).all()
        for product in products:
          cart_entries = Carts.query.filter_by(ProductId=product.Id).all()
          for entry in cart_entries:
            db.session.delete(entry)
            db.session.commit()  
          db.session.delete(product)
          db.session.commit()
        
        # Deleting Image
        imageDelete(category.Image)

        # Deleting category 
        db.session.delete(category)
        db.session.commit()

        return redirect("/home/admin")
  else:
    return redirect(url_for("login"))
  
@app.route("/create/product/<int:category_id>", methods=["GET", "POST"])
def createProduct(category_id):
  if "admin_id" in session:
    admin_id = session["admin_id"]
    category = Categories.query.filter_by(Id=category_id).first()
    categories = Categories.query.all()
    if request.method == "GET":
        return render_template("create_products.html",category = category, categories=categories) 
    
    if request.method == "POST":
      # Fetching form data
      product_name = request.form.get('product_name')
      product_price = request.form.get('product_price')
      product_quantity = request.form.get('product_quantity')
      product_units = request.form.get('units')
      product_expiry = stringToDate(request.form.get('product_expirydate'),'%Y-%m-%d')
      category_name = Categories.query.filter_by(Id = category_id).first().Name
      product_image = request.files.get('product_image')

      # Creating product
      product = Products(Name=product_name, CategoryId=category_id, CategoryName=category_name, Price=product_price, Quantity=product_quantity, Units=product_units, ExpiryDate=product_expiry  )
      db.session.add(product)
      db.session.commit()

      # Uploading Image 
      imageUpload(current_dir+"/static/products", product_image, product.Id)
      product.Image = "/static/products/"+str(product.Id)+".jpg"
      db.session.add(product)
      db.session.commit()

      return redirect("/category/page/"+str(category_id))
  else:
    return redirect(url_for("login"))     
  
@app.route("/edit/product/<int:product_id>", methods=["GET", "POST"])
def editProduct(product_id):

  if "admin_id" in session:
    admin_id = session["admin_id"]
    product = Products.query.filter_by(Id = product_id).first()
    category = Categories.query.filter_by(Name=product.CategoryName).first()

    if request.method == "GET":
        categories = Categories.query.all()
        return render_template("edit_product.html",product=product,categories=categories,category=category)
    
    if request.method == "POST":
      # Fetching form data
      product.Name = request.form.get('product_name')
      product.Price = request.form.get('product_price')
      product.Quantity = request.form.get('product_quantity')
      product.Units = request.form.get('units')
      product.ExpiryDate = stringToDate(request.form.get('product_expirydate'),'%Y-%m-%d')
      category_name =  request.form.get('product_category')
      product_image = request.files.get('product_image')

      # Editing product
      category = Categories.query.filter_by(Name=category_name).first()
      product.CategoryName = category.Name
      product.CategoryId = category.Id
      db.session.add(product)
      db.session.commit()

      # Uploading Image 
      try:
        imageUpload(current_dir+"/static/products", product_image, product.Id)
      except:
        pass

      return redirect('/category/page/'+ str(category.Id))
  else:
    return redirect(url_for("login"))  

@app.route("/delete/product/<int:product_id>", methods=["GET", "POST"])
def deleteProduct(product_id):
  if "admin_id" in session:
    admin_id = session["admin_id"]
    product = Products.query.filter_by(Id = product_id).first()

    if request.method == "GET":

        # Deleting Image
        imageDelete(product.Image)

        # Deleting product 
        category_id = product.CategoryId
        cart_entries = Carts.query.filter_by(ProductId=product.Id).all()
        for entry in cart_entries:
          db.session.delete(entry)
          db.session.commit()  
        db.session.delete(product)
        db.session.commit()

        return redirect("/category/page/" + str(category_id))
  else:
    return redirect(url_for("login")) 

@app.route("/addtocart/<int:product_id>", methods=["GET", "POST"])
def addToCart(product_id):
  if "user_id" in session:
    user_id = session["user_id"]
    product = Products.query.filter_by(Id = product_id).first()
    existing_cart_entry = Carts.query.filter_by(UserId = user_id, ProductId=product_id).first()
    if request.method == "GET":
        return render_template("add_to_cart.html",product=product)
    if request.method == "POST":
      quantity = int(request.form['quantity'])
      if product.Quantity >= quantity:
        if existing_cart_entry == None:
          cart_entry = Carts(UserId=user_id,ProductId=product.Id,ProductQuantity=quantity,TotalAmount=quantity*product.Price)
          db.session.add(cart_entry)
          db.session.commit()
        else:
          existing_cart_entry.ProductQuantity += quantity
          existing_cart_entry.TotalAmount += quantity*product.Price
        product.Quantity -= quantity
        db.session.add(product)
        db.session.commit()
      return redirect('/home/user')
  else:
    return redirect(url_for("login"))      
  

@app.route("/removefromcart/<int:product_id>", methods=["GET", "POST"])
def removeFromCart(product_id):
  if "user_id" in session:
    user_id = session["user_id"]
    product = Products.query.filter_by(Id = product_id).first()

    if request.method == "GET":
        existing_cart_item = Carts.query.filter_by(UserId=user_id,ProductId=product_id).first()
        if existing_cart_item.ProductQuantity == 1:
            db.session.delete(existing_cart_item)
            db.session.commit()
            flash("Product removed from cart")
        else:
          existing_cart_item.ProductQuantity-=1
          existing_cart_item.TotalAmount -= product.Price
          db.session.add(existing_cart_item)
          db.session.commit()
          flash("Product Quantity decreased by one")
        product.Quantity += 1
        db.session.add(product)
        db.session.commit()
          
        return redirect(request.referrer)
  else:
    return redirect(url_for("login"))

@app.route("/removeallfromcart/<int:product_id>", methods=["GET", "POST"])
def removeAllFromCart(product_id):
  if "user_id" in session:
    user_id = session["user_id"]
    product = Products.query.filter_by(Id = product_id).first()

    if request.method == "GET":
        existing_cart_item = Carts.query.filter_by(UserId=user_id,ProductId=product_id).first()
        product.Quantity += existing_cart_item.ProductQuantity
        db.session.add(product)
        db.session.commit()
        db.session.delete(existing_cart_item)
        db.session.commit()
          
        return redirect(request.referrer)
  else:
    return redirect(url_for("login"))          


@app.route("/checkout/<int:user_id>", methods=["GET", "POST"])
def checkOut(user_id):
  if "user_id" in session:
    user_id = session["user_id"]
    user = Users.query.filter_by(Id = user_id).first()
    first_order = not bool(Orders.query.filter_by(UserId=user_id).first())
    cart_items = db.session.query(Carts,Products).filter(Products.Id == Carts.ProductId).filter(Carts.UserId == user_id).all()
    grand_total = 0
    for item in cart_items:
      if first_order:
        grand_total += 0.9*(item[0].TotalAmount)
      else:
        grand_total += item[0].TotalAmount
    categories = Categories.query.all()
    if request.method == "GET":
      if len(cart_items)>0:
        return render_template('checkout.html',user=user)
      else:
        return "There are no items in your cart!"

    if request.method == "POST":
      # Fetching form data
      address = request.form['address']
      payment_method = request.form['payment_method']

      # Creating order entries and deleting cart entries
      order_entry_ids = []
      for entry in cart_items:
        if first_order:
          order_entry = Orders(UserId=user_id,ProductId=entry[0].ProductId,ProductQuantity=entry[0].ProductQuantity,TotalAmount=0.9*(entry[0].TotalAmount),Address=address,PaymentMethod=payment_method)
        else:
          order_entry = Orders(UserId=user_id,ProductId=entry[0].ProductId,ProductQuantity=entry[0].ProductQuantity,TotalAmount=entry[0].TotalAmount,Address=address,PaymentMethod=payment_method)
        db.session.add(order_entry)
        db.session.commit()
        order_entry_ids.append(order_entry.Id)
        db.session.delete(entry[0])
        db.session.commit()

      order_entries = []
      for order_entry_id in order_entry_ids:
        order_entries.append(db.session.query(Orders,Products).filter(Products.Id == Orders.ProductId).filter(Orders.Id == order_entry_id).first())
      return render_template('order_confirmed.html',order_entries=order_entries,payment_method=payment_method,address=address,grand_total=grand_total,first_order=first_order,categories=categories,user=user)

  else:
    return redirect(url_for("login"))   


@app.route("/buy/<int:product_id>", methods=["GET", "POST"])
def buyNow(product_id):
  if "user_id" in session:
    user_id = session["user_id"]
    user = Users.query.filter_by(Id = user_id).first()
    first_order = not bool(Orders.query.filter_by(UserId=user_id).first())
    product = Products.query.filter_by(Id=product_id).first()
    categories = Categories.query.all()
    if request.method == "GET":
      return render_template("buy_product.html",product=product,user=user)
    
    if request.method == "POST":
      # Fetching form data
      address = request.form['address']
      payment_method = request.form['payment_method']
      quantity = int(request.form['quantity'])
      
      if product.Quantity >= quantity:
        product.Quantity -= quantity
        db.session.add(product)
        db.session.commit()
      grand_total = 0
      if first_order:
        grand_total += 0.9*(product.Price*quantity)
        order_entry = Orders(UserId=user_id,ProductId=product.Id,ProductQuantity=quantity,TotalAmount=grand_total,Address=address,PaymentMethod=payment_method)
      else:
        grand_total += product.Price*quantity
        order_entry = Orders(UserId=user_id,ProductId=product.Id,ProductQuantity=quantity,TotalAmount=grand_total,Address=address,PaymentMethod=payment_method)
      db.session.add(order_entry)
      db.session.commit()
        
      order_entries = db.session.query(Orders,Products).filter(Products.Id == Orders.ProductId).filter(Orders.Id == order_entry.Id).all()
      return render_template('order_confirmed.html',order_entries=order_entries,payment_method=payment_method,address=address,grand_total=grand_total,first_order=first_order,categories=categories,user=user)

  else:
    return redirect(url_for("login")) 

    
