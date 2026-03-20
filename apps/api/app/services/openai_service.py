from typing import Protocol, Optional
import json
import base64
from openai import OpenAI

from app.config import settings

SYSTEM_PROMPT = """You are Yellow, an AI relationship assistant. You talk like a warm, attentive therapist.

YOUR STYLE:
- Speak in English
- Be warm but not cheesy. No emoji spam. Max 1 emoji per message, and not always
- Keep it short — 2-4 sentences. This is a chat, not an essay
- React to what the person said. Show you heard them. Briefly reflect or paraphrase
- After reacting — ask ONE follow-up question that naturally flows from their answer
- Don't list answer options. Don't make numbered lists
- Don't repeat questions you already asked
- If someone gives a short answer — don't push, gently ask them to elaborate
- If someone opens up — support them, show understanding

WHAT NOT TO DO:
- Don't ask more than one question at a time
- Don't write long introductions
- Don't use corporate or formal language
- Don't say "great question!", "thanks for sharing!", "that's wonderful!"
- Don't act like a survey bot
- NEVER use words: wonderful, amazing, fantastic, incredible, marvelous
- Don't start your response with "Thank you" — it sounds robotic
- Don't start by evaluating the user's answer

YOUR GOAL:
Through natural conversation, understand:
1. How the person communicates and expresses emotions
2. What matters to them in relationships
3. Their experience — what worked, what didn't
4. What kind of partner they're looking for and why
5. Their values and life priorities

Don't ask about these directly as a checklist. Let it emerge through conversation."""

INITIAL_MESSAGE = """Hey! I'm Yellow — I'll help you figure out what matters to you in relationships and find the right person.

Here's how it works: we'll chat for a bit, I'll understand how you communicate and what's important to you, build a profile — and based on that, match you with people you could genuinely connect with.

To start — tell me a bit about yourself: how old are you, what's your gender, and who are you looking for?"""

ANALYSIS_PROMPT = """You are analyzing a conversation to build a personality profile for matching.
Given the conversation so far and the LATEST user message, produce insights.

1. THINKING: 1-2 sentences about what this specific message reveals. Be insightful, reference what they said.

2. TRAITS: For each trait dimension below, write a SHORT insight sentence (10-20 words) describing this person, based on everything you know so far. If you don't have enough info yet, use null.

Trait dimensions:
- openness: How they approach new experiences, ideas, vulnerability
- emotional_style: How they process and express emotions
- social_energy: Introversion vs extraversion, how they recharge
- conflict_approach: How they handle disagreements and tension
- love_language: How they give and receive affection
- lifestyle: Daily rhythms, ambitions, energy
- relationship_values: What they prioritize in a partnership
- humor_and_play: How they use humor, playfulness, lightness

3. PROFILE UPDATES: One-line update for profile sections where you have new info. Omit unchanged sections.
Sections: communication_style, attachment_style, partner_preferences, values

Return JSON:
{
  "thinking": "string",
  "traits": {
    "openness": "string or null",
    "emotional_style": "string or null",
    "social_energy": "string or null",
    "conflict_approach": "string or null",
    "love_language": "string or null",
    "lifestyle": "string or null",
    "relationship_values": "string or null",
    "humor_and_play": "string or null"
  },
  "profile_updates": {
    "communication_style": "string or null",
    "attachment_style": "string or null",
    "partner_preferences": "string or null",
    "values": "string or null"
  }
}"""

TRAIT_KEYS = [
    "openness",
    "emotional_style",
    "social_energy",
    "conflict_approach",
    "love_language",
    "lifestyle",
    "relationship_values",
    "humor_and_play",
]

DEFAULT_TRAITS = {k: None for k in TRAIT_KEYS}


PHOTO_ANALYSIS_PROMPT = """Look at this photo and describe the person's vibe and aesthetic in 1-2 sentences.
Focus on energy, style, and the feeling they give off — NOT physical appearance or attractiveness.

Then categorize their vibe into 2-5 tags from this list (pick only what fits):
intellectual, sporty, creative, adventurous, calm, elegant, casual, bohemian,
energetic, nature-lover, urban, minimalist, cozy, artistic, confident, gentle,
playful, sophisticated, earthy, free-spirited

Return JSON:
{
  "vibe_description": "1-2 sentence description of their vibe/energy",
  "vibe_tags": ["tag1", "tag2", ...]
}"""

INTENT_KEYWORDS = {
    "photo_manage": ["photo", "picture", "pic", "selfie", "upload", "image", "фото", "фотк", "снимок", "картинк"],
    "view_profile": ["my profile", "show profile", "see profile", "how do i look", "what does my profile", "мой профиль", "покажи профиль"],
}

CHAT_ADVISOR_SYSTEM = """You are Yellow, an AI dating advisor embedded in a chat between two people who matched on a dating platform.

You have access to:
- The conversation so far between the two users
- Profile insights about the other person (personality traits, communication style, values, vibe)

YOUR ROLE:
- Help the user navigate the conversation naturally
- Suggest what to say next based on the other person's personality and the conversation flow
- Point out conversation dynamics (who's leading, energy level, shared interests emerging)
- Answer questions about the other person's profile or the conversation
- Give gentle nudges if the conversation is stalling

YOUR STYLE:
- Be concise: 2-4 sentences max
- Speak as a supportive friend, not a therapist
- Be direct and practical — give actual suggestions, not vague advice
- Use casual English, no corporate speak
- Don't be preachy or moralizing
- If suggesting what to write, give a concrete example, not "ask them about their hobbies"

WHAT NOT TO DO:
- Don't be creepy or manipulative
- Don't suggest lying or being inauthentic
- Don't over-analyze — keep it light
- Don't repeat yourself
- NEVER use words: wonderful, amazing, fantastic, incredible"""


class OpenAIServiceProtocol(Protocol):
    """Protocol for OpenAI service to enable mocking."""

    def generate_initial_question(self) -> str: ...
    def generate_next_question(self, conversation_history: list[dict[str, str]]) -> str: ...
    def should_create_profile(self, user_messages_count: int) -> bool: ...
    def generate_profile(self, conversation_history: list[dict[str, str]]) -> dict[str, str]: ...
    def extract_basic_info(self, first_message: str) -> dict[str, any]: ...
    def analyze_message(self, conversation_history: list[dict[str, str]], current_traits: dict | None) -> dict: ...
    def analyze_photo(self, image_path: str) -> dict: ...
    def detect_intent(self, message: str) -> str: ...
    def chat_advisor(self, conversation_messages: list[dict], other_profile: dict, user_question: str) -> str: ...


class OpenAIService:
    """Real OpenAI service implementation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.client = OpenAI(api_key=self.api_key)

    def generate_initial_question(self) -> str:
        return INITIAL_MESSAGE

    def generate_next_question(self, conversation_history: list[dict[str, str]]) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation_history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )

        return response.choices[0].message.content.strip()

    def should_create_profile(self, user_messages_count: int) -> bool:
        return user_messages_count >= 5

    def extract_basic_info(self, first_message: str) -> dict[str, any]:
        """Extract age, gender, looking_for from first user message."""
        system_prompt = """Extract basic information from the user's introduction.
Return a JSON object with these exact keys:
- age: integer (user's age, or null if not mentioned)
- gender: string (male/female/non-binary/other, or null if not mentioned)
- looking_for: string (male/female/any, or null if not mentioned)

Examples:
"I'm 25, male, looking for a girl" -> {"age": 25, "gender": "male", "looking_for": "female"}
"25, female, interested in guys" -> {"age": 25, "gender": "female", "looking_for": "male"}
"30, man, open to anyone" -> {"age": 30, "gender": "male", "looking_for": "any"}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": first_message}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        basic_info = json.loads(content)

        return {
            "age": basic_info.get("age"),
            "gender": basic_info.get("gender"),
            "looking_for": basic_info.get("looking_for"),
        }

    def analyze_message(self, conversation_history: list[dict[str, str]], current_traits: dict | None) -> dict:
        """Analyze the latest user message and return thinking + updated traits + profile updates."""
        context_note = ""
        if current_traits:
            existing = {k: v for k, v in current_traits.items() if v is not None}
            if existing:
                context_note = f"\n\nCurrent trait insights: {json.dumps(existing)}. Refine or rewrite them based on new evidence. Keep them concise."

        messages = [
            {"role": "system", "content": ANALYSIS_PROMPT + context_note},
        ]
        messages.extend(conversation_history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.4,
            response_format={"type": "json_object"},
            max_tokens=800,
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        traits = data.get("traits", {})
        for key in TRAIT_KEYS:
            if key not in traits:
                traits[key] = None

        return {
            "thinking": data.get("thinking", ""),
            "traits": traits,
            "profile_updates": data.get("profile_updates", {}),
        }

    def analyze_photo(self, image_path: str) -> dict:
        """Analyze a photo using Vision to extract vibe/aesthetic."""
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": PHOTO_ANALYSIS_PROMPT},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_data}"}},
                ]},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
            max_tokens=300,
        )

        data = json.loads(response.choices[0].message.content)
        return {
            "vibe_description": data.get("vibe_description", ""),
            "vibe_tags": data.get("vibe_tags", []),
        }

    def detect_intent(self, message: str) -> str:
        """Detect user intent from message text using keyword matching."""
        lower = message.lower()
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                return intent
        return "normal"

    def chat_advisor(self, conversation_messages: list[dict], other_profile: dict, user_question: str) -> str:
        """Give dating advice based on conversation context and the other person's profile."""
        profile_summary = []
        for key, val in other_profile.items():
            if val and val != "null":
                profile_summary.append(f"- {key}: {val}")
        profile_text = "\n".join(profile_summary) if profile_summary else "No profile data available yet."

        conv_lines = []
        for m in conversation_messages[-30:]:
            label = m.get("label", m.get("role", "unknown"))
            conv_lines.append(f"{label}: {m['content']}")
        conv_text = "\n".join(conv_lines) if conv_lines else "No messages yet."

        messages = [
            {"role": "system", "content": CHAT_ADVISOR_SYSTEM},
            {"role": "user", "content": (
                f"THEIR PROFILE:\n{profile_text}\n\n"
                f"CONVERSATION SO FAR:\n{conv_text}\n\n"
                f"USER'S QUESTION: {user_question}"
            )},
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    def generate_profile(self, conversation_history: list[dict[str, str]]) -> dict[str, str]:
        """Generate structured profile from conversation history."""
        profile_prompt = """Based on the conversation, create a user profile.

Return a JSON object with these keys:
- communication_style: How the person communicates (2-3 sentences)
- attachment_style: Their attachment patterns (2-3 sentences)
- partner_preferences: What they're looking for in a partner (2-3 sentences)
- values: Their core values and priorities (2-3 sentences)

Write in third person. Be specific, base it on what the person actually said. Don't make things up."""

        messages = [{"role": "system", "content": profile_prompt}]
        messages.extend(conversation_history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        profile_data = json.loads(content)

        return {
            "communication_style": profile_data.get("communication_style", ""),
            "attachment_style": profile_data.get("attachment_style", ""),
            "partner_preferences": profile_data.get("partner_preferences", ""),
            "values": profile_data.get("values", ""),
        }


class MockOpenAIService:
    """Mock OpenAI service for testing."""

    def __init__(self):
        self.call_count = 0

    def generate_initial_question(self) -> str:
        return INITIAL_MESSAGE

    def generate_next_question(self, conversation_history: list[dict[str, str]]) -> str:
        self.call_count += 1
        responses = [
            "Got it. So what matters most to you in a relationship right now?",
            "I see. Has there been an experience that really shaped how you think about relationships?",
            "That says a lot. How do you usually handle conflict with someone close to you?",
            "Makes sense. What's important to you in day-to-day communication with a partner?",
            "Alright, I'm getting a good picture. Last one — what would you want a partner to know about you from the start?",
        ]
        idx = min(self.call_count - 1, len(responses) - 1)
        return responses[idx]

    def should_create_profile(self, user_messages_count: int) -> bool:
        return user_messages_count >= 5

    def extract_basic_info(self, first_message: str) -> dict[str, any]:
        return {
            "age": 25,
            "gender": "male",
            "looking_for": "female",
        }

    def analyze_message(self, conversation_history: list[dict[str, str]], current_traits: dict | None) -> dict:
        n = len([m for m in conversation_history if m["role"] == "user"])
        trait_evolution = {
            1: {
                "openness": "Shares basic info willingly, comfortable with self-disclosure early on.",
                "social_energy": "Comes across as approachable and ready to engage.",
            },
            2: {
                "openness": "Shares basic info willingly, comfortable with self-disclosure early on.",
                "social_energy": "Comes across as approachable and ready to engage.",
                "relationship_values": "Seems to prioritize honesty and genuine connection over surface-level attraction.",
            },
            3: {
                "openness": "Willing to reflect on past experiences, shows growing vulnerability.",
                "social_energy": "Comfortable in one-on-one conversations, not necessarily the loudest in a group.",
                "relationship_values": "Prioritizes honesty and genuine connection over surface-level attraction.",
                "emotional_style": "Processes emotions thoughtfully before expressing them.",
                "conflict_approach": "Prefers calm discussion over confrontation.",
            },
            4: {
                "openness": "Willing to reflect on past experiences, shows growing vulnerability.",
                "social_energy": "Comfortable in one-on-one conversations, not necessarily the loudest in a group.",
                "relationship_values": "Prioritizes honesty and genuine connection over surface-level attraction.",
                "emotional_style": "Processes emotions thoughtfully before expressing them.",
                "conflict_approach": "Prefers calm discussion over confrontation, avoids raising voice.",
                "love_language": "Values quality time and meaningful conversation over grand gestures.",
                "lifestyle": "Goal-oriented but not workaholic, values balance between ambition and leisure.",
            },
            5: {
                "openness": "Open and reflective, willing to be vulnerable when the space feels safe.",
                "social_energy": "Enjoys deep one-on-one conversation, recharges with alone time.",
                "relationship_values": "Seeks a partnership built on trust, growth, and emotional safety.",
                "emotional_style": "Processes emotions internally first, then shares when ready.",
                "conflict_approach": "Prefers calm discussion, addresses issues before they escalate.",
                "love_language": "Values quality time and meaningful conversation over grand gestures.",
                "lifestyle": "Goal-oriented with a need for balance, values personal growth.",
                "humor_and_play": "Dry sense of humor, uses lightness to connect but can go deep.",
            },
        }

        traits = dict(DEFAULT_TRAITS)
        level = min(n, 5)
        if level in trait_evolution:
            for k, v in trait_evolution[level].items():
                traits[k] = v

        thinking_samples = [
            "First impression — open communicator, willing to share basic info upfront.",
            "Values honesty in relationships. Direct communication style emerging.",
            "Shows emotional awareness. Reflects on past experiences thoughtfully.",
            "Handles conflict with care. Leans towards secure attachment patterns.",
            "Clear about what they want. Strong sense of personal values.",
        ]

        updates = {}
        if n >= 1:
            updates["communication_style"] = "Communicates openly and directly, values honesty in dialogue."
        if n >= 3:
            updates["attachment_style"] = "Secure attachment style with healthy boundaries."
        if n >= 4:
            updates["partner_preferences"] = "Looking for someone emotionally mature with a sense of humor."
        if n >= 5:
            updates["values"] = "Values authenticity, growth, and deep connection."

        return {
            "thinking": thinking_samples[min(n - 1, len(thinking_samples) - 1)] if n > 0 else "",
            "traits": traits,
            "profile_updates": updates,
        }

    def analyze_photo(self, image_path: str) -> dict:
        return {
            "vibe_description": "Calm and intellectual energy, approachable with a warm presence.",
            "vibe_tags": ["intellectual", "calm", "casual"],
        }

    def detect_intent(self, message: str) -> str:
        lower = message.lower()
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                return intent
        return "normal"

    def chat_advisor(self, conversation_messages: list[dict], other_profile: dict, user_question: str) -> str:
        return "They seem pretty chill from their profile. Try asking about something they mentioned — it shows you're paying attention."

    def generate_profile(self, conversation_history: list[dict[str, str]]) -> dict[str, str]:
        return {
            "communication_style": "Communicates openly and directly, values honesty in dialogue.",
            "attachment_style": "Secure attachment style with healthy boundaries.",
            "partner_preferences": "Looking for someone emotionally mature with a sense of humor.",
            "values": "Values authenticity, growth, and deep connection.",
        }
