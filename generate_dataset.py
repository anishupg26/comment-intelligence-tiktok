import random
import string
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]


def random_id(prefix, length=8):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=length))}"


def heavy_tail_likes(n):
    # Lognormal produces a heavy tail; clip to keep within realistic bounds
    likes = np.random.lognormal(mean=2.2, sigma=1.1, size=n)
    likes = np.round(likes).astype(int)
    likes = np.clip(likes, 0, 2000)
    # Add a small fraction of viral outliers
    viral_idx = np.random.choice(n, size=max(1, n // 200), replace=False)
    likes[viral_idx] = np.random.randint(500, 2001, size=len(viral_idx))
    return likes


def generate_timestamp(n):
    now = datetime.utcnow()
    timestamps = []
    for _ in range(n):
        days_ago = random.randint(0, 89)
        seconds_ago = random.randint(0, 86400)
        ts = now - timedelta(days=days_ago, seconds=seconds_ago)
        timestamps.append(ts)
    return timestamps


def request_comment():
    starters = [
        "Can you explain",
        "Could you walk through",
        "Can you break down",
        "Please explain",
        "Would you clarify",
        "I need more detail on",
        "Can you show",
        "Could you expand on",
        "Still unsure about",
        "I wish you explained"
    ]
    objects = [
        "this step",
        "the last part",
        "the example",
        "the main idea",
        "that concept",
        "the difference",
        "the method",
        "the process",
        "the logic",
        "the takeaway"
    ]
    add_ons = [
        "with real examples",
        "a bit more slowly",
        "with a simple analogy",
        "in plain language",
        "with a quick demo",
        "with a diagram",
        "with numbers",
        "in another video",
        "step by step",
        "with context"
    ]
    return f"{random.choice(starters)} {random.choice(objects)} {random.choice(add_ons)}?"


def confusion_comment():
    openers = [
        "I'm confused about",
        "Still confused about",
        "I don't understand",
        "This part is unclear:",
        "What does",
        "Wait, what is",
        "I got lost at",
        "Can someone explain",
        "I might be missing",
        "Not sure what"
    ]
    topics = [
        "REM vs deep sleep",
        "the term you used",
        "the difference between stages",
        "how this works",
        "the key step",
        "the definition",
        "the example",
        "the transition",
        "the formula",
        "the point here"
    ]
    tails = [
        "in this context",
        "in the video",
        "exactly means",
        "you meant",
        "you said",
        "is supposed to mean",
        "in practice",
        "right there",
        "at that timestamp",
        "for beginners"
    ]
    return f"{random.choice(openers)} {random.choice(topics)} {random.choice(tails)}."


def praise_comment():
    openers = [
        "This helped me",
        "So helpful",
        "Great explanation",
        "Best video",
        "Finally get it",
        "Love this",
        "Super clear",
        "Amazing breakdown",
        "Really appreciate this",
        "Exactly what I needed"
    ]
    add_ons = [
        "so much",
        "I've seen on this topic",
        "thank you",
        "you made it click",
        "for real",
        "keep these coming",
        "saved me hours",
        "simple and clear",
        "this is gold",
        "you nailed it"
    ]
    return f"{random.choice(openers)} {random.choice(add_ons)}."


def skepticism_comment():
    openers = [
        "Is this actually",
        "Is this",
        "Where's the",
        "Not sure this",
        "I'm skeptical",
        "Do we have",
        "Source?",
        "I doubt",
        "Has this been",
        "Is there proof"
    ]
    concerns = [
        "scientifically proven",
        "backed by data",
        "supported by research",
        "accurate",
        "replicable",
        "validated",
        "real",
        "credible",
        "verified",
        "a real effect"
    ]
    tails = [
        "?",
        " or just a theory?",
        " because I can't find it.",
        " for everyone?",
        " beyond anecdotes?",
        " in a study?",
        " or just hype?",
        " in practice?",
        " at scale?",
        " for most people?"
    ]
    return f"{random.choice(openers)} {random.choice(concerns)}{random.choice(tails)}"


def discussion_comment():
    openers = [
        "Interesting point about",
        "This reminds me of",
        "I've noticed",
        "In my experience",
        "One thing I'd add is",
        "I tried this and",
        "For anyone curious,",
        "Quick note:",
        "Side thought:",
        "It also depends on"
    ]
    topics = [
        "sleep cycles",
        "routine changes",
        "the environment",
        "timing",
        "consistency",
        "screen time",
        "stress levels",
        "diet",
        "exercise",
        "habits"
    ]
    tails = [
        "made a big difference.",
        "can vary a lot.",
        "seems underrated.",
        "is what worked for me.",
        "matters more than I expected.",
        "is worth testing.",
        "is a big variable.",
        "is tricky to optimize.",
        "can be counterintuitive.",
        "is key for results."
    ]
    return f"{random.choice(openers)} {random.choice(topics)} {random.choice(tails)}"


def generate_comment(theme):
    if theme == "Request for more explanation":
        return request_comment()
    if theme == "Confusion about topic":
        return confusion_comment()
    if theme == "Positive feedback / praise":
        return praise_comment()
    if theme == "Skepticism / credibility concern":
        return skepticism_comment()
    return discussion_comment()


def generate_dataset(n_rows=8000):
    themes = [
        "Request for more explanation",
        "Confusion about topic",
        "Positive feedback / praise",
        "Skepticism / credibility concern",
        "General discussion"
    ]
    weights = [0.30, 0.20, 0.25, 0.10, 0.15]

    likes = heavy_tail_likes(n_rows)
    timestamps = generate_timestamp(n_rows)

    comments = []
    sentiments = []
    selected_themes = []

    seen = set()
    for i in range(n_rows):
        theme = weighted_choice(themes, weights)
        comment = generate_comment(theme)
        # Ensure uniqueness
        attempts = 0
        while comment in seen and attempts < 5:
            comment = generate_comment(theme)
            attempts += 1
        if comment in seen:
            comment = comment + f" ({i})"
        seen.add(comment)

        if theme == "Positive feedback / praise":
            sentiment = random.uniform(0.3, 1.0)
        elif theme == "Confusion about topic":
            sentiment = random.uniform(-0.4, 0.0)
        elif theme == "Skepticism / credibility concern":
            sentiment = random.uniform(-0.8, -0.2)
        elif theme == "Request for more explanation":
            sentiment = random.uniform(-0.1, 0.3)
        else:
            sentiment = random.uniform(-0.5, 0.5)

        comments.append(comment)
        sentiments.append(round(sentiment, 3))
        selected_themes.append(theme)

    data = pd.DataFrame({
        "comment_id": np.arange(1, n_rows + 1),
        "comment_text": comments,
        "likes": likes,
        "sentiment": sentiments,
        "theme": selected_themes,
        "timestamp": timestamps,
        "video_id": [random_id("vid") for _ in range(n_rows)],
        "user_id": [random_id("user") for _ in range(n_rows)]
    })

    return data


def main():
    random.seed(42)
    np.random.seed(42)

    n_rows = random.randint(5000, 10000)
    df = generate_dataset(n_rows)

    output_path = "synthetic_tiktok_comments_large.csv"
    df.to_csv(output_path, index=False)

    print("Generated dataset:")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("Theme distribution:")
    print(df["theme"].value_counts(normalize=True).round(3))
    print("Likes summary:")
    print(df["likes"].describe())
    print("Sentiment summary:")
    print(df["sentiment"].describe())


if __name__ == "__main__":
    main()
