from app import db
from datetime import datetime
import json
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from sqlalchemy import event
from app.utils.activity_logger import log_activity

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category_metadata = db.Column(db.JSON, nullable=True)  # Store additional data like full path
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    items = db.relationship('InventoryItem', 
                          backref='category',
                          primaryjoin="Category.id==foreign(InventoryItem.category_id)",
                          lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_full_path(self):
        """Get the full hierarchical path of the category"""
        path = [self.name]
        current = self
        while current.parent:
            current = current.parent
            path.append(current.name)
        return ' > '.join(reversed(path))

    def get_display_name(self):
        """Get indented name for dropdown display"""
        depth = 0
        current = self
        while current.parent:
            depth += 1
            current = current.parent
        return ('--' * depth) + self.name

    @staticmethod
    def get_ordered_categories():
        """Get categories in hierarchical order for dropdowns"""
        def build_hierarchy(parent_id=None, level=0):
            categories = []
            query = Category.query.filter_by(parent_id=parent_id).order_by(Category.name)
            
            for category in query.all():
                category.level = level  # Add level info for template
                categories.append(category)
                # Recursively get children
                categories.extend(build_hierarchy(category.id, level + 1))
            
            return categories
            
        return build_hierarchy()

item_tags = db.Table('item_tags',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)

system_tags = db.Table('system_tags',
    db.Column('system_id', db.Integer, db.ForeignKey('computer_systems.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False, default='#6c757d')  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tag {self.name}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quantity_changed = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    # Relationships
    item = db.relationship('InventoryItem', backref='transactions')
    user = db.relationship('User', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.transaction_type}: {self.quantity_changed}>'

class InventoryItem(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(50), unique=True)
    upc = db.Column(db.String(50), unique=True, nullable=True)
    barcode = db.Column(db.String(128), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=0)
    min_quantity = db.Column(db.Integer, default=0)
    reorder_threshold = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100), nullable=True)
    storage_location = db.Column(db.String(100), nullable=True)
    manufacturer = db.Column(db.String(128), nullable=True)
    mpn = db.Column(db.String(128), nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=True)
    sell_price = db.Column(db.Numeric(10, 2), nullable=True)
    purchase_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    status = db.Column('status', db.String(50), default='available')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator = db.relationship('User', backref='items_created')
    
    # Define the many-to-many relationship with Tag
    tags = db.relationship('Tag', 
                         secondary=item_tags,
                         lazy='joined')

    # Add relationship for purchase links
    purchase_links = db.relationship('PurchaseLink', back_populates='item', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<InventoryItem {self.name}>'

class CPU(db.Model):
    """Model for CPU information"""
    __tablename__ = 'cpu'

    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    speed = db.Column(db.String(32))
    cores = db.Column(db.Integer)
    benchmark = db.Column(db.Integer)

    def __repr__(self):
        return f'<CPU {self.manufacturer} {self.model}>'

class ComputerModel(db.Model):
    """Model for computer models"""
    __tablename__ = 'computer_model'

    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # desktop, laptop, server, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ComputerModel {self.manufacturer} {self.model_name}>'

class ComputerSystem(db.Model):
    """Model for computer systems"""
    __tablename__ = 'computer_systems'

    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(50), unique=True, nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('computer_model.id'))
    serial_tag = db.Column(db.String(100))
    status = db.Column(db.String(50), default='available')  # available, checked_out, maintenance, retired
    storage_location = db.Column(db.String(100))
    notes = db.Column(db.Text)
    cpu_id = db.Column(db.Integer, db.ForeignKey('cpu.id'))
    ram = db.Column(db.String(50))
    storage = db.Column(db.String(100))
    os = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Testing fields
    cpu_benchmark = db.Column(db.Float)
    usb_ports_status = db.Column(db.String(50))
    usb_ports_notes = db.Column(db.Text)
    video_status = db.Column(db.String(50))
    video_notes = db.Column(db.Text)
    network_status = db.Column(db.String(50))
    network_notes = db.Column(db.Text)
    general_notes = db.Column(db.Text)
    tested_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Mobile checkout fields
    checked_out_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    checked_out_at = db.Column(db.DateTime)
    checkout_reason = db.Column(db.String(100))
    checkout_notes = db.Column(db.Text)

    # Relationships
    model = relationship('ComputerModel', backref='systems')
    cpu = relationship('CPU', backref='systems')
    checked_out_by = relationship('User', 
                                foreign_keys=[checked_out_by_id],
                                backref='checked_out_systems')
    tags = db.relationship('Tag', secondary=system_tags, lazy='joined')
    tester = relationship('User', 
                         foreign_keys=[tested_by],
                         backref='tested_systems')
    creator = relationship('User',
                         foreign_keys=[creator_id],
                         backref='created_systems')

    def __repr__(self):
        return f'<ComputerSystem {self.tracking_id}>'

class BenchmarkResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('computer_systems.id'))
    test_type = db.Column(db.String(64))
    score = db.Column(db.Float)
    details = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id')) 

class WikiCategory(db.Model):
    __tablename__ = 'wiki_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pages = db.relationship('WikiPage', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<WikiCategory {self.name}>'

class WikiPage(db.Model):
    __tablename__ = 'wiki_page'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('wiki_category.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='wiki_pages')

    def __repr__(self):
        return f'<WikiPage {self.title}>'

    def can_edit(self, user):
        """Check if user can edit this page"""
        return user.is_admin or user.id == self.author_id

    def can_delete(self, user):
        """Check if user can delete this page"""
        return user.is_admin

# Add this after other association tables
roadmap_votes = db.Table('roadmap_votes',
    db.Column('item_id', db.Integer, db.ForeignKey('roadmap_items.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class RoadmapItem(db.Model):
    __tablename__ = 'roadmap_items'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Feature Request, Bug Report, Integration
    status = db.Column(db.String(20), default='open')  # open, in_progress, done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    submitter = db.relationship('User', backref='roadmap_items', foreign_keys=[submitter_id])
    voters = db.relationship('User', 
                           secondary=roadmap_votes,
                           lazy='joined',
                           backref=db.backref('voted_items', lazy=True))
    
    def __repr__(self):
        return f'<RoadmapItem {self.title}>'

    @property
    def votes(self):
        return len(self.voters)

    def has_user_voted(self, user):
        return user in self.voters

    @property
    def status_class(self):
        return {
            'open': 'bg-primary',
            'in_progress': 'bg-warning',
            'done': 'bg-success'
        }.get(self.status, 'bg-secondary')

    def to_dict(self, current_user=None):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'votes': self.votes,
            'created_at': self.created_at.isoformat(),
            'submitter': self.submitter.username,
            'has_voted': current_user in self.voters if current_user and current_user.is_authenticated else False
        }

class PurchaseLink(db.Model):
    """Model for storing additional purchase URLs for inventory items."""
    __tablename__ = 'purchase_links'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(100))  # Optional title/description for the link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    item = db.relationship('InventoryItem', back_populates='purchase_links')
    creator = db.relationship('User')
 