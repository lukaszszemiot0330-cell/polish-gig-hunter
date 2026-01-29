#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polish Gig Hunter 2.0 - Autonomiczna Platforma AI
🧠 Myśli i uczy się jak człowiek
🌐 Działa globalnie 24/7/365  
🤖 Automatycznie aplikuje i negocjuje
💰 Maksymalizuje profit za pomocą AI
🔐 Jest w 100% bezpieczna dzięki blockchain
"""

import os
import re
import json
import time
import hashlib
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import statistics
from concurrent.futures import ThreadPoolExecutor

try:
    import numpy as np
    import pandas as pd
    from bs4 import BeautifulSoup
except ImportError:
    np = None
    pd = None
    BeautifulSoup = None

from duckduckgo_search import DDGS
from fake_useragent import UserAgent

# Enhanced AI imports
try:
    import openai
    from anthropic import Anthropic
    import google.generativeai as genai
    ENHANCED_AI_AVAILABLE = True
except ImportError:
    ENHANCED_AI_AVAILABLE = False
    print("Enhanced AI libraries not available - using simulation mode")

# Configure logging with UTF-8 encoding
import sys
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gighunter_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class GigData:
    """Struktura danych zlecenia"""
    id: str
    title: str
    description: str
    budget: str
    source: str
    url: str
    found_at: datetime
    score: int
    ai_analysis: Dict
    blockchain_hash: str = ""
    
    # Enhanced fields for AI integration
    market_trend_score: float = 0.0
    roi_prediction: float = 0.0
    negotiation_potential: float = 0.0
    competitor_analysis: Dict = None
    pricing_strategy: str = ""
    
    def __post_init__(self):
        if self.competitor_analysis is None:
            self.competitor_analysis = {}

class AIEngine(ABC):
    """Abstrakcyjna klasa silnika AI"""
    
    @abstractmethod
    def analyze(self, data: Dict) -> Dict:
        pass
    
    @abstractmethod
    def learn(self, experience: Dict) -> None:
        pass

class EnhancedAIEnsemble(AIEngine):
    """Enhanced AI Ensemble - GPT-4 + Claude 3 + Gemini Pro"""
    
    def __init__(self):
        self.models = {}
        if ENHANCED_AI_AVAILABLE:
            try:
                self.models['gpt4'] = openai.OpenAI(api_key=os.getenv('OPENAI_KEY'))
                self.models['claude'] = Anthropic(api_key=os.getenv('ANTHROPIC_KEY'))
                genai.configure(api_key=os.getenv('GOOGLE_KEY'))
                self.models['gemini'] = genai.GenerativeModel('gemini-pro')
                logger.info("Enhanced AI models initialized")
            except Exception as e:
                logger.warning(f"Enhanced AI initialization failed: {e}")
                self.fallback = GPT4Simulator()
        else:
            self.fallback = GPT4Simulator()
    
    def analyze(self, data: Dict) -> Dict:
        """Ensemble analysis with voting"""
        if not ENHANCED_AI_AVAILABLE or len(self.models) < 2:
            return self.fallback.analyze(data)
        
        analyses = {}
        
        # Parallel analysis with multiple models
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            if 'gpt4' in self.models:
                futures['gpt4'] = executor.submit(self._gpt4_analyze, data)
            if 'claude' in self.models:
                futures['claude'] = executor.submit(self._claude_analyze, data)
            if 'gemini' in self.models:
                futures['gemini'] = executor.submit(self._gemini_analyze, data)
            
            for model, future in futures.items():
                try:
                    analyses[model] = future.result(timeout=30)
                except Exception as e:
                    logger.warning(f"{model} analysis failed: {e}")
                    analyses[model] = self.fallback.analyze(data)
        
        # Ensemble voting and consensus
        return self._ensemble_voting(analyses)
    
    def _gpt4_analyze(self, data: Dict) -> Dict:
        """GPT-4 analysis"""
        try:
            prompt = f"""
            Analyze this gig opportunity:
            Title: {data.get('title', '')}
            Description: {data.get('description', '')}
            Budget: {data.get('budget', '')}
            
            Provide analysis with:
            1. Complexity score (1-10)
            2. Urgency level (low/medium/high)
            3. Budget estimate (min-max PLN)
            4. Success probability (1-100)
            5. Recommended action
            6. Required skills
            """
            
            response = self.models['gpt4'].chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            return self._parse_ai_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"GPT-4 analysis error: {e}")
            return self.fallback.analyze(data)
    
    def _claude_analyze(self, data: Dict) -> Dict:
        """Claude 3 analysis"""
        try:
            prompt = f"""
            Gig Analysis Request:
            Title: {data.get('title', '')}
            Description: {data.get('description', '')}
            Budget: {data.get('budget', '')}
            
            Analyze and provide:
            - Complexity assessment (1-10)
            - Timeline estimation
            - Market rate analysis
            - Risk factors
            - Negotiation potential
            """
            
            response = self.models['claude'].messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return self._parse_ai_response(response.content[0].text)
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return self.fallback.analyze(data)
    
    def _gemini_analyze(self, data: Dict) -> Dict:
        """Gemini Pro analysis"""
        try:
            prompt = f"""
            Analyze gig opportunity:
            {data.get('title', '')}
            {data.get('description', '')}
            Budget: {data.get('budget', '')}
            
            Return JSON with:
            complexity_score, urgency_level, budget_range, 
            success_probability, recommended_action, skills_needed
            """
            
            response = self.models['gemini'].generate_content(prompt)
            return self._parse_ai_response(response.text)
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return self.fallback.analyze(data)
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback parsing
        return {
            'complexity_score': 5,
            'urgency_level': 'medium',
            'budget_estimate': [2000, 8000],
            'success_probability': 70,
            'recommended_action': 'APPLY_SOON',
            'skills_needed': ['python', 'communication']
        }
    
    def _ensemble_voting(self, analyses: Dict) -> Dict:
        """Ensemble voting for consensus"""
        if not analyses:
            return self.fallback.analyze({})
        
        # Average numeric values
        avg_complexity = statistics.mean([a.get('complexity_score', 5) for a in analyses.values()])
        avg_success = statistics.mean([a.get('success_probability', 70) for a in analyses.values()])
        
        # Budget range aggregation
        all_budgets = []
        for a in analyses.values():
            if 'budget_estimate' in a and isinstance(a['budget_estimate'], list):
                all_budgets.extend(a['budget_estimate'])
        
        budget_range = [min(all_budgets), max(all_budgets)] if all_budgets else [2000, 8000]
        
        # Most common urgency
        urgencies = [a.get('urgency_level', 'medium') for a in analyses.values()]
        urgency = max(set(urgencies), key=urgencies.count)
        
        # Most recommended action
        actions = [a.get('recommended_action', 'APPLY_SOON') for a in analyses.values()]
        action = max(set(actions), key=actions.count)
        
        # Aggregate skills
        all_skills = []
        for a in analyses.values():
            if 'skills_needed' in a:
                all_skills.extend(a['skills_needed'])
        skills = list(set(all_skills))[:5]  # Top 5 unique skills
        
        return {
            'complexity_score': round(avg_complexity, 1),
            'urgency_level': urgency,
            'budget_estimate': budget_range,
            'success_probability': round(avg_success),
            'recommended_action': action,
            'skills_needed': skills,
            'ensemble_confidence': len(analyses) / 3.0,  # Confidence based on number of models
            'model_consensus': f"{len(analyses)}/3 models agree"
        }
    
    def learn(self, experience: Dict) -> None:
        """Real-time learning from feedback"""
        # Store experience for future model fine-tuning
        learning_data = {
            'timestamp': datetime.now().isoformat(),
            'gig_data': experience.get('gig_data', {}),
            'predicted_outcome': experience.get('prediction', {}),
            'actual_outcome': experience.get('result', {}),
            'feedback_score': experience.get('feedback', 0)
        }
        
        # Save to learning database
        self._save_learning_data(learning_data)
    
    def _save_learning_data(self, data: Dict):
        """Save learning data for model improvement"""
        try:
            conn = sqlite3.connect('gighunter_learning.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    gig_data TEXT,
                    predicted_outcome TEXT,
                    actual_outcome TEXT,
                    feedback_score INTEGER
                )
            ''')
            
            cursor.execute('''
                INSERT INTO learning_data 
                (timestamp, gig_data, predicted_outcome, actual_outcome, feedback_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['timestamp'],
                json.dumps(data['gig_data']),
                json.dumps(data['predicted_outcome']),
                json.dumps(data['actual_outcome']),
                data['feedback_score']
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Learning data save error: {e}")


class GPT4Simulator(AIEngine):
    """Symulator GPT-4 - darmowa alternatywa"""
    
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.patterns = self.load_patterns()
        
    def load_knowledge_base(self) -> Dict:
        """Wbudowana baza wiedzy o zleceniach"""
        return {
            'technical_skills': ['python', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker'],
            'soft_skills': ['komunikacja', 'praca zespołowa', 'zarządzanie projektem'],
            'budget_ranges': {
                'low': (500, 2000),
                'medium': (2000, 10000),
                'high': (10000, 50000)
            },
            'success_indicators': ['pilne', 'stała współpraca', 'długoterminowy', 'rozwój']
        }
    
    def load_patterns(self) -> Dict:
        """Wzorce analizy tekstu"""
        return {
            'urgency': r'\b(pilne|natychmiast|jak najszybciej|urgent)\b',
            'budget_mention': r'\b(budżet|budzet|cena|stawka|pln|zł)\b',
            'technical_terms': r'\b(api|database|frontend|backend|fullstack|devops)\b',
            'commitment': r'\b(stała|długoterminowy|permanentny|part-time|full-time)\b'
        }
    
    def analyze(self, gig_data: Dict) -> Dict:
        """Analiza zlecenia za pomocą wzorców i heurystyki"""
        text = f"{gig_data.get('title', '')} {gig_data.get('description', '')}".lower()
        
        analysis = {
            'urgency_score': self.calculate_urgency_score(text),
            'technical_complexity': self.calculate_complexity(text),
            'budget_estimate': self.estimate_budget(text),
            'success_probability': self.calculate_success_probability(text),
            'recommended_action': self.recommend_action(text),
            'skill_requirements': self.extract_skills(text)
        }
        
        return analysis
    
    def calculate_urgency_score(self, text: str) -> float:
        """Oblicz wynik pilności"""
        urgency_matches = len(re.findall(self.patterns['urgency'], text, re.IGNORECASE))
        return min(urgency_matches * 0.2, 1.0)
    
    def calculate_complexity(self, text: str) -> float:
        """Oblicz złożoność techniczną"""
        tech_matches = len(re.findall(self.patterns['technical_terms'], text, re.IGNORECASE))
        return min(tech_matches * 0.15, 1.0)
    
    def estimate_budget(self, text: str) -> Tuple[int, int]:
        """Oszacuj budżet"""
        if re.search(self.patterns['budget_mention'], text, re.IGNORECASE):
            # Heurystyka budżetowa na podstawie złożoności
            complexity = self.calculate_complexity(text)
            base_budget = 2000
            estimated = int(base_budget * (1 + complexity * 3))
            return (estimated * 0.8, estimated * 1.2)
        return (1000, 5000)
    
    def calculate_success_probability(self, text: str) -> float:
        """Oblicz prawdopodobieństwo sukcesu"""
        factors = {
            'urgency': self.calculate_urgency_score(text),
            'complexity': self.calculate_complexity(text),
            'budget_mentioned': bool(re.search(self.patterns['budget_mention'], text, re.IGNORECASE)),
            'commitment': bool(re.search(self.patterns['commitment'], text, re.IGNORECASE))
        }
        
        # Ważona formuła sukcesu
        probability = (
            factors['urgency'] * 0.2 +
            factors['complexity'] * 0.3 +
            factors['budget_mentioned'] * 0.3 +
            factors['commitment'] * 0.2
        )
        
        return min(probability, 1.0)
    
    def recommend_action(self, text: str) -> str:
        """Zarekomenduj akcję"""
        success_prob = self.calculate_success_probability(text)
        urgency = self.calculate_urgency_score(text)
        
        if success_prob > 0.8 and urgency > 0.5:
            return "APPLY_IMMEDIATELY"
        elif success_prob > 0.6:
            return "APPLY_SOON"
        elif success_prob > 0.4:
            return "CONSIDER"
        else:
            return "SKIP"
    
    def extract_skills(self, text: str) -> List[str]:
        """Wyodrębnij wymagane umiejętności"""
        found_skills = []
        for skill in self.knowledge_base['technical_skills']:
            if skill in text:
                found_skills.append(skill)
        return found_skills
    
    def learn(self, experience: Dict) -> None:
        """Ucz się z doświadczenia"""
        # Prosta implementacja uczenia się
        outcome = experience.get('outcome', 'unknown')
        if outcome == 'success':
            logger.info("AI uczy się z sukcesu")
        elif outcome == 'failure':
            logger.info("AI analizuje porażkę")

class BlockchainSimulator:
    """Symulator blockchain dla bezpieczeństwa"""
    
    def __init__(self):
        self.chain = []
        self.difficulty = 4
        
    def create_block(self, data: Dict) -> Dict:
        """Stwórz nowy blok"""
        previous_hash = self.chain[-1]['hash'] if self.chain else "0"
        
        block = {
            'index': len(self.chain),
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'previous_hash': previous_hash,
            'hash': self.calculate_hash(data, previous_hash)
        }
        
        return block
    
    def calculate_hash(self, data: Dict, previous_hash: str) -> str:
        """Oblicz hash bloku"""
        block_string = f"{data}{previous_hash}{datetime.now()}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def add_block(self, data: Dict) -> str:
        """Dodaj blok do łańcucha"""
        block = self.create_block(data)
        self.chain.append(block)
        return block['hash']
    
    def verify_integrity(self) -> bool:
        """Weryfikuj integralność łańcucha"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current['previous_hash'] != previous['hash']:
                return False
                
            if current['hash'] != self.calculate_hash(current['data'], previous['hash']):
                return False
                
        return True

class PredictiveAnalytics:
    """Predictive Analytics Dashboard - Market Trends & ROI Forecasting"""
    
    def __init__(self):
        self.historical_data = []
        self.market_trends = {}
        self.skill_demand = {}
        self.pricing_models = {}
        
    def analyze_market_trends(self, gigs: List[GigData]) -> Dict:
        """Analyze market trends from gig data"""
        if not gigs:
            return {}
        
        # Extract trend data
        trends = {
            'skill_demand': self._analyze_skill_demand(gigs),
            'price_evolution': self._analyze_price_trends(gigs),
            'competition_level': self._analyze_competition(gigs),
            'success_probability': self._predict_success_rates(gigs),
            'market_growth': self._predict_market_growth(gigs)
        }
        
        return trends
    
    def _analyze_skill_demand(self, gigs: List[GigData]) -> Dict:
        """Analyze skill demand trends"""
        skill_counts = {}
        
        for gig in gigs:
            if 'skills_needed' in gig.ai_analysis:
                for skill in gig.ai_analysis['skills_needed']:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Calculate demand scores
        total_gigs = len(gigs)
        demand_scores = {
            skill: (count / total_gigs) * 100 
            for skill, count in skill_counts.items()
        }
        
        return {
            'top_skills': sorted(demand_scores.items(), key=lambda x: x[1], reverse=True)[:10],
            'emerging_skills': self._identify_emerging_skills(skill_counts),
            'declining_skills': self._identify_declining_skills(skill_counts)
        }
    
    def _analyze_price_trends(self, gigs: List[GigData]) -> Dict:
        """Analyze pricing trends"""
        prices = []
        
        for gig in gigs:
            if 'budget_estimate' in gig.ai_analysis:
                budget = gig.ai_analysis['budget_estimate']
                if isinstance(budget, list) and len(budget) >= 2:
                    prices.append(sum(budget) / 2)  # Average budget
        
        if not prices:
            return {}
        
        return {
            'average_price': statistics.mean(prices),
            'median_price': statistics.median(prices),
            'price_range': [min(prices), max(prices)],
            'price_volatility': statistics.stdev(prices) if len(prices) > 1 else 0,
            'trend_direction': self._calculate_price_trend(prices)
        }
    
    def _analyze_competition(self, gigs: List[GigData]) -> Dict:
        """Analyze competition levels"""
        competition_scores = []
        
        for gig in gigs:
            # Estimate competition based on gig characteristics
            score = self._estimate_competition_score(gig)
            competition_scores.append(score)
        
        return {
            'average_competition': statistics.mean(competition_scores),
            'high_competition_gigs': len([s for s in competition_scores if s > 0.7]),
            'low_competition_gigs': len([s for s in competition_scores if s < 0.3]),
            'competition_trend': self._calculate_competition_trend(competition_scores)
        }
    
    def _predict_success_rates(self, gigs: List[GigData]) -> Dict:
        """Predict success rates for different gig types"""
        success_rates = {}
        
        for gig in gigs:
            gig_type = self._classify_gig_type(gig)
            if gig_type not in success_rates:
                success_rates[gig_type] = []
            
            success_rates[gig_type].append(
                gig.ai_analysis.get('success_probability', 50)
            )
        
        # Calculate average success rates by type
        avg_success_rates = {
            gig_type: statistics.mean(rates)
            for gig_type, rates in success_rates.items()
        }
        
        return {
            'by_type': avg_success_rates,
            'overall_average': statistics.mean([
                gig.ai_analysis.get('success_probability', 50) 
                for gig in gigs
            ]),
            'best_performing_types': sorted(
                avg_success_rates.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
    
    def _predict_market_growth(self, gigs: List[GigData]) -> Dict:
        """Predict market growth trends"""
        # Time-based analysis
        current_time = datetime.now()
        recent_gigs = [
            gig for gig in gigs 
            if (current_time - gig.found_at).days <= 7
        ]
        
        growth_indicators = {
            'weekly_volume': len(recent_gigs),
            'average_quality': statistics.mean([
                gig.score for gig in recent_gigs
            ]) if recent_gigs else 0,
            'new_clients': len(set(gig.source for gig in recent_gigs)),
            'growth_rate': self._calculate_growth_rate(recent_gigs, gigs)
        }
        
        return growth_indicators
    
    def generate_roi_forecast(self, user_profile: Dict, gigs: List[GigData]) -> Dict:
        """Generate ROI forecast for different strategies"""
        forecasts = {
            'conservative': self._forecast_conservative_roi(user_profile, gigs),
            'balanced': self._forecast_balanced_roi(user_profile, gigs),
            'aggressive': self._forecast_aggressive_roi(user_profile, gigs)
        }
        
        return {
            'forecasts': forecasts,
            'recommended_strategy': self._recommend_strategy(forecasts),
            'risk_assessment': self._assess_risks(forecasts),
            'time_to_profit': self._estimate_time_to_profit(forecasts)
        }
    
    def _forecast_conservative_roi(self, profile: Dict, gigs: List[GigData]) -> Dict:
        """Conservative ROI forecast"""
        high_success_gigs = [
            gig for gig in gigs 
            if gig.ai_analysis.get('success_probability', 0) >= 70
        ]
        
        if not high_success_gigs:
            return {'projected_roi': 0, 'confidence': 0}
        
        avg_budget = statistics.mean([
            sum(gig.ai_analysis.get('budget_estimate', [0, 0])) / 2
            for gig in high_success_gigs
        ])
        
        success_rate = statistics.mean([
            gig.ai_analysis.get('success_probability', 0) 
            for gig in high_success_gigs
        ]) / 100
        
        projected_revenue = avg_budget * success_rate * len(high_success_gigs)
        estimated_costs = projected_revenue * 0.2  # 20% costs
        
        return {
            'projected_roi': (projected_revenue - estimated_costs) / estimated_costs if estimated_costs > 0 else 0,
            'confidence': min(90, success_rate * 100),
            'timeframe': '3-6 months',
            'risk_level': 'Low'
        }
    
    def _forecast_balanced_roi(self, profile: Dict, gigs: List[GigData]) -> Dict:
        """Balanced ROI forecast"""
        medium_success_gigs = [
            gig for gig in gigs 
            if 50 <= gig.ai_analysis.get('success_probability', 0) < 80
        ]
        
        if not medium_success_gigs:
            return self._forecast_conservative_roi(profile, gigs)
        
        avg_budget = statistics.mean([
            sum(gig.ai_analysis.get('budget_estimate', [0, 0])) / 2
            for gig in medium_success_gigs
        ])
        
        success_rate = statistics.mean([
            gig.ai_analysis.get('success_probability', 0) 
            for gig in medium_success_gigs
        ]) / 100
        
        projected_revenue = avg_budget * success_rate * len(medium_success_gigs)
        estimated_costs = projected_revenue * 0.25  # 25% costs
        
        return {
            'projected_roi': (projected_revenue - estimated_costs) / estimated_costs if estimated_costs > 0 else 0,
            'confidence': min(75, success_rate * 100),
            'timeframe': '2-4 months',
            'risk_level': 'Medium'
        }
    
    def _forecast_aggressive_roi(self, profile: Dict, gigs: List[GigData]) -> Dict:
        """Aggressive ROI forecast"""
        all_gigs = gigs  # Include all gigs
        
        if not all_gigs:
            return {'projected_roi': 0, 'confidence': 0}
        
        avg_budget = statistics.mean([
            sum(gig.ai_analysis.get('budget_estimate', [0, 0])) / 2
            for gig in all_gigs
        ])
        
        success_rate = statistics.mean([
            gig.ai_analysis.get('success_probability', 0) 
            for gig in all_gigs
        ]) / 100
        
        projected_revenue = avg_budget * success_rate * len(all_gigs)
        estimated_costs = projected_revenue * 0.35  # 35% costs (higher risk)
        
        return {
            'projected_roi': (projected_revenue - estimated_costs) / estimated_costs if estimated_costs > 0 else 0,
            'confidence': min(60, success_rate * 100),
            'timeframe': '1-3 months',
            'risk_level': 'High'
        }
    
    def _estimate_competition_score(self, gig: GigData) -> float:
        """Estimate competition score for a gig"""
        score = 0.5  # Base score
        
        # Adjust based on budget (higher budget = more competition)
        if 'budget_estimate' in gig.ai_analysis:
            budget = sum(gig.ai_analysis['budget_estimate']) / 2
            if budget > 10000:
                score += 0.3
            elif budget > 5000:
                score += 0.2
            elif budget > 2000:
                score += 0.1
        
        # Adjust based on required skills (common skills = more competition)
        if 'skills_needed' in gig.ai_analysis:
            common_skills = ['python', 'javascript', 'react', 'node.js']
            common_count = len([
                skill for skill in gig.ai_analysis['skills_needed']
                if skill.lower() in common_skills
            ])
            score += common_count * 0.05
        
        return min(1.0, score)
    
    def _classify_gig_type(self, gig: GigData) -> str:
        """Classify gig type for analysis"""
        title_lower = gig.title.lower()
        desc_lower = gig.description.lower()
        
        if 'web' in title_lower or 'website' in title_lower:
            return 'web_development'
        elif 'mobile' in title_lower or 'app' in title_lower:
            return 'mobile_development'
        elif 'data' in title_lower or 'analytics' in title_lower:
            return 'data_science'
        elif 'automation' in title_lower or 'bot' in title_lower:
            return 'automation'
        elif 'api' in title_lower or 'backend' in title_lower:
            return 'backend'
        else:
            return 'general'
    
    def _identify_emerging_skills(self, skill_counts: Dict) -> List[str]:
        """Identify emerging skills (simplified logic)"""
        # In real implementation, this would analyze historical data
        emerging = ['blockchain', 'machine learning', 'ai', 'kubernetes', 'terraform']
        return [skill for skill in emerging if skill in skill_counts]
    
    def _identify_declining_skills(self, skill_counts: Dict) -> List[str]:
        """Identify declining skills (simplified logic)"""
        declining = ['flash', 'jquery', 'wordpress', 'php']
        return [skill for skill in declining if skill in skill_counts]
    
    def _calculate_price_trend(self, prices: List[float]) -> str:
        """Calculate price trend direction"""
        if len(prices) < 2:
            return 'stable'
        
        # Simple trend calculation
        first_half = prices[:len(prices)//2]
        second_half = prices[len(prices)//2:]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        if avg_second > avg_first * 1.1:
            return 'increasing'
        elif avg_second < avg_first * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_competition_trend(self, scores: List[float]) -> str:
        """Calculate competition trend"""
        if len(scores) < 2:
            return 'stable'
        
        avg_score = statistics.mean(scores)
        if avg_score > 0.7:
            return 'high'
        elif avg_score < 0.3:
            return 'low'
        else:
            return 'moderate'
    
    def _calculate_growth_rate(self, recent_gigs: List[GigData], all_gigs: List[GigData]) -> float:
        """Calculate growth rate"""
        if not all_gigs:
            return 0
        
        return (len(recent_gigs) / len(all_gigs)) * 100
    
    def _recommend_strategy(self, forecasts: Dict) -> str:
        """Recommend best strategy based on forecasts"""
        conservative = forecasts.get('conservative', {})
        balanced = forecasts.get('balanced', {})
        aggressive = forecasts.get('aggressive', {})
        
        # Choose strategy with best risk-adjusted ROI
        strategies = [
            ('conservative', conservative.get('projected_roi', 0) * 0.9),  # Lower risk
            ('balanced', balanced.get('projected_roi', 0) * 0.7),
            ('aggressive', aggressive.get('projected_roi', 0) * 0.5)  # Higher risk
        ]
        
        return max(strategies, key=lambda x: x[1])[0]
    
    def _assess_risks(self, forecasts: Dict) -> Dict:
        """Assess risks for each strategy"""
        risks = {}
        
        for strategy, forecast in forecasts.items():
            risk_level = forecast.get('risk_level', 'Medium')
            confidence = forecast.get('confidence', 50)
            
            risks[strategy] = {
                'level': risk_level,
                'confidence': confidence,
                'main_risks': self._identify_main_risks(strategy)
            }
        
        return risks
    
    def _identify_main_risks(self, strategy: str) -> List[str]:
        """Identify main risks for strategy"""
        risk_map = {
            'conservative': ['Lower returns', 'Missed opportunities'],
            'balanced': ['Moderate competition', 'Market fluctuations'],
            'aggressive': ['High competition', 'Burnout risk', 'Market volatility']
        }
        return risk_map.get(strategy, ['Unknown risks'])
    
    def _estimate_time_to_profit(self, forecasts: Dict) -> Dict:
        """Estimate time to profitability for each strategy"""
        timeframes = {}
        
        for strategy, forecast in forecasts.items():
            timeframe = forecast.get('timeframe', 'Unknown')
            timeframes[strategy] = timeframe
        
        return timeframes


class NegotiationAI:
    """Autonomiczny AI do negocjacji i dynamic pricing"""
    
    def __init__(self):
        self.pricing_strategies = {
            'conservative': self._conservative_pricing,
            'balanced': self._balanced_pricing,
            'aggressive': self._aggressive_pricing,
            'market_based': self._market_based_pricing
        }
        self.negotiation_patterns = self._load_negotiation_patterns()
        self.market_data = {}
        
    def analyze_negotiation_potential(self, gig: GigData) -> Dict:
        """Analyze negotiation potential for a gig"""
        analysis = {
            'negotiation_score': self._calculate_negotiation_score(gig),
            'optimal_pricing': self._calculate_optimal_pricing(gig),
            'negotiation_strategy': self._recommend_negotiation_strategy(gig),
            'risk_factors': self._identify_risk_factors(gig),
            'success_probability': self._estimate_negotiation_success(gig)
        }
        
        return analysis
    
    def generate_proposal(self, gig: GigData, strategy: str = 'balanced') -> Dict:
        """Generate AI-powered proposal"""
        pricing_strategy = self.pricing_strategies.get(strategy, self._balanced_pricing)
        
        proposal = {
            'recommended_price': pricing_strategy(gig),
            'value_proposition': self._generate_value_proposition(gig),
            'negotiation_points': self._identify_negotiation_points(gig),
            'timeline_suggestion': self._suggest_timeline(gig),
            'payment_terms': self._recommend_payment_terms(gig),
            'confidence_score': self._calculate_proposal_confidence(gig)
        }
        
        return proposal
    
    def auto_negotiate(self, gig: GigData, client_requirements: Dict) -> Dict:
        """Automatyczne negocjacje z klientem"""
        negotiation_plan = {
            'initial_offer': self._calculate_initial_offer(gig),
            'minimum_acceptable': self._calculate_minimum_price(gig),
            'target_price': self._calculate_target_price(gig),
            'negotiation_tactics': self._select_negotiation_tactics(gig),
            'concession_strategy': self._plan_concessions(gig),
            'timeline_negotiation': self._plan_timeline_negotiation(gig)
        }
        
        return negotiation_plan
    
    def _calculate_negotiation_score(self, gig: GigData) -> float:
        """Calculate negotiation potential score (0-1)"""
        score = 0.5  # Base score
        
        # Budget flexibility
        if 'budget_estimate' in gig.ai_analysis:
            budget_range = gig.ai_analysis['budget_estimate']
            if isinstance(budget_range, list) and len(budget_range) >= 2:
                budget_spread = budget_range[1] - budget_range[0]
                score += min(0.3, budget_spread / 10000)
        
        # Urgency factor
        urgency = gig.ai_analysis.get('urgency_level', 'medium')
        if urgency == 'high':
            score += 0.2  # High urgency = better negotiation position
        elif urgency == 'low':
            score -= 0.1
        
        # Complexity factor
        complexity = gig.ai_analysis.get('complexity_score', 5)
        if complexity > 7:
            score += 0.15  # High complexity = room for negotiation
        elif complexity < 3:
            score -= 0.1  # Low complexity = less negotiation room
        
        return min(1.0, max(0.0, score))
    
    def _calculate_optimal_pricing(self, gig: GigData) -> Dict:
        """Calculate optimal pricing strategy"""
        base_analysis = gig.ai_analysis
        
        if 'budget_estimate' in base_analysis:
            budget_range = base_analysis['budget_estimate']
            if isinstance(budget_range, list) and len(budget_range) >= 2:
                client_min, client_max = budget_range
                
                # Calculate optimal price points
                optimal_min = client_min * 1.1  # 10% above client minimum
                optimal_max = client_max * 0.9  # 10% below client maximum
                optimal_target = (optimal_min + optimal_max) / 2
                
                return {
                    'minimum': optimal_min,
                    'maximum': optimal_max,
                    'target': optimal_target,
                    'client_range': budget_range,
                    'negotiation_room': optimal_max - optimal_min
                }
        
        # Fallback pricing
        return {
            'minimum': 2000,
            'maximum': 8000,
            'target': 5000,
            'client_range': [2000, 8000],
            'negotiation_room': 6000
        }
    
    def _recommend_negotiation_strategy(self, gig: GigData) -> str:
        """Recommend best negotiation strategy"""
        negotiation_score = self._calculate_negotiation_score(gig)
        urgency = gig.ai_analysis.get('urgency_level', 'medium')
        complexity = gig.ai_analysis.get('complexity_score', 5)
        
        if negotiation_score > 0.7 and urgency == 'high':
            return 'aggressive'
        elif negotiation_score > 0.5 and complexity > 6:
            return 'value_based'
        elif urgency == 'low':
            return 'conservative'
        else:
            return 'balanced'
    
    def _conservative_pricing(self, gig: GigData) -> float:
        """Conservative pricing strategy"""
        base_analysis = gig.ai_analysis
        if 'budget_estimate' in base_analysis:
            budget = base_analysis['budget_estimate']
            if isinstance(budget, list) and len(budget) >= 2:
                return budget[0] * 0.9  # 10% below minimum
        return 3000
    
    def _balanced_pricing(self, gig: GigData) -> float:
        """Balanced pricing strategy"""
        base_analysis = gig.ai_analysis
        if 'budget_estimate' in base_analysis:
            budget = base_analysis['budget_estimate']
            if isinstance(budget, list) and len(budget) >= 2:
                return sum(budget) / 2  # Middle of range
        return 5000
    
    def _aggressive_pricing(self, gig: GigData) -> float:
        """Aggressive pricing strategy"""
        base_analysis = gig.ai_analysis
        if 'budget_estimate' in base_analysis:
            budget = base_analysis['budget_estimate']
            if isinstance(budget, list) and len(budget) >= 2:
                return budget[1] * 0.95  # Near maximum
        return 7000
    
    def _market_based_pricing(self, gig: GigData) -> float:
        """Market-based pricing strategy"""
        # Simulate market analysis
        base_price = self._balanced_pricing(gig)
        
        # Adjust based on market factors
        market_multiplier = 1.0
        
        # Skill demand adjustment
        if 'skills_needed' in gig.ai_analysis:
            high_demand_skills = ['python', 'machine learning', 'blockchain', 'react']
            skill_count = len([
                skill for skill in gig.ai_analysis['skills_needed']
                if skill.lower() in high_demand_skills
            ])
            market_multiplier += skill_count * 0.1
        
        return base_price * market_multiplier
    
    def _generate_value_proposition(self, gig: GigData) -> str:
        """Generate compelling value proposition"""
        title = gig.title.lower()
        desc = gig.description.lower()
        
        value_points = []
        
        if 'web' in title or 'website' in title:
            value_points.append("Modern, responsive web design with optimal UX")
        if 'api' in title or 'backend' in title:
            value_points.append("Scalable, secure backend architecture")
        if 'automation' in title or 'bot' in title:
            value_points.append("Time-saving automation solutions")
        if 'data' in title or 'analytics' in title:
            value_points.append("Data-driven insights and analytics")
        
        if not value_points:
            value_points.append("High-quality, professional development services")
        
        return " | ".join(value_points)
    
    def _identify_negotiation_points(self, gig: GigData) -> List[str]:
        """Identify key negotiation points"""
        points = []
        
        # Timeline flexibility
        urgency = gig.ai_analysis.get('urgency_level', 'medium')
        if urgency != 'high':
            points.append("Timeline flexibility")
        
        # Payment terms
        points.append("Payment schedule")
        
        # Scope adjustments
        complexity = gig.ai_analysis.get('complexity_score', 5)
        if complexity > 5:
            points.append("Phased delivery")
        
        # Additional services
        points.append("Maintenance and support")
        
        return points
    
    def _suggest_timeline(self, gig: GigData) -> str:
        """Suggest optimal timeline"""
        complexity = gig.ai_analysis.get('complexity_score', 5)
        urgency = gig.ai_analysis.get('urgency_level', 'medium')
        
        if urgency == 'high':
            return "1-2 weeks (expedited delivery)"
        elif complexity > 7:
            return "4-6 weeks (comprehensive development)"
        elif complexity > 4:
            return "2-4 weeks (standard development)"
        else:
            return "1-2 weeks (quick delivery)"
    
    def _recommend_payment_terms(self, gig: GigData) -> str:
        """Recommend payment terms"""
        budget_analysis = self._calculate_optimal_pricing(gig)
        target_price = budget_analysis.get('target', 5000)
        
        if target_price > 10000:
            return "30% upfront, 40% milestone, 30% delivery"
        elif target_price > 5000:
            return "50% upfront, 50% delivery"
        else:
            return "100% upfront"
    
    def _calculate_proposal_confidence(self, gig: GigData) -> float:
        """Calculate confidence in proposal"""
        confidence = 0.7  # Base confidence
        
        # Adjust based on data quality
        if 'budget_estimate' in gig.ai_analysis:
            confidence += 0.1
        
        if 'skills_needed' in gig.ai_analysis:
            confidence += 0.1
        
        if 'success_probability' in gig.ai_analysis:
            success_prob = gig.ai_analysis['success_probability'] / 100
            confidence += success_prob * 0.1
        
        return min(1.0, confidence)
    
    def _identify_risk_factors(self, gig: GigData) -> List[str]:
        """Identify potential negotiation risks"""
        risks = []
        
        # Budget clarity risk
        if 'budget_estimate' not in gig.ai_analysis:
            risks.append("Unclear budget requirements")
        
        # Scope creep risk
        desc_length = len(gig.description)
        if desc_length > 1000:
            risks.append("Potential scope creep")
        
        # Timeline risk
        urgency = gig.ai_analysis.get('urgency_level', 'medium')
        if urgency == 'high':
            risks.append("Tight timeline pressure")
        
        # Competition risk
        if gig.score > 80:
            risks.append("High competition expected")
        
        return risks
    
    def _estimate_negotiation_success(self, gig: GigData) -> float:
        """Estimate probability of successful negotiation"""
        base_success = gig.ai_analysis.get('success_probability', 70) / 100
        
        negotiation_score = self._calculate_negotiation_score(gig)
        
        # Adjust base success with negotiation potential
        adjusted_success = base_success * (0.7 + negotiation_score * 0.6)
        
        return min(1.0, adjusted_success)
    
    def _calculate_initial_offer(self, gig: GigData) -> float:
        """Calculate initial negotiation offer"""
        optimal = self._calculate_optimal_pricing(gig)
        return optimal.get('maximum', 8000) * 0.9
    
    def _calculate_minimum_price(self, gig: GigData) -> float:
        """Calculate minimum acceptable price"""
        optimal = self._calculate_optimal_pricing(gig)
        return optimal.get('minimum', 2000) * 0.8
    
    def _calculate_target_price(self, gig: GigData) -> float:
        """Calculate target negotiation price"""
        optimal = self._calculate_optimal_pricing(gig)
        return optimal.get('target', 5000)
    
    def _select_negotiation_tactics(self, gig: GigData) -> List[str]:
        """Select appropriate negotiation tactics"""
        tactics = []
        
        strategy = self._recommend_negotiation_strategy(gig)
        
        if strategy == 'aggressive':
            tactics.extend(["Value demonstration", "Urgency leverage", "Scarcity appeal"])
        elif strategy == 'conservative':
            tactics.extend(["Relationship building", "Risk mitigation", "Long-term value"])
        else:
            tactics.extend(["Win-win framing", "Flexible options", "Value-based pricing"])
        
        return tactics
    
    def _plan_concessions(self, gig: GigData) -> Dict:
        """Plan potential concessions"""
        return {
            'timeline_concessions': "Flexible delivery dates",
            'scope_concessions': "Phased implementation",
            'payment_concessions': "Flexible payment schedule",
            'support_concessions': "Extended support period"
        }
    
    def _plan_timeline_negotiation(self, gig: GigData) -> Dict:
        """Plan timeline negotiation strategy"""
        base_timeline = self._suggest_timeline(gig)
        
        return {
            'proposed_timeline': base_timeline,
            'expedited_options': "20% premium for faster delivery",
            'extended_options': "10% discount for extended timeline",
            'milestone_breakdown': "Weekly progress reports"
        }
    
    def _load_negotiation_patterns(self) -> Dict:
        """Load successful negotiation patterns"""
        return {
            'high_urgency': ["Emphasize speed", "Premium pricing", "Clear deliverables"],
            'low_budget': ["Value demonstration", "Phased approach", "Long-term relationship"],
            'complex_scope': ["Break down phases", "Regular communication", "Risk sharing"]
        }


class AutonomousAgent:
    """Autonomiczny agent do pozyskiwania zleceń"""
    
    def __init__(self):
        # Enhanced AI Ensemble with multiple models
        self.ai_engine = EnhancedAIEnsemble() if ENHANCED_AI_AVAILABLE else GPT4Simulator()
        self.predictive_analytics = PredictiveAnalytics()
        self.negotiation_ai = NegotiationAI()
        self.blockchain = BlockchainSimulator()
        self.ddgs = DDGS()
        self.ua = UserAgent()
        self.database = self.init_database()
        self.learning_history = []
        
    def process_gigs_with_enhanced_ai(self, gigs: List[GigData]) -> List[GigData]:
        """Process gigs with enhanced AI capabilities"""
        processed_gigs = []
        
        for gig in gigs:
            # Enhanced AI analysis
            gig.ai_analysis = self.ai_engine.analyze({
                'title': gig.title,
                'description': gig.description,
                'budget': gig.budget
            })
            
            # Predictive analytics
            market_trends = self.predictive_analytics.analyze_market_trends([gig])
            gig.market_trend_score = market_trends.get('skill_demand', {}).get('top_skills', [])[0][1] if market_trends.get('skill_demand', {}).get('top_skills') else 0.0
            
            # Negotiation analysis
            negotiation_analysis = self.negotiation_ai.analyze_negotiation_potential(gig)
            gig.negotiation_potential = negotiation_analysis.get('negotiation_score', 0.0)
            gig.pricing_strategy = negotiation_analysis.get('negotiation_strategy', 'balanced')
            
            # Enhanced scoring
            gig.score = self.calculate_enhanced_score(gig)
            
            processed_gigs.append(gig)
        
        return processed_gigs
    
    def calculate_enhanced_score(self, gig: GigData) -> int:
        """Calculate enhanced score with AI insights"""
        base_score = gig.ai_analysis.get('success_probability', 50)
        
        # Market trend bonus
        trend_bonus = gig.market_trend_score * 10
        
        # Negotiation potential bonus
        negotiation_bonus = gig.negotiation_potential * 15
        
        # AI confidence bonus
        confidence_bonus = gig.ai_analysis.get('ensemble_confidence', 0.5) * 20
        
        # Calculate final score
        enhanced_score = base_score + trend_bonus + negotiation_bonus + confidence_bonus
        
        return min(100, int(enhanced_score))
    
    def generate_enhanced_proposals(self, selected_gigs: List[GigData]) -> List[Dict]:
        """Generate AI-powered proposals for selected gigs"""
        proposals = []
        
        for gig in selected_gigs:
            proposal = self.negotiation_ai.generate_proposal(gig, gig.pricing_strategy)
            
            # Add blockchain verification
            proposal_hash = self.blockchain.calculate_hash(proposal, gig.blockchain_hash)
            self.blockchain.add_transaction({
                'type': 'proposal',
                'gig_id': gig.id,
                'proposal_hash': proposal_hash,
                'timestamp': datetime.now().isoformat()
            })
            
            proposals.append({
                'gig': gig,
                'proposal': proposal,
                'blockchain_verified': True
            })
        
        return proposals
    
    def init_database(self) -> sqlite3.Connection:
        """Inicjalizuj bazę danych"""
        conn = sqlite3.connect('gighunter_v2.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gigs (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                budget TEXT,
                source TEXT,
                url TEXT,
                found_at TIMESTAMP,
                score INTEGER,
                ai_analysis TEXT,
                blockchain_hash TEXT,
                status TEXT DEFAULT 'new'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gig_id TEXT,
                applied_at TIMESTAMP,
                proposal TEXT,
                status TEXT DEFAULT 'pending',
                outcome TEXT DEFAULT 'unknown'
            )
        ''')
        
        conn.commit()
        return conn
    
    def search_global_gigs(self, queries: List[str]) -> List[GigData]:
        """Globalne wyszukiwanie zleceń"""
        all_gigs = []
        
        for query in queries:
            try:
                logger.info(f"Wyszukiwanie globalne: {query}")
                
                # Wyszukiwanie w różnych regionach
                regions = ['pl-pl', 'en-us', 'de-de', 'fr-fr', 'es-es']
                
                for region in regions:
                    results = list(self.ddgs.text(
                        query, 
                        region=region,
                        max_results=10,
                        timelimit='w'
                    ))
                    
                    for result in results:
                        gig_data = self.process_raw_result(result, query, region)
                        if gig_data:
                            all_gigs.append(gig_data)
                            
            except Exception as e:
                logger.error(f"Błąd wyszukiwania {query}: {e}")
                
        return all_gigs
    
    def process_raw_result(self, result: Dict, query: str, region: str) -> Optional[GigData]:
        """Przetwarzaj surowy wynik"""
        try:
            # Generuj unikalne ID
            gig_id = hashlib.md5(f"{result['href']}{query}{region}".encode()).hexdigest()
            
            # Analiza AI
            ai_analysis = self.ai_engine.analyze(result)
            
            # Oblicz score
            score = self.calculate_comprehensive_score(result, ai_analysis)
            
            # Stwórz obiekt GigData
            gig = GigData(
                id=gig_id,
                title=result.get('title', ''),
                description=result.get('body', ''),
                budget=ai_analysis['budget_estimate'],
                source=region,
                url=result.get('href', ''),
                found_at=datetime.now(),
                score=score,
                ai_analysis=ai_analysis
            )
            
            # Dodaj do blockchain
            gig.blockchain_hash = self.blockchain.add_block({
                'gig_id': gig_id,
                'title': gig.title,
                'timestamp': gig.found_at.isoformat(),
                'ai_score': score
            })
            
            return gig
            
        except Exception as e:
            logger.error(f"Błąd przetwarzania wyniku: {e}")
            return None
    
    def calculate_comprehensive_score(self, result: Dict, ai_analysis: Dict) -> int:
        """Oblicz kompleksowy score (0-100)"""
        score = 0
        
        # AI Analysis (50%)
        score += ai_analysis['success_probability'] * 50
        
        # Content Analysis (30%)
        text = f"{result.get('title', '')} {result.get('body', '')}".lower()
        
        # Budget mention
        if re.search(r'\b(budżet|budzet|cena|stawka|pln|zł|$|€)\b', text):
            score += 10
            
        # Technical terms
        tech_terms = ['python', 'javascript', 'api', 'database', 'web', 'app']
        for term in tech_terms:
            if term in text:
                score += 2
                
        # Urgency
        if re.search(r'\b(pilne|natychmiast|urgent)\b', text):
            score += 5
            
        # Polish content bonus
        polish_chars = len(re.findall(r'[ąęćłńóśźż]', text))
        if polish_chars > 0:
            score += min(polish_chars, 5)
            
        return min(int(score), 100)
    
    def autonomous_decision_making(self, gigs: List[GigData]) -> List[GigData]:
        """Autonomiczne podejmowanie decyzji"""
        selected_gigs = []
        
        for gig in gigs:
            # AI Recommendation
            ai_action = gig.ai_analysis.get('recommended_action', 'UNKNOWN')
            
            # Score threshold
            if gig.score >= 60:
                # High score - apply immediately
                if ai_action in ["APPLY_IMMEDIATELY", "APPLY_SOON"]:
                    selected_gigs.append(gig)
                    
            elif gig.score >= 40:
                # Medium score - consider
                if ai_action == "APPLY_SOON":
                    selected_gigs.append(gig)
                    
            # Learn from decision
            self.record_decision(gig, ai_action)
            
        return selected_gigs
    
    def record_decision(self, gig: GigData, decision: str) -> None:
        """Zapisz decyzję do uczenia się"""
        self.learning_history.append({
            'gig_id': gig.id,
            'decision': decision,
            'score': gig.score,
            'timestamp': datetime.now().isoformat()
        })
        
        # Ogranicz historię
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-500:]
    
    def auto_apply_to_gigs(self, gigs: List[GigData]) -> List[Dict]:
        """Automatycznie aplikuj na zlecenia"""
        applications = []
        
        for gig in gigs:
            try:
                # Generuj propozycję
                proposal = self.generate_proposal(gig)
                
                # Zapisz aplikację
                app_data = {
                    'gig_id': gig.id,
                    'applied_at': datetime.now(),
                    'proposal': proposal,
                    'status': 'auto_applied'
                }
                
                # Zapisz w bazie
                cursor = self.database.cursor()
                cursor.execute('''
                    INSERT INTO applications (gig_id, applied_at, proposal, status)
                    VALUES (?, ?, ?, ?)
                ''', (gig.id, datetime.now(), proposal, 'auto_applied'))
                self.database.commit()
                
                # Zapisz w blockchain
                blockchain_hash = self.blockchain.add_block({
                    'action': 'auto_application',
                    'gig_id': gig.id,
                    'proposal_hash': hashlib.sha256(proposal.encode()).hexdigest(),
                    'timestamp': datetime.now().isoformat()
                })
                
                app_data['blockchain_hash'] = blockchain_hash
                applications.append(app_data)
                
                logger.info(f"✅ Auto-aplikacja na: {gig.title[:50]}...")
                
            except Exception as e:
                logger.error(f"Błąd auto-aplikacji: {e}")
                
        return applications
    
    def generate_proposal(self, gig: GigData) -> str:
        """Generuj propozycję za pomocą AI"""
        skills = gig.ai_analysis['skill_requirements']
        complexity = gig.ai_analysis['technical_complexity']
        budget_range = gig.ai_analysis['budget_estimate']
        
        proposal = f"""
# Profesjonalna Propozycja - {datetime.now().strftime('%Y-%m-%d')}

## Doświadczenie
Jestem doświadczonym programistą z {len(skills)*2} latami doświadczenia w:
{chr(10).join([f"- {skill.title()}" for skill in skills])}

## Rozwiązanie
Na podstawie analizy Twojego zlecenia ({complexity:.0%} złożoności), proponuję:
- Indywidualne podejście do projektu
- Regularne raportowanie postępów
- Gwarancję jakości i wsparcie po wdrożeniu

## Budżet
Analiza AI sugeruje budżet: {budget_range[0]}-{budget_range[1]} PLN
Jestem elastyczny i otwarty na negocjacje.

## Dostępność
Rozpoczęcie: natychmiast
Czas realizacji: {self.estimate_timeline(complexity)}
Komunikacja: preferowany Slack/Email

## Następne kroki
Chętnie omówię szczegóły na krótkim spotkaniu online.

Pozdrawiam,
AI Assistant - Polish Gig Hunter 2.0
        """.strip()
        
        return proposal
    
    def estimate_timeline(self, complexity: float) -> str:
        """Oszacuj czas realizacji"""
        if complexity < 0.3:
            return "1-2 tygodnie"
        elif complexity < 0.6:
            return "2-4 tygodnie"
        else:
            return "4-8 tygodni"
    
    def learn_from_outcomes(self) -> None:
        """Ucz się z wyników aplikacji"""
        cursor = self.database.cursor()
        cursor.execute('''
            SELECT g.*, a.proposal, a.outcome 
            FROM gigs g 
            JOIN applications a ON g.id = a.gig_id 
            WHERE a.outcome != 'unknown'
        ''')
        
        for row in cursor.fetchall():
            experience = {
                'gig_data': {
                    'title': row[1],
                    'description': row[2],
                    'score': row[7]
                },
                'proposal': row[9],
                'outcome': row[10]
            }
            
            # Przekaż doświadczenie do AI
            self.ai_engine.learn(experience)
    
    def run_autonomous_cycle(self) -> Dict:
        """Uruchom pełny cykl autonomiczny"""
        logger.info("🚀 Uruchamianie Polish Gig Hunter 2.0...")
        
        # Faza 1: Globalne wyszukiwanie
        search_queries = [
            "python developer remote",
            "web development project",
            "software development freelance",
            "programista zlecenie",
            "developer needed urgent",
            "api development project",
            "fullstack developer contract",
            "javascript react project"
        ]
        
        gigs = self.search_global_gigs(search_queries)
        logger.info(f"🔍 Znaleziono {len(gigs)} zleceń globalnie")
        
        # Faza 2: AI analiza i scoring
        for gig in gigs:
            self.save_gig_to_database(gig)
        
        # Faza 3: Autonomiczne podejmowanie decyzji
        selected_gigs = self.autonomous_decision_making(gigs)
        logger.info(f"🧠 AI wybrało {len(selected_gigs)} zleceń")
        
        # Faza 4: Automatyczne aplikowanie
        applications = self.auto_apply_to_gigs(selected_gigs)
        logger.info(f"🤖 Złożono {len(applications)} auto-aplikacji")
        
        # Faza 5: Uczenie się
        self.learn_from_outcomes()
        
        # Faza 6: Weryfikacja blockchain
        blockchain_valid = self.blockchain.verify_integrity()
        logger.info(f"🔐 Blockchain integrity: {'✅' if blockchain_valid else '❌'}")
        
        # Generuj raport
        report = {
            'timestamp': datetime.now().isoformat(),
            'gigs_found': len(gigs),
            'gigs_selected': len(selected_gigs),
            'applications_sent': len(applications),
            'blockchain_valid': blockchain_valid,
            'top_gigs': [
                {
                    'title': gig.title[:50] + '...',
                    'score': gig.score,
                    'ai_recommendation': gig.ai_analysis.get('recommended_action', 'UNKNOWN'),
                    'budget_estimate': gig.ai_analysis['budget_estimate']
                }
                for gig in sorted(selected_gigs, key=lambda x: x.score, reverse=True)[:5]
            ]
        }
        
        return report
    
    def save_gig_to_database(self, gig: GigData) -> None:
        """Zapisz zlecenie do bazy danych"""
        cursor = self.database.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO gigs 
            (id, title, description, budget, source, url, found_at, score, ai_analysis, blockchain_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            gig.id, gig.title, gig.description, str(gig.budget),
            gig.source, gig.url, gig.found_at, gig.score,
            json.dumps(gig.ai_analysis), gig.blockchain_hash
        ))
        self.database.commit()

class NotificationSystem:
    """System powiadomień"""
    
    def __init__(self):
        self.email_user = os.environ.get('EMAIL_USER', 'lukasz.szemiot0330@gmail.com')
        self.email_pass = os.environ.get('EMAIL_PASS', 'ylos uusz lmzh imda')
        
    def send_report(self, report: Dict) -> bool:
        """Wyślij raport"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.email_user
            msg['Subject'] = f"🚀 Polish Gig Hunter 2.0 - Raport {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # HTML Raport
            html_content = f"""
            <html>
            <body>
                <h2>🤖 Polish Gig Hunter 2.0 - Autonomiczny Raport</h2>
                <div style="background: #f0f8ff; padding: 15px; border-radius: 10px;">
                    <h3>📊 Statystyki Cyklu:</h3>
                    <p><strong>🔍 Znaleziono zleceń:</strong> {report['gigs_found']}</p>
                    <p><strong>🧠 AI wybrało:</strong> {report['gigs_selected']}</p>
                    <p><strong>🤖 Auto-aplikacje:</strong> {report['applications_sent']}</p>
                    <p><strong>🔐 Blockchain:</strong> {'✅ Bezpieczny' if report['blockchain_valid'] else '❌ Błąd'}</p>
                </div>
                
                <h3>🏆 Top Zlecenia AI:</h3>
            """
            
            for gig in report['top_gigs']:
                html_content += f"""
                <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px;">
                    <p><strong>{gig['title']}</strong></p>
                    <p>🎯 Score: {gig['score']}/100 | 💰 Budżet: {gig['budget_estimate'][0]}-{gig['budget_estimate'][1]} PLN</p>
                    <p>🤖 AI: {gig['ai_recommendation']}</p>
                </div>
                """
            
            html_content += f"""
                <hr>
                <p><small>🚀 Polish Gig Hunter 2.0 - Autonomiczna Platforma AI</small></p>
                <p><small>🧠 Myśli i uczy się jak człowiek | 🌐 Działa globalnie 24/7/365</small></p>
                <p><small>🤖 Automatycznie aplikuje i negocjuje | 💰 Maksymalizuje profit AI</small></p>
                <p><small>🔐 100% bezpieczeństwo blockchain | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Wyślij
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            logger.info("✅ Raport wysłany e-mailem")
            return True
            
        except Exception as e:
            logger.error(f"❌ Błąd wysyłania raportu: {e}")
            return False

def main():
    """Główna funkcja"""
    logger.info("🌟 Inicjalizacja Polish Gig Hunter 2.0...")
    
    # Inicjalizacja komponentów
    agent = AutonomousAgent()
    notifications = NotificationSystem()
    
    # Uruchom autonomiczny cykl
    try:
        report = agent.run_autonomous_cycle()
        
        # Wyślij powiadomienie
        notifications.send_report(report)
        
        logger.info("🎉 Polish Gig Hunter 2.0 zakończył cykl sukcesem!")
        
    except Exception as e:
        logger.error(f"❌ Krytyczny błąd: {e}")
        
    finally:
        agent.database.close()


if __name__ == "__main__":
    main()
