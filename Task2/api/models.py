from extensions import db
from datetime import datetime, timezone

class MonitoringStation(db.Model):
    __tablename__ = 'MonitoringStations'
    station_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(9, 6), nullable=True)
    longitude = db.Column(db.Numeric(9, 6), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Measurement(db.Model):
    __tablename__ = 'Measurements'
    measurement_id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('MonitoringStations.station_id'), nullable=False)
    parameter_id = db.Column(db.Integer, db.ForeignKey('WaterQualityParameters.parameter_id'), nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    measured_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Alert(db.Model):
    __tablename__ = 'Alerts'
    alert_id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('MonitoringStations.station_id'), nullable=False)
    parameter_id = db.Column(db.Integer, db.ForeignKey('WaterQualityParameters.parameter_id'), nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class WaterQualityParameter(db.Model):
    __tablename__ = 'WaterQualityParameters'
    parameter_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    safe_min = db.Column(db.Numeric(10, 2), nullable=True)
    safe_max = db.Column(db.Numeric(10, 2), nullable=True)

class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'analyst', 'operator'), default='analyst')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    alert_id = db.Column(db.Integer, db.ForeignKey('Alerts.alert_id'), nullable=False)
