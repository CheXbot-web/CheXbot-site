import requests
import tweepy
from transformers import pipeline
from bs4 import BeautifulSoup
import torch
from transformers import pipeline
torch.backends.mkldnn.enabled = True
classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
import time
start = time.time()
result = classifier("Solar panels saved $50B in 2024.", candidate_labels=["factual", "opinion"])
print(f"Time: {time.time() - start:.2f}s, Result: {result['labels'][0]}")