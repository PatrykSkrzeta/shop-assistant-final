from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, SelectField,FieldList,FormField, FileField
from wtforms.validators import DataRequired, NumberRange, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()], render_kw={"class": "form-control logininput", "placeholder": "Enter email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "form-control logininput", "placeholder": "Password", "autocomplete": "off"})
    submit = SubmitField('Submit', render_kw={"class": "btn btn-primary"})

class VerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter verification code"})
    submit = SubmitField('Verify', render_kw={"class": "btn btn-primary"})

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Internet', 'Internet'), ('Hardware', 'Hardware'), ('Coding', 'Coding'), ('Software', 'Software'), ('Gaming', 'Gaming')], validators=[DataRequired()])
    product_type = StringField('Type', validators=[DataRequired()])
    value = IntegerField('Value', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Add')


class OrderItemForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    total_price = FloatField('Total Price', validators=[DataRequired(), NumberRange(min=0.01)])

class OrderForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    pesel = StringField('PESEL', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    order_items = FieldList(FormField(OrderItemForm), min_entries=1)
    total_order_price = FloatField('Total Order Price', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Place Order')
    add_item = SubmitField('Add Item')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    country = StringField('Country')
    user_description = StringField('Description')
    profile_image = FileField('Profile Image')
    submit = SubmitField('Update')