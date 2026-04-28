"""
Fetches real song data from two public datasets and saves to data/songs.csv.

Source 1 — TidyTuesday 2020 (6 genres: pop, hip-hop, rock, latin, R&B, EDM):
  https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-01-21/spotify_songs.csv

Source 2 — maharshipandya/spotify-tracks-dataset on HuggingFace (114 genres):
  https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset/resolve/main/dataset.csv

No API keys required — both are direct CSV downloads.

Usage:
    env/bin/python scripts/fetch_songs.py
"""

import pandas as pd
import requests
import io
import os

TIDYTUESDAY_URL = (
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/"
    "master/data/2020/2020-01-21/spotify_songs.csv"
)

HUGGINGFACE_URL = (
    "https://huggingface.co/datasets/maharshipandya/"
    "spotify-tracks-dataset/resolve/main/dataset.csv"
)

OUTPUT_PATH = "data/songs.csv"
SONGS_PER_GENRE = 30

# ── Genre maps ────────────────────────────────────────────────────────────────

# Source 1 genres → our catalog labels
TIDYTUESDAY_GENRE_MAP = {
    "pop":   "pop",
    "rap":   "hip-hop",
    "rock":  "rock",
    "latin": "latin",
    "r&b":   "R&B",
    "edm":   "EDM",
}

# Source 2 genres → our catalog labels (only the 9 genres missing from source 1)
HUGGINGFACE_GENRE_MAP = {
    "jazz":        "jazz",
    "classical":   "classical",
    "metal":       "metal",
    "blues":       "blues",
    "country":     "country",
    "ambient":     "ambient",
    "indie-pop":   "indie pop",
    "synth-pop":   "synthwave",
    "chill":       "lofi",       # chill tracks filtered to high acousticness + low energy
}


def infer_mood(energy: float, valence: float,
               danceability: float, acousticness: float) -> str:
    if energy > 0.80 and valence > 0.70:
        return "euphoric" if danceability > 0.78 else "happy"
    if energy > 0.78 and valence < 0.28:
        return "angry"
    if energy > 0.70 and valence < 0.45:
        return "intense"
    if energy > 0.68:
        return "energetic"
    if energy < 0.32 and valence < 0.30:
        return "sad"
    if energy < 0.38 and valence < 0.42:
        return "melancholic"
    if energy < 0.38 and valence > 0.68 and acousticness > 0.50:
        return "romantic"
    if energy < 0.42 and valence > 0.60:
        return "relaxed"
    if energy < 0.50:
        return "chill"
    if valence < 0.28:
        return "moody"
    if valence > 0.78 and danceability > 0.72:
        return "uplifting"
    if valence > 0.65:
        return "happy"
    return "chill"


def build_records(df: pd.DataFrame, genre_col: str,
                  genre_map: dict, extra_filter=None) -> pd.DataFrame:
    """Standardise a raw dataframe into our catalog schema."""
    df = df[df[genre_col].isin(genre_map)].copy()

    feature_cols = ["energy", "valence", "danceability", "acousticness", "tempo"]
    name_cols    = ["title", "artist"]

    # Rename columns to a common schema before filtering
    if "track_name" in df.columns:
        df = df.rename(columns={"track_name": "title", "track_artist": "artist"})
    elif "track_name" in df.columns:
        df = df.rename(columns={"track_name": "title", "artists": "artist"})
    else:
        df = df.rename(columns={"artists": "artist"})
        if "title" not in df.columns:
            df = df.rename(columns={"track_name": "title"})

    df = df.dropna(subset=name_cols + feature_cols)

    if extra_filter is not None:
        df = df[extra_filter(df)]

    pop_col = "track_popularity" if "track_popularity" in df.columns else "popularity"
    df = df.sort_values(pop_col, ascending=False)
    df = df.drop_duplicates(subset=["title", "artist"])

    chunks = [
        g.nlargest(SONGS_PER_GENRE, pop_col)
        for _, g in df.groupby(genre_col)
    ]
    df = pd.concat(chunks).reset_index(drop=True)

    records = []
    for _, row in df.iterrows():
        energy       = round(float(row["energy"]), 2)
        valence      = round(float(row["valence"]), 2)
        danceability = round(float(row["danceability"]), 2)
        acousticness = round(float(row["acousticness"]), 2)
        tempo_bpm    = round(float(row["tempo"]), 1)

        records.append({
            "title":        row["title"],
            "artist":       row["artist"],
            "genre":        genre_map[row[genre_col]],
            "mood":         infer_mood(energy, valence, danceability, acousticness),
            "energy":       energy,
            "tempo_bpm":    tempo_bpm,
            "valence":      valence,
            "danceability": danceability,
            "acousticness": acousticness,
        })

    return pd.DataFrame(records)


def fetch_csv(url: str, label: str) -> pd.DataFrame:
    print(f"Downloading {label}…")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))


def main():
    # ── Source 1: TidyTuesday (6 genres) ─────────────────────────────────────
    tt = fetch_csv(TIDYTUESDAY_URL, "TidyTuesday dataset")
    tt = tt.rename(columns={"track_name": "title", "track_artist": "artist"})
    df1 = build_records(tt, "playlist_genre", TIDYTUESDAY_GENRE_MAP)
    print(f"  → {len(df1)} songs from Source 1 ({len(TIDYTUESDAY_GENRE_MAP)} genres)")

    # ── Source 2: HuggingFace (9 missing genres) ──────────────────────────────
    hf = fetch_csv(HUGGINGFACE_URL, "HuggingFace dataset")
    hf = hf.rename(columns={"track_name": "title", "artists": "artist"})

    # For "chill" → lofi, only keep tracks that are genuinely lo-fi in texture
    def lofi_filter(df):
        is_chill = df["track_genre"] == "chill"
        is_lofi  = (df["acousticness"] > 0.30) & (df["energy"] < 0.60)
        return (~is_chill) | (is_chill & is_lofi)

    df2 = build_records(hf, "track_genre", HUGGINGFACE_GENRE_MAP,
                        extra_filter=lofi_filter)
    print(f"  → {len(df2)} songs from Source 2 ({len(HUGGINGFACE_GENRE_MAP)} genres)")

    # ── Combine, assign IDs, save ─────────────────────────────────────────────
    combined = pd.concat([df1, df2], ignore_index=True)
    combined = combined.drop_duplicates(subset=["title", "artist"]).reset_index(drop=True)
    combined.insert(0, "id", range(1, len(combined) + 1))

    combined.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved {len(combined)} songs to {OUTPUT_PATH}")
    print("\nGenre breakdown:")
    for genre, count in combined["genre"].value_counts().sort_index().items():
        print(f"  {genre:<12} {count} songs")
    print("\nMood breakdown:")
    for mood, count in combined["mood"].value_counts().items():
        print(f"  {mood:<14} {count} songs")


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    main()
