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

One improvement I would like to make is adding more user preference dimensions, such as tempo (BPM) and era (decade the song was released), to produce more personalized recommendations. I would also like to introduce a diversity penalty so the top results don't cluster around a single genre, giving users a broader range of suggestions. Another direction is building an explanation layer that tells the user *why* a song was recommended — for example, "ranked #1 because the genre and mood are a perfect match and the energy is very close to your target." Finally, expanding the song catalog with hundreds of real tracks and experimenting with collaborative filtering would help MindReader move from a classroom prototype toward a more realistic recommender system.

---

## 9. Personal Reflection  

Working on MindReader taught me that even a simple rule-based recommender can feel surprisingly smart when the feature weights are tuned thoughtfully. The most unexpected thing I discovered was how much the valence alignment matters — flipping the valence logic between "happy/intense" and "chill/moody" moods made a noticeable difference in result quality without changing anything else. I also gained a new appreciation for how much data diversity matters: when the song catalog was small, the model had no good answer for niche taste profiles, which showed me why real streaming services invest so heavily in catalog size. This project changed the way I think about apps like Spotify — what looks like magic is often a carefully weighted combination of a few well-chosen features, and the hard part is choosing the right features and getting the weights right.
