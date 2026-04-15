# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

MindReader recommends a list of songs to a user based on their preferences.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

- To keep things simple I'm gonna try to go with only 5 features (genre, mood, energy, acousticness, and valence) although I understand that for real-world system and in general for learning more complicated connection and patterns the system should have more features.
- UserProfile will store user's preferences for genre, mood, energy, and likes_acoustic which will be taken into account by system and compare with songs feature.
- Every feature will have a weight assigned to it (genre-0.4, mood-0.3, energy-0.2, and acousticness-0.1). Valence will be taken into account inside of the mood match calculations. 

#### Scoring Rule:
Scoring formula: 
  score = (0.4 × genre_match)
      + (0.3 × mood_match)
      + (0.2 × energy_match)
      + (0.1 × acoustic_match)

genre_match: 1 if song.genre == user.genre else 0
mood_match: 0.7 if mood matches + 0.3 x valence_alignment
energy_match: 1 - abc(song.energy - user.energy)
acoustic_match: song.acousticness if user.likes_acoustic else 1.0 - song.acousticness

valence_alignment will depend on user.mood:
  if user.favorite_mood in ("happy", "intense"):
    valence_alignment = song.valence          # high valence = good fit

  if user.favorite_mood in ("chill", "moody", "relaxed", "focused"):
      valence_alignment = 1.0 - song.valence   # low valence = better fit

#### Ranking Rule:
Then songs will be sorted by score desc and algorithm will return first k songs.
---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Data Flow Map
data/songs.csv
    │
    ▼
load_songs(csv_path)          ← src/recommender.py
    │  reads CSV rows into List[Dict]
    │  
    ▼
songs: List[Dict]
    │
    │                         user_prefs: Dict
    │                         (hardcoded in main.py)
    │                             │
    ▼                             ▼
recommend_songs(user_prefs, songs, k=5)    ← src/recommender.py
    │
    │  internally calls score_song() per song
    │  ranks songs by score, returns top-k
    ▼
List[Tuple[Dict, float, str]]
    │   (song_dict, score, explanation)
    ▼
main()  prints results         ← src/main.py

<img width="448" height="539" alt="Screenshot 2026-04-13 at 9 38 07 PM" src="https://github.com/user-attachments/assets/1bfb9172-2ccc-4ca3-892d-e10dbdefd732" />

<img width="830" height="163" alt="Screenshot 2026-04-14 at 10 04 47 PM" src="https://github.com/user-attachments/assets/9c7822a4-57fe-49cf-8ba8-7bcd4f1b780d" />




## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## Results
user_prefs = {
        "favorite_genre": "indie pop",   # preferred genre label (categorical match)
        "favorite_mood": "happy",        # preferred mood label (categorical match)
        "target_energy": 0.78,           # 0.0 (calm) → 1.0 (intense)
        "likes_acoustic": False,         # boolean flag for acoustic preference
    }
    
<img width="508" height="598" alt="Screenshot 2026-04-14 at 9 47 42 PM" src="https://github.com/user-attachments/assets/faf69ad7-8819-4fa5-b695-58b10241500b" />

MindReader correctly identifies the best fitted song for this user and scores it with .94. The second song is also a good choice since the genre is pop and the mood is happy for that song.

lofi_studier = {
        "favorite_genre": "lofi",
        "favorite_mood": "focused",
        "target_energy": 0.38,
        "likes_acoustic": True,
    }

<img width="508" height="598" alt="Screenshot 2026-04-14 at 9 47 51 PM" src="https://github.com/user-attachments/assets/db63f0d7-67ea-4e11-87ac-b43d3a2c73ae" />

MindReader gives a good recommendations for this user. First pick is **Focus Flow** which is very well matched with user's preferences.

gym_grinder = {
        "favorite_genre": "metal",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "likes_acoustic": False,
    }

<img width="508" height="598" alt="Screenshot 2026-04-14 at 9 47 57 PM" src="https://github.com/user-attachments/assets/c65b41a4-b536-4564-b880-5c39be2013b6" />

Different preference but the same excelent result.

brunch_vibes = {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.40,
        "likes_acoustic": True,
    }

<img width="508" height="598" alt="Screenshot 2026-04-14 at 9 48 05 PM" src="https://github.com/user-attachments/assets/0129bcbf-bd53-4422-bae9-c6aa459ec8a5" />

MindReader picked **Coffee Shop Stories** which satisfy user's genre, mood, and acoustic preferences. It also has strong energy fit.

 #### --- Adversarial profiles ---
phantom_genre = {
        "favorite_genre": "k-pop",
        "favorite_mood": "happy",
        "target_energy": 0.82,
        "likes_acoustic": False,
    }

<img width="508" height="598" alt="Screenshot 2026-04-14 at 9 49 20 PM" src="https://github.com/user-attachments/assets/17ee9f2e-8d87-4876-81b5-8d7c21977a2d" />

Since user's prefered genre isn't existing, MindReader has to relay on others parameters. It's still does a good matching job but the confident is much lower here.

out_of_bounds_energy = {
        "favorite_genre": "classical",
        "favorite_mood": "melancholic",
        "target_energy": 1.5,
        "likes_acoustic": True,
    }
    
<img width="508" height="521" alt="Screenshot 2026-04-14 at 9 49 26 PM" src="https://github.com/user-attachments/assets/bdf1d626-d7c4-4ab1-97f0-1a48d0179026" />

Here user targeting non-existing energy which creater negetive effect on scoring. Even with that MindReader is able to pick a good song. Although, there is only one good fit because of limited songs data.

valence_direction_bug = {
        "favorite_genre": "latin",
        "favorite_mood": "uplifting",
        "target_energy": 0.78,
        "likes_acoustic": False,
    }

Even with having the Recommender taking of point for valence since mood is uplifting and not happy or intense, MindReader is able to pick a good fit song with correct genre, mood and energy level. Although the confident of the recommender is lower than usual in this case.


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

