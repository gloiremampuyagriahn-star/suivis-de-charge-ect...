from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """Modèle pour les utilisateurs du système"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nom_complet = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='gestionnaire')  # admin, gestionnaire
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hacher et stocker le mot de passe"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Vérifier si le mot de passe est correct"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Proprietaire(db.Model):
    """Modèle pour les propriétaires"""
    __tablename__ = 'proprietaires'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    numero_lot = db.Column(db.String(20), unique=True, nullable=False)
    pourcentage_part = db.Column(db.Float, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)
    
    # Relations
    charges = db.relationship('Charge', backref='proprietaire', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='proprietaire', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Proprietaire {self.nom} {self.prenom}>'
    
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

class Charge(db.Model):
    """Modèle pour les charges (frais de copropriété)"""
    __tablename__ = 'charges'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey('proprietaires.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    type_charge = db.Column(db.String(50), nullable=False)  # Ex: chauffage, eau, copropriété...
    periode = db.Column(db.String(20), nullable=False)  # Ex: 2024-Q1
    date_emission = db.Column(db.DateTime, default=datetime.utcnow)
    date_echéance = db.Column(db.DateTime, nullable=False)
    date_paiement = db.Column(db.DateTime)
    statut = db.Column(db.String(20), default='en attente')  # en attente, payée, en retard
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Charge {self.numero}>'
    
    def est_payee(self):
        return self.statut == 'payée'
    
    def est_en_retard(self):
        if self.date_paiement is None:
            from datetime import datetime
            return datetime.utcnow() > self.date_échéance

class AssembléeGénérale(db.Model):
    """Modèle pour les assemblées générales"""
    __tablename__ = 'assemblees_generales'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    date_seance = db.Column(db.DateTime, nullable=False)
    lieu = db.Column(db.String(200))
    ordre_du_jour = db.Column(db.Text, nullable=False)
    proces_verbal = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='programmée')  # programmée, effectuée
    quorum = db.Column(db.Float)  # pourcentage de participation
    
    # Relations
    votes = db.relationship('Vote', backref='assemblee', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AssembléeGénérale {self.titre}>'
    
    def nombre_participants(self):
        return len(set(vote.proprietaire_id for vote in self.votes))

class Vote(db.Model):
    """Modèle pour les votes lors des assemblées générales"""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    assemblee_id = db.Column(db.Integer, db.ForeignKey('assemblees_generales.id'), nullable=False)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey('proprietaires.id'), nullable=False)
    decision = db.Column(db.String(50), nullable=False)  # pour, contre, abstention
    date_vote = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vote {self.proprietaire_id} - {self.decision}>'

class Travaux(db.Model):
    """Modèle pour les travaux de maintenance/rénovation"""
    __tablename__ = 'travaux'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type_travaux = db.Column(db.String(50), nullable=False)  # maintenance, rénovation, urgence...
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin_prevue = db.Column(db.DateTime)
    date_fin_reelle = db.Column(db.DateTime)
    statut = db.Column(db.String(20), default='planifié')  # planifié, en cours, terminé, suspendu
    budget_previsionnel = db.Column(db.Float)
    budget_reel = db.Column(db.Float)
    responsable = db.Column(db.String(100))
    entreprise = db.Column(db.String(150))
    contact_entreprise = db.Column(db.String(100))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    appel_offres = db.Column(db.Text)
    devis = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Travaux {self.titre}>'
    
    def pourcentage_avancement(self):
        if self.statut == 'terminé':
            return 100
        elif self.statut == 'en cours' and self.date_debut and self.date_fin_prevue:
            from datetime import datetime
            total_jours = (self.date_fin_prevue - self.date_debut).days
            jours_ecoules = (datetime.utcnow() - self.date_debut).days
            if total_jours > 0:
                return min((jours_ecoules / total_jours) * 100, 99)
        elif self.statut == 'planifié':
            return 0
        return 50
