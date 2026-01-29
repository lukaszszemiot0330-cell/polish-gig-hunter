#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polish Gig Hunter 2.0 - Windows Service Installer
Instalacja jako system service dla pracy 24/7
"""

import os
import sys
import time
import servicemanager
import win32service
import win32serviceutil
import win32event
import subprocess
from pathlib import Path

class PGHService(win32serviceutil.ServiceFramework):
    """Windows Service dla Polish Gig Hunter 2.0"""
    
    _svc_name_ = "PolishGigHunter2"
    _svc_display_name_ = "Polish Gig Hunter 2.0 - AI Automation"
    _svc_description_ = "Autonomiczny system AI do pozyskiwania zleceń 24/7"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        
    def SvcStop(self):
        """Zatrzymanie service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )
        
    def SvcDoRun(self):
        """Główna pętla service"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        # Ustawienia środowiska
        env = os.environ.copy()
        env['EMAIL_USER'] = 'lukasz.szemiot0330@gmail.com'
        env['EMAIL_PASS'] = 'ylos uusz lmzh imda'
        
        # Ścieżka do skryptu
        script_path = Path(__file__).parent / "pgh_v2.py"
        
        # Główna pętla
        while self.is_alive:
            try:
                # Sprawdź czy trzeba zatrzymać
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break
                
                # Uruchom PGH2 co 2 godziny
                servicemanager.LogInfo("🚀 Uruchamianie Polish Gig Hunter 2.0...")
                
                result = subprocess.run(
                    ['python', str(script_path)],
                    cwd=str(script_path.parent),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    servicemanager.LogInfo(f"✅ Sukces: {result.stdout}")
                else:
                    servicemanager.LogError(f"❌ Błąd: {result.stderr}")
                
                # Czekaj 2 godziny (7200 sekund)
                for _ in range(7200):
                    if not self.is_alive:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                servicemanager.LogError(f"💥 Błąd service: {e}")
                time.sleep(60)  # Czekaj 1 minutę przed ponowieniem

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Instalacja service
        win32serviceutil.InstallService(
            PGHService._svc_name_,
            PGHService._svc_display_name_,
            PGHService._svc_description_,
            start_type=win32service.SERVICE_AUTO_START
        )
        print(f"✅ Service '{PGHService._svc_display_name_}' zainstalowany!")
        print("🔄 Uruchom service w services.msc")
    else:
        win32serviceutil.HandleCommandLine(PGHService)
