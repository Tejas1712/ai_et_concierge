import json
import logging
import os
import re
from typing import Any, List, Optional
from langchain_groq import ChatGroq
from core.models import Persona, Message

logger = logging.getLogger(__name__)

class PersonaExtractor:
    """
    Extracts and maintains user personas from conversation history using LLM.
    Uses Groq (Llama 3) for high-speed structured extraction.
    """

    def __init__(self, groq_api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize PersonaExtractor with Groq LLM.

        Args:
            groq_api_key: API key for Groq. If None, uses GROQ_API_KEY environment variable.
            model: Groq model name to use.
        """
        if groq_api_key is None:
            groq_api_key = os.getenv("GROQ_API_KEY")

        if not groq_api_key:
            logger.warning("GROQ_API_KEY was not provided. Persona extraction will return defaults.")
            self.llm = None
        else:
            self.llm = ChatGroq(
                model_name=model,
                groq_api_key=groq_api_key,
                temperature=0.2,
            )
            
        self.current_persona = Persona()
        self.conversation_history: List[Message] = []

    @staticmethod
    def _extract_json_object(raw_text: str) -> Optional[dict[str, Any]]:
        """Extract the first JSON object from model output."""
        text = raw_text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try fenced code block first
            fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if fenced_match:
                try:
                    return json.loads(fenced_match.group(1))
                except json.JSONDecodeError:
                    return None

            # Fallback: first {...} block
            brace_match = re.search(r"\{.*\}", text, re.DOTALL)
            if not brace_match:
                return None
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                return None

    def extract(self, conversation_history: List[Message]) -> Persona:
        """
        Extract persona from conversation history using LLM.

        Args:
            conversation_history: List of Message objects from the conversation

        Returns:
            Extracted Persona object
        """
        if not conversation_history:
            return Persona()

        # Build conversation text for LLM
        conversation_text = "\n".join(
            [f"{msg.role.upper()}: {msg.content}" for msg in conversation_history]
        )

        # Create extraction prompt
        extraction_prompt = f"""
Analyze the following conversation and extract user persona information.
Return a JSON object with these optional fields:
- professional_background: User's job/career (string or null)
- financial_goals: User's financial objectives (string or null)
- risk_appetite: Risk tolerance level - one of: 'conservative', 'moderate', 'aggressive' (string or null)
- learning_goals: Learning outcomes the user wants (string or null)
- career_stage: User stage such as student, early-career, professional (string or null)
- transition_intent: Transition goal such as moving into AI development (string or null)
- interests: List of user interests/preferences (array of strings or null)

Conversation:
{conversation_text}

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.llm.invoke(extraction_prompt)
            response_text = str(response.content)

            persona_data = self._extract_json_object(response_text)
            if persona_data is None:
                logger.warning(
                    "Persona extraction failed: model did not return valid JSON"
                )
                return Persona()

            return Persona(**persona_data)
        except Exception as e:
            # If extraction fails, return empty persona
            logger.warning("Persona extraction failed: %s", str(e))
            return Persona()

    @staticmethod
    def _merge_unique_preserve_order(
        new_items: List[str], current_items: List[str]
    ) -> List[str]:
        merged: List[str] = []
        for item in (new_items or []) + (current_items or []):
            candidate = item.strip()
            if candidate and candidate not in merged:
                merged.append(candidate)
        return merged

    def update(self, new_information: Persona) -> Persona:
        """
        Merge new information into the current persona.

        Args:
            new_information: New Persona data to merge

        Returns:
            Updated Persona object
        """
        # Simple merge strategy: new information overrides old
        updated = Persona(
            professional_background=new_information.professional_background
            or self.current_persona.professional_background,
            financial_goals=new_information.financial_goals
            or self.current_persona.financial_goals,
            risk_appetite=new_information.risk_appetite
            or self.current_persona.risk_appetite,
            learning_goals=new_information.learning_goals
            or self.current_persona.learning_goals,
            career_stage=new_information.career_stage
            or self.current_persona.career_stage,
            transition_intent=new_information.transition_intent
            or self.current_persona.transition_intent,
            interests=self._merge_unique_preserve_order(
                new_information.interests or [],
                self.current_persona.interests or [],
            ),
        )

        self.current_persona = updated
        return updated

    def get_current_persona(self) -> Persona:
        """
        Get the current extracted persona.

        Returns:
            Current Persona object
        """
        return self.current_persona

    def add_message(self, message: Message) -> None:
        """
        Add a message to conversation history.

        Args:
            message: Message to add
        """
        self.conversation_history.append(message)

    def get_conversation_history(self) -> List[Message]:
        """
        Get conversation history.

        Returns:
            List of Message objects
        """
        return self.conversation_history

    def reset(self) -> None:
        """Reset extractor state."""
        self.current_persona = Persona()
        self.conversation_history = []
