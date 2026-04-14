"""
SmartAssistant — ChatGPT-like local assistant for Sougui DWH.
Answers ANY question. For data questions, queries the real DB first.
"""

import ollama
import threading
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_handler import DatabaseHandler
from core.config import OLLAMA_MODEL, DB_SCHEMA

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es Sougui AI, l'assistant intelligent de Sougui — une start-up tunisienne d'artisanat haut de gamme.

## Ton rôle
Tu réponds à TOUTES les questions en langage humain naturel, comme un conseiller expert qui parle à un dirigeant d'entreprise. Tu peux répondre à n'importe quelle question : business, général, technique, culturel, etc.

## Contexte Sougui
- Produits : céramiques contemporaines, verrerie artistique, luminaires design, objets décoratifs
- Segments : B2B (coffrets cadeaux entreprises, hôtellerie) et B2C (particuliers, collectionneurs)
- Positionnement : artisanat premium, éco-responsable, design moderne alliant tradition tunisienne
- Montants toujours en TND (Dinars Tunisiens)

## RÈGLES ABSOLUES DE RÉPONSE
1. JAMAIS de SQL, de noms de tables, de noms de colonnes dans ta réponse
2. JAMAIS de termes techniques comme "Fact_Vente_B2B", "Date_Key", "Id_Entreprise", etc.
3. Si tu as des données réelles, présente-les comme un analyste humain : "Vos ventes totales s'élèvent à...", "Votre meilleur client est..."
4. Réponds dans la langue de l'utilisateur (français par défaut)
5. Sois chaleureux, précis et actionnable — comme un conseiller business de confiance
6. Utilise du markdown pour structurer : **gras**, ## titres, listes à puces
7. Donne toujours une conclusion ou recommandation concrète
"""

SQL_PROMPT = """Tu es un expert SQL Server. Génère UNE SEULE requête SQL valide pour SQL Server.

Schéma Sougui_DWH :
{schema}

Question : {question}

Règles strictes :
- SQL Server syntax uniquement (pas MySQL, pas PostgreSQL)
- Utilise TOP 50 pour les listes longues
- Date_Key format YYYYMMDD entier (ex: 20240101)
- Joins explicites avec ON
- Aliases lisibles en français
- Agrégations avec GROUP BY correct
- Retourne UNIQUEMENT la requête SQL brute, sans markdown, sans explication

SQL:"""


class SmartAssistant:
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.db_handler = DatabaseHandler()
        self.db_connected = False
        self.conversation_history = []  # Full chat history for context

        self.total_queries = 0
        self.response_times = []

        self.init_database()
        threading.Thread(target=self._preload_model, daemon=True).start()

    # ── Init ───────────────────────────────────────────────────────────────────

    def init_database(self):
        for attempt in range(3):
            try:
                self.db_connected = self.db_handler.connect()
                if self.db_connected:
                    print(f"✅ Database connected successfully (attempt {attempt + 1})")
                    return
                time.sleep(0.5)
            except Exception as e:
                print(f"Database connection error (attempt {attempt + 1}): {e}")
                time.sleep(0.5)

    def _preload_model(self):
        try:
            print(f"🚀 Pré-chargement du modèle {self.model}...")
            ollama.generate(model=self.model, prompt="ok", options={"num_predict": 1})
            print(f"✅ Modèle {self.model} pré-chargé avec succès")
        except Exception as e:
            print(f"❌ Erreur de pré-chargement: {e}")

    # ── SQL pipeline ───────────────────────────────────────────────────────────

    def _needs_db(self, question: str) -> bool:
        """Detect if question likely needs real DB data."""
        keywords = [
            "chiffre", "ca ", " ca", "revenue", "vente", "sale", "montant", "total",
            "client", "customer", "entreprise", "acheteur", "b2b", "b2c",
            "produit", "product", "article", "stock", "catalogue",
            "fournisseur", "supplier", "achat", "livraison", "commande", "order",
            "combien", "liste", "top ", "meilleur", "plus grand", "plus petit",
            "kpi", "dashboard", "performance", "statistique", "analyse", "rapport",
            "2024", "2023", "2022", "mois", "année", "trimestre", "semaine",
            "croissance", "évolution", "tendance", "comparaison"
        ]
        q = question.lower()
        return any(k in q for k in keywords)

    def _generate_sql(self, question: str) -> str | None:
        """Use Ollama to write a SQL Server query."""
        prompt = SQL_PROMPT.format(schema=DB_SCHEMA, question=question)
        try:
            resp = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.05, "num_predict": 500, "num_ctx": 4096}
            )
            sql = resp["response"].strip()
            # Strip markdown fences
            for fence in ["```sql", "```SQL", "```"]:
                sql = sql.replace(fence, "")
            sql = sql.strip()
            # Extract from SELECT onwards
            upper = sql.upper()
            if "SELECT" in upper:
                return sql[upper.index("SELECT"):]
        except Exception as e:
            print(f"SQL generation error: {e}")
        return None

    def _run_query(self, sql: str) -> dict | None:
        if not self.db_connected or not sql:
            return None
        try:
            result = self.db_handler.execute_query(sql)
            if result.get("success") and result.get("row_count", 0) > 0:
                return result
            if result.get("success") and result.get("row_count", 0) == 0:
                return {"empty": True}
        except Exception as e:
            print(f"Query execution error: {e}")
        return None

    def _format_results(self, result: dict) -> str:
        """Format DB rows as human-readable context for the LLM — no SQL, no column names."""
        cols = result["columns"]
        rows = result["data"][:30]
        total = result["row_count"]

        lines = [f"Voici les données réelles extraites de la base Sougui ({total} résultats) :"]
        lines.append("")

        for i, row in enumerate(rows, 1):
            parts = []
            for col, val in zip(cols, row):
                # Clean up column name to be human-readable
                label = col.replace("_", " ").replace("  ", " ").strip()
                if isinstance(val, float):
                    parts.append(f"{label} : {val:,.2f} TND")
                elif isinstance(val, int) and val > 1000:
                    parts.append(f"{label} : {val:,}")
                elif val is None:
                    parts.append(f"{label} : non renseigné")
                else:
                    parts.append(f"{label} : {val}")
            lines.append(f"  {i}. " + " | ".join(parts))

        if total > 30:
            lines.append(f"  ... et {total - 30} résultats supplémentaires")

        lines.append("")
        lines.append("Utilise ces données pour répondre en langage naturel. Ne mentionne JAMAIS les noms de tables ou colonnes SQL.")
        return "\n".join(lines)

    # ── Main answer method ─────────────────────────────────────────────────────

    def answer_question(self, question: str, callback):
        """Non-blocking: process in thread, call callback(answer) when done."""
        self.total_queries += 1
        threading.Thread(
            target=self._process,
            args=(question, callback),
            daemon=True
        ).start()

    def _process(self, question: str, callback):
        start = time.time()
        db_section = ""

        try:
            # ── Step 1: Try to get real DB data ───────────────────────────
            if self._needs_db(question) and self.db_connected:
                print(f"📊 Generating SQL for: {question[:60]}...")
                sql = self._generate_sql(question)
                if sql:
                    print(f"📊 SQL: {sql[:150]}")
                    result = self._run_query(sql)
                    if result and not result.get("empty"):
                        db_section = self._format_results(result)
                        print(f"✅ DB: {result['row_count']} rows fetched")
                    elif result and result.get("empty"):
                        db_section = "La recherche dans la base de données n'a retourné aucun résultat pour cette question. Réponds en te basant sur ta connaissance générale de Sougui."
                    else:
                        db_section = "La base de données n'a pas pu être interrogée. Réponds en te basant sur ta connaissance générale de Sougui."

            # ── Step 2: Build messages ─────────────────────────────────────
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Inject DB data as a system context message — never shown to user
            if db_section:
                messages.append({
                    "role": "system",
                    "content": db_section
                })

            for msg in self.conversation_history[-20:]:
                messages.append(msg)

            # User question — clean, no raw data appended
            messages.append({"role": "user", "content": question})

            # ── Step 3: Stream response token by token ─────────────────────
            full_answer = ""
            stream = ollama.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={
                    "temperature": 0.7,
                    "num_predict": -1,
                    "num_ctx": 8192,
                    "top_k": 40,
                    "top_p": 0.9,
                    "repeat_penalty": 1.05,
                }
            )

            for chunk in stream:
                token = chunk["message"]["content"]
                full_answer += token
                # Stream each token to UI
                callback(full_answer, streaming=True)

            # ── Step 4: Final callback + history ──────────────────────────
            callback(full_answer, streaming=False)

            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": full_answer})
            if len(self.conversation_history) > 40:
                self.conversation_history = self.conversation_history[-40:]

            elapsed = time.time() - start
            self.response_times.append(elapsed)
            print(f"🤖 Ollama: {elapsed:.1f}s | {len(full_answer)} chars")

        except Exception as e:
            print(f"Processing error: {e}")
            import traceback
            traceback.print_exc()
            callback(
                f"Désolé, une erreur s'est produite.\n\nDétail : {str(e)}\n\n"
                "Vérifiez qu'Ollama est démarré et réessayez.",
                streaming=False
            )

    def reset_conversation(self):
        """Clear conversation history (new session)."""
        self.conversation_history = []

    def get_performance_stats(self):
        if not self.response_times:
            return "Aucune statistique disponible."
        avg = sum(self.response_times) / len(self.response_times)
        return (
            f"Requêtes : {self.total_queries}\n"
            f"Temps moyen : {avg:.1f}s\n"
            f"DB : {'connectée' if self.db_connected else 'non connectée'}\n"
            f"Modèle : {self.model}\n"
            f"Historique : {len(self.conversation_history)//2} échanges"
        )
