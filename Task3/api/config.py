class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:oblepiha@localhost:3306/WaterQualityMonitoring'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
