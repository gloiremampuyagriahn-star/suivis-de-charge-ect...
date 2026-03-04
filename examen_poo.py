"""
=============================================================================
EXAMEN DE PROGRAMMATION ORIENTÉE OBJET (POO)
Thème : Système de Suivi de Charge de Travail
=============================================================================

Durée : 3 heures
Documents : Non autorisés
Calculatrice : Non autorisée

Instructions générales :
- Répondez à toutes les questions dans ce fichier.
- Chaque classe doit être bien documentée (docstrings).
- Respectez les principes de la POO : encapsulation, héritage, polymorphisme.
- Le code doit être fonctionnel et sans erreur de syntaxe.

=============================================================================
"""

from abc import ABC, abstractmethod
from datetime import date


# =============================================================================
# PARTIE 1 : Classes de base (20 points)
# =============================================================================
#
# Question 1.1 (5 points)
# Créez une classe `Personne` avec les attributs privés suivants :
#   - __nom (str)
#   - __prenom (str)
#   - __email (str)
# Ajoutez :
#   - Un constructeur (__init__)
#   - Des propriétés (getters/setters) pour chaque attribut
#   - Une méthode __str__ retournant "Prénom NOM <email>"
#
# Question 1.2 (5 points)
# Créez une classe `Tache` avec :
#   - __titre (str)
#   - __description (str)
#   - __charge_heures (float) : charge en heures
#   - __date_echeance (date)
#   - __statut (str) : 'en_attente', 'en_cours', 'terminee'
# Ajoutez :
#   - Un constructeur avec statut par défaut 'en_attente'
#   - Des propriétés pour chaque attribut
#   - Une méthode `est_en_retard()` retournant True si la date d'échéance
#     est dépassée et que la tâche n'est pas terminée
#   - Une méthode __str__ affichant les informations de la tâche
#
# Question 1.3 (5 points)
# Créez une classe `Projet` avec :
#   - __nom (str)
#   - __description (str)
#   - __date_debut (date)
#   - __date_fin (date)
#   - __taches (list) : liste de Tache
# Ajoutez :
#   - Un constructeur
#   - Des propriétés
#   - Une méthode `ajouter_tache(tache)` pour ajouter une tâche
#   - Une méthode `charge_totale()` retournant la somme des charges en heures
#   - Une méthode `taches_en_retard()` retournant la liste des tâches en retard
#   - Une méthode __str__
#
# Question 1.4 (5 points)
# Créez une classe `Equipe` avec :
#   - __nom (str)
#   - __membres (list) : liste de Personne
# Ajoutez :
#   - Un constructeur
#   - Des propriétés
#   - Une méthode `ajouter_membre(personne)` pour ajouter un membre
#   - Une méthode `supprimer_membre(email)` pour supprimer un membre par email
#   - Une méthode `taille()` retournant le nombre de membres
#   - Une méthode __str__ affichant le nom de l'équipe et ses membres


# === VOS RÉPONSES À LA PARTIE 1 ===

class Personne:
    """Représente une personne dans le système de suivi de charge."""

    def __init__(self, nom: str, prenom: str, email: str):
        self.__nom = nom
        self.__prenom = prenom
        self.__email = email

    @property
    def nom(self) -> str:
        return self.__nom

    @nom.setter
    def nom(self, valeur: str):
        if not valeur.strip():
            raise ValueError("Le nom ne peut pas être vide.")
        self.__nom = valeur

    @property
    def prenom(self) -> str:
        return self.__prenom

    @prenom.setter
    def prenom(self, valeur: str):
        if not valeur.strip():
            raise ValueError("Le prénom ne peut pas être vide.")
        self.__prenom = valeur

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valeur: str):
        if "@" not in valeur:
            raise ValueError("L'email doit contenir '@'.")
        self.__email = valeur

    def __str__(self) -> str:
        return f"{self.__prenom} {self.__nom.upper()} <{self.__email}>"


class Tache:
    """Représente une tâche dans un projet."""

    STATUTS_VALIDES = ("en_attente", "en_cours", "terminee")

    def __init__(self, titre: str, description: str,
                 charge_heures: float, date_echeance: date):
        self.__titre = titre
        self.__description = description
        self.__charge_heures = charge_heures
        self.__date_echeance = date_echeance
        self.__statut = "en_attente"

    @property
    def titre(self) -> str:
        return self.__titre

    @titre.setter
    def titre(self, valeur: str):
        if not valeur.strip():
            raise ValueError("Le titre ne peut pas être vide.")
        self.__titre = valeur

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, valeur: str):
        self.__description = valeur

    @property
    def charge_heures(self) -> float:
        return self.__charge_heures

    @charge_heures.setter
    def charge_heures(self, valeur: float):
        if valeur < 0:
            raise ValueError("La charge en heures ne peut pas être négative.")
        self.__charge_heures = valeur

    @property
    def date_echeance(self) -> date:
        return self.__date_echeance

    @date_echeance.setter
    def date_echeance(self, valeur: date):
        self.__date_echeance = valeur

    @property
    def statut(self) -> str:
        return self.__statut

    @statut.setter
    def statut(self, valeur: str):
        if valeur not in self.STATUTS_VALIDES:
            raise ValueError(
                f"Statut invalide. Valeurs possibles : {self.STATUTS_VALIDES}"
            )
        self.__statut = valeur

    def est_en_retard(self) -> bool:
        """Retourne True si la date d'échéance est dépassée et la tâche n'est pas terminée."""
        return self.__statut != "terminee" and self.__date_echeance < date.today()

    def __str__(self) -> str:
        retard = " [EN RETARD]" if self.est_en_retard() else ""
        return (
            f"Tâche : {self.__titre}{retard}\n"
            f"  Description : {self.__description}\n"
            f"  Charge : {self.__charge_heures}h | Échéance : {self.__date_echeance} | Statut : {self.__statut}"
        )


class Projet:
    """Représente un projet regroupant plusieurs tâches."""

    def __init__(self, nom: str, description: str,
                 date_debut: date, date_fin: date):
        self.__nom = nom
        self.__description = description
        self.__date_debut = date_debut
        self.__date_fin = date_fin
        self.__taches: list[Tache] = []

    @property
    def nom(self) -> str:
        return self.__nom

    @nom.setter
    def nom(self, valeur: str):
        if not valeur.strip():
            raise ValueError("Le nom du projet ne peut pas être vide.")
        self.__nom = valeur

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, valeur: str):
        self.__description = valeur

    @property
    def date_debut(self) -> date:
        return self.__date_debut

    @property
    def date_fin(self) -> date:
        return self.__date_fin

    @date_fin.setter
    def date_fin(self, valeur: date):
        if valeur < self.__date_debut:
            raise ValueError("La date de fin doit être après la date de début.")
        self.__date_fin = valeur

    @property
    def taches(self) -> list:
        return list(self.__taches)

    def ajouter_tache(self, tache: Tache):
        """Ajoute une tâche au projet."""
        if not isinstance(tache, Tache):
            raise TypeError("L'argument doit être une instance de Tache.")
        self.__taches.append(tache)

    def charge_totale(self) -> float:
        """Retourne la somme des charges en heures de toutes les tâches."""
        return sum(t.charge_heures for t in self.__taches)

    def taches_en_retard(self) -> list:
        """Retourne la liste des tâches en retard."""
        return [t for t in self.__taches if t.est_en_retard()]

    def __str__(self) -> str:
        return (
            f"Projet : {self.__nom}\n"
            f"  Description : {self.__description}\n"
            f"  Période : {self.__date_debut} → {self.__date_fin}\n"
            f"  Tâches : {len(self.__taches)} | Charge totale : {self.charge_totale()}h"
        )


class Equipe:
    """Représente une équipe composée de plusieurs personnes."""

    def __init__(self, nom: str):
        self.__nom = nom
        self.__membres: list[Personne] = []

    @property
    def nom(self) -> str:
        return self.__nom

    @nom.setter
    def nom(self, valeur: str):
        if not valeur.strip():
            raise ValueError("Le nom de l'équipe ne peut pas être vide.")
        self.__nom = valeur

    @property
    def membres(self) -> list:
        return list(self.__membres)

    def ajouter_membre(self, personne: Personne):
        """Ajoute un membre à l'équipe."""
        if not isinstance(personne, Personne):
            raise TypeError("L'argument doit être une instance de Personne.")
        self.__membres.append(personne)

    def supprimer_membre(self, email: str) -> bool:
        """Supprime un membre par son email. Retourne True si supprimé."""
        avant = len(self.__membres)
        self.__membres = [m for m in self.__membres if m.email != email]
        return len(self.__membres) < avant

    def taille(self) -> int:
        """Retourne le nombre de membres dans l'équipe."""
        return len(self.__membres)

    def __str__(self) -> str:
        membres_str = "\n  ".join(str(m) for m in self.__membres) if self.__membres else "(aucun)"
        return f"Équipe : {self.__nom} ({self.taille()} membre(s))\n  {membres_str}"


# =============================================================================
# PARTIE 2 : Héritage et Polymorphisme (30 points)
# =============================================================================
#
# Question 2.1 (10 points)
# Créez une classe abstraite `Ressource` (hérite de ABC) avec :
#   - __identifiant (str)
#   - __disponible (bool)
#   - Un constructeur
#   - Des propriétés
#   - Une méthode abstraite `type_ressource()` retournant une chaîne
#   - Une méthode abstraite `cout_par_heure()` retournant un float
#   - Une méthode concrète `cout_total(heures)` = heures * cout_par_heure()
#   - Une méthode __str__
#
# Question 2.2 (10 points)
# Créez deux classes héritant de `Ressource` :
#
#   a) `RessourceHumaine(Ressource, Personne)` :
#      - Attributs supplémentaires : __role (str), __taux_horaire (float)
#      - Implémentez type_ressource() retournant "Ressource Humaine"
#      - Implémentez cout_par_heure() retournant le taux horaire
#      - Surchargez __str__
#
#   b) `RessourceMaterielle(Ressource)` :
#      - Attributs supplémentaires : __nom_materiel (str), __cout_location_heure (float)
#      - Implémentez type_ressource() retournant "Ressource Matérielle"
#      - Implémentez cout_par_heure() retournant le coût de location
#      - Surchargez __str__
#
# Question 2.3 (10 points)
# Créez une classe `PlanCharge` avec :
#   - __projet (Projet)
#   - __affectations (dict) : {Tache: [Ressource]}
# Ajoutez :
#   - Un constructeur
#   - Une méthode `affecter(tache, ressource)` pour associer une ressource à une tâche
#   - Une méthode `cout_total_projet()` calculant le coût total du projet
#     (somme de: tache.charge_heures * ressource.cout_par_heure() pour chaque affectation)
#   - Une méthode `rapport()` affichant un résumé complet du plan de charge
#   - Une méthode __str__


# === VOS RÉPONSES À LA PARTIE 2 ===

class Ressource(ABC):
    """Classe abstraite représentant une ressource affectable à une tâche."""

    def __init__(self, identifiant: str, disponible: bool = True):
        self.__identifiant = identifiant
        self.__disponible = disponible

    @property
    def identifiant(self) -> str:
        return self.__identifiant

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, valeur: bool):
        self.__disponible = valeur

    @abstractmethod
    def type_ressource(self) -> str:
        """Retourne le type de la ressource."""

    @abstractmethod
    def cout_par_heure(self) -> float:
        """Retourne le coût par heure de la ressource."""

    def cout_total(self, heures: float) -> float:
        """Calcule le coût total pour un nombre d'heures donné."""
        return heures * self.cout_par_heure()

    def __str__(self) -> str:
        dispo = "Disponible" if self.__disponible else "Indisponible"
        return (
            f"[{self.type_ressource()}] ID: {self.__identifiant} | "
            f"Coût/h: {self.cout_par_heure()}€ | {dispo}"
        )


class RessourceHumaine(Ressource, Personne):
    """Ressource humaine : une personne ayant un rôle et un taux horaire."""

    def __init__(self, identifiant: str, nom: str, prenom: str,
                 email: str, role: str, taux_horaire: float):
        Ressource.__init__(self, identifiant)
        Personne.__init__(self, nom, prenom, email)
        self.__role = role
        self.__taux_horaire = taux_horaire

    @property
    def role(self) -> str:
        return self.__role

    @role.setter
    def role(self, valeur: str):
        self.__role = valeur

    @property
    def taux_horaire(self) -> float:
        return self.__taux_horaire

    @taux_horaire.setter
    def taux_horaire(self, valeur: float):
        if valeur < 0:
            raise ValueError("Le taux horaire ne peut pas être négatif.")
        self.__taux_horaire = valeur

    def type_ressource(self) -> str:
        return "Ressource Humaine"

    def cout_par_heure(self) -> float:
        return self.__taux_horaire

    def __str__(self) -> str:
        return (
            f"[{self.type_ressource()}] {Personne.__str__(self)} | "
            f"Rôle : {self.__role} | Taux : {self.__taux_horaire}€/h"
        )


class RessourceMaterielle(Ressource):
    """Ressource matérielle : un équipement loué à l'heure."""

    def __init__(self, identifiant: str, nom_materiel: str,
                 cout_location_heure: float):
        super().__init__(identifiant)
        self.__nom_materiel = nom_materiel
        self.__cout_location_heure = cout_location_heure

    @property
    def nom_materiel(self) -> str:
        return self.__nom_materiel

    @nom_materiel.setter
    def nom_materiel(self, valeur: str):
        self.__nom_materiel = valeur

    @property
    def cout_location_heure(self) -> float:
        return self.__cout_location_heure

    @cout_location_heure.setter
    def cout_location_heure(self, valeur: float):
        if valeur < 0:
            raise ValueError("Le coût de location ne peut pas être négatif.")
        self.__cout_location_heure = valeur

    def type_ressource(self) -> str:
        return "Ressource Matérielle"

    def cout_par_heure(self) -> float:
        return self.__cout_location_heure

    def __str__(self) -> str:
        return (
            f"[{self.type_ressource()}] {self.__nom_materiel} | "
            f"Location : {self.__cout_location_heure}€/h"
        )


class PlanCharge:
    """Plan de charge associant des ressources aux tâches d'un projet."""

    def __init__(self, projet: Projet):
        if not isinstance(projet, Projet):
            raise TypeError("L'argument doit être une instance de Projet.")
        self.__projet = projet
        self.__affectations: dict[Tache, list[Ressource]] = {}

    @property
    def projet(self) -> Projet:
        return self.__projet

    def affecter(self, tache: Tache, ressource: Ressource):
        """Associe une ressource à une tâche du plan de charge."""
        if tache not in self.__projet.taches:
            raise ValueError("La tâche n'appartient pas au projet associé.")
        if not isinstance(ressource, Ressource):
            raise TypeError("L'argument ressource doit être une instance de Ressource.")
        if tache not in self.__affectations:
            self.__affectations[tache] = []
        self.__affectations[tache].append(ressource)

    def cout_total_projet(self) -> float:
        """Calcule le coût total du projet (charge × coût/h pour chaque affectation)."""
        total = 0.0
        for tache, ressources in self.__affectations.items():
            for ressource in ressources:
                total += ressource.cout_total(tache.charge_heures)
        return total

    def rapport(self) -> str:
        """Retourne un résumé complet du plan de charge."""
        lignes = [
            "=" * 60,
            f"RAPPORT DE PLAN DE CHARGE : {self.__projet.nom}",
            "=" * 60,
            str(self.__projet),
            "",
            "AFFECTATIONS :",
        ]
        for tache, ressources in self.__affectations.items():
            lignes.append(f"\n  {tache.titre} ({tache.charge_heures}h) :")
            for r in ressources:
                cout = r.cout_total(tache.charge_heures)
                lignes.append(f"    - {r} => Coût : {cout:.2f}€")
        lignes.append("")
        lignes.append(f"COÛT TOTAL DU PROJET : {self.cout_total_projet():.2f}€")
        lignes.append("=" * 60)
        return "\n".join(lignes)

    def __str__(self) -> str:
        nb_affectations = sum(len(r) for r in self.__affectations.values())
        return (
            f"Plan de charge du projet '{self.__projet.nom}' | "
            f"Affectations : {nb_affectations} | "
            f"Coût total : {self.cout_total_projet():.2f}€"
        )


# =============================================================================
# PARTIE 3 : Questions théoriques (20 points)
# =============================================================================
#
# Répondez aux questions suivantes sous forme de commentaires Python.
#
# Question 3.1 (5 points)
# Expliquez les quatre piliers de la POO et donnez un exemple de chacun
# tiré du code que vous avez écrit ci-dessus.
#
# RÉPONSE :
# 1. Encapsulation : Les attributs sont privés (ex: Personne.__nom) et
#    accessibles uniquement via des propriétés (getters/setters), ce qui
#    protège les données internes de la classe.
#
# 2. Abstraction : La classe Ressource est abstraite (ABC) et définit une
#    interface commune (type_ressource, cout_par_heure) sans fournir
#    d'implémentation, masquant ainsi la complexité aux utilisateurs.
#
# 3. Héritage : RessourceHumaine hérite de Ressource et Personne, réutilisant
#    leurs attributs et méthodes tout en ajoutant ses propres spécificités
#    (rôle, taux_horaire).
#
# 4. Polymorphisme : cout_par_heure() est définie différemment dans
#    RessourceHumaine (retourne taux_horaire) et RessourceMaterielle
#    (retourne cout_location_heure), permettant un traitement uniforme
#    via l'interface Ressource.
#
# Question 3.2 (5 points)
# Quelle est la différence entre une classe abstraite et une interface ?
# Python supporte-t-il les interfaces ? Expliquez.
#
# RÉPONSE :
# - Une classe abstraite (ABC en Python) peut avoir des méthodes concrètes
#   ET des méthodes abstraites. Elle peut aussi avoir des attributs.
# - Une interface (Java, C#) ne contient que des signatures de méthodes
#   (contrat pur), sans implémentation.
# - Python ne supporte pas les interfaces nativement. Cependant, on peut
#   simuler une interface avec ABC en ne définissant que des méthodes
#   abstraites (@abstractmethod), sans aucune implémentation concrète.
# - Les Protocol (typing.Protocol) de Python 3.8+ permettent aussi de
#   définir des interfaces structurelles (duck typing statique).
#
# Question 3.3 (5 points)
# Qu'est-ce que la surcharge de méthodes (overriding) ? Illustrez avec un
# exemple tiré de votre code.
#
# RÉPONSE :
# La surcharge (override) consiste à redéfinir une méthode héritée dans
# une sous-classe pour modifier son comportement.
# Exemple : la méthode __str__ est héritée d'object (Python), mais elle est
# redéfinie dans chaque classe (Personne, Tache, Projet, etc.) pour
# retourner une représentation textuelle adaptée à chaque classe.
# De même, cout_par_heure() est abstraite dans Ressource et redéfinie
# différemment dans RessourceHumaine et RessourceMaterielle.
#
# Question 3.4 (5 points)
# Expliquez le principe de substitution de Liskov (LSP) et vérifiez s'il
# est respecté dans votre code.
#
# RÉPONSE :
# Le LSP stipule que tout objet d'une sous-classe doit pouvoir remplacer
# un objet de sa super-classe sans altérer le comportement du programme.
# Dans notre code : RessourceHumaine et RessourceMaterielle peuvent être
# utilisées partout où une Ressource est attendue (ex: dans PlanCharge),
# car elles respectent l'interface définie par Ressource (type_ressource(),
# cout_par_heure(), cout_total()). Le LSP est donc respecté.


# =============================================================================
# PARTIE 4 : Cas pratique (30 points)
# =============================================================================
#
# Question 4 (30 points)
# En utilisant les classes créées dans les parties précédentes, écrivez un
# programme principal qui :
#
# 1. Crée un projet "Refonte Site Web ECT" avec une durée de 3 mois.
# 2. Crée au moins 4 tâches avec des charges variées.
# 3. Crée une équipe de 3 personnes avec des rôles différents.
# 4. Crée au moins une ressource matérielle.
# 5. Construit un plan de charge en affectant les ressources aux tâches.
# 6. Affiche le rapport complet du plan de charge.
# 7. Affiche la liste des tâches en retard (s'il y en a).
# 8. Calcule et affiche le coût total du projet.


# === VOTRE RÉPONSE À LA PARTIE 4 ===

def main():
    """Programme principal de démonstration du système de suivi de charge."""

    print("=" * 60)
    print("SYSTÈME DE SUIVI DE CHARGE - DÉMONSTRATION")
    print("=" * 60)

    # 1. Création du projet
    projet = Projet(
        nom="Refonte Site Web ECT",
        description="Modernisation complète du site web de l'établissement",
        date_debut=date(2026, 1, 1),
        date_fin=date(2026, 3, 31),
    )

    # 2. Création des tâches
    tache_analyse = Tache(
        titre="Analyse des besoins",
        description="Recueil et analyse des besoins utilisateurs",
        charge_heures=20.0,
        date_echeance=date(2026, 1, 15),
    )
    tache_analyse.statut = "terminee"

    tache_conception = Tache(
        titre="Conception UX/UI",
        description="Maquettage et conception des interfaces",
        charge_heures=35.0,
        date_echeance=date(2025, 12, 31),  # date passée → en retard
    )
    tache_conception.statut = "en_cours"

    tache_dev_backend = Tache(
        titre="Développement backend",
        description="Développement de l'API REST et de la base de données",
        charge_heures=80.0,
        date_echeance=date(2026, 3, 15),
    )

    tache_dev_frontend = Tache(
        titre="Développement frontend",
        description="Intégration des maquettes et développement React",
        charge_heures=60.0,
        date_echeance=date(2026, 3, 20),
    )

    for tache in [tache_analyse, tache_conception, tache_dev_backend, tache_dev_frontend]:
        projet.ajouter_tache(tache)

    # 3. Création de l'équipe
    equipe = Equipe("Équipe Projet ECT")

    chef_projet = RessourceHumaine(
        identifiant="RH001",
        nom="Martin",
        prenom="Sophie",
        email="s.martin@ect.fr",
        role="Chef de projet",
        taux_horaire=75.0,
    )

    dev_backend = RessourceHumaine(
        identifiant="RH002",
        nom="Dupont",
        prenom="Lucas",
        email="l.dupont@ect.fr",
        role="Développeur backend",
        taux_horaire=60.0,
    )

    designer = RessourceHumaine(
        identifiant="RH003",
        nom="Bernard",
        prenom="Camille",
        email="c.bernard@ect.fr",
        role="Designer UX/UI",
        taux_horaire=55.0,
    )

    equipe.ajouter_membre(chef_projet)
    equipe.ajouter_membre(dev_backend)
    equipe.ajouter_membre(designer)

    print(equipe)
    print()

    # 4. Ressource matérielle
    serveur_cloud = RessourceMaterielle(
        identifiant="RM001",
        nom_materiel="Serveur Cloud AWS",
        cout_location_heure=12.0,
    )

    # 5. Plan de charge
    plan = PlanCharge(projet)
    plan.affecter(tache_analyse, chef_projet)
    plan.affecter(tache_conception, designer)
    plan.affecter(tache_dev_backend, dev_backend)
    plan.affecter(tache_dev_backend, serveur_cloud)
    plan.affecter(tache_dev_frontend, dev_backend)
    plan.affecter(tache_dev_frontend, chef_projet)

    # 6. Rapport complet
    print(plan.rapport())

    # 7. Tâches en retard
    taches_retard = projet.taches_en_retard()
    if taches_retard:
        print(f"\n⚠️  TÂCHES EN RETARD ({len(taches_retard)}) :")
        for t in taches_retard:
            print(f"  - {t.titre} (échéance : {t.date_echeance})")
    else:
        print("\n✅ Aucune tâche en retard.")

    # 8. Coût total
    print(f"\n💰 COÛT TOTAL DU PROJET : {plan.cout_total_projet():.2f}€")
    print(f"📊 CHARGE TOTALE : {projet.charge_totale()}h")


if __name__ == "__main__":
    main()
