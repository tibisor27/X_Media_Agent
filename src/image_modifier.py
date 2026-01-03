"""
Modifică imaginile pentru a evita detectarea de duplicate pe Twitter.
Aplică modificări subtile dar suficiente pentru hash diferit.
"""

import os
import random
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from pathlib import Path


class ImageModifier:
    """Modifică imaginile pentru a le face unice pe Twitter."""
    
    def __init__(self):
        self.modifications_applied = []
    
    def make_unique(self, image_path: str, output_path: str = None) -> str:
        """
        Aplică modificări subtile pentru a face imaginea unică.
        
        Modificări aplicate (random):
        - Brightness ±5%
        - Contrast ±5%
        - Saturation ±3%
        - Crop minimal (1-5 pixeli)
        - Rotație micro (0.1-0.5 grade)
        - Noise minimal
        - Compression diferită
        
        Args:
            image_path: Calea către imaginea originală
            output_path: Calea pentru output (opțional)
            
        Returns:
            Calea către imaginea modificată
        """
        
        if not os.path.exists(image_path):
            print(f"   ❌ Imagine nu există: {image_path}")
            return image_path
        
        if not output_path:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_unique{ext}"
        
        self.modifications_applied = []
        
        try:
            # Deschide imaginea
            img = Image.open(image_path)
            
            # Convertește la RGB dacă e necesar
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            original_size = img.size
            
            # 1. Brightness (±5%)
            brightness = random.uniform(0.95, 1.05)
            img = ImageEnhance.Brightness(img).enhance(brightness)
            self.modifications_applied.append(f"brightness:{brightness:.3f}")
            
            # 2. Contrast (±5%)
            contrast = random.uniform(0.95, 1.05)
            img = ImageEnhance.Contrast(img).enhance(contrast)
            self.modifications_applied.append(f"contrast:{contrast:.3f}")
            
            # 3. Saturation (±3%)
            saturation = random.uniform(0.97, 1.03)
            img = ImageEnhance.Color(img).enhance(saturation)
            self.modifications_applied.append(f"saturation:{saturation:.3f}")
            
            # 4. Sharpness (±5%)
            sharpness = random.uniform(0.95, 1.05)
            img = ImageEnhance.Sharpness(img).enhance(sharpness)
            self.modifications_applied.append(f"sharpness:{sharpness:.3f}")
            
            # 5. Crop minimal (1-5 pixeli din fiecare parte)
            w, h = img.size
            if w > 100 and h > 100:  # Doar dacă imaginea e suficient de mare
                crop_left = random.randint(1, 5)
                crop_top = random.randint(1, 5)
                crop_right = random.randint(1, 5)
                crop_bottom = random.randint(1, 5)
                
                img = img.crop((
                    crop_left, 
                    crop_top, 
                    w - crop_right, 
                    h - crop_bottom
                ))
                self.modifications_applied.append(f"crop:{crop_left},{crop_top},{crop_right},{crop_bottom}")
            
            # 6. Resize înapoi la dimensiunea originală
            img = img.resize(original_size, Image.Resampling.LANCZOS)
            self.modifications_applied.append(f"resize:{original_size}")
            
            # 7. Rotație micro (foarte mică, imperceptibilă)
            if random.random() > 0.5:
                angle = random.uniform(-0.5, 0.5)
                img = img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False, fillcolor='white')
                self.modifications_applied.append(f"rotate:{angle:.2f}")
            
            # 8. Blur foarte ușor (50% șansă)
            if random.random() > 0.5:
                blur_radius = random.uniform(0.1, 0.3)
                img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                self.modifications_applied.append(f"blur:{blur_radius:.2f}")
            
            # 9. Adaugă noise minimal (modifică pixeli random)
            if random.random() > 0.5:
                img = self._add_minimal_noise(img)
                self.modifications_applied.append("noise:minimal")
            
            # 10. Salvează cu quality random (82-92)
            quality = random.randint(82, 92)
            self.modifications_applied.append(f"quality:{quality}")
            
            # Asigură directorul există
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Salvează
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            print(f"   🎨 Imagine modificată: {os.path.basename(output_path)}")
            
            return output_path
            
        except Exception as e:
            print(f"   ❌ Eroare modificare imagine: {e}")
            return image_path
    
    def _add_minimal_noise(self, img: Image.Image) -> Image.Image:
        """Adaugă noise minimal (modifică ~0.1% din pixeli)."""
        import numpy as np
        
        try:
            # Convertește la numpy array
            arr = np.array(img)
            
            # Calculează câți pixeli să modifice (~0.1%)
            total_pixels = arr.shape[0] * arr.shape[1]
            pixels_to_modify = max(10, int(total_pixels * 0.001))
            
            # Selectează poziții random
            for _ in range(pixels_to_modify):
                y = random.randint(0, arr.shape[0] - 1)
                x = random.randint(0, arr.shape[1] - 1)
                
                # Modifică ușor valorile RGB (±1-3)
                for c in range(min(3, arr.shape[2]) if len(arr.shape) > 2 else 1):
                    delta = random.randint(-3, 3)
                    if len(arr.shape) > 2:
                        arr[y, x, c] = np.clip(arr[y, x, c] + delta, 0, 255)
                    else:
                        arr[y, x] = np.clip(arr[y, x] + delta, 0, 255)
            
            return Image.fromarray(arr)
            
        except ImportError:
            # Dacă numpy nu e instalat, skip noise
            return img
        except Exception:
            return img
    
    def get_modifications_log(self) -> str:
        """Returnează log-ul modificărilor aplicate."""
        return " | ".join(self.modifications_applied)


# Test standalone
if __name__ == "__main__":
    modifier = ImageModifier()
    
    # Testează pe imaginile existente
    test_paths = [
        "data/raw_tweets/1234567890123456789/raw_media_1_enhanced.jpg"
    ]
    
    for path in test_paths:
        if os.path.exists(path):
            print(f"\n🔧 Testing: {path}")
            output = path.replace(".jpg", "_unique_test.jpg")
            modifier.make_unique(path, output)
            print(f"   📝 Modifications: {modifier.get_modifications_log()}")
        else:
            print(f"❌ Nu există: {path}")