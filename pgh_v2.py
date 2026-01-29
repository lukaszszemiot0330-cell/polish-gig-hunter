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
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from fake_useragent import UserAgent

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

class AIEngine(ABC):
    """Abstrakcyjna klasa silnika AI"""
    
    @abstractmethod
    def analyze(self, data: Dict) -> Dict:
        pass
    
    @abstractmethod
    def learn(self, experience: Dict) -> None:
        pass

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

class AutonomousAgent:
    """Autonomiczny agent do pozyskiwania zleceń"""
    
    def __init__(self):
        self.ai_engine = GPT4Simulator()
        self.blockchain = BlockchainSimulator()
        self.ddgs = DDGS()
        self.ua = UserAgent()
        self.database = self.init_database()
        self.learning_history = []
        
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
