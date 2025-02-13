import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.metrics import f1_score
from pathlib import Path
import pandas as pd

# Load the local model
model_name = "distilbert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, device=0)  # Use GPU if available


# Initialize VADER
sentiment_vader = SentimentIntensityAnalyzer()

# Load dataset
def load_dataset(filepath):
    sentences = []
    emotions = []
    with open(filepath, "r") as f:
        for line in f:
            sentence, label = line.strip().split("\t")
            sentences.append(sentence)
            emotions.append("Positive" if label == "1" else "Negative")
    return sentences, emotions

def analyze_sentiment_transformer(sentence):
    max_length = 512
    try:
        result = sentiment_pipeline(sentence, truncation=True, max_length=max_length)[0]
        label = "Positive" if result["label"] == "POSITIVE" else "Negative"
        score = result["score"]
        return label, score
    except Exception as e:
        print(f"Error processing sentence: {e}")
        return "Unknown", 0.0


def analyze_long_text(text, max_length=512):
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    sentiments = [analyze_sentiment_transformer(chunk) for chunk in chunks]
    return max(set(sentiments), key=sentiments.count)



def analyze_sentiment_vader(sentence):
    scores = sentiment_vader.polarity_scores(sentence)
    label = "Positive" if scores["compound"] >= 0 else "Negative"
    return label, scores["compound"]

# Optimize weights
def optimize_weights(true_labels, model1_preds, model2_preds):
    weights = np.linspace(0, 1, 101)
    best_f1 = 0
    best_weight = 0
    
    for w in weights:
        combined_preds = []
        for m1, m2 in zip(model1_preds, model2_preds):
            combined_score = w * (m1 == "Positive") + (1-w) * (m2 == "Positive")
            combined_preds.append("Positive" if combined_score >= 0.5 else "Negative")
        
        f1 = f1_score(true_labels, combined_preds, pos_label="Positive")
        if f1 > best_f1:
            best_f1 = f1
            best_weight = w
    
    return best_weight


def main():
    filepath = ""
    df = pd.read_excel(filepath)
    sentences = df.iloc[:, 2].tolist()  # Use the third column (index 2)
    
    transformer_results = [analyze_sentiment_transformer(s) for s in sentences]
    vader_results = [analyze_sentiment_vader(s) for s in sentences]
    
    print("Sample predictions:")
    for i in range(min(5, len(sentences))):
        print(f"Sentence: {sentences[i]}")
        print(f"Transformer: {transformer_results[i][0]} (Score: {transformer_results[i][1]:.4f})")
        print(f"VADER: {vader_results[i][0]} (Score: {vader_results[i][1]:.4f})")
        print()


if __name__ == "__main__":
    main()
