"""
Fetch tweets de pe Twitter - păstrează legătura tweet ↔ media.
"""

import tweepy
import requests
import os
from typing import List
from src.models import Tweet, Media, MediaType
from src.config import twitter_config, agent_config


class TwitterFetcher:
    """Fetch și download tweets cu media."""
    
    def __init__(self):
        # Client pentru READ
        self.client = tweepy.Client(
            bearer_token=twitter_config.BEARER_TOKEN,
            wait_on_rate_limit=True
        )
        
        # Creează folder pentru data
        os.makedirs(agent_config.DATA_FOLDER, exist_ok=True)
    
    def fetch_tweets(
        self, 
        username: str, 
        count: int = 10,
        skip_replies: bool = True,
        skip_retweets: bool = True
    ) -> List[Tweet]:
        """
        Fetch tweets de la un user.
        
        Returns:
            Lista de Tweet objects cu media atașat.
        """
        
        print(f"🔍 Fetching tweets de la @{username}...")
        
        # Get user ID
        user = self.client.get_user(username=username)
        print(f"User: {user}")
        if not user.data:
            print(f"❌ User @{username} nu există")
            return []
        
        user_id = user.data.id
        
        # Fetch tweets cu media
        api_count = max(count, 5)  # Minim 5 pentru API
        
        response = self.client.get_users_tweets(
            id=user_id,
            max_results=min(api_count, 100),
            tweet_fields=["created_at", "public_metrics", "attachments", "referenced_tweets"],
            expansions=["attachments.media_keys"],
            media_fields=["url", "preview_image_url", "type", "variants"]
        )
        
        # Build media dict
        media_dict = {}
        if response.includes and "media" in response.includes:
            for m in response.includes["media"]:
                media_dict[m.media_key] = m
        
        # Process tweets
        tweets = []
        
        for tweet_data in response.data or []:
            # Skip replies
            if skip_replies and tweet_data.text.startswith("@"):
                continue
            
            # Skip retweets
            if skip_retweets and tweet_data.text.startswith("RT @"):
                continue
            
            # Skip dacă are referenced_tweets (e reply sau quote)
            if skip_replies and tweet_data.referenced_tweets:
                continue
            
            # Creează Tweet object
            tweet = Tweet(
                id=str(tweet_data.id),
                author=username,
                original_text=tweet_data.text,
                created_at=tweet_data.created_at,
                likes=tweet_data.public_metrics.get("like_count", 0) if tweet_data.public_metrics else 0,
                retweets=tweet_data.public_metrics.get("retweet_count", 0) if tweet_data.public_metrics else 0
            )
            
            # Atașează media (PĂSTREAZĂ LEGĂTURA!)
            if tweet_data.attachments and "media_keys" in tweet_data.attachments:
                for media_key in tweet_data.attachments["media_keys"]:
                    if media_key in media_dict:
                        m = media_dict[media_key]
                        
                        # Determină URL
                        if m.type == "photo":
                            url = m.url
                        elif m.type == "video" and hasattr(m, "variants"):
                            # Ia varianta cu cea mai mare bitrate
                            variants = [v for v in m.variants if v.get("bit_rate")]
                            if variants:
                                url = max(variants, key=lambda x: x.get("bit_rate", 0))["url"]
                            else:
                                url = m.preview_image_url
                        else:
                            url = m.preview_image_url or ""
                        
                        tweet.media.append(Media(
                            media_key=media_key,
                            type=MediaType(m.type),
                            url=url
                        ))
            
            tweets.append(tweet)
            
            if len(tweets) >= count:
                break
        
        print(f"✅ Fetched {len(tweets)} tweets")
        return tweets
    
    def download_media(self, tweet: Tweet) -> Tweet:
        """
        Download toate media files pentru un tweet.
        Le salvează în folder organizat per tweet ID.
        """
        
        if not tweet.has_media:
            tweet.is_downloaded = True
            return tweet
        
        # Creează folder pentru acest tweet
        tweet_folder = os.path.join(agent_config.DATA_FOLDER, tweet.id)
        os.makedirs(tweet_folder, exist_ok=True)
        
        print(f"📥 Downloading media pentru tweet {tweet.id}...")
        
        for i, media in enumerate(tweet.media):
            if not media.url:
                continue
            
            # Determină extensie
            if media.type == MediaType.PHOTO:
                ext = "jpg"
            elif media.type == MediaType.VIDEO:
                ext = "mp4"
            elif media.type == MediaType.GIF:
                ext = "gif"
            else:
                ext = "bin"
            
            # Download
            filename = f"{tweet_folder}/raw_media_{i+1}.{ext}"
            
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
        return tweet
    
    def fetch_and_download(
        self, 
        username: str, 
        count: int = 10
    ) -> List[Tweet]:
        """Fetch + download într-un singur apel."""
        
        tweets = self.fetch_tweets(username, count)
        
        for tweet in tweets:
            self.download_media(tweet)
        
        return tweets