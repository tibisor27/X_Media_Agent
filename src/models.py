"""
Data models - păstrează legătura tweet ↔ media ↔ text.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MediaType(Enum):
    PHOTO = "photo"
    VIDEO = "video"
    GIF = "animated_gif"
    NONE = "none"


@dataclass
class Media:
    """Un media item (imagine/video) din tweet."""
    media_key: str
    type: MediaType
    url: str
    local_path: Optional[str] = None
    enhanced_path: Optional[str] = None


@dataclass
class Tweet:
    """
    Un tweet complet cu toate datele legate împreună.
    """
    id: str
    author: str
    original_text: str
    rephrased_text: Optional[str] = None
    media: List[Media] = field(default_factory=list)
    created_at: Optional[datetime] = None
    likes: int = 0
    retweets: int = 0
    
    # Status processing
    is_downloaded: bool = False
    is_enhanced: bool = False
    is_rephrased: bool = False
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    
    @property
    def has_media(self) -> bool:
        return len(self.media) > 0
    
    @property
    def has_photo(self) -> bool:
        return any(m.type == MediaType.PHOTO for m in self.media)
    
    @property
    def has_video(self) -> bool:
        return any(m.type == MediaType.VIDEO for m in self.media)
    
    @property
    def is_ready_to_post(self) -> bool:
        if not self.rephrased_text:
            return False
        if self.has_media and not self.is_enhanced:
            return False
        return True
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "author": self.author,
            "original_text": self.original_text,
            "rephrased_text": self.rephrased_text,
            "media": [
                {
                    "media_key": m.media_key,
                    "type": m.type.value,
                    "url": m.url,
                    "local_path": m.local_path,
                    "enhanced_path": m.enhanced_path
                }
                for m in self.media
            ],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "likes": self.likes,
            "retweets": self.retweets,
            "is_posted": self.is_posted,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Tweet":
        tweet = cls(
            id=data["id"],
            author=data["author"],
            original_text=data["original_text"],
            rephrased_text=data.get("rephrased_text"),
            likes=data.get("likes", 0),
            retweets=data.get("retweets", 0),
            is_posted=data.get("is_posted", False)
        )
        
        for m in data.get("media", []):
            tweet.media.append(Media(
                media_key=m["media_key"],
                type=MediaType(m["type"]),
                url=m["url"],
                local_path=m.get("local_path"),
                enhanced_path=m.get("enhanced_path")
            ))
        
        if data.get("created_at"):
            tweet.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("posted_at"):
            tweet.posted_at = datetime.fromisoformat(data["posted_at"])
        
        return tweet