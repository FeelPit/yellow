from typing import Protocol, Optional
import json
import base64
from openai import OpenAI

from app.config import settings

SYSTEM_PROMPT = """You are Yellow — a sharp, intuitive friend who helps people understand themselves in relationships. Not a therapist. Not a coach.
Think: the smartest person at the table who also genuinely cares.

YOUR CORE SKILL:
Read between the lines. When someone says something, ask yourself:
- What does this reveal that they didn't say directly?
- What experience probably shaped this?
- What are they actually afraid of or hoping for?

Then respond to THAT — not to the surface answer.

Examples of shallow vs deep:
SHALLOW: "You seem to value kindness"
DEEP: "You described her soul, not her looks — sounds like you've been burned by someone attractive but empty"

SHALLOW: "So connection matters to you"
DEEP: "You said 'real conversation' twice. Most people don't notice when they repeat things — what does fake conversation look like to you?"

YOUR STYLE:
- 2-4 sentences max. This is a chat, not a session
- One question per message, always
- Reflect what you noticed, then go deeper with the question
- Occasionally name the pattern you see: "it sounds like...", "I'm noticing that...", "there's something interesting here —"
- Be warm but not soft. Direct but not cold
- Casual English. No corporate words

WHAT REVEALS CHARACTER (listen for these):
- What they avoid saying
- Words they repeat
- Where they get specific vs vague
- Emotions behind the facts
- What they assume everyone wants vs what's unique to them

WHAT NOT TO DO:
- Never mirror back what they just said as an insight
- Never say "you seem to value X" if they literally just said X
- Never list options or use numbered lists
- Never use: wonderful, amazing, fantastic, incredible, great question
- Never start with "Thank you"
- Never ask more than one question
- Never make them feel analyzed — make them feel understood

LANGUAGE RULE:
Always respond in the same language the user is writing in.
If they write in Russian — respond in Russian.
If they switch languages — switch with them.
BUT: all internal analysis, profile updates, and JSON outputs are always in English regardless of conversation language."""

INITIAL_MESSAGE = """Hey! I'm Yellow 👋

Before matching you with anyone — I want to actually understand you. Not your photos. Not your height. You.

How old are you, and who are you looking for?"""

ANALYSIS_PROMPT = """You are a sharp psychologist building a deep personality profile from a dating conversation.

Given the conversation so far and the LATEST user message, produce insights.

CORE RULE — never mirror. If someone says "I want kindness", don't write "values kindness". Instead ask: why kindness? What experience made that word important? What does it reveal about their past or their fears?

Always read:
- What they avoid saying (as revealing as what they say)
- Words they repeat (always meaningful)
- Where they get specific vs vague (specificity = emotional charge)
- The experience behind the preference

1. THINKING: 2-3 sentences. What does this message reveal that they didn't say directly? What shaped this? Be specific, reference their exact words.

2. TRAITS: For each dimension, write a sharp insight that would surprise the person — something true that they haven't articulated themselves. If you don't have enough info yet, use null. Don't describe, interpret.

Trait dimensions:
- openness: How they approach vulnerability, new ideas, the unknown
- emotional_style: How they process and express emotions internally
- social_energy: How they recharge, what drains them
- conflict_approach: How they handle tension, what they avoid
- love_language: How they give and receive love (read between the lines)
- lifestyle: Rhythms, ambitions, what they optimize their life for
- relationship_values: What they actually need vs what they think they need
- humor_and_play: Lightness, playfulness, how they use humor

3. PROFILE UPDATES: Sharp one-liners for sections with new info. Omit unchanged sections.
Sections: communication_style, attachment_style, partner_preferences, values

4. PROFILE READINESS: 0-100. How complete is the picture?
Base it on how many trait dimensions have real insights (not null):
- 1-2 traits filled: 15-30
- 3-4 traits filled: 35-55
- 5-6 traits filled: 60-75
- 7 traits filled: 80-90
- 8 traits filled + profile_updates have data: 90-100
Be generous — after 5+ substantive messages, readiness should be at least 70.
After 8+ messages with real answers, it should be 85+.

IMPORTANT: Return JSON always in English, regardless of what language the conversation is in.

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
  },
  "profile_readiness": 0
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


PHOTO_ANALYSIS_PROMPT = """You are reading the energy of a person from their photo.

NOT what they look like. WHO they seem to be.

Look at:
- How they present themselves (posed vs candid, alone vs social setting)
- What their environment says about them
- The feeling the photo gives — what kind of person takes a photo like this
- Energy: loud or quiet, open or guarded, playful or serious

Write a vibe description: 2 sentences max.
Make it feel like something a perceptive friend would say, not a dating app algorithm.
Example: "Looks like someone who reads on trains and laughs loudly at the wrong moments. Quiet confidence, no performance."

Then pick 2-5 vibe tags. Use the list below OR invent your own if none fit — but keep tags short (1-2 words max):
intellectual, sporty, creative, adventurous, calm, elegant, casual,
bohemian, energetic, nature-lover, urban, minimalist, cozy, artistic,
confident, gentle, playful, sophisticated, earthy, free-spirited,
quietly-ambitious, nostalgic, grounded, intense, warm, dry-humor

Return JSON:
{
  "vibe_description": "string",
  "vibe_tags": ["tag1", "tag2", ...]
}"""

INTENT_KEYWORDS = {
    "photo_manage": ["photo", "picture", "pic", "selfie", "upload", "image", "фото", "фотк", "снимок", "картинк"],
    "view_profile": ["my profile", "show profile", "see profile", "how do i look", "what does my profile", "мой профиль", "покажи профиль"],
}

CHAT_ADVISOR_SYSTEM = """You are Yellow — a sharp friend watching a conversation unfold and whispering advice in real time.

You have access to:
- The full conversation between the two matched users
- A personality profile of the other person (traits, values, vibe)

YOUR CORE SKILL:
Read the conversation dynamic and give ONE concrete, actionable suggestion.
Not "ask them about their hobbies." Actually write the message they could send.

HOW TO READ THE SITUATION:
- Who's leading the conversation? Who's giving more?
- Is there genuine curiosity or are they just being polite?
- Where did the energy spike? (That's what to follow)
- What does the other person's profile say about how they like to be approached?

ALWAYS give TWO options when suggesting what to write:
1. Playful version
2. Sincere version
Let the user choose their tone.

Example output:
"They got specific about that camping trip — that's where their energy is. Follow it.

Playful: 'Okay but did you actually survive or just tell people you did?'
Sincere: 'That sounds like exactly the kind of trip that changes something in you — what did it feel like coming back to normal life after?'"

YOUR STYLE:
- 3-5 sentences total including the two options
- Talk like a smart friend, not a coach
- Be direct — name what you see in the conversation
- Casual English, no corporate speak

WHAT NOT TO DO:
- Never give vague advice like "be yourself" or "show interest"
- Never suggest anything manipulative or performative
- Never write an essay — get to the point
- NEVER use: wonderful, amazing, fantastic, incredible

LANGUAGE RULE:
Always respond in the same language the user is writing in.
If they write in Russian — respond in Russian.
If they switch languages — switch with them.
BUT: all internal analysis, profile updates, and JSON outputs are always in English regardless of conversation language."""


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
        user_msg_count = len([m for m in conversation_history if m["role"] == "user"])
        filled_count = 0
        context_note = f"\n\nConversation has {user_msg_count} user messages so far."
        if current_traits:
            existing = {k: v for k, v in current_traits.items() if v is not None}
            filled_count = len(existing)
            if existing:
                context_note += f"\nCurrent trait insights ({filled_count}/8 filled): {json.dumps(existing)}. Refine or rewrite them based on new evidence. Keep them concise."

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

        raw_readiness = data.get("profile_readiness", 0)
        try:
            readiness = int(raw_readiness)
        except (ValueError, TypeError):
            readiness = 0
        readiness = max(0, min(100, readiness))

        return {
            "thinking": data.get("thinking", ""),
            "traits": traits,
            "profile_updates": data.get("profile_updates", {}),
            "profile_readiness": readiness,
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

        readiness = min(n * 20, 100)

        return {
            "thinking": thinking_samples[min(n - 1, len(thinking_samples) - 1)] if n > 0 else "",
            "traits": traits,
            "profile_updates": updates,
            "profile_readiness": readiness,
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
