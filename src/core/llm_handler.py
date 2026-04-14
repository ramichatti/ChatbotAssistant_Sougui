import ollama
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import OLLAMA_MODEL, DB_SCHEMA, SOUGUI_COLORS

class LLMHandler:
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.conversation_history = []
        
        # Business context for better responses
        self.business_context = """Tu es l'assistant IA de Sougui, start-up tunisienne d'artisanat haut de gamme.

CONTEXTE BUSINESS SOUGUI:
- Entreprise: Sougui - Artisanat tunisien moderne et éco-responsable
- Produits: Art de la table, décoration, céramiques artisanales, verres soufflés, sculptures, luminaires design
- Positionnement: Excellence artisanale, design contemporain, traditions ancestrales tunisiennes
- Segments: B2B (coffrets cadeaux entreprises, hôtellerie) et B2C (particuliers, collectionneurs)
- Valeurs: Qualité premium, authenticité, durabilité, savoir-faire artisanal
- Marché: Tunisie et export international (Europe, Moyen-Orient)

STYLE DE RÉPONSE REQUIS:
- Professionnel mais chaleureux et accessible
- Focus sur les insights business actionnables
- Recommandations stratégiques basées sur les données
- Langage e-commerce, retail et marketing
- Utilise des émojis pertinents pour la clarté (📊 💰 👥 🎨 📈 ✅ 🎯)
- Réponds TOUJOURS en français
- Sois concis et précis (3-5 phrases maximum)
- Mentionne les montants en TND (Dinars Tunisiens)

EXPERTISE:
- Analyse de performance commerciale
- Intelligence client et segmentation
- Optimisation de catalogue produits
- Stratégies de croissance et marketing
- Tendances du marché artisanal
"""
        
        # Predefined queries for instant responses - CORRECTED SQL
        self.quick_queries = {
            "revenue 2024": "SELECT SUM(Total_TTC) as Revenue FROM Fact_Vente_B2B WHERE Date_Key >= 20240101 AND Date_Key <= 20241231",
            "chiffre affaires 2024": "SELECT SUM(Total_TTC) as CA FROM Fact_Vente_B2B WHERE Date_Key >= 20240101 AND Date_Key <= 20241231",
            "revenue": "SELECT SUM(Total_TTC) as Total_Revenue FROM Fact_Vente_B2B",
            "chiffre affaires": "SELECT SUM(Total_TTC) as CA_Total FROM Fact_Vente_B2B",
            "top customers": "SELECT TOP 10 e.Nom as Customer_Name, COUNT(v.Num_facture) as Orders, SUM(v.Total_TTC) as Total_Sales FROM Dim_Entreprise e INNER JOIN Fact_Vente_B2B v ON e.Id_Client = v.Id_Entreprise GROUP BY e.Nom ORDER BY Total_Sales DESC",
            "best customers": "SELECT TOP 10 e.Nom as Customer_Name, COUNT(v.Num_facture) as Orders, SUM(v.Total_TTC) as Total_Sales FROM Dim_Entreprise e INNER JOIN Fact_Vente_B2B v ON e.Id_Client = v.Id_Entreprise GROUP BY e.Nom ORDER BY Total_Sales DESC",
            "clients b2b": "SELECT TOP 20 Nom as Company_Name, Matricule_fiscal as Tax_ID, Adresse as Address FROM Dim_Entreprise ORDER BY Nom",
            "best products": "SELECT TOP 10 p.Nom as Product_Name, p.Categorie as Category, COUNT(v.Id_Produit) as Sales_Count, SUM(v.Total_TTC) as Revenue FROM Dim_Produit_Sougui p INNER JOIN Fact_Vente_B2B v ON p.Id_Produit = v.Id_Produit GROUP BY p.Nom, p.Categorie ORDER BY Revenue DESC",
            "produits": "SELECT TOP 20 Nom as Product_Name, Categorie as Category, PU_HT as Price, En_Stock as In_Stock FROM Dim_Produit_Sougui ORDER BY Nom",
            "fournisseurs": "SELECT TOP 20 nom_fournisseur as Supplier_Name, telephone as Phone FROM Dim_Fournisseur ORDER BY nom_fournisseur",
            "ventes": "SELECT COUNT(*) as Total_Orders, SUM(Total_TTC) as Total_Revenue FROM Fact_Vente_B2B",
            "achats": "SELECT COUNT(*) as Total_Purchases, SUM(montant_ttc_facture) as Total_Amount FROM Fact_Achat"
        }
        
    def generate_sql_query(self, user_question):
        """Generate SQL query - IMPROVED WITH FALLBACKS"""
        # Check for quick queries first
        question_lower = user_question.lower()
        for key, query in self.quick_queries.items():
            if key in question_lower:
                print(f"Using predefined query for: {key}")
                return query
        
        # Try to generate SQL with LLM
        try:
            prompt = f"""Generate a valid SQL Server query for: {user_question}

Database Schema:
- Fact_Vente_B2B: Date_Key, Id_Entreprise, Id_Produit, Num_facture, Quantite, Total_TTC
- Dim_Entreprise: Id_Client, Nom, Matricule_fiscal, Adresse  
- Dim_Produit_Sougui: Id_Produit, Nom, Categorie, PU_HT, En_Stock
- Dim_Fournisseur: id_fournisseur, nom_fournisseur, telephone
- Fact_Achat: id_fournisseur, id_produit, montant_ttc_facture

Rules:
- Use TOP 20 for lists
- Use proper JOIN syntax
- Date_Key format: YYYYMMDD (20240101 for Jan 1, 2024)
- Always use aliases for readability

Examples:
customers -> SELECT TOP 20 Nom FROM Dim_Entreprise
revenue -> SELECT SUM(Total_TTC) FROM Fact_Vente_B2B  
products -> SELECT TOP 20 Nom, Categorie FROM Dim_Produit_Sougui

Generate ONLY the SQL query:"""

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.1,
                    "num_predict": 100
                }
            )
            
            sql = response['response'].strip()
            sql = sql.replace("```sql", "").replace("```", "").strip()
            
            # Clean and validate
            if sql.upper().startswith('SELECT'):
                return sql
            elif 'SELECT' in sql.upper():
                return sql[sql.upper().index('SELECT'):]
            else:
                raise Exception("No valid SELECT found")
                
        except Exception as e:
            print(f"SQL generation failed: {e}")
            # Fallback based on keywords
            return self.get_fallback_query(user_question)
    
    def get_fallback_query(self, question):
        """Get fallback query based on keywords"""
        q = question.lower()
        
        if any(word in q for word in ['customer', 'client', 'entreprise']):
            return "SELECT TOP 20 Nom as Company_Name, Adresse as Address FROM Dim_Entreprise ORDER BY Nom"
        elif any(word in q for word in ['product', 'produit']):
            return "SELECT TOP 20 Nom as Product_Name, Categorie as Category FROM Dim_Produit_Sougui ORDER BY Nom"
        elif any(word in q for word in ['revenue', 'chiffre', 'vente', 'sales']):
            return "SELECT COUNT(*) as Total_Orders, SUM(Total_TTC) as Total_Revenue FROM Fact_Vente_B2B"
        elif any(word in q for word in ['supplier', 'fournisseur']):
            return "SELECT TOP 20 nom_fournisseur as Supplier_Name FROM Dim_Fournisseur ORDER BY nom_fournisseur"
        else:
            return "SELECT TOP 20 Nom as Company_Name FROM Dim_Entreprise ORDER BY Nom"
    
    def explain_results(self, user_question, query_results):
        """Explain results with enhanced LLM + fallback"""
        if not query_results["success"]:
            return "❌ Impossible de récupérer les données. Une erreur de base de données s'est produite."
        
        row_count = query_results['row_count']
        
        if row_count == 0:
            return "📊 Aucune donnée trouvée pour votre requête. La base de données pourrait être vide ou vos critères ne correspondent à aucun enregistrement."
        
        # Format data for display
        cols = query_results['columns']
        data = query_results['data'][:10]  # First 10 rows for better context
        
        try:
            # Enhanced data formatting for LLM
            data_text = ""
            for i, row in enumerate(data, 1):
                data_text += f"Ligne {i}: "
                for col, val in zip(cols, row):
                    if isinstance(val, (int, float)) and val > 1000:
                        data_text += f"{col}={val:,.2f} TND, "
                    elif isinstance(val, float):
                        data_text += f"{col}={val:.2f}, "
                    else:
                        data_text += f"{col}={val}, "
                data_text = data_text.rstrip(", ") + "\n"
            
            # Enhanced prompt with business context
            prompt = f"""Tu es l'assistant IA de Sougui, expert en analyse business.

CONTEXTE SOUGUI:
- Entreprise tunisienne d'artisanat haut de gamme
- Produits: céramiques, verres, sculptures, luminaires, art de la table
- Segments: B2B (entreprises) et B2C (particuliers)
- Positionnement: artisanat moderne, éco-responsable, design contemporain

QUESTION CLIENT: {user_question}

DONNÉES ANALYSÉES ({row_count} enregistrements):
{data_text}

INSTRUCTIONS:
1. Analyse les chiffres clés et leur signification business
2. Identifie les tendances et insights importants
3. Donne 1-2 recommandations stratégiques concrètes
4. Utilise un ton professionnel mais chaleureux
5. Mentionne les montants en TND (Dinars Tunisiens)
6. Sois concis (3-4 phrases maximum)
7. Utilise des émojis pertinents (📊 💰 📈 ✅ 🎯)

RÉPONDS EN FRANÇAIS:"""

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.7,
                    "num_predict": 300,
                    "top_p": 0.9,
                    "top_k": 40
                }
            )
            
            explanation = response['response'].strip()
            
            # Validate response quality
            if explanation and len(explanation) > 30 and not explanation.startswith("I "):
                # Add data summary if response is good
                summary = f"\n\n📋 Résumé: {row_count} enregistrement(s) analysé(s)"
                return explanation + summary
            else:
                raise Exception("Low quality LLM response")
                
        except Exception as e:
            print(f"LLM explanation failed: {e}")
            # Fallback to enhanced structured display
            return self.format_fallback_response(user_question, query_results)
    
    def format_fallback_response(self, question, results):
        """Format an enhanced professional fallback response in French"""
        row_count = results['row_count']
        cols = results['columns']
        data = results['data'][:8]  # Show more data
        
        # Determine analysis type with emoji
        q = question.lower()
        if 'revenue' in q or 'chiffre' in q or 'vente' in q:
            header = "💰 ANALYSE DU CHIFFRE D'AFFAIRES"
            insight = "\n\n✅ Ces données reflètent la performance commerciale de Sougui. Les montants sont en TND (Dinars Tunisiens)."
        elif 'customer' in q or 'client' in q or 'entreprise' in q:
            header = "👥 ANALYSE CLIENTS B2B"
            insight = "\n\n✅ Voici votre portefeuille clients professionnels. Ces entreprises représentent vos partenaires commerciaux clés."
        elif 'product' in q or 'produit' in q:
            header = "🎨 ANALYSE PRODUITS ARTISANAUX"
            insight = "\n\n✅ Catalogue des créations artisanales Sougui. Chaque pièce reflète l'excellence de l'artisanat tunisien."
        elif 'fournisseur' in q or 'supplier' in q:
            header = "🤝 ANALYSE FOURNISSEURS"
            insight = "\n\n✅ Réseau de fournisseurs et partenaires artisanaux de Sougui."
        else:
            header = "📊 RÉSULTATS D'ANALYSE"
            insight = "\n\n✅ Données extraites de la base de données Sougui."
        
        response = f"{header}\n{'='*50}\n"
        response += f"📋 {row_count} enregistrement(s) trouvé(s)\n\n"
        
        # Format data with better presentation
        for i, row in enumerate(data, 1):
            response += f"▸ Ligne {i}:\n"
            for col, val in zip(cols[:5], row[:5]):  # Max 5 columns
                if isinstance(val, (int, float)):
                    if val > 1000:
                        response += f"  • {col}: {val:,.2f} TND\n"
                    elif isinstance(val, float):
                        response += f"  • {col}: {val:.2f}\n"
                    else:
                        response += f"  • {col}: {val}\n"
                else:
                    val_str = str(val)[:50]  # Truncate long strings
                    response += f"  • {col}: {val_str}\n"
            response += "\n"
        
        if row_count > 8:
            response += f"... et {row_count - 8} enregistrement(s) supplémentaire(s)\n"
        
        response += insight
        
        # Add strategic recommendation
        if 'revenue' in q or 'chiffre' in q:
            response += "\n\n🎯 Recommandation: Analysez les tendances mensuelles pour optimiser votre stratégie commerciale."
        elif 'customer' in q or 'client' in q:
            response += "\n\n🎯 Recommandation: Identifiez vos top clients pour développer des programmes de fidélisation."
        elif 'product' in q or 'produit' in q:
            response += "\n\n🎯 Recommandation: Concentrez-vous sur les produits les plus performants pour maximiser la rentabilité."
        
        return response
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []