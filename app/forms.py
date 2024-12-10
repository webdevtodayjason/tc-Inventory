from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, FloatField, TextAreaField, DecimalField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp, ValidationError, URL
from app.models.inventory import ComputerModel, Category, CPU, Tag

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
    ('server', 'Server'),
    ('workstation', 'Workstation'),
    ('mini-pc', 'Mini PC'),
    ('all-in-one', 'All-in-One'),
    ('tablet', 'Tablet'),
    ('thin-client', 'Thin Client'),
    ('gaming', 'Gaming PC'),
    ('nas', 'NAS'),
    ('custom', 'Custom Build')
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
    
    # Testing fields
    cpu_benchmark = FloatField('CPU Benchmark Score', validators=[Optional()])
    usb_ports_status = SelectField('USB Ports Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ])
    usb_ports_notes = TextAreaField('USB Ports Notes')
    video_status = SelectField('Video Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ])
    video_notes = TextAreaField('Video Notes')
    network_status = SelectField('Network Status', choices=[
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED')
    ])
    network_notes = TextAreaField('Network Notes')
    general_notes = TextAreaField('General Notes')

class ItemForm(FlaskForm):
    type = SelectField('Type', choices=[
        ('general', 'General Item'),
        ('computer', 'Computer System')
    ], validators=[DataRequired()])
    
    # General Item Fields
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
    
    # Computer System Fields
    model_id = SelectField('Computer Model', coerce=int, validators=[Optional()])
    cpu_id = SelectField('CPU', coerce=int, validators=[Optional()])
    ram = StringField('RAM', validators=[Optional()])
    storage = StringField('Storage', validators=[Optional()])
    os = SelectField('Operating System', 
                    choices=[
                        ('Windows 10 Pro', 'Windows 10 Pro'),
                        ('Windows 11 Pro', 'Windows 11 Pro'),
                        ('Microsoft Server 2022', 'Microsoft Server 2022'),
                        ('Linux', 'Linux')
                    ],
                    validators=[Optional()])
    
    # Computer Testing Fields
    cpu_benchmark = FloatField('CPU Benchmark Score', validators=[Optional()])
    usb_ports_status = SelectField('USB Ports Status',
                                choices=[('PASSED', 'PASSED'), ('FAILED', 'FAILED')],
                                validators=[Optional()])
    usb_ports_notes = TextAreaField('USB Ports Notes', validators=[Optional()])
    video_status = SelectField('Video Status',
                            choices=[('PASSED', 'PASSED'), ('FAILED', 'FAILED')],
                            validators=[Optional()])
    video_notes = TextAreaField('Video Notes', validators=[Optional()])
    network_status = SelectField('Network Status',
                              choices=[('PASSED', 'PASSED'), ('FAILED', 'FAILED')],
                              validators=[Optional()])
    network_notes = TextAreaField('Network Notes', validators=[Optional()])
    general_notes = TextAreaField('General Notes', validators=[Optional()])
    
    def validate(self):
        if not super().validate():
            return False
            
        if self.type.data == 'computer':
            # Validate computer-specific fields
            if not self.model_id.data:
                self.model_id.errors.append('Computer model is required')
                return False
            if not self.cpu_id.data:
                self.cpu_id.errors.append('CPU is required')
                return False
            if not self.ram.data:
                self.ram.errors.append('RAM is required')
                return False
            if not self.storage.data:
                self.storage.errors.append('Storage is required')
                return False
            if not self.os.data:
                self.os.errors.append('Operating system is required')
                return False
            # Validate testing fields
            if not self.usb_ports_status.data:
                self.usb_ports_status.errors.append('USB ports test status is required')
                return False
            if not self.video_status.data:
                self.video_status.errors.append('Video test status is required')
                return False
            if not self.network_status.data:
                self.network_status.errors.append('Network test status is required')
                return False
        else:
            # Validate general item fields
            if not self.name.data:
                self.name.errors.append('Name is required')
                return False
            if not self.category.data or self.category.data == 0:
                self.category.errors.append('Category is required')
                return False
            if not self.quantity.data or self.quantity.data < 0:
                self.quantity.errors.append('Quantity must be 0 or greater')
                return False
        
        return True
    
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        # Populate category choices
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
        
        # Populate model choices
        self.model_id.choices = [(m.id, f"{m.manufacturer} {m.model_name}") 
                                for m in ComputerModel.query.order_by(ComputerModel.manufacturer).all()]
        
        # Populate CPU choices
        self.cpu_id.choices = [(c.id, f"{c.manufacturer} {c.model} ({c.speed})") 
                              for c in CPU.query.order_by(CPU.manufacturer, CPU.model).all()]
        
        # Add tag choices
        self.tags.choices = [(t.id, t.name) for t in Tag.query.order_by(Tag.name).all()]