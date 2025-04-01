from firebase_config import db

def get_vote_stats():
    votes_snapshot = db.reference("/votes").get()

    # votes_snapshot is a dictionary {vote_id: {choice, timestamp...}, ...}
    if not votes_snapshot:
        return []

    # Tally votes
    vote_counts = {}
    for vote_id, vote_data in votes_snapshot.items():
        choice = vote_data.get("choice")
        vote_counts[choice] = vote_counts.get(choice, 0) + 1

    # Convert to DataFrame
    import pandas as pd
    stats_df = pd.DataFrame(list(vote_counts.items()), columns=["Candidate", "Votes"])
    return stats_df
