"""
Modifică video-uri pentru a evita detectarea de duplicate pe Twitter.
Aplică modificări subtile dar suficiente pentru hash diferit.
Necesită ffmpeg instalat.
"""

import os
import random
import subprocess
import shutil
from typing import Optional, Tuple


class VideoModifier:
    """Modifică video-uri pentru a le face unice pe Twitter."""
    
    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
        self.modifications_applied = []
    
    def _check_ffmpeg(self) -> bool:
        """Verifică dacă ffmpeg e instalat."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("   ✅ ffmpeg detectat")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        print("   ⚠️ ffmpeg nu e instalat - video nu vor fi modificate")
        print("   💡 Instalează cu: brew install ffmpeg")
        return False
    
    def _get_video_info(self, video_path: str) -> Tuple[int, int, float]:
        """
        Obține informații despre video (width, height, duration).
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,duration',
                '-of', 'csv=p=0',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                width = int(parts[0]) if parts[0] else 1920
                height = int(parts[1]) if parts[1] else 1080
                duration = float(parts[2]) if len(parts) > 2 and parts[2] else 60.0
                return width, height, duration
        except Exception as e:
            print(f"      ⚠️ Nu pot citi info video: {e}")
        
        return 1920, 1080, 60.0  # Default values
    
    def make_unique(self, video_path: str, output_path: str = None) -> str:
        """
        Aplică modificări subtile la video pentru unicitate.
        
        Modificări aplicate:
        - Brightness ±3%
        - Contrast ±3%
        - Saturation ±2%
        - Crop minimal (2-6 pixeli din fiecare parte)
        - Hue shift minimal (±1)
        - Re-encode cu bitrate ușor diferit
        - Metadata diferită
        
        Args:
            video_path: Calea către video-ul original
            output_path: Calea pentru output (opțional)
            
        Returns:
            Calea către video-ul modificat
        """
        
        if not self.ffmpeg_available:
            print(f"      ⚠️ ffmpeg indisponibil, video rămâne original")
            return video_path
        
        if not os.path.exists(video_path):
            print(f"      ❌ Video nu există: {video_path}")
            return video_path
        
        if not output_path:
            base, ext = os.path.splitext(video_path)
            output_path = f"{base}_unique{ext}"
        
        self.modifications_applied = []
        
        print(f"      🎬 Modificare video pentru unicitate...")
        
        try:
            # Obține dimensiunile video-ului
            width, height, duration = self._get_video_info(video_path)
            print(f"      📐 Dimensiuni: {width}x{height}, {duration:.1f}s")
            
            # ═══════════════════════════════════════════════
            # Generează parametri random
            # ═══════════════════════════════════════════════
            
            # Brightness: -0.03 to 0.03 (±3%)
            brightness = round(random.uniform(-0.03, 0.03), 3)
            self.modifications_applied.append(f"bright:{brightness}")
            
            # Contrast: 0.97 to 1.03 (±3%)
            contrast = round(random.uniform(0.97, 1.03), 3)
            self.modifications_applied.append(f"contr:{contrast}")
            
            # Saturation: 0.98 to 1.02 (±2%)
            saturation = round(random.uniform(0.98, 1.02), 3)
            self.modifications_applied.append(f"sat:{saturation}")
            
            # Hue shift: -1 to 1
            hue = round(random.uniform(-1, 1), 2)
            self.modifications_applied.append(f"hue:{hue}")
            
            # Crop: 2-6 pixeli din fiecare parte (trebuie să fie par pentru codec)
            crop_px = random.randint(1, 3) * 2  # 2, 4, sau 6 pixeli
            crop_w = width - (crop_px * 2)
            crop_h = height - (crop_px * 2)
            
            # Asigură dimensiuni pare (necesar pentru h264)
            crop_w = crop_w - (crop_w % 2)
            crop_h = crop_h - (crop_h % 2)
            
            self.modifications_applied.append(f"crop:{crop_px}px")
            
            # ═══════════════════════════════════════════════
            # Construiește filtrul video
            # ═══════════════════════════════════════════════
            
            video_filters = []
            
            # 1. Crop
            video_filters.append(f"crop={crop_w}:{crop_h}:{crop_px}:{crop_px}")
            
            # 2. Scale înapoi la dimensiunile originale (creează pixeli noi)
            final_w = width - (width % 2)  # Asigură par
            final_h = height - (height % 2)
            video_filters.append(f"scale={final_w}:{final_h}:flags=lanczos")
            
            # 3. Color adjustments
            video_filters.append(f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}")
            
            # 4. Hue adjustment
            video_filters.append(f"hue=h={hue}")
            
            # 5. Noise foarte subtil (50% șansă)
            if random.random() > 0.5:
                noise_strength = random.randint(1, 3)
                video_filters.append(f"noise=alls={noise_strength}:allf=t")
                self.modifications_applied.append(f"noise:{noise_strength}")
            
            # Combină filtrele
            vf_string = ",".join(video_filters)
            
            # ═══════════════════════════════════════════════
            # Parametri de encoding variabili
            # ═══════════════════════════════════════════════
            
            # CRF random (calitate): 18-23 (lower = better quality)
            crf = random.randint(18, 23)
            self.modifications_applied.append(f"crf:{crf}")
            
            # Bitrate audio random
            audio_bitrate = random.choice(['128k', '160k', '192k'])
            self.modifications_applied.append(f"audio:{audio_bitrate}")
            
            # ═══════════════════════════════════════════════
            # Construiește comanda ffmpeg
            # ═══════════════════════════════════════════════
            
            # Creează directorul dacă nu există
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Temp output (pentru a evita probleme la overwrite)
            temp_output = output_path + ".temp.mp4"
            
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite
                '-i', video_path,
                '-vf', vf_string,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', str(crf),
                '-c:a', 'aac',
                '-b:a', audio_bitrate,
                # Metadata diferită
                '-metadata', f'comment=processed_{random.randint(10000, 99999)}',
                '-metadata', f'creation_time={self._random_timestamp()}',
                '-movflags', '+faststart',
                temp_output
            ]
            
            print(f"      ⏳ Procesare video...")
            print(f"      📝 Modificări: {' | '.join(self.modifications_applied[:5])}...")
            
            # Rulează ffmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Mută temp la final
                shutil.move(temp_output, output_path)
                
                # Verifică că fișierul există și are dimensiune
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    original_size = os.path.getsize(video_path)
                    new_size = os.path.getsize(output_path)
                    
                    print(f"      ✅ Video modificat!")
                    print(f"      📊 Size: {original_size/1024/1024:.1f}MB → {new_size/1024/1024:.1f}MB")
                    return output_path
                else:
                    print(f"      ❌ Output invalid")
                    return video_path
            else:
                print(f"      ❌ Eroare ffmpeg: {result.stderr[:200]}")
                # Cleanup temp file
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                return video_path
                
        except subprocess.TimeoutExpired:
            print(f"      ❌ Timeout la procesare video")
            return video_path
        except Exception as e:
            print(f"      ❌ Eroare: {e}")
            return video_path
    
    def _random_timestamp(self) -> str:
        """Generează un timestamp random pentru metadata."""
        import datetime
        
        # Random date în ultimele 30 de zile
        days_ago = random.randint(1, 30)
        dt = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        
        # Adaugă variație la ore/minute/secunde
        dt = dt.replace(
            hour=random.randint(6, 22),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    def get_modifications_log(self) -> str:
        """Returnează log-ul modificărilor aplicate."""
        return " | ".join(self.modifications_applied)


# Test standalone
if __name__ == "__main__":
    print("\n🎬 VIDEO MODIFIER TEST")
    print("=" * 50)
    
    modifier = VideoModifier()
    
    if not modifier.ffmpeg_available:
        print("\n❌ ffmpeg nu e instalat!")
        print("   Instalează cu: brew install ffmpeg")
    else:
        print("\n✅ ffmpeg disponibil!")
        print("\n💡 Pentru test, rulează cu un video:")
        print("   python -c \"from src.video_modifier import VideoModifier; m = VideoModifier(); m.make_unique('path/to/video.mp4')\"")