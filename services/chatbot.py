import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

print(os.getenv("GEMINI_API_KEY"))   # <-- Add this line

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Chatbot for exam questions
def ask_ai(question):

    prompt = f"""
You are an AI assistant for competitive exam students.

Answer ONLY questions related to:

UPSC
SSC
Banking Exams
Reasoning
Quantitative Aptitude
General Knowledge
Current Affairs
English Grammar
Programming aptitude

If user asks unrelated questions like movies, celebrities, sports gossip, entertainment or random topics, reply:

I can only help with competitive exam preparation topics.

User Question: {question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# Generate MCQ
def generate_mcq(topic):

    prompt = f"""
Generate exactly 3 MCQ questions on {topic}

Return EXACTLY in this format:

Q1: What is ...?

A) option1
B) option2
C) option3
D) option4

ANSWER: B

Q2: ...

A) option1
B) option2
C) option3
D) option4

ANSWER: C

Q3: ...

A) option1
B) option2
C) option3
D) option4

ANSWER: A

Do not add extra explanation.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# Parse AI MCQ text
def parse_mcq(text):

    questions = []

    blocks = text.split("Q")

    for block in blocks:

        if block.strip() == "":
            continue

        lines = block.strip().split("\n")

        question = lines[0]

        options = []
        answer = ""

        for line in lines[1:]:

            if line.startswith(("A)", "B)", "C)", "D)")):
                options.append(line[3:].strip())

            if "ANSWER:" in line:

                answer_letter = line.replace(
                    "ANSWER:",
                    ""
                ).strip()

                if answer_letter == "A":
                    answer = options[0]

                elif answer_letter == "B":
                    answer = options[1]

                elif answer_letter == "C":
                    answer = options[2]

                elif answer_letter == "D":
                    answer = options[3]

        questions.append(
            {
                "question": question,
                "options": options,
                "answer": answer
            }
        )

    return questions