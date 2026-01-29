#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polish Gig Hunter 2.0 - Scheduler
Automatyczne uruchamianie co określony czas
"""

import os
import time
import schedule
import subprocess
from datetime import datetime

def run_pgh_v2():
    """Uruchom Polish Gig Hunter 2.0"""
    print(f"🚀 Uruchamianie PGH 2.0 - {datetime.now()}")
    
    # Ustaw zmienne środowiskowe
    env = os.environ.copy()
    env['EMAIL_USER'] = 'lukasz.szemiot0330@gmail.com'
    env['EMAIL_PASS'] = 'ylos uusz lmzh imda'
    
    # Uruchom skrypt
    try:
        result = subprocess.run(
            ['python', 'pgh_v2.py'],
            cwd='c:\\pppkkkooo',
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minut timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Sukces - {datetime.now()}")
            print(result.stdout)
        else:
            print(f"❌ Błąd - {datetime.now()}")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout - {datetime.now()}")
    except Exception as e:
        print(f"💥 Błąd krytyczny: {e}")

def main():
    """Główna funkcja schedulera"""
    print("🌟 Polish Gig Hunter 2.0 Scheduler")
    print("📅 Harmonogram:")
    print("  - Co 2 godziny: Pełne skanowanie globalne")
    print("  - Co 6 godzin: Raport podsumowujący")
    print("  - Co 24 godziny: Analiza trendów")
    print("  - Ctrl+C aby zatrzymać")
    print("-" * 50)
    
    # Harmonogram
    schedule.every(2).hours.do(run_pgh_v2)  # Co 2 godziny
    schedule.every(6).hours.do(lambda: print(f"📊 Raport 6h - {datetime.now()}"))
    schedule.every(24).hours.do(lambda: print(f"📈 Analiza 24h - {datetime.now()}"))
    
    # Uruchom od razu
    run_pgh_v2()
    
    # Pętla schedulera
    while True:
        schedule.run_pending()
        time.sleep(60)  # Sprawdzaj co minutę

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Scheduler zatrzymany przez użytkownika")
    except Exception as e:
        print(f"💥 Błąd schedulera: {e}")
