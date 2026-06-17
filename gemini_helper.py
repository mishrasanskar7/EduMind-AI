from groq import Groq
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

def get_ai_response(topic, feature, learning_style="Visual", difficulty="Undergrad", language="English"):

    # Learning style instructions
    style_prompts = {
        "Visual": "Use structured formatting, analogies, diagrams in text, bullet points and visual organization.",
        "Auditory": "Use a conversational storytelling style, as if explaining to a friend out loud.",
        "Read-Write": "Use detailed notes, definitions, numbered lists and academic writing style.",
        "V": "Use structured formatting, analogies, diagrams in text, bullet points and visual organization.",
        "A": "Use a conversational storytelling style, as if explaining to a friend out loud.",
        "R": "Use detailed notes, definitions, numbered lists and academic writing style."
    }

    # Difficulty instructions
    difficulty_prompts = {
        "School": "Explain at a simple school level that a 15 year old can understand.",
        "Undergrad": "Explain at an undergraduate college student level.",
        "Research": "Explain at an advanced research and professional level with technical depth."
    }

    # Language instructions
    language_codes = {
        "English": "You must respond in English only.",
        "Hindi": "आपको केवल हिंदी में जवाब देना है। Every single word must be in Hindi only. Do not use English at all.",
        "French": "Vous devez répondre uniquement en français. Every single word must be in French only.",
        "German": "Sie müssen nur auf Deutsch antworten. Every single word must be in German only."
    }

    style = style_prompts.get(learning_style, style_prompts["Visual"])
    level = difficulty_prompts.get(difficulty, difficulty_prompts["Undergrad"])
    lang_instruction = language_codes.get(language, language_codes["English"])

    # Strong system instruction
    system_instruction = f"""You are EduMind AI - an adaptive learning assistant.
CRITICAL: {lang_instruction}
You must ONLY respond in {language}. Not a single word in any other language.
{style}
{level}"""

    # Build prompt based on feature
    if feature == "explainer":
        prompt = f"""
        LANGUAGE: Respond in {language} ONLY.
        
        You are EduMind AI - an adaptive learning assistant.
        {level}
        {style}
        
        Explain this topic clearly and thoroughly: {topic}

        First detect if this topic is a MATHEMATICAL or SCIENTIFIC topic.

        IF it is a MATHEMATICAL/SCIENTIFIC topic, format your response EXACTLY like this:

        ## 📖 What is [Topic Name]?
        [Clear theory explanation in 3-4 sentences]

        ## 📐 Standard Form / Formula
        [Write formula clearly on its own line]
        [Explain each variable on separate lines]
        - Variable 1: meaning
        - Variable 2: meaning

        ## 📝 Step-by-Step Method
        **Step 1:** [Name of step]
        [Explanation of step]

        **Step 2:** [Name of step]
        [Explanation of step]

        **Step 3:** [Name of step]
        [Explanation of step]

        [Continue for all steps, each on separate lines]

        ## ✏️ Solved Example
        **Problem:** [Write a specific problem]

        **Solution:**

        **Step 1:** [Step name]
        [Show calculation clearly]

        **Step 2:** [Step name]
        [Show calculation clearly]

        **Step 3:** [Step name]
        [Show calculation clearly]

        [Continue until final answer]

        **Final Answer:** [Clear final answer]

        ## 💡 Key Points to Remember
        - Point 1
        - Point 2
        - Point 3
        - Point 4

        IF it is a NON-MATHEMATICAL topic format like this:

        ## 📖 Definition
        [Clear simple definition]

        ## 🔑 Key Concepts
        - Concept 1: explanation
        - Concept 2: explanation
        - Concept 3: explanation

        ## 🌍 Real Life Example
        [Relatable real life example]

        ## 💡 Important Points
        - Point 1
        - Point 2
        - Point 3

        IMPORTANT FORMATTING RULES:
        - Write equations on their own separate line
        - Use plain text math notation that is easy to read
        - For example write: dy/dx + 2y = 3
        - Each step must be on its own separate line with blank line after it
        - Never mix equation and explanation on same line
        - Write calculation on one line then explanation on next line

          REMEMBER:
        - Each step on its own separate line
        - Never put multiple steps on same line  
        - Keep proper spacing between sections
        - Respond in {language} only
        - Use these math symbols for clarity:
          * For integrals use: ∫
          * For therefore use: ∴
          * For implies use: ⟹
          * For alpha, beta, mu use: α, β, μ
          * For powers write: e^(2x) or x²
          * For fractions write: dy/dx
          * Always put equations on their own line
          * Add a blank line after every step
          """
    elif feature == "summarizer":
        prompt = f"""Summarize these notes clearly: {topic}

Structure your response with:
1. Main Topic
2. Key Points (bullet points)
3. Important Terms
4. One Line Summary

Remember: Respond in {language} ONLY."""

    elif feature == "quiz":
     prompt = f"""Generate exactly 5 multiple choice questions on: {topic}

Format each question EXACTLY like this:
Q1: [Question text]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
ANSWER: [Correct letter]
EXPLANATION: [Brief explanation]

Repeat for Q2, Q3, Q4, Q5.
Remember: Respond in {language} ONLY."""

    elif feature == "flashcard":
        prompt = f"""Generate exactly 5 flashcards on: {topic}

Format EXACTLY like this:
CARD 1:
FRONT: [Term or Concept]
BACK: [Clear definition or explanation]

Repeat for CARD 2, CARD 3, CARD 4, CARD 5.
Remember: Respond in {language} ONLY."""

    elif feature == "mindmap":
        prompt = f"""Create a detailed mind map for: {topic}

Format EXACTLY like this:
🧠 {topic.upper()}
├── 📌 [Main Concept 1]
│   ├── [Sub point 1]
│   ├── [Sub point 2]
│   └── [Sub point 3]
├── 📌 [Main Concept 2]
│   ├── [Sub point 1]
│   ├── [Sub point 2]
│   └── [Sub point 3]
├── 📌 [Main Concept 3]
│   ├── [Sub point 1]
│   ├── [Sub point 2]
│   └── [Sub point 3]
└── 📌 [Main Concept 4]
    ├── [Sub point 1]
    ├── [Sub point 2]
    └── [Sub point 3]

Remember: Respond in {language} ONLY."""

    else:
        prompt = f"Explain {topic} clearly. Respond in {language} only."

    # Call Groq API
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting AI response: {str(e)}"