from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'rental-platform-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    from extensions import db, login_manager, bcrypt
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    with app.app_context():
        import models  # registers all models with db
        db.create_all()

    from routes.auth import auth
    from routes.main import main
    from routes.owner import owner
    from routes.admin import admin
    from routes.api import api

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(owner)
    app.register_blueprint(admin)
    app.register_blueprint(api)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
