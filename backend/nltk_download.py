import nltk
try:
    nltk.download('wordnet')
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')
    print("NLTK data downloaded successfully")
except Exception as e:
    print("Error downloading NLTK data:", e)
