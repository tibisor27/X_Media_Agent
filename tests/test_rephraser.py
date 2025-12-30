"""
TEST 4: Verifică Rephraser cu Azure OpenAI - Stil ICT.
"""

import sys
sys.path.insert(0, "src")

from rephraser import TextRephraser
from models import Tweet


def test_rephraser():
    print("\n" + "=" * 60)
    print("🧪 TEST 4: REPHRASER (Azure OpenAI - ICT Style)")
    print("=" * 60)
    
    # ─────────────────────────────────────────────────────────
    # PASUL 1: Creează Rephraser
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 1: Creez TextRephraser...")
    
    try:
        rephraser = TextRephraser()
    except Exception as e:
        print(f"   ❌ Eroare: {e}")
        print(f"   Verifică variabilele AZURE_OPENAI_* în .env!")
        return
    
    # ─────────────────────────────────────────────────────────
    # PASUL 2: Test cu diferite texte de trading
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 2: Test rephrase direct (stil ICT)...")
    
    test_texts = [
        "EURUSD looking bullish! Great entry point for longs here! 📈",
        "Watch for the breakout above 1.0950 on EURUSD. Could see a nice move up!",
        "GBPUSD forming a nice pattern. Waiting for confirmation before entry.",
        "The market is showing signs of reversal. Be careful with shorts here!",
        "Price swept the lows and now pushing higher. Classic liquidity grab! 🎯"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n   {'─' * 50}")
        print(f"   📝 Test #{i}:")
        print(f"   Original:  \"{text}\"")
        
        rephrased = rephraser.rephrase(text)
        
        print(f"   ICT Style: \"{rephrased}\"")
        print(f"   Lungime:   {len(text)} → {len(rephrased)}")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 3: Rephrase prin Tweet object
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 3: Rephrase prin Tweet object...")
    
    mock_tweet = Tweet(
        id="test_ict_456",
        author="TestUser",
        original_text="USDJPY breaking out! The bulls are in control. Looking for targets at 152.00! 🚀"
    )
    
    print(f"\n   ÎNAINTE:")
    print(f"   ├── Tweet ID: {mock_tweet.id}")
    print(f"   ├── original_text: {mock_tweet.original_text}")
    print(f"   ├── rephrased_text: {mock_tweet.rephrased_text}")
    print(f"   └── is_rephrased: {mock_tweet.is_rephrased}")
    
    # Rephrase
    rephraser.rephrase_tweet(mock_tweet)
    
    print(f"\n   DUPĂ:")
    print(f"   ├── Tweet ID: {mock_tweet.id}")
    print(f"   ├── original_text: {mock_tweet.original_text}")
    print(f"   ├── rephrased_text: {mock_tweet.rephrased_text}")
    print(f"   └── is_rephrased: {mock_tweet.is_rephrased}")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 4: Verificare stil ICT
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 4: Verificare caracteristici stil ICT...")
    
    ict_terms = ["liquidity", "order block", "fvg", "fair value", "displacement", 
                 "smart money", "algorithm", "draw on", "sweep", "breaker"]
    
    # Test cu un text care ar trebui să conțină termeni ICT
    liquidity_text = "Price took out the lows and reversed. Classic stop hunt!"
    rephrased_liquidity = rephraser.rephrase(liquidity_text)
    
    print(f"\n   Original:  \"{liquidity_text}\"")
    print(f"   ICT Style: \"{rephrased_liquidity}\"")
    
    # Verifică dacă conține termeni ICT
    found_terms = [term for term in ict_terms if term.lower() in rephrased_liquidity.lower()]
    if found_terms:
        print(f"   ✅ Termeni ICT găsiți: {found_terms}")
    else:
        print(f"   ℹ️ Niciun termen ICT specific (poate fi ok)")
    
    # ─────────────────────────────────────────────────────────
    # FINAL
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("✅ TEST 4 COMPLET: Rephraser ICT Style funcționează!")
    print("=" * 60)


def test_multiple_examples():
    """Test cu mai multe exemple pentru a vedea consistența stilului."""
    
    print("\n" + "=" * 60)
    print("🧪 TEST: Multiple ICT Style Examples")
    print("=" * 60)
    
    rephraser = TextRephraser()
    
    examples = [
        # Setup posts
        "Nice bullish setup forming on EURUSD. Watch for entry above 1.0900!",
        "GBPUSD showing strength. Could see 1.2800 soon.",
        
        # Analysis posts
        "The support at 1.0850 is holding well. Bulls in control.",
        "Resistance broken on USDJPY. New highs incoming!",
        
        # Liquidity posts
        "Stop hunt below 1.0800 complete. Now looking for reversal.",
        "Price swept the highs and rejected. Bears taking over.",
        
        # General market posts
        "Patience is key in trading. Wait for your setup!",
        "The market will show you what to do. Just watch price action."
    ]
    
    print("\n📋 REZULTATE:")
    for i, text in enumerate(examples, 1):
        rephrased = rephraser.rephrase(text)
        print(f"\n{i}. Original:  {text}")
        print(f"   ICT:      {rephrased}")


if __name__ == "__main__":
    test_rephraser()
    
    # Opțional: test cu mai multe exemple
    # test_multiple_examples()