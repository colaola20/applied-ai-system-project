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

    # Late-night study session listener — prefers calm, focused lofi with acoustic textures
    lofi_studier = {
        "favorite_genre": "lofi",
        "favorite_mood": "focused",
        "target_energy": 0.38,
        "likes_acoustic": True,
    }

    # High-energy gym-goer — wants punishing metal/EDM with maximum intensity
    gym_grinder = {
        "favorite_genre": "metal",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "likes_acoustic": False,
    }

    # Sunday brunch mood — prefers warm jazz/R&B with a romantic, relaxed feel
    brunch_vibes = {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.40,
        "likes_acoustic": True,
    }

    # --- Adversarial profiles ---

    # Exploit #1: genre that doesn't exist in the dataset.
    # genre_match = 0 for every song — the 0.4 weight never fires.
    # Ranking is driven entirely by mood (0.3) + energy (0.2) + acoustic (0.1).
    phantom_genre = {
        "favorite_genre": "k-pop",
        "favorite_mood": "happy",
        "target_energy": 0.82,
        "likes_acoustic": False,
    }

    # Exploit #2: target_energy above the dataset ceiling (max real value = 0.97).
    # energy_match = 1 - abs(song.energy - 1.5) goes NEGATIVE for calm songs.
    # e.g. Moonlit Sonata (energy=0.24): energy_match = 1 - 1.26 = -0.26
    out_of_bounds_energy = {
        "favorite_genre": "classical",
        "favorite_mood": "melancholic",
        "target_energy": 1.5,
        "likes_acoustic": True,
    }

    # Exploit #3: valence direction bug. "uplifting" is not in ("happy", "intense"),
    # so valence_alignment = 1 - song.valence. High-valence uplifting songs get
    # PENALIZED while sad, low-valence songs score higher on valence alignment.
    valence_direction_bug = {
        "favorite_genre": "latin",
        "favorite_mood": "uplifting",
        "target_energy": 0.78,
        "likes_acoustic": False,
    }

    profiles = [
        ("Indie Pop Fan", user_prefs),
        ("Lofi Studier", lofi_studier),
        ("Gym Grinder", gym_grinder),
        ("Brunch Vibes", brunch_vibes),
        ("[ADVERSARIAL] Phantom Genre (k-pop)", phantom_genre),
        ("[ADVERSARIAL] Out-of-Bounds Energy (target=1.5)", out_of_bounds_energy),
        ("[ADVERSARIAL] Valence Direction Bug (uplifting)", valence_direction_bug),
    ]

    width = 60
    for profile_name, prefs in profiles:
        recommendations = recommend_songs(prefs, songs, k=5)

        print("\n" + "=" * width)
        print(f"  Profile: {profile_name}")
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
