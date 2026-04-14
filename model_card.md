# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**MindReader**

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

**The MindReader** will take user preference such as favorite genre, favorite mood, target energy, and if they like acoustics, and then it will compare it with songs characteristics in particular genre, mood, energy, accoustic, and valence will be taken into account.

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

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
    There are originally 10 songs in the songs.csv, but later 8 more were added.
- What genres or moods are represented 
    The dataset contains a wide variaty of genre and moods such as pop, lofi, rock, jazz, country, R&B, metal, and so on.
- Did you add or remove data  
    Yes, I added 8 more songs.
- Are there parts of musical taste missing in the dataset
    Not sure.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
