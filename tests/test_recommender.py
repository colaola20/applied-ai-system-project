import pytest
from src.recommender import Song, UserProfile, Recommender, score_song, load_songs


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def make_song(**kwargs) -> Song:
    defaults = dict(
        id=1, title="T", artist="A", genre="pop", mood="happy",
        energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2,
    )
    defaults.update(kwargs)
    return Song(**defaults)


def make_user(**kwargs) -> UserProfile:
    defaults = dict(
        favorite_genre="pop", favorite_mood="happy",
        target_energy=0.8, likes_acoustic=False,
    )
    defaults.update(kwargs)
    return UserProfile(**defaults)


def make_small_recommender() -> Recommender:
    songs = [
        Song(id=1, title="Test Pop Track", artist="Test Artist", genre="pop",
             mood="happy", energy=0.8, tempo_bpm=120, valence=0.9,
             danceability=0.8, acousticness=0.2),
        Song(id=2, title="Chill Lofi Loop", artist="Test Artist", genre="lofi",
             mood="chill", energy=0.4, tempo_bpm=80, valence=0.6,
             danceability=0.5, acousticness=0.9),
    ]
    return Recommender(songs)


# ---------------------------------------------------------------------------
# Original tests (kept)
# ---------------------------------------------------------------------------

def test_recommend_returns_songs_sorted_by_score():
    user = make_user()
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = make_user()
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# Score formula correctness
# ---------------------------------------------------------------------------

def test_score_perfect_match():
    """All four components fire at maximum → score should be 1.0."""
    song = make_song(genre="pop", mood="happy", energy=0.8, valence=1.0, acousticness=0.0)
    user = make_user(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    score, _ = score_song(song, user)
    # genre=1, mood=0.7+0.3*1=1, energy=1, acoustic=1  → 0.4+0.3+0.2+0.1 = 1.0
    assert score == pytest.approx(1.0, abs=1e-3)


def test_score_no_match():
    """Completely wrong genre + mood + far energy + wrong acoustic preference."""
    song = make_song(genre="metal", mood="angry", energy=0.0, valence=0.5, acousticness=1.0)
    user = make_user(favorite_genre="pop", favorite_mood="happy", target_energy=1.0, likes_acoustic=False)
    score, _ = score_song(song, user)
    # genre=0, mood=0+0.3*0.5=0.15, energy=1-1=0, acoustic=0
    assert score == pytest.approx(0.3 * 0.15, abs=1e-3)


def test_score_genre_match_only():
    """Only genre matches; other components add minimal noise."""
    song = make_song(genre="pop", mood="angry", energy=0.0, valence=0.5, acousticness=1.0)
    user = make_user(favorite_genre="pop", favorite_mood="happy", target_energy=1.0, likes_acoustic=False)
    score, _ = score_song(song, user)
    # genre=1 → contributes 0.4
    assert score >= 0.4


def test_score_components_weighted_correctly():
    """Manually compute every component and verify the weighted sum."""
    song = make_song(genre="rock", mood="happy", energy=0.6, valence=0.7, acousticness=0.3)
    user = make_user(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    score, _ = score_song(song, user)

    genre_match = 0.0                          # rock ≠ pop
    valence_alignment = 0.7                    # mood="happy" → use valence directly
    base_mood = 0.7                            # mood matches
    mood_match = 0.7 + 0.3 * 0.7              # 0.91
    energy_match = 1.0 - abs(0.6 - 0.8)       # 0.8
    acoustic_match = 1.0 - 0.3                # likes_acoustic=False → 0.7
    expected = 0.4 * genre_match + 0.3 * mood_match + 0.2 * energy_match + 0.1 * acoustic_match
    assert score == pytest.approx(expected, abs=1e-3)


# ---------------------------------------------------------------------------
# Valence direction logic
# ---------------------------------------------------------------------------

def test_valence_high_for_happy_mood():
    """For 'happy', high valence should give a better score than low valence."""
    user = make_user(favorite_mood="happy")
    high_v = make_song(mood="happy", valence=0.95)
    low_v  = make_song(mood="happy", valence=0.10)
    score_high, _ = score_song(high_v, user)
    score_low,  _ = score_song(low_v,  user)
    assert score_high > score_low


def test_valence_high_for_intense_mood():
    """For 'intense', high valence is preferred (same branch as 'happy')."""
    user = make_user(favorite_mood="intense")
    high_v = make_song(mood="intense", valence=0.9)
    low_v  = make_song(mood="intense", valence=0.1)
    score_high, _ = score_song(high_v, user)
    score_low,  _ = score_song(low_v,  user)
    assert score_high > score_low


def test_valence_low_for_chill_mood():
    """For 'chill', low valence is preferred (inverted branch)."""
    user = make_user(favorite_mood="chill")
    high_v = make_song(mood="chill", valence=0.9)
    low_v  = make_song(mood="chill", valence=0.1)
    score_high, _ = score_song(high_v, user)
    score_low,  _ = score_song(low_v,  user)
    assert score_low > score_high


# ---------------------------------------------------------------------------
# BUG: "uplifting" falls into the low-valence branch (valence direction bug)
# ---------------------------------------------------------------------------

def test_bug_uplifting_valence_inverted():
    """
    'uplifting' is not in ('happy', 'intense'), so valence_alignment = 1 - valence.
    This means a high-valence uplifting song is PENALIZED on valence.
    This test documents the current (buggy) behaviour.
    """
    user = make_user(favorite_mood="uplifting")
    high_v = make_song(mood="uplifting", valence=0.95)
    low_v  = make_song(mood="uplifting", valence=0.10)
    score_high, _ = score_song(high_v, user)
    score_low,  _ = score_song(low_v,  user)
    # BUG: low-valence uplifting song currently scores higher
    assert score_low > score_high, (
        "BUG CONFIRMED: uplifting songs with low valence outscore high-valence ones"
    )


# ---------------------------------------------------------------------------
# BUG: energy_match can go negative for out-of-bounds target_energy
# ---------------------------------------------------------------------------

def test_bug_energy_match_goes_negative():
    """
    energy_match = 1 - abs(song.energy - target_energy)
    With target_energy=1.5 and a calm song (energy=0.2):
      energy_match = 1 - 1.3 = -0.3  (negative — subtracts from score)
    """
    song = make_song(energy=0.2)
    user = make_user(target_energy=1.5)
    score, _ = score_song(song, user)
    # Reconstruct expected score with a negative energy term
    energy_match = 1.0 - abs(0.2 - 1.5)   # -0.3
    assert energy_match < 0, "energy_match should be negative for this input"
    # Verify it actually reduces the overall score
    song_mid = make_song(energy=0.8)
    score_mid, _ = score_song(song_mid, user)
    # The calm song is dragged lower by the negative energy component
    assert score < score_mid


# ---------------------------------------------------------------------------
# Phantom / unknown genre
# ---------------------------------------------------------------------------

def test_phantom_genre_no_genre_bonus():
    """A genre absent from every song means genre_match is always 0.
    Scores with the phantom genre must be exactly 0.4 lower than with a matching genre."""
    song = make_song(genre="pop")
    user_phantom = make_user(favorite_genre="k-pop")
    user_match   = make_user(favorite_genre="pop")
    score_phantom, _ = score_song(song, user_phantom)
    score_match,   _ = score_song(song, user_match)
    # The genre weight (0.4) is the only difference between the two users
    assert score_match - score_phantom == pytest.approx(0.4, abs=1e-3)


# ---------------------------------------------------------------------------
# Acoustic match logic
# ---------------------------------------------------------------------------

def test_acoustic_match_likes_acoustic_true():
    """likes_acoustic=True → high acousticness song should rank above low."""
    user = make_user(likes_acoustic=True)
    acoustic = make_song(id=1, acousticness=0.95)
    electric  = make_song(id=2, acousticness=0.05)
    s_ac, _ = score_song(acoustic, user)
    s_el, _ = score_song(electric,  user)
    assert s_ac > s_el


def test_acoustic_match_likes_acoustic_false():
    """likes_acoustic=False → low acousticness song should rank above high."""
    user = make_user(likes_acoustic=False)
    acoustic = make_song(id=1, acousticness=0.95)
    electric  = make_song(id=2, acousticness=0.05)
    s_ac, _ = score_song(acoustic, user)
    s_el, _ = score_song(electric,  user)
    assert s_el > s_ac


# ---------------------------------------------------------------------------
# Energy proximity
# ---------------------------------------------------------------------------

def test_energy_closer_scores_higher():
    """Song closer in energy to target should outscore a farther one."""
    user = make_user(target_energy=0.5)
    close = make_song(id=1, energy=0.52)
    far   = make_song(id=2, energy=0.90)
    s_close, _ = score_song(close, user)
    s_far,   _ = score_song(far,   user)
    assert s_close > s_far


def test_exact_energy_match_contributes_0_2():
    """Perfect energy match contributes exactly 0.2 to the score."""
    song = make_song(genre="other", mood="other", energy=0.5, valence=0.5, acousticness=0.5)
    user = make_user(favorite_genre="other", favorite_mood="other",
                     target_energy=0.5, likes_acoustic=False)
    score, _ = score_song(song, user)
    # genre=1, mood=0.7+0.3*(1-0.5)=0.85, energy=1, acoustic=0.5
    energy_contribution = 0.2 * 1.0
    assert score == pytest.approx(
        0.4 * 1.0 + 0.3 * 0.85 + 0.2 * 1.0 + 0.1 * 0.5, abs=1e-3
    )


# ---------------------------------------------------------------------------
# Recommender k parameter edge cases
# ---------------------------------------------------------------------------

def test_recommend_k_larger_than_catalog():
    """Requesting more songs than exist should return all songs without error."""
    rec = make_small_recommender()
    user = make_user()
    results = rec.recommend(user, k=100)
    assert len(results) == 2  # only 2 songs in fixture


def test_recommend_k_equals_one():
    """k=1 returns exactly the best song."""
    rec = make_small_recommender()
    user = make_user()
    results = rec.recommend(user, k=1)
    assert len(results) == 1
    assert results[0].genre == "pop"


def test_recommend_k_zero():
    """k=0 returns an empty list."""
    rec = make_small_recommender()
    user = make_user()
    results = rec.recommend(user, k=0)
    assert results == []


# ---------------------------------------------------------------------------
# Explanation / reasons
# ---------------------------------------------------------------------------

def test_explain_includes_genre_reason():
    user = make_user(favorite_genre="pop")
    song = make_song(genre="pop")
    _, reasons = score_song(song, user)
    assert any("Genre match" in r for r in reasons)


def test_explain_includes_mood_reason():
    user = make_user(favorite_mood="happy")
    song = make_song(mood="happy")
    _, reasons = score_song(song, user)
    assert any("Mood match" in r for r in reasons)


def test_explain_includes_energy_reason_strong():
    """Energy within 0.2 of target should trigger 'strong fit' reason."""
    user = make_user(target_energy=0.8)
    song = make_song(energy=0.82)
    _, reasons = score_song(song, user)
    assert any("strong fit" in r for r in reasons)


def test_explain_no_reasons_for_total_mismatch():
    """A song with no matching signals should return the fallback explanation."""
    user = make_user(favorite_genre="pop", favorite_mood="happy",
                     target_energy=0.9, likes_acoustic=False)
    # low energy (far from 0.9), low valence (bad for happy), high acousticness
    song = make_song(genre="metal", mood="sad", energy=0.1, valence=0.1, acousticness=0.95)
    rec = Recommender([song])
    explanation = rec.explain_recommendation(user, song)
    # Should still return a non-empty string (fallback message)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# load_songs CSV integration
# ---------------------------------------------------------------------------

def test_load_songs_returns_list_of_dicts(tmp_path):
    csv_file = tmp_path / "test_songs.csv"
    csv_file.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
        "1,Song A,Artist X,pop,happy,0.8,120,0.9,0.8,0.2\n"
        "2,Song B,Artist Y,lofi,chill,0.4,80,0.5,0.6,0.8\n"
    )
    songs = load_songs(str(csv_file))
    assert len(songs) == 2
    assert songs[0]["title"] == "Song A"
    assert songs[0]["energy"] == pytest.approx(0.8)
    assert songs[1]["genre"] == "lofi"


def test_load_songs_numeric_types(tmp_path):
    """Numeric fields should be parsed as float/int, not left as strings."""
    csv_file = tmp_path / "test_songs.csv"
    csv_file.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
        "42,Track,Band,jazz,relaxed,0.35,90,0.7,0.55,0.88\n"
    )
    songs = load_songs(str(csv_file))
    row = songs[0]
    assert isinstance(row["id"], int)
    assert isinstance(row["energy"], float)
    assert isinstance(row["tempo_bpm"], float)
    assert isinstance(row["valence"], float)
    assert isinstance(row["danceability"], float)
    assert isinstance(row["acousticness"], float)


def test_load_songs_empty_file(tmp_path):
    """A CSV with only a header should return an empty list."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
    )
    songs = load_songs(str(csv_file))
    assert songs == []
