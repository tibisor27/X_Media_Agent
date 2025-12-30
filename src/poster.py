"""
Safe Twitter Poster - postează cu rate limiting și randomizare.
"""

import tweepy
import random
import time
from datetime import datetime, timedelta
from typing import Optional
from src.models import Tweet, MediaType
from src.config import twitter_config, agent_config


class SafePoster:
    """Postează tweets safe, cu delay și randomizare."""
    
    def __init__(self):
        # API v1.1 pentru media upload
        auth = tweepy.OAuth1UserHandler(
            twitter_config.API_KEY,
            twitter_config.API_SECRET,
            twitter_config.ACCESS_TOKEN,
            twitter_config.ACCESS_TOKEN_SECRET
        )
        self.api_v1 = tweepy.API(auth)
        
        # API v2 pentru tweet
        self.client = tweepy.Client(
            consumer_key=twitter_config.API_KEY,
            consumer_secret=twitter_config.API_SECRET,
            access_token=twitter_config.ACCESS_TOKEN,
            access_token_secret=twitter_config.ACCESS_TOKEN_SECRET
        )
        
        self.posts_today = 0
        self.last_post_time: Optional[datetime] = None
    
    def _is_human_hours(self) -> bool:
        """Verifică dacă e în ore 'umane'."""
        hour = datetime.now().hour
        return agent_config.HUMAN_HOURS_START <= hour < agent_config.HUMAN_HOURS_END
    
    def _get_random_delay(self) -> int:
        """Returnează un delay random între posturi."""
        return random.randint(
            agent_config.MIN_DELAY_BETWEEN_POSTS,
            agent_config.MAX_DELAY_BETWEEN_POSTS
        )
    
    def _can_post(self) -> tuple[bool, str]:
        """Verifică dacă poate posta acum."""
        
        # Verifică limita zilnică
        if self.posts_today >= agent_config.MAX_POSTS_PER_DAY:
            return False, f"Limita zilnică atinsă ({agent_config.MAX_POSTS_PER_DAY})"
        
        # Verifică ore umane
        if not self._is_human_hours():
            return False, f"În afara orelor umane ({agent_config.HUMAN_HOURS_START}-{agent_config.HUMAN_HOURS_END})"
        
        # Verifică delay de la ultimul post
        if self.last_post_time:
            elapsed = (datetime.now() - self.last_post_time).total_seconds()
            if elapsed < agent_config.MIN_DELAY_BETWEEN_POSTS:
                remaining = agent_config.MIN_DELAY_BETWEEN_POSTS - elapsed
                return False, f"Așteaptă încă {int(remaining/60)} minute"
        
        return True, "OK"
    
    def post_tweet(
        self, 
        tweet: Tweet,
        wait_if_needed: bool = True
    ) -> bool:
        """
        Postează un tweet procesat.
        
        Args:
            tweet: Tweet object procesat (cu rephrased text și enhanced media)
            wait_if_needed: Dacă True, așteaptă dacă nu poate posta acum
            
        Returns:
            True dacă s-a postat cu succes
        """
        
        # Verifică dacă e gata de post
        if not tweet.is_ready_to_post:
            print(f"❌ Tweet {tweet.id} nu e gata de post")
            return False
        
        # Verifică dacă poate posta
        can_post, reason = self._can_post()
        
        if not can_post:
            if wait_if_needed:
                print(f"⏳ {reason}. Aștept...")
                
                # Calculează cât să aștepte
                if "minute" in reason:
                    wait_time = int(reason.split()[2]) * 60 + random.randint(60, 300)
                else:
                    # Așteaptă până în ore umane
                    wait_time = self._get_random_delay()
                
                time.sleep(wait_time)
            else:
                print(f"❌ Nu pot posta: {reason}")
                return False
        
        # Upload media dacă există
        media_ids = []
        
        for media in tweet.media:
            # Folosește enhanced dacă există, altfel original
            media_path = media.enhanced_path or media.local_path
            
            if not media_path:
                continue
            
            try:
                if media.type == MediaType.PHOTO:
                    uploaded = self.api_v1.media_upload(filename=media_path)
                    media_ids.append(uploaded.media_id)
                    print(f"   📤 Uploaded: {media_path}")
                    
                elif media.type == MediaType.VIDEO:
                    uploaded = self.api_v1.media_upload(
                        filename=media_path,
                        media_category="tweet_video"
                    )
                    media_ids.append(uploaded.media_id)
                    print(f"   📤 Uploaded video: {media_path}")
                    
            except Exception as e:
                print(f"   ❌ Eroare upload: {e}")
        
        # Postează tweet
        try:
            response = self.client.create_tweet(
                text=tweet.rephrased_text,
                media_ids=media_ids if media_ids else None
            )
            
            tweet.is_posted = True
            tweet.posted_at = datetime.now()
            self.posts_today += 1
            self.last_post_time = datetime.now()
            
            tweet_id = response.data["id"]
            print(f"✅ Tweet postat!")
            print(f"🔗 https://twitter.com/i/status/{tweet_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Eroare post: {e}")
            return False
    
    def schedule_post(self, tweet: Tweet, delay_minutes: Optional[int] = None):
        """
        Programează un post cu delay.
        
        Args:
            tweet: Tweet de postat
            delay_minutes: Delay în minute (sau random dacă None)
        """
        
        if delay_minutes is None:
            delay_minutes = self._get_random_delay() // 60
        
        print(f"⏰ Tweet programat în {delay_minutes} minute")
        time.sleep(delay_minutes * 60)
        
        return self.post_tweet(tweet)