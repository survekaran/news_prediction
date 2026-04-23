# src/model1_news/finbert_scorer.py

from typing import List, Dict
from loguru import logger
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class FinBERTScorer:
    """
    FinBERT-based sentiment scorer for financial news headlines
    """

    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Load tokenizer and model once (expensive step)
        """
        try:
            logger.info("[FinBERT] Loading model...")

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            self.model.eval()

            logger.info("[FinBERT] Model loaded successfully")

        except Exception as e:
            logger.exception(f"[FinBERT] Failed to load model: {e}")
            raise

    def score_batch(self, texts: List[str]) -> List[Dict]:
        """
        Score a batch of texts

        Returns:
            List of dicts with sentiment scores
        """

        if not texts:
            return []

        try:
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = F.softmax(outputs.logits, dim=1)

            results = []

            for p in probs:
                neg, neu, pos = p.tolist()

                score = pos - neg  # range approx [-1, +1]

                # Determine label
                if score > 0.2:
                    label = "positive"
                elif score < -0.2:
                    label = "negative"
                else:
                    label = "neutral"

                results.append({
                    "positive": round(pos, 4),
                    "negative": round(neg, 4),
                    "neutral": round(neu, 4),
                    "score": round(score, 4),
                    "label": label
                })

            return results

        except Exception as e:
            logger.exception(f"[FinBERT] Scoring failed: {e}")
            return []