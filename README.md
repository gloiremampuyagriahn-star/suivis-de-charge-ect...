README.md

# Système de Gestion de Copropriété

Une application web complète pour la gestion des copropriétés construite avec Flask et SQLite.

## Fonctionnalités

- **Gestion des Propriétaires**: Ajouter, modifier, lister les propriétaires avec leur lot et leur part
- **Suivi des Charges**: Créer et suivre les charges (chauffage, eau, électricité, etc.) avec contrôle des paiements
- **Assemblées Générales**: Organiser et archiver les assemblées générale avec votes des propriétaires
- **Gestion des Travaux**: Planifier et suivre les travaux de maintenance/rénovation avec budgets et progression

## Installation

### Prérequis

- Python 3.7+
- pip

### Étapes d'installation

1. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

2. **Créer la base de données** (automatique au premier lancement):
La base de données SQLite sera créée automatiquement au premier lancement de l'application.

3. **Lancer l'application**:
```bash
python run.py
```

4. **Accéder l'application**:
Ouvrez votre navigateur et allez à `http://127.0.0.1:5000`

## Structure du Projet

```
.
├── app/
│   ├── __init__.py        # Factory de l'application Flask
│   ├── models.py          # Modèles SQLAlchemy
│   ├── routes.py          # Routes et vues
│   ├── templates/         # Templates HTML
│   └── static/            # Fichiers statiques (CSS, JS)
├── config.py              # Configuration de l'application
├── run.py                 # Point d'entrée de l'application
├── requirements.txt       # Dépendances Python
└── copropriete.db         # Base de données SQLite (créée automatiquement)
```

## Utilisation

### Propriétaires
- Ajouter/Modifier/Supprimer des propriétaires
- Assigner un lot et un pourcentage de part
- Marquer les propriétaires comme actifs ou inactifs

### Charges
- Créer des charges mensuelles/trimestrielles/annuelles
- Suivre les paiements
- Générer des rapports par type ou propriétaire
- Filtrer par statut (en attente, payée, en retard)

### Assemblées Générales
- Créer et gérer les assemblées générales
- Enregistrer les votes des propriétaires
- Archiver les procès-verbaux
- Voir les statistiques de participation

### Travaux
- Planifier les travaux de maintenance
- Suivre la progression et les budgets
- Associer des entreprises et devis
- Générer des rapports sur les dépenses

## Technologies Utilisées

- **Flask**: Framework web Python
- **SQLAlchemy**: ORM pour la base de données
- **SQLite**: Base de données
- **HTML/CSS**: Interface utilisateur

## Fonctionnalités Futures

- Génération de PDF pour les rapports
- Envoi d'e-mails aux propriétaires
- Interface de paiement en ligne
- Application mobile
- Système de notifications

## Support

Pour toute question ou bug, merci de créer une issue dans le dépôt.

## Licence

MIT
