"""
Agent principal - orchestrează tot flow-ul.
"""

import json
import os
import random
from typing import List, Optional
from datetime import datetime
from src.models import Tweet
from src.fetcher import TwitterFetcher
from src.enhancer import ImageEnhancer
from src.rephraser import TextRephraser
from src.poster import SafePoster
from src.config import agent_config


class TwitterRepurposeAgent:
    """
    Agent complet pentru repurposing tweets.
    """
    
    def __init__(self):
        self.fetcher = TwitterFetcher()
        self.enhancer = ImageEnhancer()
        self.rephraser = TextRephraser()
        self.poster = SafePoster()
        
        self.tweets_queue: List[Tweet] = []
        self.posted_tweets: List[Tweet] = []
        
        self._load_state()
    
    def _get_state_path(self) -> str:
        return os.path.join(agent_config.DATA_FOLDER, "agent_state.json")
    
    def _save_state(self):
        """Salvează starea agentului."""
        state = {
            "queue": [t.to_dict() for t in self.tweets_queue],
            "posted": [t.to_dict() for t in self.posted_tweets],
            "last_updated": datetime.now().isoformat()
        }
        
        os.makedirs(agent_config.DATA_FOLDER, exist_ok=True)
        with open(self._get_state_path(), "w") as f:
            json.dump(state, f, indent=2)
    
    def _load_state(self):
        """Încarcă starea anterioară."""
        state_path = self._get_state_path()
        
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    state = json.load(f)
                
                self.tweets_queue = [Tweet.from_dict(t) for t in state.get("queue", [])]
                self.posted_tweets = [Tweet.from_dict(t) for t in state.get("posted", [])]
                
                print(f"📂 State loaded: {len(self.tweets_queue)} în queue, {len(self.posted_tweets)} postate")
            except Exception as e:
                print(f"⚠️ Eroare load state: {e}")
    
    def fetch_from_account(
        self, 
        username: str, 
        count: int = 10,
        filter_with_media: bool = False
    ) -> List[Tweet]:
        """Fetch tweets de la un account și le adaugă în queue."""
        
        print(f"\n{'='*50}")
        print(f"📥 FETCHING de la @{username}")
        print(f"{'='*50}")
        
        tweets = self.fetcher.fetch_and_download(username, count)
        
        if filter_with_media:
            tweets = [t for t in tweets if t.has_media]
            print(f"   Filtrate: {len(tweets)} tweets cu media")
        
        existing_ids = {t.id for t in self.tweets_queue + self.posted_tweets}
        new_tweets = [t for t in tweets if t.id not in existing_ids]
        
        self.tweets_queue.extend(new_tweets)
        self._save_state()
        
        print(f"✅ Adăugate {len(new_tweets)} tweets noi în queue")
        return new_tweets
    
    def process_tweet(self, tweet: Tweet) -> Tweet:
        """
        Procesează un tweet: enhance + rephrase (stil ICT).
        """
        
        print(f"\n{'='*50}")
        print(f"⚙️ PROCESSING tweet {tweet.id}")
        print(f"{'='*50}")
        
        # Enhance imagini
        if tweet.has_photo:
            self.enhancer.enhance_tweet_media(tweet)
        else:
            tweet.is_enhanced = True  # Marchează ca enhanced dacă nu are imagini
        
        # Rephrase text (stil ICT - hardcodat)
        self.rephraser.rephrase_tweet(tweet)
        
        self._save_state()
        return tweet
    
    def process_all_queue(self):
        """Procesează toate tweets din queue."""
        
        print(f"\n🔄 Processing {len(self.tweets_queue)} tweets...")
        
        for tweet in self.tweets_queue:
            if not tweet.is_ready_to_post:
                self.process_tweet(tweet)
        
        self._save_state()
    
    def post_one_random(self) -> bool:
        """Postează un tweet random din queue."""
        
        ready = [t for t in self.tweets_queue if t.is_ready_to_post and not t.is_posted]
        
        if not ready:
            print("❌ Niciun tweet gata de post în queue")
            return False
        
        tweet = random.choice(ready)
        
        print(f"\n{'='*50}")
        print(f"📤 POSTING tweet {tweet.id}")
        print(f"{'='*50}")
        
        success = self.poster.post_tweet(tweet)
        
        if success:
            self.tweets_queue.remove(tweet)
            self.posted_tweets.append(tweet)
            self._save_state()
        
        return success
    
    def run_daily_cycle(
        self,
        source_accounts: List[str],
        tweets_per_account: int = 5,
        posts_per_day: int = 3
    ):
        """Rulează un ciclu zilnic complet."""
        
        print(f"\n{'='*60}")
        print(f"🤖 STARTING DAILY CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")
        
        # 1. Fetch dacă queue e aproape gol
        if len(self.tweets_queue) < posts_per_day * 2:
            for account in source_accounts:
                self.fetch_from_account(account, tweets_per_account, filter_with_media=True)
        
        # 2. Procesează toate
        self.process_all_queue()
        
        # 3. Postează cu delay
        for i in range(posts_per_day):
            print(f"\n📍 Post {i+1}/{posts_per_day}")
            
            success = self.post_one_random()
            
            if success and i < posts_per_day - 1:
                delay = random.randint(
                    agent_config.MIN_DELAY_BETWEEN_POSTS,
                    agent_config.MAX_DELAY_BETWEEN_POSTS
                )
                print(f"😴 Sleeping {delay//60} minute până la următorul post...")
                import time
                time.sleep(delay)
        
        print(f"\n✅ Daily cycle complete!")
        self._save_state()
    
    def get_status(self):
        """Afișează status agent."""
        
        print(f"\n{'='*40}")
        print("📊 AGENT STATUS")
        print(f"{'='*40}")
        print(f"📋 În queue: {len(self.tweets_queue)}")
        print(f"   - Gata de post: {len([t for t in self.tweets_queue if t.is_ready_to_post])}")
        print(f"   - Need processing: {len([t for t in self.tweets_queue if not t.is_ready_to_post])}")
        print(f"✅ Postate: {len(self.posted_tweets)}")
        print(f"📤 Posturi azi: {self.poster.posts_today}/{agent_config.MAX_POSTS_PER_DAY}")