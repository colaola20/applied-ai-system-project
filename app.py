"""
Streamlit UI for MindReader.

Run with:
    env/bin/streamlit run app.py
"""

import sys
import os
sys.path.insert(0, "src")

from dotenv import load_dotenv
load_dotenv(".env")

import streamlit as st
from recommender import load_songs, recommend_songs
from profile_parser import parse_profile

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="MindReader", page_icon="🎵", layout="centered")

# ── Load catalog once ─────────────────────────────────────────────────────────
@st.cache_data
def get_songs():
    return load_songs("data/songs.csv")

songs = get_songs()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎵 MindReader")
st.caption("Tell me what you're in the mood for — I'll find the music.")

st.divider()

# ── Query input ───────────────────────────────────────────────────────────────
query = st.text_input(
    label="What kind of music do you want?",
    placeholder="e.g. something slow and melancholic for a rainy evening…",
)

k = st.slider("Number of recommendations", min_value=1, max_value=10, value=5)

submitted = st.button("Find Music", type="primary", use_container_width=True)

# ── Results ───────────────────────────────────────────────────────────────────
if submitted:
    if not query.strip():
        st.warning("Please describe what you're in the mood for.")
    else:
        with st.spinner("Thinking…"):
            try:
                profile, prefs = parse_profile(query)
                recs = recommend_songs(prefs, songs, k=k)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        # Inferred profile
        st.subheader("What I understood")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Genre", prefs["favorite_genre"])
        c2.metric("Mood", prefs["favorite_mood"])
        c3.metric("Energy", f"{prefs['target_energy']:.2f}")
        c4.metric("Acoustic", "Yes" if prefs["likes_acoustic"] else "No")

        st.divider()

        # Recommendations
        st.subheader(f"Top {len(recs)} Recommendations")

        for rank, (song, score, explanation) in enumerate(recs, 1):
            with st.container(border=True):
                col_title, col_score = st.columns([4, 1])
                col_title.markdown(f"**#{rank} — {song['title']}**  \n*{song['artist']}*")
                col_score.metric("Score", f"{score:.2f}")

                tag_cols = st.columns(4)
                tag_cols[0].caption(f"🎸 {song['genre']}")
                tag_cols[1].caption(f"💭 {song['mood']}")
                tag_cols[2].caption(f"⚡ energy {song['energy']}")
                tag_cols[3].caption(f"🎙️ acoustic {song['acousticness']}")

                reasons = [r.strip() for r in explanation.split(";") if r.strip()]
                if reasons:
                    with st.expander("Why this song?"):
                        for reason in reasons:
                            st.markdown(f"- {reason}")
