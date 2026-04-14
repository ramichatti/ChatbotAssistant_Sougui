"""
Sougui AI - Ollama Optimizer
Optimisations spécifiques pour améliorer les performances d'Ollama
"""

import ollama
import time
import threading
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import OLLAMA_MODEL

class OllamaOptimizer:
    """Optimiseur spécialisé pour Ollama LLM"""
    
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.model_loaded = False
        self.optimization_active = False
        
        # Paramètres optimisés pour différents types de requêtes
        self.optimized_params = {
            'instant': {
                'temperature': 0.3,
                'num_predict': 150,
                'top_k': 20,
                'top_p': 0.7,
                'repeat_penalty': 1.05,
                'num_ctx': 2048
            },
            'business': {
                'temperature': 0.5,
                'num_predict': 250,
                'top_k': 30,
                'top_p': 0.8,
                'repeat_penalty': 1.1,
                'num_ctx': 4096
            },
            'detailed': {
                'temperature': 0.7,
                'num_predict': 400,
                'top_k': 40,
                'top_p': 0.9,
                'repeat_penalty': 1.15,
                'num_ctx': 4096
            }
        }
        
        # Prompts optimisés pour différents contextes
        self.optimized_prompts = {
            'sougui_context': """Tu es l'Assistant IA de Sougui, expert en artisanat tunisien et intelligence business.

CONTEXTE SOUGUI:
- Entreprise tunisienne d'artisanat haut de gamme depuis 2018
- Spécialités: céramiques contemporaines, verrerie artistique, luminaires design
- Segments: B2B (60% CA) coffrets entreprises, B2C (40% CA) particuliers
- Performance 2024: 2,738,050 TND CA (+15%), 150+ clients, 85% rétention
- Positionnement: Excellence artisanale, design moderne, éco-responsabilité

EXPERTISE:
- Analyse financière et KPIs business
- Intelligence client et segmentation
- Performance produits et tendances marché
- Stratégies de croissance et recommandations
- Connaissance approfondie de l'artisanat tunisien

STYLE DE RÉPONSE:
- Professionnel mais chaleureux et accessible
- Concis et actionnable (2-4 phrases optimales)
- Utilise émojis business pertinents (📊 💰 👥 🎨 📈 ✅ 🎯)
- Mentionne montants en TND (Dinars Tunisiens)
- Focus sur insights et recommandations concrètes
- TOUJOURS en français sauf demande contraire""",

            'quick_analysis': """Analyse rapide et professionnelle requise.
Contexte: Sougui - artisanat tunisien premium.
Style: Concis, données chiffrées, recommandations.
Langue: Français. Émojis business appropriés.""",

            'financial_context': """Expert financier Sougui. CA 2024: 2,738,050 TND.
Segments: B2B 60%, B2C 40%. Croissance +15%.
Analyse: Chiffres clés, tendances, recommandations.
Format: Professionnel, concis, émojis 💰📊📈."""
        }
        
        # Initialiser l'optimisation
        self.initialize_optimization()
    
    def initialize_optimization(self):
        """Initialise les optimisations Ollama"""
        threading.Thread(target=self._preload_model, daemon=True).start()
        threading.Thread(target=self._warm_up_model, daemon=True).start()
    
    def _preload_model(self):
        """Pré-charge le modèle Ollama pour des réponses plus rapides"""
        try:
            print(f"🚀 Pré-chargement du modèle {self.model}...")
            
            # Test de connectivité et pré-chargement
            response = ollama.generate(
                model=self.model,
                prompt="Test de pré-chargement",
                options=self.optimized_params['instant']
            )
            
            if response:
                self.model_loaded = True
                print(f"✅ Modèle {self.model} pré-chargé avec succès")
            
        except Exception as e:
            print(f"❌ Erreur de pré-chargement: {e}")
            self.model_loaded = False
    
    def _warm_up_model(self):
        """Réchauffe le modèle avec des requêtes d'exemple"""
        if not self.model_loaded:
            return
        
        try:
            print("🔥 Réchauffage du modèle avec requêtes d'exemple...")
            
            warm_up_queries = [
                "Bonjour, je suis l'assistant Sougui.",
                "Analyse rapide des ventes.",
                "Performance des produits artisanaux."
            ]
            
            for query in warm_up_queries:
                ollama.generate(
                    model=self.model,
                    prompt=f"{self.optimized_prompts['quick_analysis']}\n\nQuestion: {query}",
                    options=self.optimized_params['instant']
                )
                time.sleep(0.5)
            
            print("✅ Modèle réchauffé - prêt pour des réponses ultra-rapides")
            self.optimization_active = True
            
        except Exception as e:
            print(f"❌ Erreur de réchauffage: {e}")
    
    def generate_optimized_response(self, question, context_type='business'):
        """Génère une réponse optimisée selon le type de contexte"""
        if not self.model_loaded:
            raise Exception("Modèle non chargé")
        
        # Sélectionner les paramètres optimaux
        params = self.optimized_params.get(context_type, self.optimized_params['business'])
        
        # Construire le prompt optimisé
        prompt = self._build_optimized_prompt(question, context_type)
        
        try:
            start_time = time.time()
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options=params
            )
            
            generation_time = time.time() - start_time
            
            if generation_time < 2.0:
                print(f"⚡ Réponse optimisée: {generation_time:.3f}s")
            else:
                print(f"⚠️ Réponse lente: {generation_time:.3f}s")
            
            return response['response'].strip()
            
        except Exception as e:
            print(f"❌ Erreur génération optimisée: {e}")
            raise
    
    def _build_optimized_prompt(self, question, context_type):
        """Construit un prompt optimisé selon le contexte"""
        base_context = self.optimized_prompts['sougui_context']
        
        # Adapter selon le type de question
        q_lower = question.lower()
        
        if any(word in q_lower for word in ['ca', 'chiffre', 'revenue', 'ventes', 'financier']):
            context_addon = "\n\nSPÉCIALISATION: Analyse financière et performance commerciale."
        elif any(word in q_lower for word in ['client', 'customer', 'entreprise']):
            context_addon = "\n\nSPÉCIALISATION: Intelligence client et analyse de portefeuille."
        elif any(word in q_lower for word in ['produit', 'product', 'artisanat', 'céramique']):
            context_addon = "\n\nSPÉCIALISATION: Performance produits et expertise artisanale."
        else:
            context_addon = "\n\nSPÉCIALISATION: Conseil business général et stratégie."
        
        return f"""{base_context}{context_addon}

Question: {question}

Réponds de manière experte, concise et professionnelle:"""
    
    def get_model_status(self):
        """Retourne le statut du modèle"""
        return {
            'model': self.model,
            'loaded': self.model_loaded,
            'optimized': self.optimization_active,
            'status': '🚀 Optimal' if self.optimization_active else '⚠️ En cours d\'optimisation'
        }
    
    def benchmark_performance(self):
        """Teste les performances du modèle"""
        if not self.model_loaded:
            return "Modèle non disponible pour le benchmark"
        
        test_questions = [
            "Quel est le chiffre d'affaires?",
            "Qui sont les meilleurs clients?",
            "Performance des produits?"
        ]
        
        results = []
        
        for question in test_questions:
            try:
                start_time = time.time()
                response = self.generate_optimized_response(question, 'instant')
                response_time = time.time() - start_time
                
                results.append({
                    'question': question,
                    'time': response_time,
                    'success': True,
                    'length': len(response)
                })
                
            except Exception as e:
                results.append({
                    'question': question,
                    'time': 0,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculer les statistiques
        successful_tests = [r for r in results if r['success']]
        if successful_tests:
            avg_time = sum(r['time'] for r in successful_tests) / len(successful_tests)
            avg_length = sum(r['length'] for r in successful_tests) / len(successful_tests)
            
            return f"""⚡ **BENCHMARK OLLAMA SOUGUI AI**

**📊 Résultats:**
• Tests réussis: **{len(successful_tests)}/{len(results)}**
• Temps moyen: **{avg_time:.3f}s**
• Longueur moyenne: **{avg_length:.0f} caractères**
• Performance: **{'🚀 Excellente' if avg_time < 2.0 else '⚠️ À améliorer'}**

**🎯 Statut:** {'Optimisé pour production' if avg_time < 2.0 else 'Optimisation requise'}"""
        
        return "❌ Aucun test réussi - vérifier la configuration Ollama"

# Instance globale
ollama_optimizer = OllamaOptimizer()