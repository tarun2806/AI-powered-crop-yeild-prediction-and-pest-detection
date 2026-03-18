from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    farms = db.relationship('Farm', backref='owner', lazy=True)

class Farm(db.Model):
    __tablename__ = 'farms'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    total_area = db.Column(db.Float)
    soil_type = db.Column(db.String(50))
    crop_records = db.relationship('CropRecord', backref='farm', lazy=True)

class CropRecord(db.Model):
    __tablename__ = 'crop_records'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = db.Column(UUID(as_uuid=True), db.ForeignKey('farms.id'), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    planting_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='growing')

class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(UUID(as_uuid=True), db.ForeignKey('farms.id'), nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    ph_level = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    prediction_type = db.Column(db.String(20)) # 'yield' or 'pest'
    inputs = db.Column(db.JSON)
    result = db.Column(db.String(200))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
