"""
Agent principal - orchestrează tot flow-ul.
"""

import json
import os
import re
import random
import requests
from typing import List, Optional
from datetime import datetime
from src.models import Tweet, Media, MediaType
from src.fetcher import TwitterFetcher
from src.enhancer import ImageEnhancer
from src.rephraser import TextRephraser
from src.poster import SafePoster
from src.config import agent_config


class TwitterRepurposeAgent:
    """
    Agent complet pentru repurposing tweets.
    """
    
    def __init__(self, skip_fetch_init: bool = True):
        """
        Args:
            skip_fetch_init: Dacă True, nu inițializează fetcher-ul (pentru cloud)
        """
        # Fetcher e opțional (poate să nu fie nevoie pe cloud)
        self.fetcher = None if skip_fetch_init else TwitterFetcher()
        
        self.enhancer = ImageEnhancer()
        self.rephraser = TextRephraser()
        self.poster = SafePoster()
        
        self.tweets_queue: List[Tweet] = []
        self.posted_tweets: List[Tweet] = []
        
        self._load_state()
    
    # ═══════════════════════════════════════════════════════════
    # IMPORT MANUAL - Pentru adăugare locală de tweets
    # ═══════════════════════════════════════════════════════════
    
    def add_tweet_manual(
        self,
        tweet_id: str,
        author: str,
        text: str,
        image_urls: List[str] = None,
        likes: int = 0,
        retweets: int = 0
    ) -> Optional[Tweet]:
        """
        Adaugă un tweet manual (fără API).
        
        Args:
            tweet_id: ID-ul tweet-ului (din URL)
            author: Username-ul autorului
            text: Textul tweet-ului
            image_urls: Lista de URL-uri pentru imagini
            likes: Număr de likes
            retweets: Număr de retweets
            
        Returns:
            Tweet object sau None dacă există deja
        """
        
        print(f"\n{'='*50}")
        print(f"📥 ADDING TWEET MANUALLY")
        print(f"{'='*50}")
        
        # Verifică duplicat
        existing_ids = {t.id for t in self.tweets_queue + self.posted_tweets}
        if tweet_id in existing_ids:
            print(f"⚠️ Tweet {tweet_id} există deja!")
            return None
        
        # Creează Tweet
        tweet = Tweet(
            id=tweet_id,
            author=author,
            original_text=text,
            created_at=datetime.now(),
            likes=likes,
            retweets=retweets
        )
        
        # Adaugă media
        if image_urls:
            for i, url in enumerate(image_urls):
                tweet.media.append(Media(
                    media_key=f"manual_{tweet_id}_{i}",
                    type=MediaType.PHOTO,
                    url=url
                ))
        
        print(f"✅ Tweet creat: {tweet_id}")
        print(f"   Author: @{author}")
        print(f"   Text: {text[:50]}...")
        print(f"   Media: {len(tweet.media)} items")
        
        # Download media
        if tweet.has_media:
            self._download_media_manual(tweet)
        
        # Adaugă în queue
        self.tweets_queue.append(tweet)
        self._save_state()
        
        return tweet
    
    def add_tweet_from_url(self, tweet_url: str) -> Optional[Tweet]:
        """
        Adaugă un tweet după URL - extrage ID și fetch minimal.
        NOTĂ: Necesită API pentru fetch complet, sau folosește add_tweet_manual.
        
        Args:
            tweet_url: URL complet (ex: https://twitter.com/user/status/123456)
            
        Returns:
            Tweet object sau None
        """
        
        # Extrage tweet ID
        match = re.search(r'status/(\d+)', tweet_url)
        if not match:
            print(f"❌ URL invalid: {tweet_url}")
            return None
        
        tweet_id = match.group(1)
        
        # Extrage username din URL
        username_match = re.search(r'(?:twitter|x)\.com/(\w+)/status', tweet_url)
        username = username_match.group(1) if username_match else "unknown"
        
        print(f"📋 Extras din URL:")
        print(f"   ID: {tweet_id}")
        print(f"   User: @{username}")
        print(f"\n⚠️ Pentru date complete, folosește add_tweet_manual() cu text și imagini.")
        
        return None  # Returnează None - user trebuie să folosească add_tweet_manual
    
    def _download_media_manual(self, tweet: Tweet) -> None:
        """Download media pentru un tweet adăugat manual."""
        
        tweet_folder = os.path.join(agent_config.DATA_FOLDER, tweet.id)
        os.makedirs(tweet_folder, exist_ok=True)
        
        print(f"📥 Downloading media...")
        
        for i, media in enumerate(tweet.media):
            if not media.url:
                continue
            
            filename = f"{tweet_folder}/raw_media_{i+1}.jpg"
            
            try:
                response = requests.get(media.url, timeout=30)
                response.raise_for_status()
                
                with open(filename, "wb") as f:
                    f.write(response.content)
                
                media.local_path = filename
                print(f"   ✅ Salvat: {filename}")
                
            except Exception as e:
                print(f"   ❌ Eroare download: {e}")
        
        tweet.is_downloaded = True
    
    def import_tweets_batch(self, tweets_data: List[dict]) -> int:
        """
        Import batch de tweets dintr-o listă de dicționare.
        
        Args:
            tweets_data: Lista de dicts cu chei: id, author, text, images (optional)
            
        Returns:
            Numărul de tweets importate
        """
        
        print(f"\n{'='*50}")
        print(f"📦 BATCH IMPORT: {len(tweets_data)} tweets")
        print(f"{'='*50}")
        
        imported = 0
        
        for data in tweets_data:
            tweet = self.add_tweet_manual(
                tweet_id=data.get("id"),
                author=data.get("author", "unknown"),
                text=data.get("text", ""),
                image_urls=data.get("images", []),
                likes=data.get("likes", 0),
                retweets=data.get("retweets", 0)
            )
            
            if tweet:
                imported += 1
        
        print(f"\n✅ Importate: {imported}/{len(tweets_data)} tweets")
        return imported
    
    # ═══════════════════════════════════════════════════════════
    # EXISTING METHODS (unchanged)
    # ═══════════════════════════════════════════════════════════
    
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
        
        if not self.fetcher:
            print("❌ Fetcher nu e inițializat! Folosește add_tweet_manual()")
            return []
        
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
        """Procesează un tweet: enhance + rephrase."""
        
        print(f"\n{'='*50}")
        print(f"⚙️ PROCESSING tweet {tweet.id}")
        print(f"{'='*50}")
        
        # Enhance imagini
        if tweet.has_photo and not tweet.is_enhanced:
            self.enhancer.enhance_tweet_media(tweet)
        else:
            tweet.is_enhanced = True
        
        # Rephrase text
        if not tweet.is_rephrased:
            self.rephraser.rephrase_tweet(tweet)
        
        self._save_state()
        return tweet
    
    def process_all_queue(self):
        """Procesează toate tweets din queue."""
        
        unprocessed = [t for t in self.tweets_queue if not t.is_ready_to_post]
        print(f"\n🔄 Processing {len(unprocessed)} tweets...")
        
        for tweet in unprocessed:
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
        
        if self.tweets_queue:
            print(f"\n📋 QUEUE:")
            for i, t in enumerate(self.tweets_queue[:5], 1):
                status = "✅" if t.is_ready_to_post else "⏳"
                print(f"   {i}. {status} [{t.id}] {t.original_text[:40]}...")