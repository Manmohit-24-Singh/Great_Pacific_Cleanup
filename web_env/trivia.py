# trivia.py
import random

TRIVIA_QUESTIONS = [
    {
        "question": "What percentage of the Earth's surface is covered by oceans?",
        "options": ["50%", "60%", "71%", "85%"],
        "answer": 2
    },
    {
        "question": "Which type of plastic is most commonly found in the ocean?",
        "options": ["Microplastics", "Plastic bags", "Straws", "Bottles"],
        "answer": 0
    },
    {
        "question": "Approximately how long does a plastic bottle take to decompose?",
        "options": ["10 years", "50 years", "450 years", "1000 years"],
        "answer": 2
    },
    {
        "question": "What is the Great Pacific Garbage Patch?",
        "options": ["A solid plastic island", "A collection of marine debris", "A landfill in Hawaii", "A sunken ship"],
        "answer": 1
    },
    {
        "question": "Which marine animal is most known to mistake plastic bags for jellyfish?",
        "options": ["Sea Turtles", "Sharks", "Dolphins", "Seagulls"],
        "answer": 0
    }
]

class TriviaManager:
    def __init__(self):
        self.current_question = None
        self.time_limit = 10.0
        self.timer = 0.0

    def start_question(self):
        self.current_question = random.choice(TRIVIA_QUESTIONS)
        self.timer = self.time_limit

    def update(self, dt):
        if self.current_question:
            self.timer -= dt
            if self.timer <= 0:
                self.timer = 0
                return "TIMEOUT"
        return "WAITING"

    def check_answer(self, user_choice_index):
        if not self.current_question:
            return False
        return user_choice_index == self.current_question["answer"]
