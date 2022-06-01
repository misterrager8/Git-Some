from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

db = SQLAlchemy()
pymysql.install_as_MySQLdb()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    with app.app_context():
        from ProjectManager.views.projects import projects
        from ProjectManager.views.todos import todos

        db.create_all()

        app.register_blueprint(projects)
        app.register_blueprint(todos)

        return app
