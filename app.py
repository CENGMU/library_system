from flask import Flask
from config import Config
from extensions import db, login_manager
from blueprints import register_blueprints
from models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    register_blueprints(app)

    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", role="admin", email="admin@example.com")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Initialized admin account: admin / admin123")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
