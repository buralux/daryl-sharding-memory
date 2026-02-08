#!/usr/bin/env python3
"""
DARYL Sub-Agent: Comptable Plombier (France)
Auteur: DARYL
Version: 1.0
Date: 2026-02-06
"""

import sqlite3
import sys
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

# Constants de comptabilité française
TVA_RATE = 0.20  # 20%
COUT_KM = 1.50   # Exemple de coût kilométrique fictif

class ComptablePlombier:
    """Sous-agent comptable pour une société de plombiers française."""

    def __init__(self, db_path: str = "comptable_plombier.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def initialiser(self) -> None:
        """Initialise la base de données SQLite."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.creer_tables()

    def creer_tables(self) -> None:
        """Crée les tables nécessaires."""
        # Table Clients
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                adresse TEXT,
                telephone TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table Devis (Quotes)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS devis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                date_devis DATE NOT NULL,
                montant_ht REAL NOT NULL,
                montant_tva REAL NOT NULL,
                statut TEXT DEFAULT 'envoyé',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
        """)

        # Table Factures
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS factures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                numero_facture TEXT NOT NULL UNIQUE,
                date_facture DATE NOT NULL,
                date_echeance DATE,
                montant_ht REAL NOT NULL,
                montant_tva REAL NOT NULL,
                montant_ttc REAL NOT NULL,
                statut TEXT DEFAULT 'en_attente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
        """)

        # Table Dépenses (Expenses)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS depenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categorie TEXT NOT NULL,
                description TEXT,
                date_depense DATE NOT NULL,
                montant_ht REAL NOT NULL,
                montant_tva REAL NOT NULL,
                montant_ttc REAL NOT NULL,
                facture_fournisseur TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def ajouter_client(self, nom: str, adresse: str = "", telephone: str = "", email: str = "") -> int:
        """Ajoute un nouveau client."""
        self.cursor.execute("""
            INSERT INTO clients (nom, adresse, telephone, email)
            VALUES (?, ?, ?, ?)
        """, (nom, adresse, telephone, email))
        self.conn.commit()
        return self.cursor.lastrowid

    def creer_devis(self, client_id: int, date_devis: str, montant_ht: float, description: str = "") -> int:
        """Crée un nouveau devis (Quote)."""
        tva = montant_ht * TVA_RATE
        ttc = montant_ht + tva

        self.cursor.execute("""
            INSERT INTO devis (client_id, date_devis, montant_ht, montant_tva, statut)
            VALUES (?, ?, ?, ?, 'brouillon')
        """, (client_id, date_devis, montant_ht, tva))
        self.conn.commit()
        return self.cursor.lastrowid

    def emettre_facture(self, client_id: int, numero_facture: str, date_facture: str, montant_ht: float, date_echeance: str = "") -> int:
        """Émet une nouvelle facture."""
        tva = montant_ht * TVA_RATE
        ttc = montant_ht + tva

        self.cursor.execute("""
            INSERT INTO factures (client_id, numero_facture, date_facture, date_echeance, montant_ht, montant_tva, montant_ttc, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'en_attente')
        """, (client_id, numero_facture, date_facture, date_echeance, montant_ht, tva, ttc))
        self.conn.commit()
        return self.cursor.lastrowid

    def ajouter_depense(self, categorie: str, description: str, date_depense: str, montant_ht: float, facture_fournisseur: str = "") -> int:
        """Ajoute une dépense (Expense)."""
        tva = montant_ht * TVA_RATE
        ttc = montant_ht + tva

        self.cursor.execute("""
            INSERT INTO depenses (categorie, description, date_depense, montant_ht, montant_tva, montant_ttc, facture_fournisseur)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (categorie, description, date_depense, montant_ht, tva, ttc, facture_fournisseur))
        self.conn.commit()
        return self.cursor.lastrowid

    def lister_factures(self, statut: str = None) -> List[Dict]:
        """Liste toutes les factures, optionnellement filtrées par statut."""
        if statut:
            self.cursor.execute("SELECT * FROM factures WHERE statut = ?", (statut,))
        else:
            self.cursor.execute("SELECT * FROM factures")
        colonnes = [desc[0] for desc in self.cursor.description]
        lignes = [dict(zip(colonnes, row)) for row in self.cursor.fetchall()]
        return lignes

    def generer_rapport_mensuel(self, annee: int, mois: int) -> Dict:
        """Génère un rapport mensuel simplifié (Recettes - Dépenses)."""
        # Calculer les recettes du mois
        self.cursor.execute("""
            SELECT SUM(montant_ttc) FROM factures
            WHERE strftime('%Y', date_facture) = ? AND strftime('%m', date_facture) = ?
            AND statut != 'annulée'
        """, (str(annee), str(mois).zfill(2, '0')))
        recettes = self.cursor.fetchone()[0] or 0.0

        # Calculer les dépenses du mois
        self.cursor.execute("""
            SELECT SUM(montant_ttc) FROM depenses
            WHERE strftime('%Y', date_depense) = ? AND strftime('%m', date_depense) = ?
        """, (str(annee), str(mois).zfill(2, '0')))
        depenses = self.cursor.fetchone()[0] or 0.0

        resultat = recettes - depenses

        return {
            "periode": f"{annee}-{mois:02d}",
            "recettes": recettes,
            "depenses": depenses,
            "resultat": resultat
        }

    def fermer(self) -> None:
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()


# Fonction CLI principale
def main():
    comptable = ComptablePlombier()
    comptable.initialiser()

    print("📊 Sous-Agent Comptable Plombier (France) - Mode CLI")
    print("------------------------------------------------")
    print("1. Ajouter un client")
    print("2. Créer un devis")
    print("3. Émettre une facture")
    print("4. Ajouter une dépense")
    print("5. Lister les factures")
    print("6. Générer un rapport mensuel")
    print("7. Quitter")

    while True:
        choix = input("\nQue voulez-vous faire ? (1-7) : ")

        if choix == "1":
            nom = input("Nom du client : ")
            adresse = input("Adresse (optionnel) : ")
            telephone = input("Téléphone (optionnel) : ")
            email = input("Email (optionnel) : ")

            client_id = comptable.ajouter_client(nom, adresse, telephone, email)
            print(f"✅ Client ajouté (ID: {client_id})")

        elif choix == "2":
            # Lister les clients disponibles
            comptable.cursor.execute("SELECT id, nom FROM clients")
            clients = comptable.cursor.fetchall()
            print("\nClients disponibles :")
            for c in clients:
                print(f"  [{c[0]}] {c[1]}")

            try:
                client_id = int(input("ID du client : "))
                date_devis = input("Date du devis (YYYY-MM-DD) : ")
                montant_ht = float(input("Montant HT (€) : "))

                devis_id = comptable.creer_devis(client_id, date_devis, montant_ht)
                print(f"✅ Devis créé (ID: {devis_id}, TVA incluse)")

            except ValueError:
                print("❌ Erreur : ID client invalide ou montant invalide")

        elif choix == "3":
            # Lister les clients
            comptable.cursor.execute("SELECT id, nom FROM clients")
            clients = comptable.cursor.fetchall()
            print("\nClients disponibles :")
            for c in clients:
                print(f"  [{c[0]}] {c[1]}")

            try:
                client_id = int(input("ID du client : "))
                numero_facture = input("Numéro de facture : ")
                date_facture = input("Date de facture (YYYY-MM-DD) : ")
                montant_ht = float(input("Montant HT (€) : "))
                date_echeance = input("Date d'échéance (YYYY-MM-DD, optionnel) : ") or ""

                facture_id = comptable.emettre_facture(client_id, numero_facture, date_facture, montant_ht, date_echeance)
                print(f"✅ Facture émise (ID: {facture_id}, TVA 20%, TTC: {montant_ht * 1.20:.2f} €)")

            except ValueError:
                print("❌ Erreur : ID client invalide ou montant invalide")

        elif choix == "4":
            categorie = input("Catégorie (ex: Matériaux, Outillage, Salaires) : ")
            description = input("Description : ")
            date_depense = input("Date de la dépense (YYYY-MM-DD) : ")
            montant_ht = float(input("Montant HT (€) : "))
            facture_fournisseur = input("Numéro de facture fournisseur (optionnel) : ") or ""

            depense_id = comptable.ajouter_depense(categorie, description, date_depense, montant_ht, facture_fournisseur)
            print(f"✅ Dépense ajoutée (ID: {depense_id}, TVA incluse)")

        elif choix == "5":
            statut_filter = input("Filtrer par statut (en_attente/payée/annulée/Enter pour tout) : ") or None
            if statut_filter == "":
                statut_filter = None

            factures = comptable.lister_factures(statut_filter)
            print(f"\n📄 {len(factures)} facture(s) trouvée(s) :")
            for f in factures:
                print(f"  ID: {f['id']} | N°: {f['numero_facture']} | Date: {f['date_facture']} | TTC: {f['montant_ttc']} € | Statut: {f['statut']}")

        elif choix == "6":
            try:
                annee = int(input("Année (ex: 2026) : "))
                mois = int(input("Mois (1-12) : "))

                rapport = comptable.generer_rapport_mensuel(annee, mois)

                print("\n📊 RAPPORT MENSUEL")
                print("------------------------------------------------")
                print(f"Période : {rapport['periode']}")
                print(f"Recettes : {rapport['recettes']:.2f} €")
                print(f"Dépenses : {rapport['depenses']:.2f} €")
                print(f"Résultat : {rapport['resultat']:.2f} €")

                if rapport['resultat'] < 0:
                    print("⚠️ Attention : Résultat négatif (Déficit)")

            except ValueError:
                print("❌ Erreur : Année ou mois invalide")

        elif choix == "7":
            print("👋 Au revoir !")
            comptable.fermer()
            sys.exit(0)

        else:
            print("❌ Choix invalide. Veuillez entrer un chiffre entre 1 et 7.")

if __name__ == "__main__":
    main()
