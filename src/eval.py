"""
Evaluation loop for MindReader.

Runs all 7 user profiles through the recommender and computes four metrics
for each result set — no external API required.

Metrics (all 0.0–1.0):
  genre_hit_rate   — fraction of top-k songs whose genre matches the request
  mood_hit_rate    — fraction of top-k songs whose mood matches the request
  avg_energy_fit   — average energy proximity  (1 - |song.energy - target|)
  avg_score        — average recommender score across the top-k songs

Usage:
    env/bin/python src/eval.py
    env/bin/python src/eval.py --save   # also writes eval_results.json
"""

import json
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs

PROFILES = {
    "Indie Pop Fan": {
        "favorite_genre": "indie pop",
        "favorite_mood": "happy",
        "target_energy": 0.78,
        "likes_acoustic": False,
    },
    "Lofi Studier": {
        "favorite_genre": "lofi",
        "favorite_mood": "focused",
        "target_energy": 0.38,
        "likes_acoustic": True,
    },
    "Gym Grinder": {
        "favorite_genre": "metal",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "likes_acoustic": False,
    },
    "Brunch Vibes": {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.40,
        "likes_acoustic": True,
    },
    "[ADV] Phantom Genre (k-pop)": {
        "favorite_genre": "k-pop",
        "favorite_mood": "happy",
        "target_energy": 0.82,
        "likes_acoustic": False,
    },
    "[ADV] Out-of-Bounds Energy": {
        "favorite_genre": "classical",
        "favorite_mood": "melancholic",
        "target_energy": 1.5,
        "likes_acoustic": True,
    },
    "[ADV] Uplifting Mood": {
        "favorite_genre": "latin",
        "favorite_mood": "uplifting",
        "target_energy": 0.78,
        "likes_acoustic": False,
    },
}


def evaluate_profile(user_prefs: dict, recs: list) -> dict:
    """Compute evaluation metrics for one profile's recommendation set."""
    if not recs:
        return {
            "genre_hit_rate": 0.0,
            "mood_hit_rate": 0.0,
            "avg_energy_fit": 0.0,
            "avg_score": 0.0,
        }

    target_genre = user_prefs["favorite_genre"]
    target_mood = user_prefs["favorite_mood"]
    # Use clamped energy (mirrors the fix in score_song)
    target_energy = max(0.0, min(1.0, float(user_prefs["target_energy"])))

    genre_hits = sum(1 for song, _, _ in recs if song["genre"] == target_genre)
    mood_hits = sum(1 for song, _, _ in recs if song["mood"] == target_mood)
    energy_fits = [1.0 - abs(float(song["energy"]) - target_energy) for song, _, _ in recs]
    scores = [score for _, score, _ in recs]

    return {
        "genre_hit_rate": round(genre_hits / len(recs), 3),
        "mood_hit_rate": round(mood_hits / len(recs), 3),
        "avg_energy_fit": round(sum(energy_fits) / len(energy_fits), 3),
        "avg_score": round(sum(scores) / len(scores), 3),
    }


def flag_issues(profile_name: str, metrics: dict) -> list[str]:
    """Return a list of warnings for metrics that fall below acceptable thresholds."""
    warnings = []
    is_adversarial = profile_name.startswith("[ADV]")

    if not is_adversarial:
        if metrics["genre_hit_rate"] < 0.6:
            warnings.append(f"low genre hit rate ({metrics['genre_hit_rate']:.0%})")
        if metrics["mood_hit_rate"] < 0.4:
            warnings.append(f"low mood hit rate ({metrics['mood_hit_rate']:.0%})")
    if metrics["avg_energy_fit"] < 0.6:
        warnings.append(f"poor energy fit ({metrics['avg_energy_fit']:.2f})")
    if metrics["avg_score"] < 0.3:
        warnings.append(f"low average score ({metrics['avg_score']:.2f})")

    return warnings


def print_report(all_results: dict) -> None:
    col = 32
    header = f"{'Profile':<{col}} {'Genre%':>7} {'Mood%':>6} {'Energy':>7} {'Score':>6}  Notes"

    print("\n" + "=" * 75)
    print("  MindReader — Evaluation Report")
    print("=" * 75)
    print(header)
    print("-" * 75)

    for name, metrics in all_results.items():
        issues = flag_issues(name, metrics)
        note = "  ⚠ " + ", ".join(issues) if issues else "  ✓ ok"
        print(
            f"{name:<{col}} "
            f"{metrics['genre_hit_rate']:>6.0%}  "
            f"{metrics['mood_hit_rate']:>5.0%}  "
            f"{metrics['avg_energy_fit']:>6.2f}  "
            f"{metrics['avg_score']:>5.2f}"
            f"{note}"
        )

    print("=" * 75)

    avg_score = sum(m["avg_score"] for m in all_results.values()) / len(all_results)
    avg_energy = sum(m["avg_energy_fit"] for m in all_results.values()) / len(all_results)
    print(f"\n  Mean avg_score:      {avg_score:.3f}")
    print(f"  Mean avg_energy_fit: {avg_energy:.3f}")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true", help="Save results to eval_results.json")
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    all_results = {}

    for name, prefs in PROFILES.items():
        recs = recommend_songs(prefs, songs, k=5)
        all_results[name] = evaluate_profile(prefs, recs)

    print_report(all_results)

    if args.save:
        with open("eval_results.json", "w") as f:
            json.dump(all_results, f, indent=2)
        print("Results saved to eval_results.json\n")


if __name__ == "__main__":
    main()
