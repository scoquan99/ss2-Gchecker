import re
from collections import Counter
import textstat
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import sent_tokenize

def analyze_text_stats(text):
    if not text.strip():
        return {}
    
    # Word & Char counts
    char_count = len(text)
    words = [w for w in re.split(r'\W+', text.lower()) if w]
    word_count = len(words)
    
    # Reading/Speaking time
    # Average adult reading speed: 238 wpm. Speaking: 130 wpm
    reading_time_mins = round(word_count / 238, 1)
    speaking_time_mins = round(word_count / 130, 1)
    
    # Reading Level
    reading_ease = textstat.flesch_reading_ease(text)
    
    # Keywords
    try:
        stop_words = set(stopwords.words('english'))
    except:
        stop_words = set()
    
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
    word_freq = Counter(filtered_words)
    top_keywords = [{"word": k, "count": v} for k, v in word_freq.most_common(5)]
    
    # Sentence highlights
    try:
        sentences = sent_tokenize(text)
    except:
        sentences = [text] # fallback
        
    sentence_highlights = []
    for s in sentences:
        s_words = len([w for w in re.split(r'\W+', s) if w])
        category = "short"
        if s_words >= 20:
            category = "long"
        elif s_words >= 10:
            category = "medium"
            
        sentence_highlights.append({
            "text": s,
            "word_count": s_words,
            "category": category
        })
        
    return {
        "word_count": word_count,
        "char_count": char_count,
        "reading_time_mins": reading_time_mins,
        "speaking_time_mins": speaking_time_mins,
        "reading_ease": reading_ease,
        "top_keywords": top_keywords,
        "sentence_highlights": sentence_highlights
    }

def get_synonyms_antonyms(word):
    synonyms = set()
    antonyms = set()
    
    try:
        for syn in wordnet.synsets(word):
            for l in syn.lemmas():
                if l.name() != word:
                    synonyms.add(l.name().replace('_', ' '))
                if l.antonyms():
                    for antonym in l.antonyms():
                        antonyms.add(antonym.name().replace('_', ' '))
    except Exception as e:
        print(f"Error getting synonyms for '{word}': {e}")
        
    return {
        "word": word,
        "synonyms": list(synonyms)[:10] if synonyms else [],
        "antonyms": list(antonyms)[:10] if antonyms else []
    }
