"""
Entry point pentru Twitter Repurpose Agent.
Rulează DOAR process și post (fără fetch).
Tweets trebuie importate înainte cu import_tweets.py
"""

import sys
from src.agent import TwitterRepurposeAgent


def main():
    """
    Flow principal:
    1. Încarcă tweets din state (deja importate)
    2. Procesează cele neprocesate
    3. Postează unul random
    """
    
    print("🤖 TWITTER REPURPOSE AGENT")
    print("=" * 50)
    
    # Inițializează FĂRĂ fetcher (nu avem nevoie)
    agent = TwitterRepurposeAgent(skip_fetch_init=True)
    
    # Afișează status
    agent.get_status()
    
    # Verifică dacă avem tweets
    if not agent.tweets_queue:
        print("\n❌ Queue-ul e gol!")
        print("   Rulează mai întâi: python import_tweets.py")
        return
    
    # Procesează toate din queue (enhance + rephrase)
    agent.process_all_queue()
    
    # Postează unul random
    agent.post_one_random()
    
    # Status final
    print("\n" + "=" * 50)
    agent.get_status()


def menu():
    """Menu interactiv pentru control manual."""
    
    agent = TwitterRepurposeAgent(skip_fetch_init=True)
    
    while True:
        print(f"\n{'='*40}")
        print("🤖 TWITTER AGENT - MENU")
        print(f"{'='*40}")
        print("1. 📊 Status")
        print("2. ⚙️  Process all queue")
        print("3. 📤 Post one random")
        print("4. 📋 View queue details")
        print("5. 🔄 Process + Post (auto)")
        print("0. ❌ Exit")
        
        choice = input("\nChoose: ").strip()
        
        if choice == "1":
            agent.get_status()
        elif choice == "2":
            agent.process_all_queue()
        elif choice == "3":
            agent.post_one_random()
        elif choice == "4":
            view_queue(agent)
        elif choice == "5":
            agent.process_all_queue()
            agent.post_one_random()
        elif choice == "0":
            print("👋 Bye!")
            break


def view_queue(agent):
    """Afișează detalii queue."""
    
    print(f"\n📋 QUEUE ({len(agent.tweets_queue)} tweets):")
    print("-" * 60)
    
    for i, tweet in enumerate(agent.tweets_queue, 1):
        ready = "✅" if tweet.is_ready_to_post else "⏳"
        enhanced = "🖼️" if tweet.is_enhanced else "📷"
        rephrased = "✍️" if tweet.is_rephrased else "📝"
        
        print(f"\n{i}. {ready} [{tweet.id}]")
        print(f"   Author: @{tweet.author}")
        print(f"   Original: {tweet.original_text[:50]}...")
        
        if tweet.rephrased_text:
            print(f"   Rephrased: {tweet.rephrased_text[:50]}...")
        
        print(f"   Status: {enhanced} {rephrased}")
        print(f"   Media: {len(tweet.media)} items")


if __name__ == "__main__":
    # Mod automat (default)
    if len(sys.argv) == 1:
        main()
    
    # Mod interactiv
    elif sys.argv[1] == "--menu":
        menu()
    
    # Help
    else:
        print("Usage:")
        print("  python main.py         # Auto: process + post")
        print("  python main.py --menu  # Interactive menu")