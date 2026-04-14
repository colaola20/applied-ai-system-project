"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

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

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
