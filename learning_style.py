# Learning Style Detection Engine
# Classifies users as Visual / Auditory / Read-Write learner

def get_questions(language="English"):
    """Returns 10 learning style questions with weighted options"""
    questions = [
        {
            "question": "Q1. When you study a new topic, what do you prefer?",
            "options": {
                "A": "Draw diagrams or mind maps to understand",
                "B": "Listen to someone explain it out loud",
                "C": "Read detailed notes and write summaries"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q2. When you forget something, you usually remember it by:",
            "options": {
                "A": "Picturing where you saw it or how it looked",
                "B": "Remembering the sound or someone saying it",
                "C": "Remembering what you wrote or read about it"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q3. In class, you learn best when the teacher:",
            "options": {
                "A": "Uses diagrams, charts and visual examples",
                "B": "Explains verbally with stories and examples",
                "C": "Gives handouts, notes and reading material"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q4. When learning something new, you prefer to:",
            "options": {
                "A": "Watch a video or see a demonstration",
                "B": "Have someone walk you through it verbally",
                "C": "Read a manual or step by step instructions"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q5. When you are trying to concentrate, you are distracted by:",
            "options": {
                "A": "Untidy or visually cluttered environment",
                "B": "Noises and sounds around you",
                "C": "People moving around or interrupting your reading"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q6. When solving a problem, you usually:",
            "options": {
                "A": "Draw it out or visualize the solution",
                "B": "Talk through it with someone or out loud",
                "C": "Write down the steps and work through it"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q7. Your study notes usually look like:",
            "options": {
                "A": "Diagrams, mind maps and highlighted keywords",
                "B": "You prefer not to take notes, just listen",
                "C": "Detailed written notes with proper structure"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q8. When given new information, you understand it best by:",
            "options": {
                "A": "Seeing it visually represented with colors and images",
                "B": "Hearing it explained with real life examples",
                "C": "Reading it thoroughly and writing key points"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q9. When revising for exams, you prefer to:",
            "options": {
                "A": "Look at diagrams, flowcharts and visual summaries",
                "B": "Recite notes out loud or explain to someone",
                "C": "Re-read notes and rewrite important points"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        },
        {
            "question": "Q10. You find it easiest to remember:",
            "options": {
                "A": "Faces, places and visual scenes",
                "B": "Names, music and spoken conversations",
                "C": "Facts, details and things you have written"
            },
            "weights": {"A": "V", "B": "A", "C": "R"}
        }
    ]
    return questions


def calculate_learning_style(answers):
    """
    Takes list of answers (e.g. ['A','B','C','A'...])
    Returns learning style and description
    """
    scores = {"V": 0, "A": 0, "R": 0}
    questions = get_questions()

    for i, answer in enumerate(answers):
        weight = questions[i]["weights"].get(answer, "V")
        scores[weight] += 1

    # Find dominant style
    dominant = max(scores, key=scores.get)

    # Style details
    styles = {
        "V": {
            "name": "Visual Learner 🎨",
            "description": "You learn best through images, diagrams, and visual organization. EduMind will explain topics using structured formats, analogies and visual text organization.",
            "tips": [
                "Use mind maps and diagrams while studying",
                "Highlight notes with different colors",
                "Watch video explanations",
                "Create visual summaries before exams"
            ],
            "emoji": "🎨"
        },
        "A": {
            "name": "Auditory Learner 🎧",
            "description": "You learn best through listening and verbal explanation. EduMind will explain topics in a conversational storytelling style that feels like someone talking to you.",
            "tips": [
                "Read notes out loud while studying",
                "Explain topics to friends or yourself",
                "Use rhymes or patterns to memorize",
                "Record yourself and listen back"
            ],
            "emoji": "🎧"
        },
        "R": {
            "name": "Read-Write Learner 📖",
            "description": "You learn best through reading and writing. EduMind will explain topics with detailed notes, definitions and structured academic content.",
            "tips": [
                "Rewrite notes in your own words",
                "Make detailed written summaries",
                "Use lists and structured formats",
                "Read textbooks and write key points"
            ],
            "emoji": "📖"
        }
    }

    return {
        "style": dominant,
        "details": styles[dominant],
        "scores": scores
    }