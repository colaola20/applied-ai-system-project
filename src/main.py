"""
Command line runner for the Music Recommender.

Default mode  — interactive: type what you're in the mood for in plain English.
  env/bin/python src/main.py

Demo mode — runs the original 7 hardcoded profiles (no API call needed).
  env/bin/python src/main.py --demo
"""

import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs
from profile_parser import parse_profile

WIDTH = 60


def print_recommendations(profile_name: str, prefs: dict, songs: list, k: int = 5) -> None:
    recommendations = recommend_songs(prefs, songs, k=k)

    print("\n" + "=" * WIDTH)
    print(f"  Profile: {profile_name}")
    acoustic = "yes" if prefs["likes_acoustic"] else "no"
    print(f"  Genre: {prefs['favorite_genre']}  |  Mood: {prefs['favorite_mood']}  "
          f"|  Energy: {prefs['target_energy']}  |  Acoustic: {acoustic}")
    print(f"  Top {len(recommendations)} Music Recommendations")
    print("=" * WIDTH)

    for rank, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reasons = explanation.split("; ")

        title_line = f"  #{rank}  {song['title']}"
        score_str = f"Score: {score:.2f}"
        gap = WIDTH - len(title_line) - len(score_str)
        print(f"\n{title_line}{' ' * max(1, gap)}{score_str}")
        print(f"      Artist: {song['artist']}")
        print(f"      Why we picked this:")
        for reason in reasons:
            print(f"        • {reason}")

    print("\n" + "=" * WIDTH + "\n")


def run_interactive(songs: list) -> None:
    print("\n  MindReader — Music Recommender")
    print("  Tell me what you're in the mood for. Type 'quit' to exit.\n")

    while True:
        try:
            query = input("  What kind of music do you want? > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("  Goodbye!")
            break

        print("  Thinking...")
        try:
            _, prefs = parse_profile(query)
            print_recommendations(f'"{query}"', prefs, songs)
        except Exception as e:
            print(f"  Error: {e}\n")


def run_demo(songs: list) -> None:
    profiles = [
        ("Indie Pop Fan", {
            "favorite_genre": "indie pop",
            "favorite_mood": "happy",
            "target_energy": 0.78,
            "likes_acoustic": False,
        }),
        ("Lofi Studier", {
            "favorite_genre": "lofi",
            "favorite_mood": "focused",
            "target_energy": 0.38,
            "likes_acoustic": True,
        }),
        ("Gym Grinder", {
            "favorite_genre": "metal",
            "favorite_mood": "intense",
            "target_energy": 0.95,
            "likes_acoustic": False,
        }),
        ("Brunch Vibes", {
            "favorite_genre": "jazz",
            "favorite_mood": "relaxed",
            "target_energy": 0.40,
            "likes_acoustic": True,
        }),
        ("[ADVERSARIAL] Phantom Genre (k-pop)", {
            "favorite_genre": "k-pop",
            "favorite_mood": "happy",
            "target_energy": 0.82,
            "likes_acoustic": False,
        }),
        ("[ADVERSARIAL] Out-of-Bounds Energy (target=1.5)", {
            "favorite_genre": "classical",
            "favorite_mood": "melancholic",
            "target_energy": 1.5,
            "likes_acoustic": True,
        }),
        ("[ADVERSARIAL] Uplifting Mood", {
            "favorite_genre": "latin",
            "favorite_mood": "uplifting",
            "target_energy": 0.78,
            "likes_acoustic": False,
        }),
    ]

    for profile_name, prefs in profiles:
        print_recommendations(profile_name, prefs, songs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true",
                        help="Run the 7 hardcoded test profiles instead of interactive mode")
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")

    if args.demo:
        run_demo(songs)
    else:
        run_interactive(songs)


if __name__ == "__main__":
    main()
