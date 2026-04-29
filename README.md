
https://github.com/user-attachments/assets/6550729f-ee02-4464-8012-92d61ead9ca5
# 🎵 Music Recommender Simulation — MindReader

## 1. Title and Summary

**MindReader** is a hybrid music recommendation system that combines rule-based scoring with LLM-powered natural language understanding.

It takes user preferences (favorite genre, mood, target energy, acoustic preference) and a catalog of songs, then computes a relevance score for each song and returns the top-k results.

Originally, the system required strict keyword-based inputs and suffered from poor generalization. With the introduction of an LLM-based parser (Groq API), users can now describe their preferences naturally (e.g. *"calm acoustic music for studying late at night"*).

---

## 2. Architecture Overview

### Old flow

```
UserProfile (strict keywords)
        ↓
Score ALL 68 songs
        ↓
Rank
        ↓
Top-5 results
```

### Limitations of the old system

* Required exact vocabulary (“indie pop”, “melancholic”, etc.)
* No semantic understanding of user intent
* Failed on natural language queries

---

### New flow

```
Natural Language Input
        ↓
Groq LLM (profile parser)
        ↓
Structured UserProfile
        ↓
Scoring engine (existing)
        ↓
Top-k recommendations
```

### Improvements

* Accepts natural language input
* Handles vague or unseen requests
* Maps user intent to valid structured profiles

---

## 3. Setup Instructions

### 1. Clone repository and create environment

```bash
git clone <your-repo-url>
cd applied-ai-system-project
python -m venv env
source env/bin/activate        # Mac/Linux
env\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add API key

Create `.env`:

```
GROQ_API_KEY=your-groq-key-here
```

Get key: [https://console.groq.com](https://console.groq.com)

### 4. Fetch dataset (439 songs)

```bash
python scripts/fetch_songs.py
```

### 5. Run app

```bash
streamlit run app.py
```

CLI mode:

```bash
python src/main.py
python src/main.py --demo
```

### 6. Tests

```bash
pytest
```

### 7. Evaluation

```bash
python src/eval.py
```

---

## 4. Sample Interactions

Quick Search:

> “I’m having a long drive and need something focused and energetic.”

https://github.com/user-attachments/assets/3016ccb8-30c3-4c36-b6d1-f47b41cfaa5b


Discover mode (sad music):

https://github.com/user-attachments/assets/82c968a6-bcbc-46bb-b63f-034d951c51f3


Discover mode (happy music):

https://github.com/user-attachments/assets/0ec8ef96-9e33-4aaa-a104-97ea384e28de




---

## 5. Data

* 439 songs
* 15 genres
* Sources:

  * TidyTuesday Spotify dataset
  * HuggingFace Spotify tracks dataset

Genres include: pop, hip-hop, rock, jazz, classical, EDM, lofi, indie pop, ambient, etc.

### Mood inference

Mood is not manually labeled. It is derived from:

* energy
* valence

Dataset distribution:

* ~65% chill or energetic tracks

---

## 6. Design Decisions

The goal was to build a system that is both **usable for non-technical users** and **interpretable for debugging**.

### Key idea: LLM as intent parser

Instead of forcing users to match strict keywords, Groq converts natural language into a structured `UserProfile`.

This enables:

* Quick Search mode (direct intent → results)
* Discover mode (interactive exploration)

---

### Scoring formula

```
score = (0.4 × genre_match)
      + (0.3 × mood_match)
      + (0.2 × energy_match)
      + (0.1 × acoustic_match)
```

#### Components

* `genre_match`: exact match (1 or 0)
* `mood_match`: categorical match + valence alignment
* `energy_match`: inverse distance from target energy
* `acoustic_match`: preference-based similarity

#### Valence logic

* High valence: happy, intense, uplifting
* Low valence: chill, moody, relaxed, focused

---

## 7. Testing Summary

### Unit tests (`tests/test_recommender.py`)

* 26 tests, all passing
* Covers scoring logic, edge cases, and explanations

#### Bugs found & fixed

| Issue                        | Fix                           |
| ---------------------------- | ----------------------------- |
| Uplifting mood misclassified | Corrected valence grouping    |
| Negative energy scores       | Clamped energy input to [0,1] |

---

### Evaluation loop (`src/eval.py`)

Mean score improvement:

```
0.507 → 0.803
```

| Profile              | Genre | Mood | Energy | Score |
| -------------------- | ----- | ---- | ------ | ----- |
| Indie Pop Fan        | 100%  | 100% | 0.88   | 0.95  |
| Lofi Studier         | 100%  | 0%   | 0.94   | 0.74  |
| Gym Grinder          | 100%  | 80%  | 0.96   | 0.90  |
| Brunch Vibes         | 100%  | 80%  | 0.89   | 0.87  |
| Phantom Genre        | 0%    | 100% | 0.96   | 0.57  |
| Out-of-Bounds Energy | 100%  | 100% | 0.16   | 0.79  |
| Uplifting Mood       | 100%  | 20%  | 0.97   | 0.80  |

---

### What worked

* Strong genre + energy alignment
* LLM handles vocabulary mismatches
* Stable scoring after fixes

### What didn’t work

* Mood mismatch (lofi labeled as chill, not focused)
* Dataset skew toward chill/energetic songs
* Binary genre matching limits nuance

---

## 8. Experiments

* **LLM parsing**: solved rigid keyword problem
* **Real dataset swap**: improved mean score from 0.507 → 0.803
* **Adversarial testing**: exposed energy and valence bugs
* **Valence design choice**: embedded into mood instead of separate feature

---

## 9. Strengths

* Transparent scoring system
* Strong performance on normal user profiles
* Natural language input support
* Lightweight (no training required)

---

## 10. Limitations

* Small dataset (439 songs)
* No personalization across sessions
* Binary genre matching
* Mood inference is heuristic (not learned)
* Repetitive results for generic prompts

---

## 11. Future Work

* Add user history / personalization
* Replace genre matching with embeddings
* Improve diversity in top-k results
* Train proper mood classifier
* Expand dataset (10k+ songs)

---

## 12. Reflection

AI is useful for speeding up development, but it should not replace careful design and validation. Every component still needs to be reviewed and tested to ensure correct behavior.

---

## 13. Conclusion

MindReader demonstrates how a simple rule-based recommender can be significantly improved by combining:

* real datasets
* transparent scoring functions
* LLM-based intent parsing

The result is a system that is both practical and interpretable, without requiring heavy ML training pipelines.
