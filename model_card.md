# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**MindReader**

---

## 2. Intended Use  

MindReader recommends a list of songs from a list of all available songs to a user based on user preferences and reasons its suggestions.

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

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
There are originally 10 songs in the songs.csv, but later 8 more were added. The dataset contains a wide variaty of genre and moods such as pop, lofi, rock, jazz, country, R&B, metal, and so on.

- Did you add or remove data  
    Yes, I added 8 more songs.
- Are there parts of musical taste missing in the dataset
    Not sure.

---

## 5. Strengths  

The MindReader seams to work well when user gives them stright forward preferences instead of mixed in (for example when genre is metal and mood is happy).

---

## 6. Limitations and Bias 

The MindReader struggels a bit with incorrect preferences like unexisting genre or mixed preference like (genre: metal and mood: happy), but even with that give good results which means that this  effects only system confident but not results.

---

## 7. Evaluation  

I checked the system with variety of user profiles and analized recommender's results if thay matching user preferences. I also added adversarial profiles and run recommender for these as well. The System worked correctly. Finally, I added tests cases and run pytests.

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
