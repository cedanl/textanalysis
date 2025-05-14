import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import polars as pl
from collections import Counter
import langdetect

def remove_stopwords(column_data):
    # Download required NLTK resources
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    
    # Get stopwords
    stopwords_en = set(stopwords.words('english'))
    stopwords_nl = set(stopwords.words('dutch'))
    
    # Convert input to list if it's a polars Series
    if isinstance(column_data, pl.Series):
        texts = column_data.drop_nulls().cast(pl.Utf8).to_list()
    else:
        texts = [str(item) for item in column_data if item is not None]
    
    # Clean each text
    cleaned_texts = []
    all_clean_words = []
    
    for text in texts:
        if not text.strip():  # Skip empty texts
            cleaned_texts.append('')
            continue
            
        # Try to detect language
        try:
            lang = langdetect.detect(text)
            # Use appropriate stopwords based on detected language
            if lang == 'nl':
                current_stopwords = stopwords_nl
            elif lang == 'en':
                current_stopwords = stopwords_en
            else:
                # Default to both if language is neither English nor Dutch
                current_stopwords = stopwords_en.union(stopwords_nl)
        except:
            # If language detection fails, use both stopword sets
            current_stopwords = stopwords_en.union(stopwords_nl)
        
        tokens = word_tokenize(text.lower())
        cleaned_tokens = [w for w in tokens if w.isalpha() and w not in current_stopwords]
        cleaned_texts.append(' '.join(cleaned_tokens))
        all_clean_words.extend(cleaned_tokens)
    
    # Generate word frequencies
    word_counts = Counter(all_clean_words)
    
    # Convert to Polars DataFrame
    frequencies_df = pl.DataFrame({
        "Word": list(word_counts.keys()),
        "Count": list(word_counts.values())
    }).sort("Count", descending=True)
    
    return pl.Series(cleaned_texts), frequencies_df