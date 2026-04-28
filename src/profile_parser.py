"""
Natural language → UserProfile parser for MindReader.

Takes a free-form description of what a listener wants and uses Groq
to map it to a structured UserProfile using only the genres and moods
that exist in the catalog.

This is where the LLM actually contributes to the recommendation pipeline —
it decides the profile values that drive score_song().

Usage:
    env/bin/python src/profile_parser.py
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

sys.path.insert(0, os.path.dirname(__file__))

from groq import Groq
from recommender import UserProfile, load_songs, recommend_songs

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Every value the scorer recognises — nothing outside these lists will score correctly
VALID_GENRES = [
    "pop", "lofi", "rock", "jazz", "ambient", "synthwave",
    "hip-hop", "classical", "latin", "EDM", "country", "R&B",
    "metal", "blues", "indie pop",
]

VALID_MOODS = [
    "happy", "chill", "intense", "relaxed", "focused", "moody",
    "sad", "melancholic", "uplifting", "energetic", "euphoric",
    "nostalgic", "romantic", "angry",
]

SYSTEM_PROMPT = f"""You are a music preference interpreter.
Convert a listener's natural language description into a structured music profile.

Rules:
- favorite_genre MUST be one of: {VALID_GENRES}
  Pick the closest match — never invent a genre not in this list.
- favorite_mood MUST be one of: {VALID_MOODS}
  Pick the closest match — never invent a mood not in this list.
- target_energy: a float from 0.0 (very calm) to 1.0 (very intense).
- likes_acoustic: true if the listener wants acoustic/organic sound, false for electric/produced.

Return ONLY valid JSON with exactly these four keys:
{{
  "favorite_genre": "<genre>",
  "favorite_mood": "<mood>",
  "target_energy": <float>,
  "likes_acoustic": <bool>
}}"""


def parse_profile(query: str) -> tuple[UserProfile, dict]:
    """
    Parse a natural language query into a UserProfile.
    Returns (UserProfile, raw_dict) — the dict is useful for display.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,  # low temperature — we want consistent structured output
        max_tokens=100,
    )

    raw = json.loads(response.choices[0].message.content)

    # Validate and clamp so we never pass bad values to score_song()
    genre = raw["favorite_genre"] if raw["favorite_genre"] in VALID_GENRES else VALID_GENRES[0]
    mood = raw["favorite_mood"] if raw["favorite_mood"] in VALID_MOODS else VALID_MOODS[0]
    energy = max(0.0, min(1.0, float(raw["target_energy"])))
    acoustic = bool(raw["likes_acoustic"])

    profile = UserProfile(
        favorite_genre=genre,
        favorite_mood=mood,
        target_energy=energy,
        likes_acoustic=acoustic,
    )
    return profile, {"favorite_genre": genre, "favorite_mood": mood,
                     "target_energy": energy, "likes_acoustic": acoustic}


def recommend_from_query(query: str, songs: list, k: int = 5) -> tuple[UserProfile, list]:
    """Parse a natural language query and return (profile, recommendations)."""
    profile, prefs = parse_profile(query)
    recs = recommend_songs(prefs, songs, k=k)
    return profile, recs


def main():
    songs = load_songs("data/songs.csv")

    queries = [
        "I want calm acoustic music for studying late at night",
        "Something aggressive and high energy for the gym",
        "Lazy Sunday morning, warm and jazzy, nothing too intense",
        "I'm in the mood for k-pop — upbeat and danceable",
        "Feeling nostalgic, something melancholic and slow",
    ]

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"  Query: \"{query}\"")

        profile, prefs = parse_profile(query)

        print(f"  Parsed profile:")
        print(f"    Genre:    {profile.favorite_genre}")
        print(f"    Mood:     {profile.favorite_mood}")
        print(f"    Energy:   {profile.target_energy}")
        print(f"    Acoustic: {profile.likes_acoustic}")

        recs = recommend_songs(prefs, songs, k=3)
        print(f"  Top recommendations:")
        for song, score, explanation in recs:
            print(f"    • {song['title']} by {song['artist']}  (score: {score:.2f})")
            print(f"      {explanation}")


if __name__ == "__main__":
    main()
