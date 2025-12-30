import sys
sys.path.insert(0, "src")

from models import Tweet, Media, MediaType
from datetime import datetime


def test_models():
    print("\n" + "=" * 60)
    print("🧪 TEST 1: MODELS")
    print("=" * 60)
    
    # ─────────────────────────────────────────────────────────
    # PASUL 1: Creează un Media object
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 1: Creez un Media object...")
    
    media = Media(
        media_key="abc123",
        type=MediaType.PHOTO,
        url="https://pbs.twimg.com/media/test.jpg"
    )
    
    print(f"   ✅ Media creat!")
    print(f"   │")
    print(f"   ├── media_key: {media.media_key}")
    print(f"   ├── type: {media.type}")
    print(f"   ├── type.value: {media.type.value}")
    print(f"   ├── url: {media.url}")
    print(f"   ├── local_path: {media.local_path}")  # None (nu l-am descărcat)
    print(f"   └── enhanced_path: {media.enhanced_path}")  # None (nu l-am enhanced)
    
    # ─────────────────────────────────────────────────────────
    # PASUL 2: Creează un Tweet FĂRĂ media
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 2: Creez un Tweet FĂRĂ media...")
    
    tweet_no_media = Tweet(
        id="111111",
        author="TestUser",
        original_text="Acesta este un tweet de test fără imagine!"
    )
    
    print(f"   ✅ Tweet creat!")
    print(f"   │")
    print(f"   ├── id: {tweet_no_media.id}")
    print(f"   ├── author: {tweet_no_media.author}")
    print(f"   ├── original_text: {tweet_no_media.original_text}")
    print(f"   ├── rephrased_text: {tweet_no_media.rephrased_text}")  # None
    print(f"   ├── media: {tweet_no_media.media}")  # [] (listă goală)
    print(f"   ├── has_media: {tweet_no_media.has_media}")  # False
    print(f"   ├── has_photo: {tweet_no_media.has_photo}")  # False
    print(f"   ├── is_enhanced: {tweet_no_media.is_enhanced}")  # False
    print(f"   ├── is_rephrased: {tweet_no_media.is_rephrased}")  # False
    print(f"   └── is_ready_to_post: {tweet_no_media.is_ready_to_post}")  # False
    
    # ─────────────────────────────────────────────────────────
    # PASUL 3: Creează un Tweet CU media
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 3: Creez un Tweet CU media...")
    
    tweet_with_media = Tweet(
        id="222222",
        author="TestUser",
        original_text="Tweet cu imagine! 📈",
        likes=100,
        retweets=50
    )
    
    # Adaugă media la tweet
    tweet_with_media.media.append(media)
    
    print(f"   ✅ Tweet cu media creat!")
    print(f"   │")
    print(f"   ├── id: {tweet_with_media.id}")
    print(f"   ├── original_text: {tweet_with_media.original_text}")
    print(f"   ├── likes: {tweet_with_media.likes}")
    print(f"   ├── retweets: {tweet_with_media.retweets}")
    print(f"   ├── has_media: {tweet_with_media.has_media}")  # True!
    print(f"   ├── has_photo: {tweet_with_media.has_photo}")  # True!
    print(f"   ├── media count: {len(tweet_with_media.media)}")
    print(f"   │")
    print(f"   └── media[0]:")
    print(f"       ├── type: {tweet_with_media.media[0].type.value}")
    print(f"       └── url: {tweet_with_media.media[0].url}")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 4: Simulează procesarea
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 4: Simulez procesarea (setez valori manual)...")
    
    print(f"\n   ÎNAINTE:")
    print(f"   ├── rephrased_text: {tweet_with_media.rephrased_text}")
    print(f"   ├── media[0].enhanced_path: {tweet_with_media.media[0].enhanced_path}")
    print(f"   └── is_ready_to_post: {tweet_with_media.is_ready_to_post}")
    
    # Simulez enhance
    tweet_with_media.media[0].local_path = "data/tweets/222222/media_1.jpg"
    tweet_with_media.media[0].enhanced_path = "data/tweets/222222/media_1_enhanced.jpg"
    tweet_with_media.is_enhanced = True
    
    # Simulez rephrase
    tweet_with_media.rephrased_text = "Tweet reformulat cu imagine! 📊"
    tweet_with_media.is_rephrased = True
    
    print(f"\n   DUPĂ:")
    print(f"   ├── rephrased_text: {tweet_with_media.rephrased_text}")
    print(f"   ├── media[0].local_path: {tweet_with_media.media[0].local_path}")
    print(f"   ├── media[0].enhanced_path: {tweet_with_media.media[0].enhanced_path}")
    print(f"   ├── is_enhanced: {tweet_with_media.is_enhanced}")
    print(f"   ├── is_rephrased: {tweet_with_media.is_rephrased}")
    print(f"   └── is_ready_to_post: {tweet_with_media.is_ready_to_post}")  # True!
    
    # ─────────────────────────────────────────────────────────
    # PASUL 5: Test serializare (to_dict / from_dict)
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 5: Test serializare (salvare/încărcare)...")
    
    # Convertește la dict
    tweet_dict = tweet_with_media.to_dict()
    print(f"\n   to_dict() result:")
    print(f"   {tweet_dict}")
    
    # Recreează din dict
    tweet_restored = Tweet.from_dict(tweet_dict)
    print(f"\n   from_dict() - Tweet restaurat:")
    print(f"   ├── id: {tweet_restored.id}")
    print(f"   ├── rephrased_text: {tweet_restored.rephrased_text}")
    print(f"   └── media[0].enhanced_path: {tweet_restored.media[0].enhanced_path}")
    
    # ─────────────────────────────────────────────────────────
    # FINAL
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("✅ TEST 1 COMPLET: Models funcționează corect!")
    print("=" * 60)


if __name__ == "__main__":
    test_models()