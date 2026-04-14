from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

def score_song(song: Song, user: UserProfile) -> Tuple[float, List[str]]:
    """
    Scores a single song against a user profile using the weighted formula:
      score = 0.4 × genre_match + 0.3 × mood_match + 0.2 × energy_match + 0.1 × acoustic_match

    Returns (score, reasons) where reasons explains each component that contributed.
    """
    reasons: List[str] = []

    # --- genre_match ---
    genre_match = 1.0 if song.genre == user.favorite_genre else 0.0
    if genre_match:
        reasons.append(f"Genre match: {song.genre}")

    # --- valence_alignment ---
    if user.favorite_mood in ("happy", "intense"):
        valence_alignment = song.valence          # high valence = good fit
    else:  # chill, moody, relaxed, focused, or anything else
        valence_alignment = 1.0 - song.valence    # low valence = better fit

    # --- mood_match ---
    base_mood = 0.7 if song.mood == user.favorite_mood else 0.0
    mood_match = base_mood + 0.3 * valence_alignment
    if base_mood:
        reasons.append(f"Mood match: {song.mood}")
    if valence_alignment >= 0.6:
        reasons.append(f"Valence suits your '{user.favorite_mood}' preference (valence={song.valence:.2f})")

    # --- energy_match ---
    energy_match = 1.0 - abs(song.energy - user.target_energy)
    if energy_match >= 0.8:
        reasons.append(f"Energy level is a strong fit ({song.energy:.2f} vs target {user.target_energy:.2f})")
    elif energy_match >= 0.5:
        reasons.append(f"Energy level is a reasonable fit ({song.energy:.2f} vs target {user.target_energy:.2f})")

    # --- acoustic_match ---
    if user.likes_acoustic:
        acoustic_match = song.acousticness
        if acoustic_match >= 0.6:
            reasons.append(f"Acoustic-friendly song (acousticness={song.acousticness:.2f})")
    else:
        acoustic_match = 1.0 - song.acousticness
        if acoustic_match >= 0.6:
            reasons.append(f"Non-acoustic style fits your preference (acousticness={song.acousticness:.2f})")

    score = (
        0.4 * genre_match
        + 0.3 * mood_match
        + 0.2 * energy_match
        + 0.1 * acoustic_match
    )

    return round(score, 4), reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of songs available for recommendation."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by score for the given user profile."""
        scored = [(song, score_song(song, user)[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        _, reasons = score_song(song, user)
        return "; ".join(reasons) if reasons else "No strong match factors found."

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    user = UserProfile(
        favorite_genre=user_prefs["favorite_genre"],
        favorite_mood=user_prefs["favorite_mood"],
        target_energy=float(user_prefs["target_energy"]),
        likes_acoustic=bool(user_prefs["likes_acoustic"]),
    )

    def _score(song_dict: Dict) -> Tuple[Dict, float, str]:
        """Score a single song dict and return it paired with its score and reason string."""
        song = Song(
            id=int(song_dict["id"]),
            title=song_dict["title"],
            artist=song_dict["artist"],
            genre=song_dict["genre"],
            mood=song_dict["mood"],
            energy=float(song_dict["energy"]),
            tempo_bpm=float(song_dict["tempo_bpm"]),
            valence=float(song_dict["valence"]),
            danceability=float(song_dict["danceability"]),
            acousticness=float(song_dict["acousticness"]),
        )
        score, reasons = score_song(song, user)
        return song_dict, score, "; ".join(reasons) if reasons else "No strong match factors."

    return sorted((_score(s) for s in songs), key=lambda x: x[1], reverse=True)[:k]
