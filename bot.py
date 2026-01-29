#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polish Gig Hunter - Bot automatycznie przeszukujący internet w poszukiwaniu polskich zleceń
Autor: AI Assistant
Cel: Znajdowanie płatnych zleceń programistycznych (Python) i biurowych (Office Automation)
"""

import os
import re
import json
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Tuple

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from fake_useragent import UserAgent

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolishGigHunter:
    """Główna klasa do wyszukiwania polskich zleceń"""
    
    def __init__(self):
        """Inicjalizacja bota"""
        self.ua = UserAgent()
        self.ddgs = DDGS()
        
        # Dane do e-maila - pobierz ze zmiennych środowiskowych lub z konfiguracji
        self.email_user = os.environ.get('EMAIL_USER', 'lukasz.szemiot0330@gmail.com')
        self.email_pass = os.environ.get('EMAIL_PASS', 'ylos uusz lmzh imda')
        self.email_recipient = os.environ.get('EMAIL_RECIPIENT', self.email_user)
        
        logger.info("🚀 Polish Gig Hunter zainicjalizowany")
        
        # Słowa kluczowe dla różnych kategorii zleceń
        self.python_keywords = [
            "zlecam napisanie skryptu python",
            "szukam programisty python", 
            "potrzebuję bota python",
            "kupię scraper python",
            "zlecenie python",
            "zlecę skrypt python",
            "programista python zlecenie",
            "automatyzacja python",
            "bot python zlecenie"
        ]
        
        self.office_keywords = [
            "zlecam konwersję pdf",
            "łączenie plików excel zlecenie", 
            "przepisanie danych do excela",
            "masowa zmiana nazw plików",
            "problem z formatowaniem zapłacę",
            "konwersja plików zlecenie",
            "przetwarzanie danych excel",
            "automatyzacja excel zlecenie",
            "przenoszenie danych zlecenie"
        ]
        
        # Kontekst finansowy - dodawany do zapytań
        self.financial_context = ["budżet", "faktura", "płatne", "zlecenie", "honorarium", "stawka"]
        
        # Słowa kluczowe do filtrowania negatywnego
        self.negative_keywords = ["kurs", "szkolenie", "tutorial", "nauka", "jak zrobić", "poradnik", "instrukcja"]
        
        # Wzorce walut i formatów plików
        self.currency_patterns = [r'\bzł\b', r'PLN', r'stawka', r'netto', r'brutto', r'cena']
        self.file_patterns = [r'\.xlsx?', r'\.csv', r'\.pdf', r'\.xml', r'\.txt', r'\.docx?']
        
    def search_gigs(self, max_results_per_query: int = 10) -> List[Dict]:
        """
        Główne wyszukiwanie zleceń
        Returns: Lista znalezionych zleceń z ocenami
        """
        all_results = []
        
        # Ogranicz do 5 kluczowych fraz dla testów
        all_keywords = self.python_keywords[:5] + self.office_keywords[:5]
        
        for keyword in all_keywords:
            try:
                logger.info(f"Wyszukiwanie dla: {keyword}")
                
                # Dodaj kontekst finansowy do zapytania
                search_query = f"{keyword} {self.financial_context[0]}"
                
                # Wyszukiwanie z DuckDuckGo (polski region)
                results = list(self.ddgs.text(
                    search_query, 
                    region='pl-pl',
                    max_results=max_results_per_query,
                    timelimit='w'  # ostatni tydzień
                ))
                
                for result in results:
                    # Debugowanie - pokaż pierwsze wyniki
                    logger.info(f"Tytuł: {result.get('title', 'Brak')[:50]}...")
                    
                    # Oceń wynik
                    score = self._score_result(result)
                    logger.info(f"Score: {score}")
                    
                    if score > 0:  # Tylko wyniki z pozytywną oceną
                        result['score'] = score
                        result['search_query'] = keyword
                        all_results.append(result)
                        
            except Exception as e:
                logger.error(f"Błąd podczas wyszukiwania dla '{keyword}': {e}")
                continue
        
        # Sortuj wyniki po ocenie
        all_results.sort(key=lambda x: x['score'], reverse=True)
        logger.info(f"Znaleziono łącznie {len(all_results)} potencjalnych zleceń")
        
        return all_results[:50]  # Ogranicz do top 50 wyników
    
    def _score_result(self, result: Dict) -> int:
        """
        Ocena wyniku (0-10 punktów)
        +3 pkt za walutę
        +2 pkt za formaty plików
        -10 pkt za słowa negatywne
        """
        score = 0
        text = f"{result.get('title', '')} {result.get('body', '')}".lower()
        
        # Sprawdź słowa negatywne (odrzucanie)
        for negative in self.negative_keywords:
            if negative in text:
                return -10  # Odrzuć wynik
        
        # +3 punkty za walutę
        for pattern in self.currency_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 3
                break
        
        # +2 punkty za formaty plików
        for pattern in self.file_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 2
                break
        
        # +1 punkt za słowa kluczowe zleceń
        gig_keywords = ["zlecę", "zlecam", "potrzebuję", "szukam", "kupię", "zapłacę", "honorarium"]
        for keyword in gig_keywords:
            if keyword in text:
                score += 1
                break
        
        return min(score, 10)  # Maksimum 10 punktów
    
    def deep_dive_verification(self, results: List[Dict], top_n: int = 5) -> List[Dict]:
        """
        Weryfikacja top wyników przez pobranie treści strony
        """
        verified_results = []
        
        for result in results[:top_n]:
            try:
                url = result.get('href', '')
                if not url:
                    continue
                
                logger.info(f"Weryfikacja strony: {url}")
                
                # Ustawienia requesta z fake user agent
                headers = {'User-Agent': self.ua.random}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Parsowanie HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Pobierz tekst (pierwsze 500 znaków)
                text = soup.get_text()[:500]
                result['deep_dive_content'] = text.strip()
                
                # Ponowna ocena na podstawie pełnej treści
                additional_score = self._score_result({'title': result.get('title', ''), 'body': text})
                result['score'] += additional_score
                
                verified_results.append(result)
                
            except Exception as e:
                logger.warning(f"Błąd weryfikacji dla {url}: {e}")
                verified_results.append(result)  # Dodaj mimo błędu
        
        return verified_results
    
    def send_email_notification(self, results: List[Dict]) -> bool:
        """
        Wysyłanie powiadomienia e-mail z wynikami
        """
        # Dane do e-maila - pobierz ze zmiennych środowiskowych lub z konfiguracji
        email_user = os.environ.get('EMAIL_USER') or getattr(self, 'email_user', '')
        email_pass = os.environ.get('EMAIL_PASS') or getattr(self, 'email_pass', '')
        email_recipient = os.environ.get('EMAIL_RECIPIENT') or getattr(self, 'email_recipient', email_user)
        
        if not email_user or not email_pass:
            logger.error("Brak danych logowania e-mail w zmiennych środowiskowych")
            return False
        
        try:
            # Tworzenie wiadomości
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_recipient
            msg['Subject'] = f"Polish Gig Hunter - {len(results)} nowe zlecenia ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            
            # Treść HTML
            html_content = self._create_email_html(results)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Wysyłanie przez Gmail SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(email_user, email_pass)
                server.send_message(msg)
            
            logger.info(f"Wysłano powiadomienie e-mail z {len(results)} wynikami")
            return True
            
        except Exception as e:
            logger.error(f"Błąd wysyłania e-maila: {e}")
            return False
    
    def _create_email_html(self, results: List[Dict]) -> str:
        """Tworzenie treści HTML e-maila"""
        html = f"""
        <html>
        <body>
            <h2>🔍 Polish Gig Hunter - Nowe Zlecenia</h2>
            <p>Znaleziono <strong>{len(results)}</strong> potencjalnych zleceń:</p>
            <hr>
        """
        
        for i, result in enumerate(results, 1):
            score_emoji = "🟢" if result['score'] >= 5 else "🟡" if result['score'] >= 3 else "🔴"
            
            html += f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h3>{score_emoji} Zlecenie #{i} (Ocena: {result['score']}/10)</h3>
                <p><strong>Tytuł:</strong> {result.get('title', 'Brak tytułu')}</p>
                <p><strong>Opis:</strong> {result.get('body', 'Brak opisu')[:200]}...</p>
                <p><strong>Link:</strong> <a href="{result.get('href', '#')}">{result.get('href', 'Brak linku')}</a></p>
                <p><strong>Zapytanie:</strong> {result.get('search_query', 'Nieznane')}</p>
            </div>
            """
        
        html += """
            <hr>
            <p><small>Wiadomość wygenerowana przez Polish Gig Hunter - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </body>
        </html>
        """
        
        return html
    
    def run(self):
        """Główna metoda uruchomieniowa"""
        logger.info("🚀 Uruchamianie Polish Gig Hunter...")
        
        try:
            # Krok 1: Wyszukiwanie zleceń
            results = self.search_gigs()
            
            if not results:
                logger.info("Nie znaleziono żadnych zleceń")
                return
            
            # Krok 2: Weryfikacja deep dive dla top wyników
            verified_results = self.deep_dive_verification(results, top_n=10)
            
            # Krok 3: Filtrowanie najlepszych wyników
            best_results = [r for r in verified_results if r['score'] >= 3][:5]
            
            if best_results:
                # Krok 4: Wysyłanie powiadomienia
                success = self.send_email_notification(best_results)
                if success:
                    logger.info(f"✅ Zakończono. Wysłano {len(best_results)} najlepszych zleceń")
                else:
                    logger.error("❌ Błąd wysyłania powiadomienia")
            else:
                logger.info("Nie znaleziono zleceń wystarczająco wysokiej jakości")
                
        except Exception as e:
            logger.error(f"Krytyczny błąd w run(): {e}")

if __name__ == "__main__":
    hunter = PolishGigHunter()
    hunter.run()
