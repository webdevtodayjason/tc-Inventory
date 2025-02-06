from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, FloatField, TextAreaField, DecimalField, SelectMultipleField, PasswordField, BooleanField
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
    ('tablet', 'Tablet'),
    ('surface', 'Surface')
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
        Regexp(r'^\d+(\.\d+)?\s*(GHz|MHz|ghz|mhz)$', message="Speed must be in format: 3.5 GHz or 3500 MHz")
    ])
    cores = IntegerField('Cores', validators=[
        DataRequired(),
        NumberRange(min=1, max=128, message="Core count must be between 1 and 128")
    ])
    benchmark = IntegerField('Benchmark Score', validators=[
        Optional(),
        NumberRange(min=0, message="Benchmark score must be a positive number")
    ])

    def validate_speed(self, field):
        """Validate and format the speed value as a string"""
        try:
            # Convert input to lowercase for consistent processing
            value = field.data.lower().strip()
            
            # Extract numeric part and unit
            import re
            match = re.match(r'(\d+(?:\.\d+)?)\s*(ghz|mhz)', value)
            if not match:
                raise ValidationError("Invalid speed format")
                
            number, unit = match.groups()
            
            # Format the speed consistently
            if unit == 'mhz':
                # Convert MHz to GHz for display
                speed_value = float(number) / 1000
                field.data = f"{speed_value:.2f} GHz"
            else:
                # Keep GHz as is, but format consistently
                field.data = f"{float(number):.2f} GHz"
            
        except (ValueError, AttributeError) as e:
            raise ValidationError('Invalid speed value')

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
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])
    
    # Testing fields
    cpu_benchmark = FloatField('CPU Benchmark Score', validators=[Optional()])
    usb_ports_status = SelectField('USB Ports Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ], validators=[DataRequired()])
    usb_ports_notes = TextAreaField('USB Ports Notes', validators=[Optional()])
    video_status = SelectField('Video Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ], validators=[DataRequired()])
    video_notes = TextAreaField('Video Notes', validators=[Optional()])
    network_status = SelectField('Network Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ], validators=[DataRequired()])
    network_notes = TextAreaField('Network Notes', validators=[Optional()])
    general_notes = TextAreaField('General Notes', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(ComputerSystemForm, self).__init__(*args, **kwargs)
        # Populate model choices
        self.model_id.choices = [(m.id, f"{m.manufacturer} {m.model_name}") 
                                for m in ComputerModel.query.order_by(ComputerModel.manufacturer).all()]
        
        # Populate CPU choices
        self.cpu_id.choices = [(c.id, f"{c.manufacturer} {c.model} ({c.speed})") 
                              for c in CPU.query.order_by(CPU.manufacturer, CPU.model).all()]
        
        # Populate tag choices
        self.tags.choices = [(t.id, t.name) 
                            for t in Tag.query.order_by(Tag.name).all()]

class GeneralItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    quantity = IntegerField('Quantity', default=0)
    reorder_threshold = IntegerField('Minimum Quantity (Reorder Point)', default=0)
    location = StringField('Location', validators=[Length(max=100)])
    storage_location = StringField('Storage Location', validators=[Length(max=100)])
    manufacturer = StringField('Manufacturer', validators=[Length(max=128)])
    mpn = StringField('Manufacturer Part Number', validators=[Length(max=128)])
    barcode = StringField('Barcode', validators=[Length(max=128)])
    upc = StringField('UPC', validators=[Length(max=50)])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    cost = DecimalField('Cost', places=2, validators=[Optional()])
    sell_price = DecimalField('Sell Price', places=2, validators=[Optional()])
    purchase_url = StringField('Purchase URL', validators=[Optional(), URL()])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])
    min_quantity = IntegerField('Minimum Quantity', default=0)

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

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    category_type = StringField('Category Type', validators=[DataRequired()])
    parent_id = SelectField('Parent Category', 
                          coerce=lambda x: int(x) if x else None,
                          choices=[])

    def validate_parent_id(form, field):
        if form.category_type.data == 'child' and not field.data:
            raise ValidationError('Please select a valid parent category.')

class InventoryItemForm(GeneralItemForm):
    """Form for creating and editing inventory items with purchase links support."""
    pass