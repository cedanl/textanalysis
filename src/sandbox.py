import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
#import spacy

# Load Excel file
df = pd.read_excel("data/input/opleidingen_feedback.xlsx")

# Select the second column (index 1)
texts = df.iloc[:, 1].dropna().astype(str).tolist()

# NLTK
nltk.download('punkt_tab')  # For tokenization
nltk.download('stopwords')  # For stopword lists

stopwords_en = set(stopwords.words('english'))
stopwords_nl = set(stopwords.words('dutch'))

def clean_text_nltk(text):
    tokens = word_tokenize(text.lower())
    return [w for w in tokens if w.isalpha() and w not in stopwords_en and w not in stopwords_nl]

# Apply to all texts
cleaned_texts = [clean_text_nltk(text) for text in texts]
print(cleaned_texts)
