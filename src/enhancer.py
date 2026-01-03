"""
Image Enhancer - Enhance imagini cu Recraft AI + Modificare pentru unicitate.
"""

import os
import requests
import json
import time
import base64
from typing import Optional
from src.models import Tweet, MediaType
from src.config import ai_config
from src.image_modifier import ImageModifier  # ← ADAUGĂ ACEST IMPORT


class ImageEnhancer:
    """Enhance imagini cu Recraft AI."""
    
    def __init__(self):
        self.api_key = ai_config.WAVESPEED_API_KEY
        self.base_url = "https://api.wavespeed.ai/api/v3"
        self.timeout = ai_config.ENHANCE_TIMEOUT
        self.modifier = ImageModifier()  # ← ADAUGĂ ACEASTĂ LINIE
        
        if not self.api_key:
            print("⚠️ WAVESPEED_API_KEY nu e setat în config!")
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        print(f"   📦 Encodez imaginea în Base64...")
        
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        print(f"   ✅ Encoded! (lungime: {len(encoded_string)} caractere)")
        return encoded_string
    
    def _submit_upscale_task(self, image_base64: str) -> Optional[str]:
        """
        Trimite task-ul de upscale la API.
        Returnează request_id sau None în caz de eroare.
        """
        print(f"   🚀 Trimit task la Recraft AI...")
        
        url = f"{self.base_url}/recraft-ai/recraft-crisp-upscale"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "enable_base64_output": False,
            "image": image_base64
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            
            if response.status_code == 200:
                result = response.json()["data"]
                request_id = result["id"]
                print(f"   ✅ Task trimis! Request ID: {request_id}")
                return request_id
            else:
                print(f"   ❌ Eroare submit: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Eroare request: {e}")
            return None
    
    def _poll_for_result(self, request_id: str) -> Optional[str]:
        """
        Așteaptă rezultatul și returnează URL-ul imaginii.
        """
        print(f"   ⏳ Aștept rezultatul...")
        
        url = f"{self.base_url}/predictions/{request_id}/result"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                print(f"   ❌ Timeout după {self.timeout} secunde")
                return None
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()["data"]
                    status = result["status"]
                    
                    if status == "completed":
                        image_url = result["outputs"][0]
                        print(f"   ✅ Completat în {elapsed:.1f} secunde!")
                        return image_url
                        
                    elif status == "failed":
                        error = result.get('error', 'Unknown error')
                        print(f"   ❌ Task eșuat: {error}")
                        return None
                        
                    else:
                        print(f"   ⏳ Status: {status} ({elapsed:.1f}s)...")
                        
                else:
                    print(f"   ❌ Eroare poll: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"   ⚠️ Eroare poll: {e}")
            
            time.sleep(1)
    
    def _download_image(self, image_url: str, output_path: str) -> bool:
        """Descarcă imaginea enhanced."""
        print(f"   📥 Descarc imaginea enhanced...")
        
        try:
            response = requests.get(image_url, timeout=30)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                print(f"   ✅ Salvat: {output_path}")
                return True
            else:
                print(f"   ❌ Eroare download: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Eroare download: {e}")
            return False
    
    def _make_image_unique(self, image_path: str) -> str:
        """
        Face imaginea unică pentru a evita detectarea de duplicate.
        ← METODĂ NOUĂ
        """
        print(f"   🎨 Fac imaginea unică...")
        
        result = self.modifier.make_unique(image_path, image_path)  # Suprascrie
        
        print(f"      ✅ Modificări: {self.modifier.get_modifications_log()}")
        
        return result
    
    def enhance_image(
        self, 
        input_path: str, 
        output_path: Optional[str] = None,
        make_unique: bool = True  # ← PARAMETRU NOU
    ) -> Optional[str]:
        """
        Enhance o imagine cu Recraft AI + face unică.
        
        Args:
            input_path: Calea către imaginea originală
            output_path: Calea pentru salvare (optional)
            make_unique: Dacă True, aplică modificări pentru unicitate (anti-detectare)
            
        Returns:
            Calea către imaginea enhanced sau None în caz de eroare
        """
        
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_enhanced{ext}"
        
        print(f"\n✨ ENHANCE IMAGE: {input_path}")
        print(f"   {'─' * 50}")
        
        if not os.path.exists(input_path):
            print(f"   ❌ Fișierul nu există: {input_path}")
            return None
        
        if not self.api_key:
            print(f"   ❌ WAVESPEED_API_KEY nu e configurat!")
            # ← FALLBACK: doar fă imaginea unică
            if make_unique:
                print(f"   ℹ️ Aplic doar modificări de unicitate...")
                import shutil
                shutil.copy2(input_path, output_path)
                self._make_image_unique(output_path)
                return output_path
            return None
        
        # Step 1: Encode în Base64
        image_base64 = self._encode_image_to_base64(input_path)
        
        # Step 2: Submit task
        request_id = self._submit_upscale_task(image_base64)
        if not request_id:
            # ← FALLBACK: doar fă imaginea unică
            if make_unique:
                print(f"   ℹ️ API failed, aplic doar modificări de unicitate...")
                import shutil
                shutil.copy2(input_path, output_path)
                self._make_image_unique(output_path)
                return output_path
            return None
        
        # Step 3: Poll pentru rezultat
        image_url = self._poll_for_result(request_id)
        if not image_url:
            # ← FALLBACK: doar fă imaginea unică
            if make_unique:
                print(f"   ℹ️ Poll failed, aplic doar modificări de unicitate...")
                import shutil
                shutil.copy2(input_path, output_path)
                self._make_image_unique(output_path)
                return output_path
            return None
        
        # Step 4: Download imaginea
        success = self._download_image(image_url, output_path)
        if not success:
            return None
        
        # ═══════════════════════════════════════════════════
        # Step 5: FAC IMAGINEA UNICĂ (ANTI-DETECTARE)  ← NOU!
        # ═══════════════════════════════════════════════════
        if make_unique:
            self._make_image_unique(output_path)
        
        print(f"   {'─' * 50}")
        print(f"   🎉 ENHANCE COMPLET!")
        
        return output_path
    
    def enhance_tweet_media(self, tweet: Tweet) -> Tweet:
        """
        Enhance toate imaginile dintr-un tweet.
        Păstrează legătura media ↔ tweet.
        """
        
        print(f"\n{'═' * 60}")
        print(f"🎨 ENHANCE TWEET MEDIA (ID: {tweet.id})")
        print(f"{'═' * 60}")
        
        if not tweet.has_media:
            print(f"   ℹ️ Tweet-ul nu are media")
            tweet.is_enhanced = True
            return tweet
        
        enhanced_count = 0
        
        for i, media in enumerate(tweet.media):
            print(f"\n   📷 Media #{i+1}:")
            
            if media.type != MediaType.PHOTO:
                print(f"      ⏭️ Skip (type: {media.type.value})")
                continue
            
            if not media.local_path or not os.path.exists(media.local_path):
                print(f"      ⚠️ Media nu e descărcat: {media.local_path}")
                continue
            
            base, ext = os.path.splitext(media.local_path)
            enhanced_path = f"{base}_enhanced{ext}"
            
            # Enhance + Make Unique (make_unique=True by default)
            result = self.enhance_image(media.local_path, enhanced_path, make_unique=True)
            
            if result:
                media.enhanced_path = result
                enhanced_count += 1
            else:
                print(f"      ⚠️ Fallback: folosesc imaginea originală")
                media.enhanced_path = media.local_path
        
        tweet.is_enhanced = True
        
        print(f"\n{'═' * 60}")
        print(f"✅ ENHANCE COMPLET: {enhanced_count}/{len(tweet.media)} imagini")
        print(f"{'═' * 60}")
        
        return tweet