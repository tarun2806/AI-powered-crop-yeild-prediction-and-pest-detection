from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from .models import User, Farm, CropRecord, SensorData, PredictionHistory

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6))

class FarmSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Farm
        load_instance = True

class YieldPredictionSchema(ma.Schema):
    district = fields.String(required=True)
    area = fields.Float(required=True)
    crop = fields.String(required=True)
    soil_type = fields.String(required=True)
    temperature = fields.Float()
    humidity = fields.Float()
    soil_moisture = fields.Float()

class SensorDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SensorData
        load_instance = True
    farm_id = fields.UUID(required=True)
