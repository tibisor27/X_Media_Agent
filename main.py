"""
Entry point pentru Twitter Repurpose Agent.
"""

from src.agent import TwitterRepurposeAgent


def main():
    """Exemplu de utilizare."""
    
    agent = TwitterRepurposeAgent()
    
    # Afișează status
    agent.get_status()
    
    # === OPȚIUNI DE UTILIZARE ===
    
    # 1. Fetch de la un account
    agent.fetch_from_account("SheTradesIct", count=5, filter_with_media=True)
    
    # 2. Procesează tot din queue
    agent.process_all_queue()
    
    # 3. Postează unul random
    # agent.post_one_random()
    
    # 4. Ciclu zilnic automat (fetch + process + post)
    # agent.run_daily_cycle(
    #     source_accounts=["SheTradesIct", "AnotherAccount"],
    #     tweets_per_account=5,
    #     posts_per_day=3
    # )


if __name__ == "__main__":
    main()