#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polish Gig Hunter 2.0 - Enhanced AI Demo
🧠 Prawdziwe AI Integration
📊 Predictive Analytics Dashboard  
🤖 Autonomous Negotiation
"""

import os
import sys
from datetime import datetime

# Dodaj ścieżkę do głównego pliku
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pgh_v2 import (
    EnhancedAIEnsemble, 
    PredictiveAnalytics, 
    NegotiationAI,
    AutonomousAgent,
    GigData,
    ENHANCED_AI_AVAILABLE
)

def demo_enhanced_ai():
    """Demo Enhanced AI capabilities"""
    print("🚀 Polish Gig Hunter 2.0 - Enhanced AI Demo")
    print("=" * 50)
    
    # Test data
    test_gig = GigData(
        id="test_001",
        title="Python AI Developer Needed",
        description="Looking for experienced Python developer for AI project",
        budget="$5000-8000",
        source="upwork",
        url="https://example.com/gig/1",
        found_at=datetime.now(),
        score=0,
        ai_analysis={}
    )
    
    # 1. Enhanced AI Ensemble Demo
    print("\n🧠 Enhanced AI Ensemble Demo")
    print("-" * 30)
    
    if ENHANCED_AI_AVAILABLE:
        ai_ensemble = EnhancedAIEnsemble()
        print("✅ Enhanced AI Ensemble initialized")
        
        # Test analysis
        analysis = ai_ensemble.analyze({
            'title': test_gig.title,
            'description': test_gig.description,
            'budget': test_gig.budget
        })
        
        print(f"📊 Analysis Result: {analysis}")
        print(f"🎯 Ensemble Confidence: {analysis.get('ensemble_confidence', 0):.1%}")
        print(f"🤖 Model Consensus: {analysis.get('model_consensus', 'N/A')}")
    else:
        print("⚠️ Enhanced AI libraries not available - using simulation")
    
    # 2. Predictive Analytics Demo
    print("\n📈 Predictive Analytics Demo")
    print("-" * 30)
    
    analytics = PredictiveAnalytics()
    
    # Analyze market trends
    market_trends = analytics.analyze_market_trends([test_gig])
    print(f"📊 Market Trends: {market_trends}")
    
    # ROI Forecast
    user_profile = {'experience': 'senior', 'skills': ['python', 'ai']}
    roi_forecast = analytics.generate_roi_forecast(user_profile, [test_gig])
    print(f"💰 ROI Forecast: {roi_forecast}")
    
    # 3. Negotiation AI Demo
    print("\n🤖 Negotiation AI Demo")
    print("-" * 30)
    
    negotiation_ai = NegotiationAI()
    
    # Analyze negotiation potential
    negotiation_analysis = negotiation_ai.analyze_negotiation_potential(test_gig)
    print(f"💡 Negotiation Score: {negotiation_analysis.get('negotiation_score', 0):.1%}")
    print(f"🎯 Recommended Strategy: {negotiation_analysis.get('negotiation_strategy', 'N/A')}")
    
    # Generate proposal
    proposal = negotiation_ai.generate_proposal(test_gig, 'balanced')
    print(f"📝 Recommended Price: ${proposal.get('recommended_price', 0):,.0f}")
    print(f"💼 Value Proposition: {proposal.get('value_proposition', 'N/A')}")
    print(f"⏰ Timeline: {proposal.get('timeline_suggestion', 'N/A')}")
    
    # 4. Full Autonomous Agent Demo
    print("\n🚀 Full Autonomous Agent Demo")
    print("-" * 30)
    
    try:
        agent = AutonomousAgent()
        print("✅ Autonomous Agent initialized with Enhanced AI")
        
        # Process with enhanced AI
        processed_gigs = agent.process_gigs_with_enhanced_ai([test_gig])
        enhanced_gig = processed_gigs[0]
        
        print(f"📊 Enhanced Score: {enhanced_gig.score}/100")
        print(f"🧠 Market Trend Score: {enhanced_gig.market_trend_score:.1f}")
        print(f"💡 Negotiation Potential: {enhanced_gig.negotiation_potential:.1f}")
        print(f"🎯 Pricing Strategy: {enhanced_gig.pricing_strategy}")
        
        # Generate enhanced proposals
        proposals = agent.generate_enhanced_proposals([enhanced_gig])
        print(f"📝 Generated {len(proposals)} enhanced proposals")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("⚠️ This is expected if some dependencies are missing")

def demo_vision_statement():
    """Display the vision statement"""
    print("\n" + "=" * 60)
    print("🌟 Polish Gig Hunter 2.0 - Vision Statement")
    print("=" * 60)
    print("""
Polish Gig Hunter 2.0 to nie tylko narzędzie - to autonomiczna, 
zdecentralizowana platforma AI która:

🧠 Myśli i uczy się jak człowiek
🌐 Działa globalnie 24/7/365  
🤖 Automatycznie aplikuje i negocjuje
💰 Maksymalizuje profit za pomocą AI
🔐 Jest w 100% bezpieczna dzięki blockchain

To przyszłość freelancingu - już dziś!
""")
    print("=" * 60)

if __name__ == "__main__":
    demo_vision_statement()
    demo_enhanced_ai()
    
    print("\n🎉 Polish Gig Hunter 2.0 Enhanced AI Demo Complete!")
    print("\n📋 Next Steps:")
    print("1. Install enhanced dependencies: pip install -r requirements_enhanced.txt")
    print("2. Set up AI API keys (OPENAI_KEY, ANTHROPIC_KEY, GOOGLE_KEY)")
    print("3. Configure email settings (EMAIL_USER, EMAIL_PASS)")
    print("4. Run: python pgh_v2.py")
    print("5. Enjoy autonomous gig hunting with Enhanced AI!")
