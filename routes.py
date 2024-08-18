from flask import render_template, redirect, url_for, request, flash, send_file, abort, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, login_manager, mail
from flask_mail import Message
from models import User, Product, Order, OrderItem
from forms import LoginForm, ProductForm, OrderForm, VerificationForm, EditProfileForm
from datetime import *
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from functools import wraps
from collections import Counter, defaultdict
import secrets
import os
from mongoengine.queryset.visitor import Q
from werkzeug.utils import secure_filename

# ---- POMOCNE FUNKCJE ----

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_layout():
    return 'admin_layout.html' if current_user.is_admin else 'user_layout.html'

def get_top_selling_products():
    try:
        all_orders = Order.objects()
        all_order_items = []
        
        for order in all_orders:
            all_order_items.extend(order.order_items)
        
        product_counter = Counter()
        for item in all_order_items:
            product_counter[item.product.name] += item.quantity
        
        top_selling_products = product_counter.most_common(3)
        
        return top_selling_products
    
    except Exception as e:
        print(f"An error occurred while fetching top selling products: {e}")
        return []
    
def get_orders_count_by_date():
    try:
        orders = Order.objects()
        orders_count_by_date = defaultdict(int)
        
        for order in orders:
            order_date = order.date_added.date()
            orders_count_by_date[order_date] += 1
        
        sorted_dates = sorted(orders_count_by_date.keys())
        
        labels = [date.strftime('%Y-%m-%d') for date in sorted_dates]
        values = [orders_count_by_date[date] for date in sorted_dates]
        
        return labels, values
    
    except Exception as e:
        print(f"An error occurred while fetching orders count by date: {e}")
        return [], []
    
def get_least_popular_products(limit=3):
    try:
        all_orders = Order.objects()
        all_order_items = []

        for order in all_orders:
            all_order_items.extend(order.order_items)

        product_counter = Counter()
        for item in all_order_items:
            product_counter[item.product_name] += item.quantity

        least_popular_products = sorted(product_counter.items(), key=lambda x: x[1])[:limit]

        return least_popular_products

    except Exception as e:
        print(f"An error occurred while fetching least popular products: {e}")
        return []
    
def get_revenue_by_date():
    try:
        orders = Order.objects()
        revenue_by_date = defaultdict(float)

        for order in orders:
            order_date = order.date_added.date()
            revenue_by_date[order_date] += order.total_order_price
        
        sorted_dates = sorted(revenue_by_date.keys())

        labels = [date.strftime('%Y-%m-%d') for date in sorted_dates]
        values = [revenue_by_date[date] for date in sorted_dates]

        return labels, values

    except Exception as e:
        print(f"An error occurred while fetching revenue by date: {e}")
        return [], []

# ---- INDEX ----

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    labels_orders, values_orders = get_orders_count_by_date()
    least_popular_products = get_least_popular_products()
    top_selling_products = get_top_selling_products()
    revenue_labels, revenue_values = get_revenue_by_date()  

    return render_template('dashboard.html',
                           top_selling_products=top_selling_products,
                           least_popular_products=least_popular_products,
                           labels_orders=labels_orders,
                           values_orders=values_orders,
                           revenue_labels=revenue_labels,
                           revenue_values=revenue_values,
                           layout=get_layout())

# ---- ZARZADZANIE LOGOWANIEM ----

@login_manager.user_loader
def load_user(user_id):
    return User.objects(email=user_id).first()

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('magazine'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
            hashed_code = generate_password_hash(verification_code, method='pbkdf2:sha256')
            user.verification_code = hashed_code
            user.save()

            msg = Message('Your verification code', sender='domo241@wp.pl', recipients=[user.email])
            msg.html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verification Code</title>
                <style>
                    body {{
                        background-color: rgb(57, 57, 227);
                        margin: 0;
                        padding: 0;
                        font-family: Arial, sans-serif;
                        color: rgb(245, 245, 5);
                    }}
                    .container {{
                        max-width: 600px;
                        margin: auto;
                        background: rgb(57, 57, 227);
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        text-align: center;
                    }}

                    h1{{
                    font-size: 5rem;
                    }}

                
                    .header, .footer {{
                        background-color: rgb(57, 57, 227);
                        padding: 10px;
                        color: rgb(245, 245, 5);
                        text-shadow: 1px 1px 1px black;
                    }}
                    .verification-code {{
                        font-size: 4rem;
                        color: white;
                        font-weight: bold;
                    }}


                    p{{
                    font-size: 3rem;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Marketplace</h1>
                    </div>
                    <p style="color: rgb(245, 245, 5);">Your 6-digit verification code:</p>
                    <p class="verification-code">{verification_code}</p>
                    <p class="footer">Hallelujah!</p>
                </div>
            </body>
            </html>
                """
            try:
                mail.send(msg)
                session['verification_email'] = user.email
                return redirect(url_for('verify'))
            except Exception as e:
                flash(f'An error occurred while sending email: {str(e)}', 'danger')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route("/verify", methods=['GET', 'POST'])
def verify():
    email = session.get('verification_email')

    user = User.objects(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    form = VerificationForm()
    if form.validate_on_submit():
        if check_password_hash(user.verification_code, form.code.data):
            user.verification_code = None
            user.save()
            login_user(user)
            session.pop('verification_email', None)
            flash('Verification successful. You are now logged in.', 'success')
            return redirect(url_for('magazine'))
        else:
            flash('Invalid verification code.', 'danger')
    
    return render_template('verify.html', title='Verify', form=form)

@app.route("/logout")
def logout():
    logout_user()
    session.pop('verification_email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---- WIZUALIZACJA DANYCH ----

@app.route('/customers', methods=['GET'])
@login_required
def customers():
    search_query = request.args.get('search', '')
    color_filter = request.args.get('color', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    orders_query = Order.objects()

    if search_query:
        orders_query = orders_query.filter(
            Q(last_name__icontains=search_query) | 
            Q(date_added__startswith=search_query)
        )

    if color_filter:
        orders_query = orders_query.filter(dot=color_filter)

    total_orders = orders_query.count()

    total_pages = (total_orders + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    paginated_orders = orders_query[start_idx:end_idx]

    for order in paginated_orders:
        order.total_quantity = sum(item.quantity for item in order.order_items)

    return render_template(
        'customers.html',
        orders=paginated_orders,
        total_orders=total_orders,
        layout=get_layout(),
        current_page=page,
        total_pages=total_pages,
        per_page=per_page
    )

@app.route('/magazine', methods=['GET'])
@login_required
def magazine():
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    if search_query:
        filtered_products = Product.objects(name__icontains=search_query)
    else:
        filtered_products = Product.objects()
    
    total_products = filtered_products.count()

    total_pages = (total_products + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_products = filtered_products[start_idx:end_idx]
    
    return render_template(
        'magazine.html',
        products=paginated_products,
        total_products=total_products,
        layout=get_layout(),
        current_page=page,
        total_pages=total_pages,
        per_page=per_page
    )

@app.route('/customers/<order_id>')
@login_required
def order_details(order_id):
    try:
        order = Order.objects(id=order_id).first()
        if not order:
            flash('Order not found')
            return redirect(url_for('customers'))

        total_quantity = sum(item.quantity for item in order.order_items)

        return render_template('customers-details.html', order=order, total_quantity=total_quantity, layout=get_layout())
    except Exception as e:
        flash(f'An error occurred: {e}')
        return redirect(url_for('customers'))
    
@app.route('/customize/<order_id>', methods=['GET', 'POST'])
@login_required
def customize_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        if request.method == 'POST':
            order.dot = request.form.get('dot')
            order.description = request.form.get('description')
            order.save()
            flash('Details changed.', 'info')
            return redirect(url_for('order_details', order_id=order.id))
        total_quantity = sum(item.quantity for item in order.order_items)

        return render_template('customize_order.html', order=order, total_quantity=total_quantity, layout=get_layout())
    
    except Exception as e:
        flash(f'An error occurred: {e}')
        return redirect(url_for('customers'))

# ---- WPROWADZANIE DANYCH ----

@app.route('/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            category=form.category.data,
            product_type=form.product_type.data,
            value=form.value.data,
            price=form.price.data
        )
        product.save()
        flash('Product added successfully', 'info')
        return redirect(url_for('addproduct'))
    return render_template('add_product.html', form=form, layout=get_layout())

@app.route('/addorder', methods=['GET', 'POST'])
@login_required
def addorder():
    order_success = False
    form = OrderForm()
    new_order = None  

    if request.method == 'POST':
        if form.add_item.data:
            form.order_items.append_entry()
            return render_template('add_order.html', form=form, layout=get_layout())

        if form.submit.data:
            try:
                order_items = []
                total_order_price = 0

                for item in form.order_items.entries:
                    try:
                        product = Product.objects.get(name=item.product_name.data)
                        if product.value < item.quantity.data:
                            flash(f"Not enough stock for '{item.product_name.data}'. Available: {product.value}.")
                            return render_template('add_order.html', form=form, layout=get_layout())

                        total_price = item.quantity.data * product.price
                        total_order_price += total_price
                        order_item = OrderItem(
                            product=product,
                            product_name=product.name,
                            quantity=item.quantity.data,
                            total_price=total_price
                        )
                        order_items.append(order_item)

                        product.value -= item.quantity.data
                        product.save()
                    except Product.DoesNotExist:
                        flash(f"Product '{item.product_name.data}' does not exist.")
                        return render_template('add_order.html', form=form, layout=get_layout())

                discount = 0
                if total_order_price >= 500:
                    discount = total_order_price * 0.07
                    total_order_price -= discount
                    discount_note = f"Discount of {discount:.2f} applied."
                    flash('Discount has been applied successfully.', 'info')
                else:
                    discount_note = ""

                new_order = Order(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    pesel=form.pesel.data,
                    contact=form.contact.data,
                    address=form.address.data,
                    order_items=order_items,
                    total_order_price=total_order_price,
                    discount=discount,
                    description=discount_note  
                )

                new_order.save()

                order_success = True
                flash('Order placed successfully!')

            except Exception as e:
                flash(f"An error occurred while processing the order: {e}")

    return render_template('add_order.html', form=form, order_success=order_success, order=new_order, layout=get_layout())

# ---- USUWANIE DANYCH ----

@app.route('/customers/delete/<order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.objects.get(id=order_id)
    order.delete()
    flash('Order deleted successfully', 'info')
    return redirect(url_for('customers'))

@app.route('/delete_product/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    flash('Product deleted successfully', 'info')
    return redirect(url_for('magazine'))

# ---- PDF GENERATOR ----

@app.route('/download_pdf/<order_id>')
def download_pdf(order_id):
    order = Order.objects(id=order_id).first()
    if not order:
        return 'Order not found', 404

    pdf_dir = 'shopassistant/pdf'
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"order_{order_id}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)

    c.setFont("Helvetica-Bold", 24)
    market_place_text = "MARKETPLACE"
    market_place_width = c.stringWidth(market_place_text, "Helvetica-Bold", 24)
    c.drawString((A4[0] - market_place_width) / 2, A4[1] - 50, market_place_text)

    c.setFont("Helvetica", 12)
    c.drawString((A4[0] - c.stringWidth("Powered by ⚙️ engine", "Helvetica", 12)) / 2, 30, "Powered by \u26D1 engine")

    top_margin = 100

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, A4[1] - top_margin, f"Order ID: {order_id}")

    c.setFont("Helvetica", 12)
    y = A4[1] - top_margin - 50
    c.drawString(50, y, f"Date: {order.date_added.strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, y - 20, f"Customer: {order.first_name} {order.last_name}")
    c.drawString(50, y - 40, f"Address: {order.address}")
    c.drawString(50, y - 60, f"Contact: {order.contact}")

    y -= 100
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Products")
    y -= 30

    c.setFont("Helvetica", 12)
    for item in order.order_items:
        c.drawString(50, y, f"Product: {item.product_name}")
        c.drawString(250, y, f"Quantity: {item.quantity}")
        c.drawString(400, y, f"Total Price: {item.total_price} USD")
        y -= 20

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Total Order Price: {order.total_order_price} USD")
    if order.discount > 0:
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Discount: {order.discount} USD")

    c.save()
    return send_file(pdf_path, as_attachment=True)

# -- PROFILE --

@app.route("/profile/<nickname>")
def profile(nickname):
    user = User.objects(nickname=nickname).first()
    if not user:
        return "User not found", 404

    image_url = url_for('get_image', file_id=user.profile_image_url) if user.profile_image_url else None

    return render_template('profile.html', user=user, image_url=image_url, layout=get_layout())


@app.route("/edit_profile/<nickname>", methods=["GET", "POST"])
def edit_profile(nickname):
    user = User.objects(nickname=nickname).first()
    if not user:
        return "User not found", 404

    form = EditProfileForm(obj=user)  # Inicjalizuj formularz z istniejącym użytkownikiem

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.country = form.country.data
        user.user_description = form.user_description.data

        file = request.files.get('profile_image')
        if file and file.filename:
            filename = secure_filename(file.filename)
            fs = current_app.fs
            file_id = fs.put(file, filename=filename)
            user.profile_image_url = str(file_id)

        try:
            user.save()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile', nickname=nickname))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')

    return render_template('edit_profile.html', form=form, user=user, layout=get_layout())


@app.route("/image/<file_id>")
def get_image(file_id):
    try:
        fs = current_app.fs
        # Pobierz plik z GridFS
        file = fs.get(file_id)
        return send_file(io.BytesIO(file.read()), mimetype='image/jpeg')
    except Exception as e:
        print(f"Error retrieving image: {str(e)}")
        return "Image not found", 404

if __name__ == '__main__':
    app.run(debug=True)
