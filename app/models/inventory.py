from app import db
from datetime import datetime
import json

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    items = db.relationship('InventoryItem', backref='item_category', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryItem(db.Model):
    __tablename__ = 'inventory_item'
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    reorder_threshold = db.Column(db.Integer)
    status = db.Column(db.String(20), default='in_stock')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Add type column for polymorphic identity
    type = db.Column(db.String(50))

    # Relationships
    creator = db.relationship('User', backref='created_items')

    __mapper_args__ = {
        'polymorphic_identity': 'inventory_item',
        'polymorphic_on': type
    }

class ComputerModel(db.Model):
    __tablename__ = 'computer_model'
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(64), nullable=False)
    model_name = db.Column(db.String(128), nullable=False)
    model_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CPU(db.Model):
    __tablename__ = 'cpu'
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    speed = db.Column(db.String(32))
    cores = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComputerSystem(InventoryItem):
    __tablename__ = 'computer_system'
    id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'), primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('computer_model.id'))
    cpu_id = db.Column(db.Integer, db.ForeignKey('cpu.id'))
    ram = db.Column(db.String(64))
    storage = db.Column(db.String(128))
    os = db.Column(db.String(50))
    cpu_benchmark = db.Column(db.Float)
    usb_ports_status = db.Column(db.String(20))
    usb_ports_notes = db.Column(db.Text)
    video_status = db.Column(db.String(20))
    video_notes = db.Column(db.Text)
    network_status = db.Column(db.String(20))
    network_notes = db.Column(db.Text)
    general_notes = db.Column(db.Text)
    tested_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    model = db.relationship('ComputerModel', backref='computers')
    cpu = db.relationship('CPU', backref='computers')
    tester = db.relationship('User', backref='tested_computers', foreign_keys=[tested_by])

    __mapper_args__ = {
        'polymorphic_identity': 'computer_system',
    }

class InventoryTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'))
    transaction_type = db.Column(db.String(20))  # check_in, check_out, update
    quantity = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    client_info = db.Column(db.JSON)

class BenchmarkResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('computer_system.id'))
    test_type = db.Column(db.String(64))
    score = db.Column(db.Float)
    details = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id')) 