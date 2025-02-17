from flask import Flask
from extensions import db, migrate
from config import Config
from main_routes import api_blueprint

app = Flask(__name__)
app.config.from_object(Config)



db.init_app(app)
migrate.init_app(app, db)

# Реєстрація маршрутів
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
