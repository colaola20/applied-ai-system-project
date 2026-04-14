"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Taste profile: target values for each song feature used in scoring
    user_prefs = {
        "favorite_genre": "indie pop",   # preferred genre label (categorical match)
        "favorite_mood": "happy",        # preferred mood label (categorical match)
        "target_energy": 0.78,           # 0.0 (calm) → 1.0 (intense)
        "likes_acoustic": False,         # boolean flag for acoustic preference
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 60
    print("\n" + "=" * width)
    print(f"  Top {len(recommendations)} Music Recommendations")
    print("=" * width)

    for rank, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reasons = explanation.split("; ")

        title_line = f"  #{rank}  {song['title']}"
        score_str = f"Score: {score:.2f}"
        gap = width - len(title_line) - len(score_str)
        print(f"\n{title_line}{' ' * max(1, gap)}{score_str}")
        print(f"      Artist: {song['artist']}")
        print(f"      Why we picked this:")
        for reason in reasons:
            print(f"        • {reason}")

    print("\n" + "=" * width + "\n")


if __name__ == "__main__":
    main()
