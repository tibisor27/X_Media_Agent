"""
LLM Text Rephrasing cu Azure OpenAI - Stil ICT (Inner Circle Trader).
"""

import os
from openai import AzureOpenAI
from typing import Optional
from src.models import Tweet
from src.config import ai_config


class TextRephraser:
    """Reformulează text cu Azure OpenAI în stilul ICT."""
    
    def __init__(self):
        # Azure OpenAI config
        self.client = AzureOpenAI(
            api_key=ai_config.API_KEY,
            api_version=ai_config.API_VERSION,
            azure_endpoint=ai_config.ENDPOINT
        )
        self.deployment_name = ai_config.DEPLOYMENT_NAME
        
        print(f"   ✅ Azure OpenAI client creat")
        print(f"   └── Deployment: {self.deployment_name}")
    
    def rephrase(
        self, 
        text: str, 
        max_length: int = 280
    ) -> str:
        """
        Reformulează text în stilul ICT (Inner Circle Trader).
        
        Args:
            text: Textul original
            max_length: Lungime maximă (280 pentru Twitter)
            
        Returns:
            Textul reformulat în stilul ICT
        """
        
        # Curăță textul de mentions și links
        clean_text = self._clean_text(text)
        
        if not clean_text.strip():
            return text
        
        # System prompt - definește stilul ICT
        system_prompt = """You are ICT (Inner Circle Trader / Michael J. Huddleston). 
You rephrase trading-related tweets in YOUR authentic voice and style.

YOUR STYLE CHARACTERISTICS:
- Direct, confident, and authoritative
- Concise - no fluff, no unnecessary explanations
- Use ICT terminology when relevant: liquidity, order blocks, fair value gaps (FVG), breaker blocks, displacement, institutional order flow, smart money
- Assume the audience already knows the basics
- Sometimes use phrases like: "Draw on liquidity", "Seek and destroy", "The algorithm", "Judas swing"
- Can be slightly provocative or challenging
- Use emojis sparingly (only if original has them)

IMPORTANT RULES:
1. Keep the EXACT same meaning - do NOT add new information
2. Do NOT add explanations the original didn't have
3. Keep it under 280 characters
4. Do NOT copy word for word - rephrase naturally
5. If the original mentions a specific pair (EURUSD, GBPUSD, etc.), keep it
6. Do NOT add hashtags unless original has them
7. Be concise - ICT doesn't ramble

Return ONLY the rephrased text, nothing else."""

        user_prompt = f"""Rephrase this trading tweet in ICT's voice:

"{clean_text}"

Remember: 
- Same meaning, ICT's voice
- Max {max_length} characters
- No extra information
- Return ONLY the rephrased text"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=150
            )
            
            rephrased = response.choices[0].message.content.strip()
            
            # Elimină ghilimele dacă LLM le-a adăugat
            rephrased = rephrased.strip('"\'')
            
            # Asigură-te că nu depășește limita
            if len(rephrased) > max_length:
                rephrased = rephrased[:max_length-3] + "..."
            
            return rephrased
            
        except Exception as e:
            print(f"   ❌ Eroare Azure OpenAI: {e}")
            return text  # Returnează originalul în caz de eroare
    
    def _clean_text(self, text: str) -> str:
        """Curăță textul de mentions, links etc."""
        import re
        
        # Remove mentions la început
        text = re.sub(r'^(@\w+\s*)+', '', text)
        
        # Remove t.co links
        text = re.sub(r'https?://t\.co/\w+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def rephrase_tweet(self, tweet: Tweet) -> Tweet:
        """
        Reformulează textul unui tweet în stilul ICT.
        Păstrează legătura cu media.
        
        Args:
            tweet: Tweet object cu original_text
            
        Returns:
            Același Tweet object cu rephrased_text setat
        """
        
        print(f"\n{'═' * 60}")
        print(f"📝 REPHRASE TWEET (ID: {tweet.id})")
        print(f"{'═' * 60}")
        
        print(f"\n   📄 Original:")
        print(f"   \"{tweet.original_text[:100]}{'...' if len(tweet.original_text) > 100 else ''}\"")
        
        print(f"\n   🔄 Apelând Azure OpenAI (stil ICT)...")
        
        tweet.rephrased_text = self.rephrase(tweet.original_text)
        tweet.is_rephrased = True
        
        print(f"\n   ✅ Rephrased (ICT style):")
        print(f"   \"{tweet.rephrased_text}\"")
        
        print(f"\n   📊 Lungime: {len(tweet.original_text)} → {len(tweet.rephrased_text)} caractere")
        
        return tweet