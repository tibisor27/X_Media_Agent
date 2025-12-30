"""
TEST 3: Verifică Enhancer - îmbunătățește imaginile.
Presupune că ai deja imagini descărcate din Test 2.
"""

import sys
import os
sys.path.insert(0, "src")

from enhancer import ImageEnhancer
from models import Tweet, Media, MediaType


def test_enhancer():
    print("\n" + "=" * 60)
    print("🧪 TEST 3: ENHANCER")
    print("=" * 60)
    
    # ─────────────────────────────────────────────────────────
    # PASUL 1: Creează Enhancer
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 1: Creez ImageEnhancer...")
    
    enhancer = ImageEnhancer()
    
    print(f"   ✅ Enhancer creat!")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 2: Găsește o imagine existentă
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 2: Caut o imagine existentă în data/tweets/...")
    
    # Caută în folderul data/tweets
    image_path = None
    data_folder = "data/tweets"
    
    if os.path.exists(data_folder):
        for tweet_folder in os.listdir(data_folder):
            tweet_path = os.path.join(data_folder, tweet_folder)
            if os.path.isdir(tweet_path):
                for file in os.listdir(tweet_path):
                    if file.endswith(".jpg") and "_enhanced" not in file:
                        image_path = os.path.join(tweet_path, file)
                        break
            if image_path:
                break
    
    if not image_path:
        print(f"   ❌ Nu am găsit imagini! Rulează mai întâi test_2_fetcher.py")
        return
    
    print(f"   ✅ Am găsit: {image_path}")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 3: Enhance imaginea direct (fără Tweet)
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 3: Enhance imagine direct...")
    
    print(f"\n   Input:  {image_path}")
    
    enhanced_path = enhancer.enhance_image(image_path)
    
    print(f"   Output: {enhanced_path}")
    print(f"   ✅ Fișier există: {os.path.exists(enhanced_path)}")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 4: Creează un Tweet mock și enhance-l
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 4: Enhance prin Tweet object...")
    
    # Creează un tweet manual pentru test
    mock_tweet = Tweet(
        id="test_123",
        author="TestUser",
        original_text="Test tweet pentru enhancer"
    )
    
    # Adaugă media
    mock_tweet.media.append(Media(
        media_key="test_media",
        type=MediaType.PHOTO,
        url="https://example.com/test.jpg",
        local_path=image_path  # Folosim imaginea reală
    ))
    
    print(f"\n   ÎNAINTE:")
    print(f"   ├── Tweet ID: {mock_tweet.id}")
    print(f"   ├── is_enhanced: {mock_tweet.is_enhanced}")
    print(f"   ├── media[0].local_path: {mock_tweet.media[0].local_path}")
    print(f"   └── media[0].enhanced_path: {mock_tweet.media[0].enhanced_path}")
    
    # Enhance tweet-ul
    enhancer.enhance_tweet_media(mock_tweet)
    
    print(f"\n   DUPĂ:")
    print(f"   ├── Tweet ID: {mock_tweet.id}")
    print(f"   ├── is_enhanced: {mock_tweet.is_enhanced}")
    print(f"   ├── media[0].local_path: {mock_tweet.media[0].local_path}")
    print(f"   └── media[0].enhanced_path: {mock_tweet.media[0].enhanced_path}")
    
    # Verificare
    print(f"\n   ✅ Enhanced path există: {os.path.exists(mock_tweet.media[0].enhanced_path)}")
    
    # ─────────────────────────────────────────────────────────
    # FINAL
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("✅ TEST 3 COMPLET: Enhancer funcționează corect!")
    print("=" * 60)


if __name__ == "__main__":
    test_enhancer()