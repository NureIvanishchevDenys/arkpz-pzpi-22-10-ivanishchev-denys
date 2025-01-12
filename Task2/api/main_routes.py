from flask import Blueprint, request, jsonify
from extensions import db
from models import MonitoringStation, Measurement, Alert, WaterQualityParameter, User
from datetime import datetime

api_blueprint = Blueprint('api', __name__)

# CRUD для MonitoringStations
@api_blueprint.route('/stations', methods=['GET'])
def get_stations():
    stations = MonitoringStation.query.all()
    return jsonify([{
        'station_id': s.station_id,
        'name': s.name,
        'location': s.location,
        'latitude': float(s.latitude) if s.latitude else None,
        'longitude': float(s.longitude) if s.longitude else None,
        'created_at': s.created_at
    } for s in stations])

@api_blueprint.route('/stations', methods=['POST'])
def create_station():
    data = request.json
    station = MonitoringStation(
        name=data['name'],
        location=data['location'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    db.session.add(station)
    db.session.commit()
    return jsonify({'message': 'Station created successfully'}), 201

@api_blueprint.route('/stations/<int:station_id>', methods=['DELETE'])
def delete_station(station_id):
    station = MonitoringStation.query.get(station_id)
    if not station:
        return jsonify({'message': 'Station not found'}), 404
    db.session.delete(station)
    db.session.commit()
    return jsonify({'message': 'Station deleted successfully'})

# Отримати всі вимірювання
@api_blueprint.route('/measurements', methods=['GET'])
def get_measurements():
    measurements = Measurement.query.all()
    return jsonify([{
        'measurement_id': m.measurement_id,
        'station_id': m.station_id,
        'parameter_id': m.parameter_id,
        'value': float(m.value),
        'measured_at': m.measured_at
    } for m in measurements])

@api_blueprint.route('/measurements', methods=['POST'])
def create_measurement():
    data = request.json
    
    # Перевірка вхідних даних
    required_fields = ['station_id', 'parameter_id', 'value']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing field: {field}'}), 400

    try:
        # Додаємо вимірювання
        measurement = Measurement(
            station_id=data['station_id'],
            parameter_id=data['parameter_id'],
            value=data['value']
        )
        db.session.add(measurement)
        db.session.commit()
        return jsonify({'message': 'Measurement added successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error adding measurement', 'error': str(e)}), 500

# Видалити вимірювання
@api_blueprint.route('/measurements/<int:measurement_id>', methods=['DELETE'])
def delete_measurement(measurement_id):
    measurement = Measurement.query.get(measurement_id)
    if not measurement:
        return jsonify({'message': 'Measurement not found'}), 404
    db.session.delete(measurement)
    db.session.commit()
    return jsonify({'message': 'Measurement deleted successfully'})

# Отримати всі сповіщення
@api_blueprint.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = Alert.query.all()
    return jsonify([{
        'alert_id': a.alert_id,
        'station_id': a.station_id,
        'parameter_id': a.parameter_id,
        'value': float(a.value),
        'message': a.message,
        'alert_time': a.alert_time
    } for a in alerts])

# Додати нове сповіщення
@api_blueprint.route('/alerts', methods=['POST'])
def create_alert():
    data = request.json
    alert = Alert(
        station_id=data['station_id'],
        parameter_id=data['parameter_id'],
        value=data['value'],
        message=data['message']
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify({'message': 'Alert created successfully'}), 201

# Отримати всіх користувачів
@api_blueprint.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'user_id': u.user_id,
        'name': u.name,
        'email': u.email,
        'role': u.role,
        'alert_id': u.alert_id,
        'created_at': u.created_at
    } for u in users])

# Додати нового користувача
@api_blueprint.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=data['password_hash'],
        role=data.get('role', 'analyst'),
        alert_id=data['alert_id']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# Отримати всі параметри
@api_blueprint.route('/parameters', methods=['GET'])
def get_parameters():
    parameters = WaterQualityParameter.query.all()
    return jsonify([{
        'parameter_id': p.parameter_id,
        'name': p.name,
        'unit': p.unit,
        'safe_min': float(p.safe_min) if p.safe_min else None,
        'safe_max': float(p.safe_max) if p.safe_max else None
    } for p in parameters])

# Додати новий параметр
@api_blueprint.route('/parameters', methods=['POST'])
def create_parameter():
    data = request.json
    parameter = WaterQualityParameter(
        name=data['name'],
        unit=data['unit'],
        safe_min=data.get('safe_min'),
        safe_max=data.get('safe_max')
    )
    db.session.add(parameter)
    db.session.commit()
    return jsonify({'message': 'Parameter created successfully'}), 201

@api_blueprint.route('/report', methods=['GET'])
def generate_report():
    # Отримуємо параметри з запиту
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    station_id = request.args.get('station_id')
    
    # Базовий запит до таблиці Measurements
    query = db.session.query(
        Measurement.measurement_id,
        MonitoringStation.name.label('station_name'),
        MonitoringStation.location,
        WaterQualityParameter.name.label('parameter_name'),
        Measurement.value,
        Measurement.measured_at
    ).join(
        MonitoringStation, Measurement.station_id == MonitoringStation.station_id
    ).join(
        WaterQualityParameter, Measurement.parameter_id == WaterQualityParameter.parameter_id
    )
    
    # Фільтруємо за датами
    if start_date:
        query = query.filter(Measurement.measured_at >= start_date)
    if end_date:
        query = query.filter(Measurement.measured_at <= end_date)
    
    # Фільтруємо за станцією (якщо вказана)
    if station_id:
        query = query.filter(Measurement.station_id == station_id)
    
    # Виконуємо запит
    results = query.all()
    
    # Формуємо звіт
    report = []
    for row in results:
        report.append({
            'measurement_id': row.measurement_id,
            'station_name': row.station_name,
            'location': row.location,
            'parameter_name': row.parameter_name,
            'value': float(row.value),
            'measured_at': row.measured_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({'report': report}), 200
