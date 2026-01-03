"""
Script pentru importul manual de tweets.
Rulează ÎNAINTE de deploy pentru a încărca tweets.
"""

from src.agent import TwitterRepurposeAgent


# ═══════════════════════════════════════════════════════════
# TWEETS DE IMPORTAT - Editează aici!
# ═══════════════════════════════════════════════════════════

TWEETS_TO_IMPORT = [
    # Exemplu 1
    {
        "id": "1234567890123456790",
        "author": "shetradesict",
        "text": "Study",
        "images": [
            "https://pbs.twimg.com/media/G9pElNYXMAADojN?format=jpg&name=900x900"
        ],
        "likes": 60,
        "retweets": 3
    },
        {
        "id": "1234567890123456791",
        "author": "ict_dinesh",
        "text": " Study.",
        "images": [
            "https://pbs.twimg.com/media/G9l_7frXsAEqbLm?format=jpg&name=medium"
        ],
        "likes": 60,
        "retweets": 3
    },
    {
        "id": "1234567890123456792",
        "author": "ict_dinesh",
        "text": "A lot of information in one photo",
        "images": [
            "https://pbs.twimg.com/media/G9auUt_XQAAvYHQ?format=jpg&name=900x900"
        ],
        "likes": 100,
        "retweets": 5
    },
    {
        "id": "1234567890123456793",
        "author": "ict_dinesh",
        "text": "Mark these words",
        "images": [
            "https://pbs.twimg.com/media/G9at6FqWoAENk-J?format=jpg&name=900x900"
        ],
        "likes": 60,
        "retweets": 3
    },
    {
        "id": "1234567890123456794",
        "author": "ict_dinesh",
        "text": "Study",
        "images": [
            "https://pbs.twimg.com/media/G9ZpNusXMAAO-ue?format=jpg&name=large"
        ],
        "likes": 320,
        "retweets": 10
    },


]


def main():
    print("🚀 IMPORT TWEETS SCRIPT")
    print("=" * 50)
    
    # Inițializează agent (fără fetcher)
    agent = TwitterRepurposeAgent(skip_fetch_init=True)
    
    # Afișează status înainte
    print("\n📊 ÎNAINTE:")
    agent.get_status()
    
    # Import batch
    if TWEETS_TO_IMPORT:
        agent.import_tweets_batch(TWEETS_TO_IMPORT)
    else:
        print("\n⚠️ TWEETS_TO_IMPORT e gol!")
        print("   Editează import_tweets.py și adaugă tweets.")
    
    # Afișează status după
    print("\n📊 DUPĂ:")
    agent.get_status()
    
    print("\n✅ DONE! Tweets salvate în data/raw_tweets/agent_state.json")
    print("   Acum poți rula: python main.py")


def add_single_tweet():
    """Helper pentru adăugare rapidă de un singur tweet."""
    
    agent = TwitterRepurposeAgent(skip_fetch_init=True)
    
    # Editează aici pentru adăugare rapidă
    agent.add_tweet_manual(
        tweet_id="PUT_ID_HERE",
        author="PUT_USERNAME_HERE",
        text="PUT_TEXT_HERE",
        image_urls=[
            "https://pbs.twimg.com/media/EXAMPLE.jpg"
        ]
    )
    
    agent.get_status()


if __name__ == "__main__":
    main()
    
    # Sau pentru un singur tweet:
    # add_single_tweet()