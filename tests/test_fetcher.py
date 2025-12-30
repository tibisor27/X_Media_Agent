"""
Test DOAR funcționalitatea de fetch - izolat.
"""

import sys
sys.path.insert(0, "src")

from src.fetcher import TwitterFetcher


def test_fetch():
    print("🧪 TEST: Fetch tweets")
    print("=" * 50)
    
    # 1. Creează fetcher-ul
    print("\n1️⃣ Creez TwitterFetcher...")
    fetcher = TwitterFetcher()
    print("   ✅ Fetcher creat!")
    
    # 2. Fetch tweets (fără download)
    print("\n2️⃣ Fetch tweets de la @SheTradesIct...")
    tweets = fetcher.fetch_tweets(
        username="SheTradesIct",
        count=5
    )
    print(f"   ✅ Am primit {len(tweets)} tweets!")
    
    # 3. Afișează ce am primit
    print("\n3️⃣ Conținutul tweets:")
    print("-" * 50)
    
    for i, tweet in enumerate(tweets, 1):
        print(f"\n📝 Tweet #{i}")
        print(f"   ID: {tweet.id}")
        print(f"   Author: @{tweet.author}")
        print(f"   Text: {tweet.original_text[:100]}...")
        print(f"   Has media: {tweet.has_media}")
        
        if tweet.has_media:
            print(f"   Media count: {len(tweet.media)}")
            for m in tweet.media:
                print(f"      - {m.type.value}: {m.url[:50]}...")
    
    print("\n" + "=" * 50)
    print("✅ TEST COMPLET!")
    
    return tweets


if __name__ == "__main__":
    test_fetch()