"""
Script pentru adăugare manuală de tweets (imagini + video).
Usage: python add_tweet.py
"""

import json
import os
import re
import requests
import subprocess
from datetime import datetime
from pathlib import Path


STATE_FILE = "data/raw_tweets/agent_state.json"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"queue": [], "posted": [], "last_updated": None}


def save_state(state):
    state["last_updated"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def download_image(url: str, save_path: str) -> bool:
    """Descarcă imagine de la URL."""
    try:
        # Curăță URL-ul
        if '?' in url:
            clean_url = url.split('?')[0]
            if not clean_url.endswith(('.jpg', '.png', '.jpeg', '.gif')):
                clean_url = url  # Păstrează original dacă nu are extensie
        else:
            clean_url = url
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(clean_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"   ✅ Imagine salvată: {save_path}")
        return True
    except Exception as e:
        print(f"   ❌ Eroare download imagine: {e}")
        return False


def download_video_yt_dlp(tweet_url: str, save_path: str) -> bool:
    """
    Descarcă video cu audio folosind yt-dlp.
    Install: pip install yt-dlp
    """
    try:
        print(f"   📥 Descarc video cu yt-dlp...")
        
        # Asigură directorul
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Comandă yt-dlp - descarcă BEST VIDEO + BEST AUDIO și le combină
        cmd = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Video + Audio
            '--merge-output-format', 'mp4',  # Output MP4
            '-o', save_path,
            '--no-playlist',
            '--no-warnings',
            tweet_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0 and os.path.exists(save_path):
            # Verifică dimensiunea fișierului
            size_mb = os.path.getsize(save_path) / (1024 * 1024)
            print(f"   ✅ Video salvat: {save_path} ({size_mb:.1f} MB)")
            return True
        else:
            # Încearcă metoda alternativă
            print(f"   ⚠️ Prima metodă eșuată, încerc alternativa...")
            return download_video_alternative(tweet_url, save_path)
            
    except FileNotFoundError:
        print(f"   ❌ yt-dlp nu e instalat!")
        print(f"   💡 Instalează cu: pip install yt-dlp")
        return False
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout la download video")
        return False
    except Exception as e:
        print(f"   ❌ Eroare download video: {e}")
        return False


def download_video_alternative(tweet_url: str, save_path: str) -> bool:
    """
    Metodă alternativă de download - fără selecție de format.
    Uneori Twitter nu are stream-uri separate.
    """
    try:
        print(f"   🔄 Încerc download simplu...")
        
        cmd = [
            'yt-dlp',
            '-f', 'best',  # Cea mai bună calitate disponibilă (video+audio combinat)
            '-o', save_path,
            '--no-playlist',
            '--no-warnings',
            tweet_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0 and os.path.exists(save_path):
            size_mb = os.path.getsize(save_path) / (1024 * 1024)
            print(f"   ✅ Video salvat: {save_path} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"   ❌ Download eșuat: {result.stderr[:300]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Eroare: {e}")
        return False


def check_video_has_audio(video_path: str) -> bool:
    """Verifică dacă video-ul are audio."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a',
            '-show_entries', 'stream=codec_type',
            '-of', 'csv=p=0',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        has_audio = 'audio' in result.stdout.lower()
        
        if has_audio:
            print(f"   ✅ Video are audio")
        else:
            print(f"   ⚠️ Video NU are audio!")
            
        return has_audio
        
    except Exception:
        return True  # Presupunem că are


def extract_tweet_id(url_or_id: str) -> str:
    """Extrage ID din URL sau returnează ID-ul direct."""
    if 'status/' in url_or_id:
        match = re.search(r'status/(\d+)', url_or_id)
        if match:
            return match.group(1)
    return url_or_id


def add_tweet():
    """Adaugă un tweet interactiv (imagini sau video)."""
    
    print("\n" + "="*60)
    print("📥 ADĂUGARE TWEET MANUAL (Imagini + Video)")
    print("="*60)
    
    # Tweet URL sau ID
    print("\n1️⃣ Tweet URL sau ID:")
    print("   Exemplu: https://x.com/user/status/123456789")
    url_or_id = input("   > ").strip()
    
    tweet_id = extract_tweet_id(url_or_id)
    tweet_url = url_or_id if 'status/' in url_or_id else None
    print(f"   📋 ID extras: {tweet_id}")
    
    # Verifică duplicat
    state = load_state()
    existing_ids = [t['id'] for t in state['queue'] + state['posted']]
    if tweet_id in existing_ids:
        print(f"   ⚠️ Tweet {tweet_id} există deja!")
        return
    
    # Author
    print("\n2️⃣ Username autor (fără @):")
    author = input("   > ").strip().replace('@', '')
    
    # Text
    print("\n3️⃣ Text tweet (paste, apoi Enter de 2 ori):")
    lines = []
    while True:
        line = input()
        if line == "" and lines:
            break
        if line:
            lines.append(line)
    text = "\n".join(lines)
    
    # Tip media
    print("\n4️⃣ Ce tip de media are?")
    print("   1. 🖼️  Imagini")
    print("   2. 🎬 Video")
    print("   3. 📝 Fără media")
    
    media_choice = input("   > ").strip()
    
    tweet_folder = f"data/raw_tweets/{tweet_id}"
    os.makedirs(tweet_folder, exist_ok=True)
    
    media_list = []
    
    # ═══════════════════════════════════════════════════════════
    # IMAGINI
    # ═══════════════════════════════════════════════════════════
    if media_choice == "1":
        print("\n5️⃣ URL-uri imagini (câte unul pe linie, Enter gol când gata):")
        print("   💡 Click dreapta pe imagine → Copy Image Address")
        
        img_count = 0
        while True:
            url = input("   > ").strip()
            if not url:
                break
            
            img_count += 1
            local_path = f"{tweet_folder}/raw_media_{img_count}.jpg"
            
            if download_image(url, local_path):
                media_list.append({
                    "media_key": f"manual_{tweet_id}_{img_count}",
                    "type": "photo",
                    "url": url,
                    "local_path": local_path,
                    "enhanced_path": None
                })
    
    # ═══════════════════════════════════════════════════════════
    # VIDEO
    # ═══════════════════════════════════════════════════════════
    elif media_choice == "2":
        print("\n5️⃣ Cum vrei să adaugi video-ul?")
        print("   1. 🔗 Download automat din URL tweet (necesită yt-dlp)")
        print("   2. 📂 Am descărcat deja video-ul manual")
        
        video_choice = input("   > ").strip()
        
        local_path = f"{tweet_folder}/raw_media_1.mp4"
        
        if video_choice == "1":
            # Download automat
            if tweet_url:
                success = download_video_yt_dlp(tweet_url, local_path)
                if success:
                    media_list.append({
                        "media_key": f"manual_{tweet_id}_video",
                        "type": "video",
                        "url": tweet_url,
                        "local_path": local_path,
                        "enhanced_path": None
                    })
            else:
                print("   ❌ Trebuie URL-ul complet al tweet-ului pentru download!")
                tweet_url = input("   Introdu URL tweet: ").strip()
                if tweet_url:
                    success = download_video_yt_dlp(tweet_url, local_path)
                    if success:
                        media_list.append({
                            "media_key": f"manual_{tweet_id}_video",
                            "type": "video",
                            "url": tweet_url,
                            "local_path": local_path,
                            "enhanced_path": None
                        })
        
        elif video_choice == "2":
            # Video descărcat manual
            print(f"\n   📂 Pune video-ul în: {tweet_folder}/")
            print(f"   Apoi scrie numele fișierului (ex: video.mp4):")
            filename = input("   > ").strip()
            
            if filename:
                source_path = filename if '/' in filename else f"{tweet_folder}/{filename}"
                
                # Dacă e în alt loc, mută-l
                if os.path.exists(filename) and '/' in filename:
                    import shutil
                    shutil.copy2(filename, local_path)
                    print(f"   ✅ Video copiat în: {local_path}")
                elif os.path.exists(source_path):
                    # Redenumește dacă nu e raw_media_1.mp4
                    if source_path != local_path:
                        import shutil
                        shutil.copy2(source_path, local_path)
                    print(f"   ✅ Video găsit: {local_path}")
                else:
                    print(f"   ❌ Fișierul nu există: {source_path}")
                    print(f"   💡 Descarcă video-ul și pune-l în {tweet_folder}/")
                    return
                
                if os.path.exists(local_path):
                    media_list.append({
                        "media_key": f"manual_{tweet_id}_video",
                        "type": "video",
                        "url": None,
                        "local_path": local_path,
                        "enhanced_path": None
                    })
    
    # Creează tweet dict
    tweet = {
        "id": tweet_id,
        "author": author,
        "original_text": text,
        "rephrased_text": None,
        "media": media_list,
        "created_at": datetime.now().isoformat(),
        "likes": 0,
        "retweets": 0,
        "is_posted": False,
        "posted_at": None
    }
    
    # Adaugă în queue
    state['queue'].append(tweet)
    save_state(state)
    
    print(f"\n✅ TWEET ADĂUGAT!")
    print(f"   ID: {tweet_id}")
    print(f"   Author: @{author}")
    print(f"   Text: {text[:50]}...")
    print(f"   Media: {len(media_list)} items")
    
    if media_list:
        for m in media_list:
            print(f"      - {m['type']}: {m['local_path']}")
    
    print(f"\n📊 Total în queue: {len(state['queue'])}")


def list_queue():
    """Afișează queue-ul."""
    state = load_state()
    
    print(f"\n📋 QUEUE: {len(state['queue'])} tweets")
    print("-" * 60)
    
    for i, t in enumerate(state['queue'], 1):
        ready = "✅" if t.get('rephrased_text') else "⏳"
        media_info = ""
        for m in t.get('media', []):
            media_info += f" [{m['type']}]"
        
        print(f"\n{i}. {ready} [{t['id']}]{media_info}")
        print(f"   @{t['author']}: {t['original_text'][:50]}...")


def check_yt_dlp():
    """Verifică dacă yt-dlp e instalat."""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ yt-dlp instalat: v{result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ yt-dlp nu e instalat")
    print("💡 Instalează cu: pip install yt-dlp")
    return False


def main():
    while True:
        print(f"\n{'='*40}")
        print("📝 TWEET MANAGER")
        print("="*40)
        
        state = load_state()
        print(f"📊 Queue: {len(state['queue'])} | Posted: {len(state['posted'])}")
        
        print("\n1. ➕ Adaugă tweet (imagini/video)")
        print("2. 📋 Vezi queue")
        print("3. 🗑️  Șterge din queue")
        print("4. 🔧 Check yt-dlp (pentru video)")
        print("0. ❌ Ieșire")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            add_tweet()
        elif choice == "2":
            list_queue()
        elif choice == "3":
            list_queue()
            idx = input("\nNr. tweet de șters (sau 'c' pentru cancel): ").strip()
            if idx.isdigit():
                idx = int(idx) - 1
                if 0 <= idx < len(state['queue']):
                    removed = state['queue'].pop(idx)
                    save_state(state)
                    print(f"✅ Șters: {removed['id']}")
        elif choice == "4":
            check_yt_dlp()
        elif choice == "0":
            print("👋 Bye!")
            break


if __name__ == "__main__":
    main()