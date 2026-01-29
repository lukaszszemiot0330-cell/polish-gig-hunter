#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polish Gig Hunter - Dashboard Streamlit
Interfejs użytkownika do ręcznego uruchamiania i podglądu wyników
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Dodaj bieżący katalog do ścieżki Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import PolishGigHunter

# Konfiguracja strony Streamlit
st.set_page_config(
    page_title="Polish Gig Hunter",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .result-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .high-score { color: #2ecc71; font-weight: bold; }
    .medium-score { color: #f39c12; font-weight: bold; }
    .low-score { color: #e74c3c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def main():
    """Główna funkcja aplikacji Streamlit"""
    
    # Nagłówek
    st.markdown('<h1 class="main-header">🔍 Polish Gig Hunter</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar z ustawieniami
    with st.sidebar:
        st.header("⚙️ Ustawienia")
        
        # Parametry wyszukiwania
        max_results = st.slider("Maksymalna liczba wyników na zapytanie", 10, 50, 20)
        top_verification = st.slider("Liczba wyników do weryfikacji deep-dive", 3, 15, 5)
        min_score = st.slider("Minimalna ocena do wyświetlenia", 0, 10, 3)
        
        st.markdown("---")
        st.header("📧 Konfiguracja E-mail")
        
        email_user = st.text_input("E-mail Gmail", type="default")
        email_pass = st.text_input("Hasło aplikacji Gmail", type="password")
        email_recipient = st.text_input("Odbiorca powiadomień", value=email_user)
        
        # Przycisk zapisu ustawień
        if st.button("💾 Zapisz ustawienia e-mail"):
            os.environ['EMAIL_USER'] = email_user
            os.environ['EMAIL_PASS'] = email_pass
            os.environ['EMAIL_RECIPIENT'] = email_recipient
            st.success("✅ Ustawienia zapisane!")
    
    # Główna zawartość
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.header("🚀 Akcje")
        
        if st.button("🔍 Szukaj zleceń", type="primary", use_container_width=True):
            with st.spinner("Przeszukiwanie internetu..."):
                try:
                    # Inicjalizacja i uruchomienie bota
                    hunter = PolishGigHunter()
                    
                    # Wyszukiwanie
                    results = hunter.search_gigs(max_results_per_query=max_results)
                    
                    # Weryfikacja deep-dive
                    verified_results = hunter.deep_dive_verification(results, top_n=top_verification)
                    
                    # Filtrowanie
                    filtered_results = [r for r in verified_results if r['score'] >= min_score]
                    
                    # Zapis w session state
                    st.session_state.results = filtered_results
                    st.session_state.search_time = datetime.now()
                    
                    st.success(f"✅ Znaleziono {len(filtered_results)} zleceń!")
                    
                except Exception as e:
                    st.error(f"❌ Błąd: {str(e)}")
                    st.session_state.results = []
        
        if st.button("📧 Wyślij e-mail", use_container_width=True):
            if 'results' in st.session_state and st.session_state.results:
                with st.spinner("Wysyłanie powiadomienia..."):
                    try:
                        hunter = PolishGigHunter()
                        success = hunter.send_email_notification(st.session_state.results)
                        if success:
                            st.success("✅ E-mail wysłany!")
                        else:
                            st.error("❌ Błąd wysyłania e-maila")
                    except Exception as e:
                        st.error(f"❌ Błąd: {str(e)}")
            else:
                st.warning("⚠️ Najpierw wyszukaj zlecenia")
        
        # Statystyki
        if 'results' in st.session_state and st.session_state.results:
            st.header("📊 Statystyki")
            results = st.session_state.results
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Znalezione", len(results))
            with col_stat2:
                high_score = len([r for r in results if r['score'] >= 7])
                st.metric("Wysoka jakość", high_score)
            with col_stat3:
                avg_score = sum(r['score'] for r in results) / len(results) if results else 0
                st.metric("Średnia ocena", f"{avg_score:.1f}")
    
    with col2:
        st.header("📋 Wyniki wyszukiwania")
        
        if 'results' in st.session_state and st.session_state.results:
            results = st.session_state.results
            
            if 'search_time' in st.session_state:
                st.caption(f"Ostatnie wyszukiwanie: {st.session_state.search_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Filtrowanie wyników
            score_filter = st.select_slider("Filtruj po ocenie", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], value=min_score)
            filtered_display = [r for r in results if r['score'] >= score_filter]
            
            st.caption(f"Wyświetlanie {len(filtered_display)} z {len(results)} wyników")
            
            # Wyświetlanie wyników
            for i, result in enumerate(filtered_display, 1):
                score = result['score']
                score_class = "high-score" if score >= 7 else "medium-score" if score >= 4 else "low-score"
                score_emoji = "🟢" if score >= 7 else "🟡" if score >= 4 else "🔴"
                
                with st.expander(f"{score_emoji} Zlecenie #{i} - Ocena: <span class='{score_class}'>{score}/10</span>", expanded=i <= 3):
                    col_title, col_link = st.columns([3, 1])
                    
                    with col_title:
                        st.markdown(f"**Tytuł:** {result.get('title', 'Brak tytułu')}")
                        st.markdown(f"**Opis:** {result.get('body', 'Brak opisu')}")
                        st.markdown(f"**Zapytanie:** `{result.get('search_query', 'Nieznane')}`")
                    
                    with col_link:
                        if result.get('href'):
                            st.markdown(f"[🔗 Otwórz]({result['href']})")
                    
                    # Deep dive content jeśli dostępny
                    if 'deep_dive_content' in result:
                        with st.expander("📄 Treść strony (deep dive)"):
                            st.text(result['deep_dive_content'])
                    
                    # Metadane
                    st.caption(f"Źródło: {result.get('href', 'Brak')}")
            
            # Przyciski akcji na wynikach
            st.markdown("---")
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                if st.button("📥 Eksportuj do CSV"):
                    df = pd.DataFrame(filtered_display)
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="Pobierz CSV",
                        data=csv,
                        file_name=f"gig_hunter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col_export2:
                if st.button("🔄 Wyczyść wyniki"):
                    st.session_state.results = []
                    st.rerun()
        
        else:
            st.info("👆 Kliknij 'Szukaj zleceń' aby rozpocząć")
            
            # Przykładowe zapytania
            st.markdown("---")
            st.subheader("💡 Przykładowe zapytania:")
            example_queries = [
                "zlecam napisanie skryptu python",
                "łączenie plików excel zlecenie", 
                "potrzebuję bota python",
                "konwersja pdf zlecenie",
                "automatyzacja excel"
            ]
            
            for query in example_queries:
                st.markdown(f"• `{query}`")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Polish Gig Hunter - Automatyczny system wyszukiwania polskich zleceń<br>"
        f"Uruchomiono: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
