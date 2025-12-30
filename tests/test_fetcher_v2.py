"""
TEST 2: Verifică Fetcher - descarcă tweets de pe Twitter.
ATENȚIE: Acest test apelează Twitter API!
"""

import sys
sys.path.insert(0, "src")

from fetcher import TwitterFetcher
from models import MediaType


def test_fetcher():
    print("\n" + "=" * 60)
    print("🧪 TEST 2: FETCHER")
    print("=" * 60)
    
    # ─────────────────────────────────────────────────────────
    # PASUL 1: Creează Fetcher
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 1: Creez TwitterFetcher...")
    
    fetcher = TwitterFetcher()
    
    print(f"   ✅ Fetcher creat!")
    print(f"   │")
    print(f"   └── client: {type(fetcher.client)}")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 2: Fetch tweets (FĂRĂ download)
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 2: Fetch tweets (fără download)...")
    print(f"   Apelând Twitter API...")
    
    tweets = fetcher.fetch_tweets(
        username="SheTradesIct",
        count=5
    )
    
    print(f"\n   ✅ Am primit {len(tweets)} tweets de la API!")
    
    # Afișează fiecare tweet
    for i, tweet in enumerate(tweets, 1):
        print(f"\n   📝 Tweet #{i}:")
        print(f"   │")
        print(f"   ├── ID: {tweet.id}")
        print(f"   ├── Author: @{tweet.author}")
        print(f"   ├── Text: {tweet.original_text[:60]}...")
        print(f"   ├── Likes: {tweet.likes}")
        print(f"   ├── Retweets: {tweet.retweets}")
        print(f"   ├── has_media: {tweet.has_media}")
        print(f"   ├── has_photo: {tweet.has_photo}")
        print(f"   ├── is_downloaded: {tweet.is_downloaded}")  # False (nu am descărcat)
        
        if tweet.has_media:
            print(f"   │")
            print(f"   └── Media ({len(tweet.media)} items):")
            for j, m in enumerate(tweet.media):
                print(f"       [{j}] type: {m.type.value}")
                print(f"           url: {m.url[:50]}...")
                print(f"           local_path: {m.local_path}")  # None
    
    # ─────────────────────────────────────────────────────────
    # PASUL 3: Download media pentru UN tweet
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 3: Download media pentru un tweet...")
    
    # Găsește primul tweet cu imagine
    tweet_with_photo = None
    for tweet in tweets:
        if tweet.has_photo:
            tweet_with_photo = tweet
            break
    
    if tweet_with_photo:
        print(f"   Am găsit tweet cu imagine: {tweet_with_photo.id}")
        print(f"\n   ÎNAINTE de download:")
        print(f"   ├── is_downloaded: {tweet_with_photo.is_downloaded}")
        print(f"   └── media[0].local_path: {tweet_with_photo.media[0].local_path}")
        
        # Download
        fetcher.download_media(tweet_with_photo)
        
        print(f"\n   DUPĂ download:")
        print(f"   ├── is_downloaded: {tweet_with_photo.is_downloaded}")
        print(f"   └── media[0].local_path: {tweet_with_photo.media[0].local_path}")
    else:
        print(f"   ⚠️ Nu am găsit tweets cu imagini")
    
    # ─────────────────────────────────────────────────────────
    # PASUL 4: Fetch AND download într-un singur apel
    # ─────────────────────────────────────────────────────────
    print("\n📌 PASUL 4: fetch_and_download() - totul într-un apel...")
    
    all_tweets = fetcher.fetch_and_download(
        username="SheTradesIct",
        count=3
    )
    
    print(f"\n   ✅ Rezultat final:")
    for i, tweet in enumerate(all_tweets, 1):
        print(f"\n   Tweet #{i} (ID: {tweet.id}):")
        print(f"   ├── Text: {tweet.original_text[:40]}...")
        print(f"   ├── is_downloaded: {tweet.is_downloaded}")
        if tweet.has_media:
            print(f"   └── media[0].local_path: {tweet.media[0].local_path}")
    
    # ─────────────────────────────────────────────────────────
    # FINAL
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("✅ TEST 2 COMPLET: Fetcher funcționează corect!")
    print("=" * 60)
    
    return all_tweets  # Returnăm pentru testele următoare


if __name__ == "__main__":
    test_fetcher()