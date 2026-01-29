#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polish Gig Hunter 2.0 - Service Status Checker
Sprawdzanie statusu service i logów
"""

import os
import time
import win32service
import win32serviceutil
import win32event
import servicemanager

def check_service_status():
    """Sprawdź status service"""
    try:
        service_name = "PolishGigHunter2"
        
        # Pobierz status
        status = win32serviceutil.QueryServiceStatus(service_name)
        
        status_map = {
            win32service.SERVICE_STOPPED: "Zatrzymany",
            win32service.SERVICE_START_PENDING: "Uruchamianie...",
            win32service.SERVICE_STOP_PENDING: "Zatrzymywanie...",
            win32service.SERVICE_RUNNING: "✅ Działa",
            win32service.SERVICE_CONTINUE_PENDING: "Wznawianie...",
            win32service.SERVICE_PAUSE_PENDING: "Pauzowanie...",
            win32service.SERVICE_PAUSED: "Pauzowany"
        }
        
        print(f"🤖 Polish Gig Hunter 2.0 Service Status:")
        print(f"📊 Status: {status_map.get(status, 'Nieznany')}")
        print(f"🔄 Last check: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if status == win32service.SERVICE_RUNNING:
            print("✅ Service działa poprawnie!")
            print("📧 Email raporty będą wysyłane co 2 godziny")
            print("🔍 AI analizuje zlecenia 24/7")
        else:
            print("❌ Service nie działa!")
            print("🔧 Uruchom service w services.msc")
            
    except Exception as e:
        print(f"❌ Błąd sprawdzania service: {e}")
        print("💡 Service może nie być zainstalowany")

def show_logs():
    """Pokaż ostatnie logi"""
    log_file = "gighunter_v2.log"
    if os.path.exists(log_file):
        print(f"\n📋 Ostatnie logi ({log_file}):")
        print("-" * 50)
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Pokaż ostatnie 10 linii
                for line in lines[-10:]:
                    print(line.strip())
        except Exception as e:
            print(f"❌ Błąd odczytu logów: {e}")
    else:
        print(f"❌ Plik logów nie istnieje: {log_file}")

def main():
    """Główna funkcja"""
    print("🔍 Polish Gig Hunter 2.0 - Service Monitor")
    print("=" * 50)
    
    check_service_status()
    show_logs()
    
    print("\n📞 Komendy zarządzania:")
    print("  Start: python install_service.py start")
    print("  Stop:  python install_service.py stop")
    print("  Status:python check_service.py")

if __name__ == "__main__":
    main()
