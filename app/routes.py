from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from app import db
from app.models import User, Proprietaire, Charge, AssembléeGénérale, Vote, Travaux
from datetime import datetime, timedelta
import math

# Créer les blueprints
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
charges_bp = Blueprint('charges', __name__, url_prefix='/charges')
assemblees_bp = Blueprint('assemblees', __name__, url_prefix='/assemblees')
travaux_bp = Blueprint('travaux', __name__, url_prefix='/travaux')

# ==================== ROUTES D'AUTHENTIFICATION ====================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.actif:
            flash('Ce compte a été désactivé', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_has_allowed_host_and_scheme(next_page):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))

def url_has_allowed_host_and_scheme(url):
    """Vérifier si l'URL est sûre"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.scheme == '' and parsed.netloc == ''

# ==================== ROUTES PRINCIPALES ====================

@main_bp.route('/')
@login_required
def index():
    """Page d'accueil avec tableaux de bord"""
    stats = {
        'proprietaires': Proprietaire.query.count(),
        'charges_en_retard': Charge.query.filter_by(statut='en retard').count(),
        'travaux_en_cours': Travaux.query.filter_by(statut='en cours').count(),
        'assemblees_a_venir': AssembléeGénérale.query.filter(
            AssembléeGénérale.date_seance > datetime.utcnow(),
            AssembléeGénérale.statut == 'programmée'
        ).count()
    }
    
    charges_recentes = Charge.query.order_by(Charge.date_emission.desc()).limit(5).all()
    travaux_recents = Travaux.query.order_by(Travaux.date_creation.desc()).limit(5).all()
    
    # Calcul du montant collecté ce mois (charges payées)
    debut_mois = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    fin_mois = (debut_mois + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    montant_collecte = db.session.query(db.func.sum(Charge.montant)).filter(
        Charge.date_paiement.isnot(None),
        Charge.date_paiement >= debut_mois,
        Charge.date_paiement <= fin_mois,
        Charge.statut == 'payée'
    ).scalar() or 0
    
    # Statistiques de charges supplémentaires
    montant_total_attendu = db.session.query(db.func.sum(Charge.montant)).filter(
        Charge.date_echéance >= debut_mois,
        Charge.date_echéance <= fin_mois
    ).scalar() or 0
    
    montant_en_attente = db.session.query(db.func.sum(Charge.montant)).filter(
        Charge.statut.in_(['en attente', 'en retard']),
        Charge.date_echéance >= debut_mois,
        Charge.date_echéance <= fin_mois
    ).scalar() or 0
    
    taux_recouvrement = (montant_collecte / montant_total_attendu * 100) if montant_total_attendu > 0 else 0
    
    return render_template('index.html', 
                         stats=stats, 
                         charges_recentes=charges_recentes,
                         travaux_recents=travaux_recents,
                         montant_collecte=montant_collecte,
                         montant_total_attendu=montant_total_attendu,
                         montant_en_attente=montant_en_attente,
                         taux_recouvrement=taux_recouvrement)

@main_bp.route('/proprietaires')
@login_required
def proprietaires():
    """Lister tous les propriétaires"""
    page = request.args.get('page', 1, type=int)
    proprietaires = Proprietaire.query.paginate(page=page, per_page=20)
    return render_template('proprietaires.html', proprietaires=proprietaires)

@main_bp.route('/proprietaire/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_proprietaire():
    """Ajouter un nouveau propriétaire"""
    if request.method == 'POST':
        try:
            proprietaire = Proprietaire(
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                email=request.form['email'],
                telephone=request.form.get('telephone', ''),
                numero_lot=request.form['numero_lot'],
                pourcentage_part=float(request.form['pourcentage_part'])
            )
            db.session.add(proprietaire)
            db.session.commit()
            flash(f'Propriétaire {proprietaire.nom_complet()} ajouté avec succès', 'success')
            return redirect(url_for('main.proprietaires'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'error')
    
    return render_template('ajouter_proprietaire.html')

@main_bp.route('/proprietaire/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_proprietaire(id):
    """Modifier un propriétaire"""
    proprietaire = Proprietaire.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            proprietaire.nom = request.form['nom']
            proprietaire.prenom = request.form['prenom']
            proprietaire.email = request.form['email']
            proprietaire.telephone = request.form.get('telephone', '')
            proprietaire.numero_lot = request.form['numero_lot']
            proprietaire.pourcentage_part = float(request.form['pourcentage_part'])
            proprietaire.actif = request.form.get('actif') == 'on'
            
            db.session.commit()
            flash('Propriétaire modifié avec succès', 'success')
            return redirect(url_for('main.proprietaires'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('modifier_proprietaire.html', proprietaire=proprietaire)

@main_bp.route('/proprietaire/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer_proprietaire(id):
    """Supprimer un propriétaire"""
    proprietaire = Proprietaire.query.get_or_404(id)
    try:
        db.session.delete(proprietaire)
        db.session.commit()
        flash('Propriétaire supprimé avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('main.proprietaires'))

# ==================== ROUTES CHARGES ====================

@charges_bp.route('/')
@login_required
def liste_charges():
    """Lister toutes les charges"""
    page = request.args.get('page', 1, type=int)
    filtre_statut = request.args.get('statut', '')
    filtre_type = request.args.get('type', '')
    
    query = Charge.query
    if filtre_statut:
        query = query.filter_by(statut=filtre_statut)
    if filtre_type:
        query = query.filter_by(type_charge=filtre_type)
    
    charges = query.order_by(Charge.date_emission.desc()).paginate(page=page, per_page=20)
    types_charge = db.session.query(Charge.type_charge).distinct().all()
    
    return render_template('charges.html', charges=charges, types_charge=types_charge,
                         filtre_statut=filtre_statut, filtre_type=filtre_type)

@charges_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_charge():
    """Créer une nouvelle charge"""
    proprietaires = Proprietaire.query.filter_by(actif=True).all()
    
    if request.method == 'POST':
        try:
            charge = Charge(
                numero=request.form['numero'],
                proprietaire_id=int(request.form['proprietaire_id']),
                montant=float(request.form['montant']),
                type_charge=request.form['type_charge'],
                periode=request.form['periode'],
                date_echéance=datetime.strptime(request.form['date_echeance'], '%Y-%m-%d'),
                statut=request.form.get('statut', 'en attente'),
                notes=request.form.get('notes', '')
            )
            
            if request.form.get('date_paiement'):
                charge.date_paiement = datetime.strptime(request.form['date_paiement'], '%Y-%m-%d')
                if charge.date_paiement:
                    charge.statut = 'payée'
            
            db.session.add(charge)
            db.session.commit()
            flash('Charge créée avec succès', 'success')
            return redirect(url_for('charges.liste_charges'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création: {str(e)}', 'error')
    
    return render_template('ajouter_charge.html', proprietaires=proprietaires)

@charges_bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_charge(id):
    """Modifier une charge"""
    charge = Charge.query.get_or_404(id)
    proprietaires = Proprietaire.query.filter_by(actif=True).all()
    
    if request.method == 'POST':
        try:
            charge.numero = request.form['numero']
            charge.proprietaire_id = int(request.form['proprietaire_id'])
            charge.montant = float(request.form['montant'])
            charge.type_charge = request.form['type_charge']
            charge.periode = request.form['periode']
            charge.date_echéance = datetime.strptime(request.form['date_echeance'], '%Y-%m-%d')
            charge.statut = request.form.get('statut', 'en attente')
            charge.notes = request.form.get('notes', '')
            
            if request.form.get('date_paiement'):
                charge.date_paiement = datetime.strptime(request.form['date_paiement'], '%Y-%m-%d')
                if charge.date_paiement:
                    charge.statut = 'payée'
            else:
                charge.date_paiement = None
            
            db.session.commit()
            flash('Charge modifiée avec succès', 'success')
            return redirect(url_for('charges.liste_charges'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('modifier_charge.html', charge=charge, proprietaires=proprietaires)

@charges_bp.route('/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer_charge(id):
    """Supprimer une charge"""
    charge = Charge.query.get_or_404(id)
    try:
        db.session.delete(charge)
        db.session.commit()
        flash('Charge supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('charges.liste_charges'))

@charges_bp.route('/rapport')
@login_required
def rapport_charges():
    """Rapport détaillé sur les charges"""
    totaux_par_type = db.session.query(
        Charge.type_charge,
        db.func.sum(Charge.montant).label('total')
    ).group_by(Charge.type_charge).all()
    
    totaux_par_statut = db.session.query(
        Charge.statut,
        db.func.sum(Charge.montant).label('total'),
        db.func.count(Charge.id).label('nombre')
    ).group_by(Charge.statut).all()
    
    charges_par_prop = db.session.query(
        Proprietaire.nom_complet,
        db.func.sum(Charge.montant).label('total'),
        db.func.count(Charge.id).label('nombre')
    ).join(Charge).group_by(Proprietaire.id).all()
    
    return render_template('rapport_charges.html',
                         totaux_par_type=totaux_par_type,
                         totaux_par_statut=totaux_par_statut,
                         charges_par_prop=charges_par_prop)

# ==================== ROUTES ASSEMBLÉES ====================

@assemblees_bp.route('/')
@login_required
def liste_assemblees():
    """Lister toutes les assemblées générales"""
    page = request.args.get('page', 1, type=int)
    filtre_statut = request.args.get('statut', '')
    
    query = AssembléeGénérale.query
    if filtre_statut:
        query = query.filter_by(statut=filtre_statut)
    
    assemblees = query.order_by(AssembléeGénérale.date_seance.desc()).paginate(page=page, per_page=20)
    return render_template('assemblees.html', assemblees=assemblees, filtre_statut=filtre_statut)

@assemblees_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_assemblee():
    """Créer une nouvelle assemblée générale"""
    if request.method == 'POST':
        try:
            assemblee = AssembléeGénérale(
                titre=request.form['titre'],
                date_seance=datetime.strptime(request.form['date_seance'], '%Y-%m-%dT%H:%M'),
                lieu=request.form.get('lieu', ''),
                ordre_du_jour=request.form['ordre_du_jour'],
                statut=request.form.get('statut', 'programmée')
            )
            
            if request.form.get('proces_verbal'):
                assemblee.proces_verbal = request.form['proces_verbal']
            
            db.session.add(assemblee)
            db.session.commit()
            flash('Assemblée générale créée avec succès', 'success')
            return redirect(url_for('assemblees.liste_assemblees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création: {str(e)}', 'error')
    
    return render_template('ajouter_assemblee.html')

@assemblees_bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_assemblee(id):
    """Modifier une assemblée générale"""
    assemblee = AssembléeGénérale.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            assemblee.titre = request.form['titre']
            assemblee.date_seance = datetime.strptime(request.form['date_seance'], '%Y-%m-%dT%H:%M')
            assemblee.lieu = request.form.get('lieu', '')
            assemblee.ordre_du_jour = request.form['ordre_du_jour']
            assemblee.statut = request.form.get('statut', 'programmée')
            assemblee.proces_verbal = request.form.get('proces_verbal', '')
            
            db.session.commit()
            flash('Assemblée générale modifiée avec succès', 'success')
            return redirect(url_for('assemblees.liste_assemblees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('modifier_assemblee.html', assemblee=assemblee)

@assemblees_bp.route('/<int:id>')
@login_required
def detail_assemblee(id):
    """Détail d'une assemblée générale"""
    assemblee = AssembléeGénérale.query.get_or_404(id)
    votes = Vote.query.filter_by(assemblee_id=id).all()
    
    stats_votes = db.session.query(
        Vote.decision,
        db.func.count(Vote.id).label('nombre')
    ).filter_by(assemblee_id=id).group_by(Vote.decision).all()
    
    stats_votes_dict = {s[0]: s[1] for s in stats_votes}
    
    return render_template('detail_assemblee.html', assemblee=assemblee, votes=votes, stats_votes=stats_votes_dict)

@assemblees_bp.route('/<int:id>/ajouter-vote', methods=['POST'])
@login_required
def ajouter_vote(id):
    """Ajouter un vote à une assemblée"""
    assemblee = AssembléeGénérale.query.get_or_404(id)
    
    try:
        vote = Vote(
            assemblee_id=id,
            proprietaire_id=int(request.form['proprietaire_id']),
            decision=request.form['decision']
        )
        
        db.session.add(vote)
        db.session.commit()
        flash('Vote enregistré avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'enregistrement du vote: {str(e)}', 'error')
    
    return redirect(url_for('assemblees.detail_assemblee', id=id))

@assemblees_bp.route('/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer_assemblee(id):
    """Supprimer une assemblée générale"""
    assemblee = AssembléeGénérale.query.get_or_404(id)
    try:
        db.session.delete(assemblee)
        db.session.commit()
        flash('Assemblée générale supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('assemblees.liste_assemblees'))

# ==================== ROUTES TRAVAUX ====================

@travaux_bp.route('/')
@login_required
def liste_travaux():
    """Lister tous les travaux"""
    page = request.args.get('page', 1, type=int)
    filtre_statut = request.args.get('statut', '')
    filtre_type = request.args.get('type', '')
    
    query = Travaux.query
    if filtre_statut:
        query = query.filter_by(statut=filtre_statut)
    if filtre_type:
        query = query.filter_by(type_travaux=filtre_type)
    
    travaux = query.order_by(Travaux.date_creation.desc()).paginate(page=page, per_page=20)
    types_travaux = db.session.query(Travaux.type_travaux).distinct().all()
    
    return render_template('travaux.html', travaux=travaux, types_travaux=types_travaux,
                         filtre_statut=filtre_statut, filtre_type=filtre_type)

@travaux_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_travaux():
    """Créer un nouveau travail"""
    if request.method == 'POST':
        try:
            travaux = Travaux(
                titre=request.form['titre'],
                description=request.form['description'],
                type_travaux=request.form['type_travaux'],
                date_debut=datetime.strptime(request.form['date_debut'], '%Y-%m-%dT%H:%M'),
                statut=request.form.get('statut', 'planifié'),
                responsable=request.form.get('responsable', ''),
                entreprise=request.form.get('entreprise', ''),
                contact_entreprise=request.form.get('contact_entreprise', ''),
                notes=request.form.get('notes', '')
            )
            
            if request.form.get('date_fin_prevue'):
                travaux.date_fin_prevue = datetime.strptime(request.form['date_fin_prevue'], '%Y-%m-%dT%H:%M')
            
            if request.form.get('budget_previsionnel'):
                travaux.budget_previsionnel = float(request.form['budget_previsionnel'])
            
            if request.form.get('appel_offres'):
                travaux.appel_offres = request.form['appel_offres']
            
            if request.form.get('devis'):
                travaux.devis = request.form['devis']
            
            db.session.add(travaux)
            db.session.commit()
            flash('Travaux créés avec succès', 'success')
            return redirect(url_for('travaux.liste_travaux'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création: {str(e)}', 'error')
    
    return render_template('ajouter_travaux.html')

@travaux_bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_travaux(id):
    """Modifier des travaux"""
    travaux = Travaux.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            travaux.titre = request.form['titre']
            travaux.description = request.form['description']
            travaux.type_travaux = request.form['type_travaux']
            travaux.date_debut = datetime.strptime(request.form['date_debut'], '%Y-%m-%dT%H:%M')
            travaux.statut = request.form.get('statut', 'planifié')
            travaux.responsable = request.form.get('responsable', '')
            travaux.entreprise = request.form.get('entreprise', '')
            travaux.contact_entreprise = request.form.get('contact_entreprise', '')
            travaux.notes = request.form.get('notes', '')
            
            if request.form.get('date_fin_prevue'):
                travaux.date_fin_prevue = datetime.strptime(request.form['date_fin_prevue'], '%Y-%m-%dT%H:%M')
            
            if request.form.get('date_fin_reelle'):
                travaux.date_fin_reelle = datetime.strptime(request.form['date_fin_reelle'], '%Y-%m-%dT%H:%M')
            
            if request.form.get('budget_previsionnel'):
                travaux.budget_previsionnel = float(request.form['budget_previsionnel'])
            
            if request.form.get('budget_reel'):
                travaux.budget_reel = float(request.form['budget_reel'])
            
            if request.form.get('appel_offres'):
                travaux.appel_offres = request.form['appel_offres']
            
            if request.form.get('devis'):
                travaux.devis = request.form['devis']
            
            db.session.commit()
            flash('Travaux modifiés avec succès', 'success')
            return redirect(url_for('travaux.liste_travaux'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('modifier_travaux.html', travaux=travaux)

@travaux_bp.route('/<int:id>')
@login_required
def detail_travaux(id):
    """Détail des travaux"""
    travaux = Travaux.query.get_or_404(id)
    return render_template('detail_travaux.html', travaux=travaux)

@travaux_bp.route('/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer_travaux(id):
    """Supprimer des travaux"""
    travaux = Travaux.query.get_or_404(id)
    try:
        db.session.delete(travaux)
        db.session.commit()
        flash('Travaux supprimés avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('travaux.liste_travaux'))

@travaux_bp.route('/rapport')
@login_required
def rapport_travaux():
    """Rapport détaillé sur les travaux"""
    totaux_par_type = db.session.query(
        Travaux.type_travaux,
        db.func.sum(Travaux.budget_previsionnel).label('total_previsionnel'),
        db.func.sum(Travaux.budget_reel).label('total_reel'),
        db.func.count(Travaux.id).label('nombre')
    ).group_by(Travaux.type_travaux).all()
    
    totaux_par_statut = db.session.query(
        Travaux.statut,
        db.func.count(Travaux.id).label('nombre')
    ).group_by(Travaux.statut).all()
    
    return render_template('rapport_travaux.html',
                         totaux_par_type=totaux_par_type,
                         totaux_par_statut=totaux_par_statut)
