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
from profile_parser import parse_profile, chat_to_profile

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="MindReader", page_icon="🎵", layout="centered")

# ── Catalog ───────────────────────────────────────────────────────────────────
@st.cache_data
def get_songs():
    return load_songs("data/songs.csv")

songs = get_songs()

# ── Shared helpers ────────────────────────────────────────────────────────────
def show_profile(prefs: dict) -> None:
    st.subheader("What I understood")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Genre",   prefs["favorite_genre"])
    c2.metric("Mood",    prefs["favorite_mood"])
    c3.metric("Energy",  f"{prefs['target_energy']:.2f}")
    c4.metric("Acoustic", "Yes" if prefs["likes_acoustic"] else "No")


def show_recommendations(recs: list) -> None:
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


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎵 MindReader")
st.caption("Find the right music for your moment.")

tab_quick, tab_discover = st.tabs(["🔍 Quick Search", "✨ Discover"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Quick Search (existing behaviour)
# ══════════════════════════════════════════════════════════════════════════════
with tab_quick:
    st.markdown("**Tell me what you want** and I'll find it instantly.")

    query = st.text_input(
        label="What kind of music do you want?",
        placeholder="e.g. something slow and melancholic for a rainy evening…",
        key="quick_query",
    )
    k = st.slider("Number of recommendations", min_value=1, max_value=10,
                  value=5, key="quick_k")
    submitted = st.button("Find Music", type="primary",
                          use_container_width=True, key="quick_submit")

    if submitted:
        if not query.strip():
            st.warning("Please describe what you're in the mood for.")
        else:
            with st.spinner("Thinking…"):
                try:
                    _, prefs = parse_profile(query)
                    recs = recommend_songs(prefs, songs, k=k)
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                    st.stop()

            show_profile(prefs)
            st.divider()
            show_recommendations(recs)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Discover (conversational)
# ══════════════════════════════════════════════════════════════════════════════
FIRST_QUESTION = "What are you up to right now?"

def init_discover():
    """Set up fresh discover session state."""
    st.session_state.d_messages     = [{"role": "assistant", "content": FIRST_QUESTION}]
    st.session_state.d_api_messages = []   # only user + assistant turns for the API
    st.session_state.d_profile      = None
    st.session_state.d_recs         = None
    st.session_state.d_k            = 5

if "d_messages" not in st.session_state:
    init_discover()

with tab_discover:
    st.markdown("**Not sure what you want?** Answer a couple of questions and I'll figure it out.")

    k_discover = st.slider("Number of recommendations", min_value=1, max_value=10,
                            value=st.session_state.d_k, key="discover_k")
    st.session_state.d_k = k_discover

    # ── Recommendations sit above the chat once the profile is ready ──────────
    if st.session_state.d_profile:
        show_profile(st.session_state.d_profile)
        st.divider()
        if st.session_state.d_recs:
            show_recommendations(st.session_state.d_recs)
        st.divider()
        if st.button("Start over", key="discover_reset"):
            init_discover()
            st.rerun()

    # ── Chat history in a scrollable container ────────────────────────────────
    msg_count = len(st.session_state.d_messages)
    chat_height = min(500, max(150, msg_count * 120))
    chat_box = st.container(height=chat_height, border=False)
    with chat_box:
        for msg in st.session_state.d_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# ── Chat input — outside tab so Streamlit renders it sticky at the bottom ────
if not st.session_state.get("d_profile"):
    if user_input := st.chat_input("Type your answer…"):
        st.session_state.d_messages.append({"role": "user", "content": user_input})
        st.session_state.d_api_messages.append({"role": "user", "content": user_input})

        with chat_box:
            with st.chat_message("user"):
                st.markdown(user_input)

        with chat_box:
            with st.chat_message("assistant"):
                with st.spinner(""):
                    try:
                        result = chat_to_profile(st.session_state.d_api_messages)
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")
                        st.stop()

                if result.get("ready"):
                    summary = result.get("summary", "Here's what I found for you.")
                    st.markdown(summary)
                    st.session_state.d_messages.append(
                        {"role": "assistant", "content": summary}
                    )
                    st.session_state.d_profile = {
                        "favorite_genre": result["favorite_genre"],
                        "favorite_mood":  result["favorite_mood"],
                        "target_energy":  result["target_energy"],
                        "likes_acoustic": result["likes_acoustic"],
                    }
                    st.session_state.d_recs = recommend_songs(
                        st.session_state.d_profile, songs, k=st.session_state.d_k
                    )
                    st.rerun()
                else:
                    question = result.get("message", "Tell me more.")
                    st.markdown(question)
                    st.session_state.d_messages.append(
                        {"role": "assistant", "content": question}
                    )
                    st.session_state.d_api_messages.append(
                        {"role": "assistant", "content": question}
                    )
