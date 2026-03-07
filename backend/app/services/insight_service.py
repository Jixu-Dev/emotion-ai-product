from typing import Dict


class InsightService:
    """Generates short coaching insights from dominant emotion."""

    _default_message = "Take one deep breath and notice what you need in this moment."

    _emotion_messages: Dict[str, str] = {
        "happy": "Great energy—channel it into one meaningful action right now.",
        "sad": "Be kind to yourself; try a short walk or reach out to someone you trust.",
        "angry": "Pause for 10 seconds before reacting to create space for a better choice.",
        "fear": "Ground yourself by naming three things you can see and hear around you.",
        "surprise": "Stay curious—write down what changed and what you can learn from it.",
        "neutral": "You seem steady—this is a great time to prioritize your next key task.",
        "disgust": "Acknowledge the discomfort and refocus on what you can control.",
    }

    def generate(self, emotion: str, confidence: float) -> str:
        message = self._emotion_messages.get(emotion.lower(), self._default_message)
        return f"{message} (confidence: {confidence:.0%})"
