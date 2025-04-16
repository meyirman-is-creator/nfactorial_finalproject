from typing import Dict, Any, Optional
import json
import re


class ChatbotService:
    """
    Simple rule-based chatbot for educational support.

    In a production system, this would be replaced with an actual NLP model or
    integration with a service like OpenAI.
    """

    def __init__(self):
        # Load predefined responses
        self.responses = {
            "greeting": [
                "Hello! How can I help you with your learning today?",
                "Hi there! What do you need help with?"
            ],
            "course_inquiry": [
                "We offer various courses in different subjects. You can browse them in the Courses section.",
                "Our platform has many courses available. Check the Courses tab to see what's available."
            ],
            "assignment_help": [
                "For assignment help, I recommend checking course materials or asking your instructor.",
                "If you need help with assignments, try reviewing the lesson materials or posting in discussions."
            ],
            "test_preparation": [
                "To prepare for tests, review your course materials and try practice quizzes if available.",
                "Test preparation involves reviewing lessons, completing practice exercises, and getting enough rest."
            ],
            "technical_issue": [
                "If you're experiencing technical issues, try refreshing the page or clearing your browser cache.",
                "For technical problems, you might want to contact support through the Help section."
            ],
            "goodbye": [
                "Goodbye! Feel free to return if you have more questions.",
                "Have a great day! Come back anytime you need help."
            ],
            "default": [
                "I'm not sure I understand. Could you rephrase your question?",
                "I'm still learning and don't have information about that yet. Can I help with something else?"
            ]
        }

        # Define patterns for intent recognition
        self.patterns = {
            "greeting": r"\b(hi|hello|hey|greetings)\b",
            "course_inquiry": r"\b(course|courses|class|classes|learn|study)\b",
            "assignment_help": r"\b(assignment|homework|task|project)\b",
            "test_preparation": r"\b(test|exam|quiz|assessment|prepare|study)\b",
            "technical_issue": r"\b(error|problem|issue|bug|not working|broken)\b",
            "goodbye": r"\b(bye|goodbye|see you|farewell)\b"
        }

    def get_response(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response based on the user's message.

        Args:
            message: User's message
            context: Optional context (e.g., current course or lesson)

        Returns:
            Dict containing response text and confidence score
        """
        # Convert message to lowercase for pattern matching
        message = message.lower()

        # Detect intent based on patterns
        intent = self._detect_intent(message)

        # Get response based on intent
        responses = self.responses.get(intent, self.responses["default"])

        # Simple selection of response (in a real system, this would be more sophisticated)
        import random
        response = random.choice(responses)

        # Add context-specific information if available
        if context and intent in ["course_inquiry", "assignment_help", "test_preparation"]:
            response += f" Since you're asking about {context}, you might find specific information in that section."

        # Calculate confidence (in a real system, this would be more sophisticated)
        confidence = 0.9 if intent != "default" else 0.3

        return {
            "response": response,
            "confidence": confidence
        }

    def _detect_intent(self, message: str) -> str:
        """
        Detect intent based on pattern matching.

        Args:
            message: User's message

        Returns:
            Detected intent
        """
        for intent, pattern in self.patterns.items():
            if re.search(pattern, message):
                return intent

        return "default"