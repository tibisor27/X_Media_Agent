"""
TEST 3: Verifică Enhancer cu Recraft AI.
"""

import sys
import os
sys.path.insert(0, "src")

from enhancer import ImageEnhancer
from models import Tweet, Media, MediaType


def test_enhancer():
    print("\n" + "=" * 60)
    print("🧪 TEST 3: ENHANCER (Recraft AI)")
    print("=" * 60)
    
    # ─────────────────────────────────────────────────────────
    # PASUL 1: Creează Enhancer
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 1: Creez ImageEnhancer...")
    
    enhancer = ImageEnhancer()
    
    print(f"   ✅ Enhancer creat!")
    print(f"   ├── API Key setat: {'✅ Da' if enhancer.api_key else '❌ Nu'}")
    print(f"   ├── Base URL: {enhancer.base_url}")
    print(f"   └── Timeout: {enhancer.timeout}s")
    

    # ─────────────────────────────────────────────────────────
    # PASUL 2: Găsește o imagine existentă
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 2: Caut o imagine existentă...")
    
    image_path = None
    data_folder = "data/tweets"
    
    if os.path.exists(data_folder):
        for tweet_folder in os.listdir(data_folder):
            tweet_path = os.path.join(data_folder, tweet_folder)
            if os.path.isdir(tweet_path):
                for file in os.listdir(tweet_path):
                    if file.endswith((".jpg", ".png")) and "_enhanced" not in file:
                        image_path = os.path.join(tweet_path, file)
                        break
            if image_path:
                break
    
    if not image_path:
        print(f"   ❌ Nu am găsit imagini!")
        print(f"   Rulează mai întâi: python tests/test_2_fetcher.py")
        return
    
    print(f"   ✅ Am găsit: {image_path}")
    print(f"   📊 Size: {os.path.getsize(image_path) / 1024:.1f} KB")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 3: Enhance imaginea direct
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 3: Enhance imagine direct...")
    
    print(f"\n   Input: {image_path}")
    
    enhanced_path = enhancer.enhance_image(image_path)
    
    if enhanced_path:
        print(f"\n   ✅ Output: {enhanced_path}")
        print(f"   📊 Size: {os.path.getsize(enhanced_path) / 1024:.1f} KB")
    else:
        print(f"\n   ❌ Enhance eșuat!")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 4: Enhance prin Tweet object
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 4: Enhance prin Tweet object...")
    
    # Creează un tweet mock
    mock_tweet = Tweet(
        id="test_recraft_123",
        author="TestUser",
        original_text="Test tweet pentru Recraft AI enhancer"
    )
    
    # Adaugă media
    mock_tweet.media.append(Media(
        media_key="test_media",
        type=MediaType.PHOTO,
        url="https://example.com/test.jpg",
        local_path=image_path
    ))
    
    print(f"\n   ÎNAINTE:")
    print(f"   ├── Tweet ID: {mock_tweet.id}")
    print(f"   ├── is_enhanced: {mock_tweet.is_enhanced}")
    print(f"   ├── media[0].local_path: {mock_tweet.media[0].local_path}")
    print(f"   └── media[0].enhanced_path: {mock_tweet.media[0].enhanced_path}")
    
    # Enhance
    enhancer.enhance_tweet_media(mock_tweet)
    
    print(f"\n   DUPĂ:")
    print(f"   ├── Tweet ID: {mock_tweet.id}")
    print(f"   ├── is_enhanced: {mock_tweet.is_enhanced}")
    print(f"   ├── media[0].local_path: {mock_tweet.media[0].local_path}")
    print(f"   └── media[0].enhanced_path: {mock_tweet.media[0].enhanced_path}")
    
    # ─────────────────────────────────────────────────────────
    # FINAL
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    if mock_tweet.is_enhanced and mock_tweet.media[0].enhanced_path:
        print("✅ TEST 3 COMPLET: Enhancer funcționează!")
    else:
        print("⚠️ TEST 3: Enhancer a avut probleme")
    print("=" * 60)


def test_compare_local_vs_api():
    """Compară rezultatele local vs API."""
    
    print("\n" + "=" * 60)
    print("🧪 COMPARAȚIE: Local vs Recraft AI")
    print("=" * 60)
    
    # Găsește imagine
    image_path = None
    for root, dirs, files in os.walk("data/tweets"):
        for file in files:
            if file.endswith((".jpg", ".png")) and "_enhanced" not in file:
                image_path = os.path.join(root, file)
                break
        if image_path:
            break
    
    if not image_path:
        print("❌ Nu am găsit imagini pentru test")
        return
    
    print(f"\n📷 Imagine test: {image_path}")
    
    # Test Local
    print("\n🔹 LOCAL (Pillow):")
    local_enhancer = LocalImageEnhancer()
    base, ext = os.path.splitext(image_path)
    local_result = local_enhancer.enhance_image(image_path, f"{base}_local{ext}")
    
    # Test API
    print("\n🔹 API (Recraft AI):")
    api_enhancer = ImageEnhancer()
    if api_enhancer.api_key:
        api_result = api_enhancer.enhance_image(image_path, f"{base}_recraft{ext}")
    else:
        print("   ⚠️ API key nu e setat, skip")
        api_result = None
    
    # Comparație
    print("\n📊 REZULTATE:")
    print(f"   Original: {os.path.getsize(image_path) / 1024:.1f} KB")
    if local_result:
        print(f"   Local:    {os.path.getsize(local_result) / 1024:.1f} KB")
    if api_result:
        print(f"   Recraft:  {os.path.getsize(api_result) / 1024:.1f} KB")


if __name__ == "__main__":
    test_enhancer()
    
    # Opțional: compară local vs API
    # test_compare_local_vs_api()