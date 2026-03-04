from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Factory function pour créer l'app Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialiser la base de données
    db.init_app(app)
    
    # Initialiser LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Enregistrer les blueprints
    from app.routes import main_bp, charges_bp, assemblees_bp, travaux_bp, auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(charges_bp)
    app.register_blueprint(assemblees_bp)
    app.register_blueprint(travaux_bp)
    
    # Créer les tables
    with app.app_context():
        db.create_all()
        
        # Créer un utilisateur admin par défaut
        from app.models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@copropriete.local',
                nom_complet='Administrateur',
                role='admin',
                actif=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    return app
