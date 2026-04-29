
# 🎵 Music Recommender Simulation

## 1. Title and Summary:
**MindReader**

## Original goals and capabilities:
The system takes into user preferences (favorite genre, favorite mood, target energy, and if a user likes accoustic) and list of songs with its caracteristics and calculates a score for each song based on similarities between user's preferences and songs' characteristics. The system returns first k songs with highest score.

Originally, system design was very simple and not reliable. For example, if user ask for genre which not present in the song data, the system scores all song's genre match as 0 instead of giving some points for similar genre. Onother words, the system perform exact matching instead of similarities search which could be improved by implementing RAG.

## 2. Architecture Overview:
Old flow:
  UserProfile (structured) → score ALL 68 songs → rank → top-5

* Requires users to use exact vacabulary like "indie pop", focused", "melancholic", etc. whike some users would be more comfortable promting "I want calm acoustic music for studying late at night".


New flow:
Natural language input  →  Groq (profile parser)  →  UserProfile
                                                           ↓
                                                    score_song() [existing]
                                                           ↓
                                                      top-k results

* Uses Groq api to parse natural user input into a structured UserProfile and to prompt user for an input in Discover mode.



<img width="822" height="712" alt="MindReader System diagram" src="https://github.com/user-attachments/assets/f2f1d30d-edaf-4f23-87f4-ea5c1733eaad" />


## 3. Setup Instructions:

### 1. Clone the repository and create a virtual environment:
git clone <your-repo-url>
cd applied-ai-system-project
python -m venv env
source env/bin/activate        # Mac/Linux
env\Scripts\activate           # Windows

### 2. Install dependencies:
pip install -r requirements.txt

### 3. Add your API key — create a .env file in the project root:
GROQ_API_KEY=your-groq-key-here
Get a free key at console.groq.com.

### 4. Fetch the real song catalog (439 songs across 15 genres):
python scripts/fetch_songs.py
This downloads from two public datasets — no API key needed.

### 5. Run the Streamlit app:
streamlit run app.py

Or run the CLI instead:
python src/main.py              # interactive natural language mode
python src/main.py --demo       # run 7 hardcoded test profiles

### 6. Run the test suite:
pytest

### 7. Run the evaluation loop:
python src/eval.py

## 4. Sample Interactions:

Quick search example with "I’m having a very long drive and need to stay focus and energized." prompt.

https://github.com/user-attachments/assets/e2f71984-d567-45cc-bc73-0057ec9da568

Discover mode. Asked for something sad.

https://github.com/user-attachments/assets/f562dd7b-b526-4a02-ab26-a143b7b5376c

Discover mode. Asked for something happy.

https://github.com/user-attachments/assets/0bc66db7-0ece-4955-87b2-521418d72a17

### 5. Data

439 songs across 15 genres fetched from two public Spotify datasets — TidyTuesday (pop, hip-hop, rock, latin, R&B, EDM) and HuggingFace maharshipandya/spotify-tracks-dataset (jazz, classical, metal, blues, country, ambient, indie pop, synthwave, lofi). No songs were added by hand. Mood is inferred from audio features (energy + valence), not from a label in the source data. The catalog skews toward `chill` and `energetic` — those two moods cover about 65% of songs.

## 6. Design Decisions:
I wanted the app to be easy to use for everyone and reliable with real data recommendations. First, I added the Groq API to interpret user requests, so users can describe what they want in plain English without knowing the app's specifics. Groq converts the request into a structured UserProfile that the scoring system understands. This approach has two modes — Quick Search and Discover — offering a lot of flexibility. The underlying scoring still uses exact genre matching, but because the LLM maps user input to a valid genre first, vocabulary mismatches are no longer a problem.

I wanted the recommendations to make sense in practice, so I replaced the synthetic songs with real data — 439 songs across 15 genres fetched from two public Spotify datasets.

#### Scoring formula:
```
score = (0.4 × genre_match)
      + (0.3 × mood_match)
      + (0.2 × energy_match)
      + (0.1 × acoustic_match)
```

- `genre_match`: 1 if song.genre == user.genre, else 0
- `mood_match`: 0.7 if mood matches + 0.3 × valence_alignment
- `energy_match`: 1 - abs(song.energy - user.target_energy)
- `acoustic_match`: song.acousticness if user.likes_acoustic, else 1.0 - song.acousticness

`valence_alignment` depends on the mood direction:
- `("happy", "intense", "uplifting")` → high valence is a good fit
- `("chill", "moody", "relaxed", "focused")` → low valence is a better fit

Songs are then sorted by score descending and the top k are returned.

Finally, I tested the app using pytest (unit tests for the scoring logic) and an eval loop (rule-based metrics across 7 profiles).

The main trade-off is that if the prompt is generic, the system will always return the same results, since there is no personalization beyond the current session.

## 7. Testing Summary:

### Unit tests — `tests/test_recommender.py`
26 tests, all passing. Coverage includes the scoring formula, each weighted component, valence direction logic for every mood group, acoustic preference flipping, energy proximity ranking, edge cases (k=0, k larger than catalog, empty CSV), and the explanation output.

Two bugs were caught and fixed during development:

| Bug | What happened | Fix |
|-----|--------------|-----|
| Uplifting valence inverted | `"uplifting"` fell into the low-valence branch, so high-valence uplifting songs were penalized | Added `"uplifting"` to the `("happy", "intense")` high-valence group |
| Negative energy score | `target_energy=1.5` produced `energy_match = 1 - 1.3 = -0.3`, dragging calm songs below zero | Clamped `target_energy` to `[0.0, 1.0]` before scoring |

### Evaluation loop — `src/eval.py`
Automated metrics across 7 profiles (4 normal + 3 adversarial). After migrating to the real 439-song catalog, mean score improved from **0.507 → 0.803**.

| Profile | Genre% | Mood% | Energy | Score |
|---------|--------|-------|--------|-------|
| Indie Pop Fan | 100% | 100% | 0.88 | 0.95 |
| Lofi Studier | 100% | 0% | 0.94 | 0.74 |
| Gym Grinder | 100% | 80% | 0.96 | 0.90 |
| Brunch Vibes | 100% | 80% | 0.89 | 0.87 |
| [ADV] Phantom Genre (k-pop) | 0% | 100% | 0.96 | 0.57 |
| [ADV] Out-of-Bounds Energy | 100% | 100% | 0.16 | 0.79 |
| [ADV] Uplifting Mood | 100% | 20% | 0.97 | 0.80 |

### What worked
- Genre and energy matching is strong across all normal profiles — 100% genre hit rate and energy fit above 0.88 for every non-adversarial case
- The LLM profile parser correctly handles vocabulary mismatches: a user asking for "k-pop" gets mapped to pop with matching energy and mood, scoring 0.57 despite zero genre matches
- Fixing the two scoring bugs lifted the uplifting profile from ~0.65 to 0.80 and eliminated negative scores entirely

### What didn't work
- **Lofi Studier mood hit rate is 0%** — real dataset lofi tracks were labelled `chill` during mood inference (derived from audio features), but the profile requests `focused`. The songs are acoustically correct; the mood label mismatch is a limitation of inferring mood purely from energy and valence
- **Out-of-bounds energy fit is 0.16** — `target_energy=1.5` is clamped to `1.0`, but classical songs have energy ~0.22–0.35, so the gap is inherent and expected
- **Mood diversity is uneven** — the real dataset skews heavily toward `chill` and `energetic` (65% of songs), leaving moods like `focused`, `nostalgic`, and `romantic` underrepresented

## Experiments You Tried

- **Weight tuning**: started with equal weights across all four features, then shifted genre to 0.4 and mood to 0.3 because early tests showed the system recommending wrong-genre songs that matched energy well. Genre turned out to be the strongest signal.
- **Valence as a separate feature vs. inside mood**: originally considered valence as its own scoring component, but folded it into `mood_match` as a 30% sub-weight — this kept the formula simple while still capturing emotional direction (whether a mood calls for high or low valence).
- **Synthetic vs. real data**: the original 68 hand-crafted songs produced a mean eval score of 0.507. After replacing them with 439 real Spotify tracks, the mean score jumped to 0.803 — the larger and more diverse catalog gave the scorer more to work with.
- **LLM for profile parsing**: before adding Groq, users had to type exact vocabulary like "indie pop" or "melancholic". After adding the parser, natural queries like "something for a late night drive" work correctly. The phantom genre test (k-pop → mapped to pop) confirmed this handles unknown inputs gracefully.
- **Adversarial profiles**: running out-of-bounds energy (target=1.5) and a phantom genre through the eval loop exposed both bugs — the negative energy score and the inverted uplifting valence — before they could affect real users.

---

## 8. Strengths

- Genre and energy matching is consistently strong — 100% genre hit rate and energy fit above 0.88 for all normal profiles
- The LLM parser bridges the vocabulary gap: users can describe what they want naturally and the system maps it to a valid profile
- Two modes (Quick Search and Discover) cover different use cases — fast lookup vs. guided conversation
- The scoring formula is transparent and easy to debug — every component can be inspected and the weights can be adjusted without retraining
- Both bugs were caught by automated tests before they could affect real users

---

## 9. Limitations and Risks

- **Small catalog**: 439 songs is enough to demonstrate the system, but a real recommender needs tens of thousands. Some moods (focused, nostalgic, romantic) have very few matching tracks, so the top-k results can feel repetitive.
- **Mood inference is a simplification**: mood is derived from energy and valence thresholds, not from actual listening data or lyrics. This is why the Lofi Studier profile gets 0% mood hits — the tracks are acoustically correct but labeled `chill` instead of `focused`.
- **Genre matching is binary**: a song either matches the genre or scores zero for that component. A jazz song gets no credit when the user asks for blues, even though they are closely related.
- **No cross-session personalization**: every session starts fresh. The system has no memory of what a user liked or skipped before, so it cannot improve recommendations over time.
- **Generic prompts return identical results**: two users who type "something relaxing" will get the exact same list, because the LLM maps their inputs to the same profile. There is no diversity or exploration built in.
- **Potential bias toward dominant moods**: `chill` and `energetic` make up 65% of the catalog, so users asking for rarer moods like `nostalgic` or `romantic` are likely to get suggestions that are close but not exact matches.


## 10. Reflection:
Ai is a great tool but I should be relying too much on it. It makes mistakes and not always knows what's best/better. Using AI can speed up the development a lot, but in the process every step should be oversees and checked.

---

## 8. Future Work

- Add user history so the system can learn from past sessions and avoid repeating the same results
- Replace binary genre matching with embedding similarity so related genres (e.g. blues → jazz) still score partial credit
- Add diversity to the top-k results — right now the system always picks the closest match, which can produce a repetitive list
- Improve mood labeling by using a richer feature set (tempo, danceability, speechiness) or a pre-trained classifier instead of the energy/valence quadrant
- Expand the catalog to reduce the dominance of `chill` and `energetic` tracks
