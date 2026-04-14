# Database Configuration
DB_CONFIG = {
    "DRIVER": "{ODBC Driver 17 for SQL Server}",
    "SERVER": "localhost,1433",
    "DATABASE": "Sougui_DWH",
    "UID": "sa",
    "PWD": "admin",
    "TrustServerCertificate": "yes"
}

# Ollama Configuration
OLLAMA_MODEL = "qwen2.5:3b"

# Sougui Brand Colors - Professional Blue & White Theme
SOUGUI_COLORS = {
    "primary": "#1e40af",       # Deep Blue
    "secondary": "#3b82f6",     # Bright Blue
    "accent": "#60a5fa",        # Light Blue
    "dark": "#0f172a",          # Dark Navy
    "light": "#f8fafc",         # Off White
    "text_primary": "#1e293b",  # Dark Gray
    "text_secondary": "#64748b", # Medium Gray
    "success": "#10b981",       # Green
    "error": "#ef4444",         # Red
    "warning": "#f59e0b",       # Orange
    "border": "#e2e8f0",        # Light Gray Border
    "hover": "#2563eb"          # Hover Blue
}

# Database Schema Context for LLM
DB_SCHEMA = """
Database: Sougui_DWH - E-commerce Data Warehouse

FACT TABLES:
- Fact_Vente_B2B: Ventes entreprises (Date_Key, Id_Entreprise, Id_Produit, Quantite, Total_TTC)
- Fact_Vente_B2C: Ventes particuliers (Date_Key, Client_Key, Produit_Key, Montant_total_de_la_commande)
- Fact_Achat: Achats fournisseurs (date_key, id_fournisseur, id_produit, montant_ttc_facture)
- Fact_Livraison: Livraisons (Date_Key, Id_Entreprise, Id_Produit, Quantite)

DIMENSIONS:
- Dim_Entreprise: Clients B2B (Id_Client, Nom, Matricule_fiscal, Adresse)
- Dim_Client: Clients B2C (Client_Key, Nom, Prenom)
- Dim_Produit_Sougui: Catalogue produits artisanaux (Id_Produit, Nom, Categorie, PU_HT)
- Dim_Fournisseur: Fournisseurs (id_fournisseur, nom_fournisseur)
- Dim_Date: Calendrier (Date_Key format YYYYMMDD, Full_Date, Mois, Annee)

BUSINESS CONTEXT:
Sougui est une start-up tunisienne spécialisée dans l'artisanat moderne:
- Produits: Art de la table, décoration, céramiques, verres, sculptures, luminaires
- Segments: B2B (coffrets entreprises) et B2C (particuliers)
- Positionnement: Artisanat haut de gamme, éco-responsable, pièces uniques
"""
