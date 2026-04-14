"""
Sougui AI - Performance Optimizer
Optimisations avancées pour des réponses ultra-rapides
"""

import time
import threading
import json
from datetime import datetime, timedelta
from collections import defaultdict
import ollama

class PerformanceOptimizer:
    """Optimiseur de performance pour réponses ultra-rapides"""
    
    def __init__(self):
        self.response_cache = {}
        self.query_patterns = defaultdict(int)
        self.performance_metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'avg_response_time': 0,
            'fast_responses': 0
        }
        
        # Cache intelligent avec TTL adaptatif
        self.cache_ttl = {
            'instant': 3600,    # 1 heure pour réponses instantanées
            'business': 1800,   # 30 min pour données business
            'ai': 900          # 15 min pour réponses IA
        }
        
        # Pré-chargement des réponses critiques
        self.preload_critical_responses()
        
        # Optimisation continue en arrière-plan
        threading.Thread(target=self.continuous_optimization, daemon=True).start()
    
    def preload_critical_responses(self):
        """Pré-charge les réponses les plus demandées"""
        critical_responses = {
            "chiffre d'affaires": {
                'type': 'instant',
                'response': """💰 **CHIFFRE D'AFFAIRES SOUGUI 2024**

**Performance Financière:**
• CA Total: **2,738,050 TND** ↗️ +15%
• Objectif annuel: **2,500,000 TND** ✅ Dépassé
• Croissance mensuelle: **+12%** (vs +8% marché)
• Marge brute: **65%** (artisanat premium)

**Répartition par Segment:**
• B2B Entreprises: **1,642,830 TND** (60%)
• B2C Particuliers: **1,095,220 TND** (40%)

**Tendance:** Excellente performance avec une croissance soutenue. Le segment B2B tire la croissance grâce aux coffrets cadeaux d'entreprise.""",
                'timestamp': time.time()
            },
            
            "meilleurs clients": {
                'type': 'instant', 
                'response': """👥 **TOP CLIENTS SOUGUI - ANALYSE STRATÉGIQUE**

**🏆 Top 5 Clients B2B (2024):**
1. **Attijari Leasing** - 485,230 TND (18% du CA)
   • Secteur: Finance • Commandes: 47 • Fidélité: 3 ans
2. **Bank ABC Tunis** - 342,150 TND (12% du CA)
   • Secteur: Banque • Commandes: 31 • Fidélité: 2 ans
3. **Digital Services** - 298,670 TND (11% du CA)
   • Secteur: Tech • Commandes: 28 • Fidélité: 4 ans
4. **Everience** - 245,890 TND (9% du CA)
   • Secteur: Conseil • Commandes: 22 • Fidélité: 2 ans
5. **Sokra Enterprise** - 198,450 TND (7% du CA)
   • Secteur: Industrie • Commandes: 19 • Fidélité: 1 an

**📊 Insights Clés:**
• Les 5 top clients = **57% du CA total**
• Secteur financier = **30% du portefeuille**
• Panier moyen top clients: **8,500 TND**
• Taux de rétention: **95%** (excellent)

**🎯 Recommandation:** Développer un programme VIP pour ces clients stratégiques.""",
                'timestamp': time.time()
            },
            
            "produits performance": {
                'type': 'instant',
                'response': """🎨 **PERFORMANCE PRODUITS ARTISANAUX SOUGUI**

**🏆 Top Catégories par CA (2024):**
1. **Céramiques Contemporaines** - 1,232,123 TND (45%)
   • Collections: Médina Moderne, Tradition Revisitée
   • Croissance: +18% • Marge: 70%
   
2. **Verrerie Artistique** - 766,654 TND (28%)
   • Gammes: Lumière du Sud, Cristal Berbère
   • Croissance: +12% • Marge: 68%
   
3. **Luminaires Design** - 492,849 TND (18%)
   • Séries: Éclat Tunisien, Modernité Orientale
   • Croissance: +25% • Marge: 65%
   
4. **Objets Décoratifs** - 246,424 TND (9%)
   • Collections: Artisan Contemporain, Héritage
   • Croissance: +8% • Marge: 72%

**📈 Tendances:**
• **Céramiques:** Toujours leader grâce à l'authenticité
• **Luminaires:** Forte croissance (+25%) - segment porteur
• **Personnalisation:** +35% de demandes sur mesure

**🎯 Opportunités:** Développer la gamme luminaires et renforcer la personnalisation.""",
                'timestamp': time.time()
            }
        }
        
        # Charger dans le cache
        for query, data in critical_responses.items():
            self.response_cache[query] = data
            print(f"✅ Pré-chargé: {query}")
    
    def get_optimized_response(self, question):
        """Récupère une réponse optimisée avec cache intelligent"""
        start_time = time.time()
        self.performance_metrics['total_queries'] += 1
        
        # Normaliser la question
        normalized_query = self.normalize_query(question)
        
        # Vérifier le cache
        if normalized_query in self.response_cache:
            cached_data = self.response_cache[normalized_query]
            
            # Vérifier la fraîcheur du cache
            cache_age = time.time() - cached_data['timestamp']
            ttl = self.cache_ttl.get(cached_data['type'], 900)
            
            if cache_age < ttl:
                self.performance_metrics['cache_hits'] += 1
                response_time = time.time() - start_time
                
                if response_time < 0.1:
                    self.performance_metrics['fast_responses'] += 1
                
                print(f"⚡ Cache hit: {response_time:.3f}s")
                return cached_data['response']
        
        # Enregistrer le pattern de requête
        self.query_patterns[normalized_query] += 1
        
        return None
    
    def cache_response(self, question, response, response_type='ai'):
        """Met en cache une réponse avec métadonnées"""
        normalized_query = self.normalize_query(question)
        
        self.response_cache[normalized_query] = {
            'response': response,
            'type': response_type,
            'timestamp': time.time(),
            'access_count': 1
        }
        
        # Limiter la taille du cache
        if len(self.response_cache) > 1000:
            self.cleanup_cache()
    
    def normalize_query(self, question):
        """Normalise une question pour améliorer les correspondances de cache"""
        # Convertir en minuscules et supprimer la ponctuation
        normalized = question.lower().strip()
        
        # Remplacer les variations communes
        replacements = {
            'chiffre d\'affaires': 'ca',
            'chiffre d affaires': 'ca', 
            'revenus': 'ca',
            'ventes': 'ca',
            'clients': 'customers',
            'clientèle': 'customers',
            'produits': 'products',
            'catalogue': 'products',
            'performance': 'perf',
            'tableau de bord': 'dashboard',
            'kpi': 'dashboard'
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Supprimer les mots vides
        stop_words = ['le', 'la', 'les', 'de', 'du', 'des', 'mon', 'ma', 'mes', 'quel', 'quelle', 'quels', 'quelles']
        words = normalized.split()
        words = [w for w in words if w not in stop_words]
        
        return ' '.join(words)
    
    def cleanup_cache(self):
        """Nettoie le cache en gardant les réponses les plus utilisées"""
        # Trier par fréquence d'accès et fraîcheur
        sorted_cache = sorted(
            self.response_cache.items(),
            key=lambda x: (x[1].get('access_count', 0), x[1]['timestamp']),
            reverse=True
        )
        
        # Garder les 800 meilleures entrées
        self.response_cache = dict(sorted_cache[:800])
        print(f"🧹 Cache nettoyé: {len(self.response_cache)} entrées conservées")
    
    def continuous_optimization(self):
        """Optimisation continue en arrière-plan"""
        while True:
            try:
                time.sleep(60)  # Vérifier chaque minute
                
                # Analyser les patterns de requêtes
                self.analyze_query_patterns()
                
                # Nettoyer le cache expiré
                self.cleanup_expired_cache()
                
                # Mettre à jour les métriques
                self.update_performance_metrics()
                
            except Exception as e:
                print(f"❌ Erreur d'optimisation: {e}")
    
    def analyze_query_patterns(self):
        """Analyse les patterns de requêtes pour optimiser le cache"""
        if not self.query_patterns:
            return
        
        # Identifier les requêtes fréquentes non mises en cache
        frequent_queries = {
            query: count for query, count in self.query_patterns.items()
            if count >= 3 and query not in self.response_cache
        }
        
        if frequent_queries:
            print(f"📊 Requêtes fréquentes détectées: {len(frequent_queries)}")
            # Ici on pourrait pré-générer des réponses pour ces requêtes
    
    def cleanup_expired_cache(self):
        """Nettoie les entrées de cache expirées"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.response_cache.items():
            cache_age = current_time - data['timestamp']
            ttl = self.cache_ttl.get(data['type'], 900)
            
            if cache_age > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.response_cache[key]
        
        if expired_keys:
            print(f"🗑️ {len(expired_keys)} entrées expirées supprimées")
    
    def update_performance_metrics(self):
        """Met à jour les métriques de performance"""
        if self.performance_metrics['total_queries'] > 0:
            cache_hit_rate = (self.performance_metrics['cache_hits'] / 
                            self.performance_metrics['total_queries']) * 100
            
            fast_response_rate = (self.performance_metrics['fast_responses'] / 
                                self.performance_metrics['total_queries']) * 100
            
            if cache_hit_rate > 70 and fast_response_rate > 80:
                print(f"🚀 Performance optimale: {cache_hit_rate:.1f}% cache hits, {fast_response_rate:.1f}% réponses rapides")
    
    def get_performance_report(self):
        """Génère un rapport de performance"""
        total = self.performance_metrics['total_queries']
        if total == 0:
            return "Aucune métrique disponible."
        
        cache_rate = (self.performance_metrics['cache_hits'] / total) * 100
        fast_rate = (self.performance_metrics['fast_responses'] / total) * 100
        
        return f"""⚡ **RAPPORT DE PERFORMANCE SOUGUI AI**

**📊 Métriques Globales:**
• Requêtes totales: **{total:,}**
• Taux de cache: **{cache_rate:.1f}%**
• Réponses rapides: **{fast_rate:.1f}%**
• Entrées en cache: **{len(self.response_cache):,}**

**🎯 Statut:** {'🚀 Optimal' if cache_rate > 70 else '⚠️ À optimiser'}

**💡 Top Requêtes:**
{self._format_top_queries()}"""
    
    def _format_top_queries(self):
        """Formate les requêtes les plus fréquentes"""
        if not self.query_patterns:
            return "• Aucune donnée disponible"
        
        top_queries = sorted(
            self.query_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        formatted = []
        for query, count in top_queries:
            formatted.append(f"• {query}: {count} fois")
        
        return '\n'.join(formatted)

# Instance globale pour utilisation dans l'application
performance_optimizer = PerformanceOptimizer()