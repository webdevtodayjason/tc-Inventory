from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, FloatField, TextAreaField, DecimalField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp, ValidationError, URL, EqualTo
from app.models.inventory import ComputerModel, Category, CPU, Tag, WikiCategory, WikiPage

# Define choices as constants for easy maintenance
MANUFACTURER_CHOICES = [
    ('Dell', 'Dell'),
    ('HP', 'HP'),
    ('Lenovo', 'Lenovo'),
    ('Apple', 'Apple'),
    ('Custom', 'Custom Build'),
    ('Acer', 'Acer'),
    ('ASUS', 'ASUS'),
    ('Microsoft', 'Microsoft'),
    ('Toshiba', 'Toshiba'),
    ('MSI', 'MSI'),
    ('Razer', 'Razer'),
    ('Samsung', 'Samsung'),
    ('LG', 'LG'),
    ('Intel', 'Intel'),
    ('AMD', 'AMD'),
    ('Other', 'Other')
]

COMPUTER_TYPES = [
    ('desktop', 'Desktop'),
    ('laptop', 'Laptop'),
    ('workstation', 'Workstation'),
    ('server', 'Server'),
    ('tablet', 'Tablet')
]

class ComputerModelForm(FlaskForm):
    manufacturer = SelectField('Manufacturer', 
                             choices=MANUFACTURER_CHOICES, 
                             validators=[DataRequired()])
    
    model_name = StringField('Model Name', 
                           validators=[DataRequired(), Length(min=2, max=128)])
    
    model_type = SelectField('Type', 
                           choices=COMPUTER_TYPES, 
                           validators=[DataRequired()])

    def validate_model_name(self, field):
        exists = ComputerModel.query.filter_by(
            manufacturer=self.manufacturer.data,
            model_name=field.data
        ).first()
        if exists:
            raise ValidationError('This model already exists for this manufacturer')

class CPUForm(FlaskForm):
    manufacturer = SelectField('Manufacturer', choices=[
        ('Intel', 'Intel'),
        ('AMD', 'AMD')
    ], validators=[DataRequired()])
    model = StringField('Model', validators=[
        DataRequired(),
        Length(min=2, max=128),
        Regexp(r'^[a-zA-Z0-9\-\s]+$', message="Model name can only contain letters, numbers, spaces, and hyphens")
    ])
    speed = StringField('Speed', validators=[
        DataRequired(),
        Regexp(r'^\d+(\.\d+)?\s*(GHz|MHz)$', message="Speed must be in format: 3.6 GHz or 3600 MHz")
    ])
    cores = IntegerField('Cores', validators=[
        DataRequired(),
        NumberRange(min=1, max=128, message="Core count must be between 1 and 128")
    ])

    def validate_speed(self, field):
        # Convert all speeds to GHz for consistency
        value = field.data.lower()
        if 'mhz' in value:
            speed = float(value.replace('mhz', '').strip()) / 1000
            field.data = f"{speed:.2f} GHz"

class ComputerSystemForm(FlaskForm):
    tracking_id = StringField('Tracking ID', validators=[Optional()])
    serial_tag = StringField('Serial/Service Tag', validators=[Optional(), Length(max=100)])
    model_id = SelectField('Computer Model', coerce=int, validators=[DataRequired()])
    cpu_id = SelectField('CPU', coerce=int, validators=[DataRequired()])
    ram = StringField('RAM', validators=[DataRequired()])
    storage = StringField('Storage', validators=[DataRequired()])
    os = SelectField('Operating System', choices=[
        ('Windows 10 Pro', 'Windows 10 Pro'),
        ('Windows 11 Pro', 'Windows 11 Pro'),
        ('Microsoft Server 2022', 'Microsoft Server 2022'),
        ('Linux', 'Linux')
    ], validators=[DataRequired()])
    storage_location = StringField('Storage Location', validators=[Optional(), Length(max=64)])
    
    # Testing fields
    cpu_benchmark = FloatField('CPU Benchmark Score', validators=[Optional()])
    usb_ports_status = SelectField('USB Ports Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ], validators=[DataRequired()])
    usb_ports_notes = TextAreaField('USB Ports Notes')
    video_status = SelectField('Video Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ], validators=[DataRequired()])
    video_notes = TextAreaField('Video Notes')
    network_status = SelectField('Network Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ], validators=[DataRequired()])
    network_notes = TextAreaField('Network Notes')
    general_notes = TextAreaField('General Notes')
    
    def __init__(self, *args, **kwargs):
        super(ComputerSystemForm, self).__init__(*args, **kwargs)
        # Populate model choices
        self.model_id.choices = [(m.id, f"{m.manufacturer} {m.model_name}") 
                                for m in ComputerModel.query.order_by(ComputerModel.manufacturer).all()]
        
        # Populate CPU choices
        self.cpu_id.choices = [(c.id, f"{c.manufacturer} {c.model} ({c.speed})") 
                              for c in CPU.query.order_by(CPU.manufacturer, CPU.model).all()]

class GeneralItemForm(FlaskForm):
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=128)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)], default=1)
    reorder_threshold = IntegerField('Reorder Threshold', validators=[Optional(), NumberRange(min=0)], default=5)
    storage_location = StringField('Storage Location', validators=[Optional(), Length(max=64)])
    
    # Barcode Fields
    barcode = StringField('Barcode', validators=[Optional(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional()])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=128)])
    mpn = StringField('Manufacturer Part Number (MPN)', validators=[Optional(), Length(max=128)])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    
    # Cost Fields
    cost = DecimalField('Cost', validators=[Optional(), NumberRange(min=0)], places=2)
    sell_price = DecimalField('Sell Price', validators=[Optional(), NumberRange(min=0)], places=2)
    purchase_url = StringField('Purchase URL', validators=[Optional(), URL()])
    
    # Tags
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(GeneralItemForm, self).__init__(*args, **kwargs)
        # Populate category choices
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
        # Add tag choices
        self.tags.choices = [(t.id, t.name) for t in Tag.query.order_by(Tag.name).all()]

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'.*[a-z].*', message='Password must contain at least one lowercase letter'),
        Regexp(r'.*[A-Z].*', message='Password must contain at least one uppercase letter'),
        Regexp(r'.*[0-9].*', message='Password must contain at least one number'),
        Regexp(r'.*[!@#$%^&*(),.?":{}|<>].*', message='Password must contain at least one special character')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])

class WikiCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])

class WikiPageForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(WikiPageForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [
            (c.id, c.name) for c in WikiCategory.query.order_by(WikiCategory.name).all()
        ]