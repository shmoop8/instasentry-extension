from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import random
import re
from datetime import datetime, timedelta

app = FastAPI()

# Allow requests from Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str

class CommentData(BaseModel):
    username: str
    text: str
    timestamp: str  # ISO formatted string
    likes: int

class AccountAnalysis(BaseModel):
    username: str
    bot_score: int
    likelihood: str
    reasons: List[str]

# Utility: Validate Instagram URL
def is_valid_instagram_url(url: str) -> bool:
    pattern = r"^https?://(www\.)?instagram\.com/p/[\w-]+/?$"
    return re.match(pattern, url) is not None

# Utility: Score an account based on mock metrics
def analyze_account(username: str, comments: List[CommentData]) -> AccountAnalysis:
    reasons = []
    score = 50  # Start at neutral
    
    # Mock behavioral checks
    for comment in comments:
        # Check for emoji flooding
        emoji_count = len(re.findall(r"[^\w\s,]", comment.text))
        if emoji_count > 5:
            score -= 5
            reasons.append(f"High emoji usage in comment '{comment.text}'")
        
        # Check for short repetitive comments
        if len(comment.text) < 10:
            score -= 3
            reasons.append(f"Short comment '{comment.text}'")

    # Mock account metadata
    account_age_days = random.randint(1, 2000)
    if account_age_days < 30:
        score -= 10
        reasons.append("New account (less than 1 month old)")
    
    follower_count = random.randint(0, 5000)
    following_count = random.randint(0, 5000)
    if follower_count / max(following_count, 1) < 0.1:
        score -= 5
        reasons.append("Low follower-to-following ratio")

    # Clamp score to 1–99
    score = max(1, min(99, score))

    # Determine likelihood
    if score <= 25:
        likelihood = "Very Likely Automated"
    elif score <= 50:
        likelihood = "Likely Automated"
    elif score <= 70:
        likelihood = "Uncertain"
    elif score <= 85:
        likelihood = "Likely Human"
    else:
        likelihood = "Highly Likely Human"

    return AccountAnalysis(username=username, bot_score=score, likelihood=likelihood, reasons=reasons)

# Endpoint to analyze a URL
@app.post("/analyze", response_model=Dict[str, List[AccountAnalysis]])
def analyze_post(request: AnalyzeRequest):
    if not is_valid_instagram_url(request.url):
        return {"error": "Invalid Instagram post URL."}

    # MOCK: Simulate fetching comments (replace with real API or scraping)
    mock_comments = [
        CommentData(username="user1", text="😍😍😍", timestamp=str(datetime.now()), likes=3),
        CommentData(username="user2", text="Great post!", timestamp=str(datetime.now() - timedelta(minutes=5)), likes=1),
        CommentData(username="user3", text="Check this out!", timestamp=str(datetime.now() - timedelta(minutes=10)), likes=0),
    ]

    # Group comments by username
    users = {}
    for comment in mock_comments:
        users.setdefault(comment.username, []).append(comment)

    # Analyze each account
    results = []
    for username, comments in users.items():
        analysis = analyze_account(username, comments)
        results.append(analysis)

    return {"results": results}

@app.get("/")
def read_root():
    return {"message": "InstaSentry backend is running!"}
