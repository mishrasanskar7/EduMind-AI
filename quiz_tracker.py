# Quiz Performance Tracker
# Stores and analyzes quiz scores during session

def initialize_tracker():
    """Returns empty tracker dictionary"""
    return {
        "quizzes": [],
        "total_attempted": 0,
        "total_score": 0
    }


def save_score(tracker, topic, score, total=5):
    """
    Saves a quiz result to tracker
    topic: name of topic quizzed on
    score: number of correct answers
    total: total questions (default 5)
    """
    percentage = (score / total) * 100

    tracker["quizzes"].append({
        "topic": topic,
        "score": score,
        "total": total,
        "percentage": round(percentage, 1)
    })

    tracker["total_attempted"] += 1
    tracker["total_score"] += percentage

    return tracker


def get_average_score(tracker):
    """Returns average score across all quizzes"""
    if tracker["total_attempted"] == 0:
        return 0
    return round(tracker["total_score"] / tracker["total_attempted"], 1)


def get_weak_topics(tracker):
    """Returns list of topics where score is below 60%"""
    weak = []
    for quiz in tracker["quizzes"]:
        if quiz["percentage"] < 60:
            weak.append(quiz["topic"])
    return weak


def get_strong_topics(tracker):
    """Returns list of topics where score is 70% or above"""
    strong = []
    for quiz in tracker["quizzes"]:
        if quiz["percentage"] >= 70:
            strong.append(quiz["topic"])
    return strong


def get_best_topic(tracker):
    """Returns topic with highest score"""
    if not tracker["quizzes"]:
        return None
    best = max(tracker["quizzes"], key=lambda x: x["percentage"])
    return best["topic"]


def get_worst_topic(tracker):
    """Returns topic with lowest score"""
    if not tracker["quizzes"]:
        return None
    worst = min(tracker["quizzes"], key=lambda x: x["percentage"])
    return worst["topic"]


def get_all_scores(tracker):
    """Returns all quiz data for analytics chart"""
    topics = []
    percentages = []
    colors = []

    for quiz in tracker["quizzes"]:
        topics.append(quiz["topic"])
        percentages.append(quiz["percentage"])
        # Green if good, red if weak
        if quiz["percentage"] >= 70:
            colors.append("green")
        elif quiz["percentage"] >= 50:
            colors.append("orange")
        else:
            colors.append("red")

    return topics, percentages, colors