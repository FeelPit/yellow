"""
Seed script to create fake users with profiles for testing matching.
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.user import User
from app.models.session import Session
from app.models.profile import Profile
from app.services.auth_service import AuthService


SAMPLE_PROFILES = [
    {
        "email": "alice@example.com",
        "username": "alice",
        "password": "password123",
        "profile": {
            "age": 28, "gender": "female", "looking_for": "male",
            "communication_style": "Direct and honest communicator who values clarity and openness in conversations.",
            "attachment_style": "Secure attachment with healthy boundaries and emotional availability.",
            "partner_preferences": "Looking for someone emotionally intelligent, ambitious, and values personal growth.",
            "values": "Values authenticity, meaningful connections, and continuous self-improvement.",
        },
        "traits": {
            "openness": "Highly open to new experiences, willing to be vulnerable early.",
            "emotional_style": "Expresses emotions clearly and directly, good self-awareness.",
            "social_energy": "Balanced — enjoys socializing but values quiet alone time too.",
            "conflict_approach": "Addresses issues head-on with empathy and clarity.",
            "love_language": "Quality time and words of affirmation.",
            "lifestyle": "Career-driven with space for personal passions.",
            "relationship_values": "Prioritizes growth, trust, and intellectual partnership.",
            "humor_and_play": "Witty and playful, uses humor to bond.",
        },
    },
    {
        "email": "bob@example.com",
        "username": "bob",
        "password": "password123",
        "profile": {
            "age": 32, "gender": "male", "looking_for": "female",
            "communication_style": "Thoughtful listener who prefers deep conversations over small talk.",
            "attachment_style": "Secure with slight anxious tendencies, working on emotional regulation.",
            "partner_preferences": "Seeks someone patient, understanding, and values emotional connection.",
            "values": "Values empathy, authenticity, and building strong emotional bonds.",
        },
        "traits": {
            "openness": "Opens up gradually once trust is established.",
            "emotional_style": "Deeply reflective, processes emotions internally before sharing.",
            "social_energy": "Introverted, prefers small groups and one-on-one conversations.",
            "conflict_approach": "Tends to withdraw initially but returns to resolve with care.",
            "love_language": "Acts of service and physical touch.",
            "lifestyle": "Steady routines, values stability and predictability.",
            "relationship_values": "Seeks emotional safety and consistent presence.",
            "humor_and_play": "Dry humor, appreciates subtlety.",
        },
    },
    {
        "email": "carol@example.com",
        "username": "carol",
        "password": "password123",
        "profile": {
            "age": 26, "gender": "female", "looking_for": "male",
            "communication_style": "Warm and expressive, enjoys sharing feelings and experiences openly.",
            "attachment_style": "Secure attachment, comfortable with intimacy and independence.",
            "partner_preferences": "Looking for someone adventurous, spontaneous, and emotionally available.",
            "values": "Values adventure, spontaneity, and living life to the fullest.",
        },
        "traits": {
            "openness": "Thrives on novelty, always eager to try new things.",
            "emotional_style": "Wears heart on sleeve, expressive and animated.",
            "social_energy": "Extroverted, energized by social settings and new people.",
            "conflict_approach": "Confronts issues immediately, prefers quick resolution.",
            "love_language": "Physical touch and quality time.",
            "lifestyle": "Active, outdoorsy, values spontaneous plans over structure.",
            "relationship_values": "Values passion, shared experiences, and emotional intensity.",
            "humor_and_play": "Energetic, loves teasing and laughter.",
        },
    },
    {
        "email": "david@example.com",
        "username": "david",
        "password": "password123",
        "profile": {
            "age": 35, "gender": "male", "looking_for": "female",
            "communication_style": "Analytical and precise, prefers structured conversations with clear outcomes.",
            "attachment_style": "Avoidant-leaning but working towards secure attachment through therapy.",
            "partner_preferences": "Seeks someone independent, intellectually stimulating, and respects personal space.",
            "values": "Values independence, intellectual growth, and personal development.",
        },
        "traits": {
            "openness": "Open to ideas but guarded with personal emotions.",
            "emotional_style": "Logical processor, prefers rational discussion over emotional venting.",
            "social_energy": "Self-sufficient, enjoys solitude and deep focus work.",
            "conflict_approach": "Analytical, seeks to understand the root cause before responding.",
            "love_language": "Words of affirmation and gifts that show thoughtfulness.",
            "lifestyle": "Structured days, intellectual hobbies, values efficiency.",
            "relationship_values": "Needs autonomy within partnership, values mutual respect.",
            "humor_and_play": "Cerebral humor, enjoys wordplay and clever observations.",
        },
    },
    {
        "email": "emma@example.com",
        "username": "emma",
        "password": "password123",
        "profile": {
            "age": 29, "gender": "female", "looking_for": "male",
            "communication_style": "Empathetic and supportive, creates safe space for vulnerable conversations.",
            "attachment_style": "Secure attachment with strong emotional intelligence and self-awareness.",
            "partner_preferences": "Looking for someone kind, emotionally mature, and values deep connection.",
            "values": "Values kindness, emotional intelligence, and building meaningful relationships.",
        },
        "traits": {
            "openness": "Deeply open, invites vulnerability through warmth.",
            "emotional_style": "Highly empathetic, feels others' emotions naturally.",
            "social_energy": "Ambivert, adapts energy to the person and setting.",
            "conflict_approach": "Patient mediator, listens fully before offering perspective.",
            "love_language": "Words of affirmation and quality time.",
            "lifestyle": "Balanced pace, values wellness and personal growth.",
            "relationship_values": "Seeks deep emotional intimacy and mutual understanding.",
            "humor_and_play": "Gentle humor, loves inside jokes and shared stories.",
        },
    },
    {
        "email": "frank@example.com",
        "username": "frank",
        "password": "password123",
        "profile": {
            "age": 31, "gender": "male", "looking_for": "female",
            "communication_style": "Playful and humorous, uses wit to connect but can be serious when needed.",
            "attachment_style": "Secure with good balance between closeness and independence.",
            "partner_preferences": "Seeks someone with good sense of humor, easy-going, and values fun.",
            "values": "Values humor, spontaneity, and not taking life too seriously.",
        },
        "traits": {
            "openness": "Open and easy-going, shares freely in relaxed settings.",
            "emotional_style": "Defaults to humor but can access deeper emotions when needed.",
            "social_energy": "Social butterfly, draws energy from being around people.",
            "conflict_approach": "Uses humor to defuse tension, avoids unnecessary drama.",
            "love_language": "Quality time and physical affection.",
            "lifestyle": "Active social life, values experiences over possessions.",
            "relationship_values": "Wants a partner who feels like a best friend.",
            "humor_and_play": "Quick wit, loves banter and keeps things light.",
        },
    },
    {
        "email": "grace@example.com",
        "username": "grace",
        "password": "password123",
        "profile": {
            "age": 27, "gender": "female", "looking_for": "male",
            "communication_style": "Gentle and considerate, takes time to process before responding thoughtfully.",
            "attachment_style": "Secure but introverted, needs alone time to recharge.",
            "partner_preferences": "Looking for someone understanding, patient, and respects need for space.",
            "values": "Values peace, understanding, and maintaining healthy boundaries.",
        },
        "traits": {
            "openness": "Thoughtful and selective about what she shares, but deeply honest.",
            "emotional_style": "Quiet emotional depth, processes internally before expressing.",
            "social_energy": "Introverted, needs substantial alone time to feel balanced.",
            "conflict_approach": "Non-confrontational but firm once she's processed her feelings.",
            "love_language": "Acts of service and quiet presence.",
            "lifestyle": "Calm routines, enjoys reading, nature, and creative pursuits.",
            "relationship_values": "Needs space and patience, rewards it with deep loyalty.",
            "humor_and_play": "Understated humor, appreciates absurdity and quiet jokes.",
        },
    },
    {
        "email": "henry@example.com",
        "username": "henry",
        "password": "password123",
        "profile": {
            "age": 33, "gender": "male", "looking_for": "female",
            "communication_style": "Passionate and intense, expresses emotions strongly and authentically.",
            "attachment_style": "Anxious attachment, working on self-soothing and emotional regulation.",
            "partner_preferences": "Seeks someone reassuring, consistent, and values emotional intimacy.",
            "values": "Values passion, emotional depth, and intense connections.",
        },
        "traits": {
            "openness": "Wears heart on sleeve, shares feelings quickly and intensely.",
            "emotional_style": "Passionate and expressive, emotions run high and visibly.",
            "social_energy": "Moderate, needs a mix of social time and introspection.",
            "conflict_approach": "Emotionally reactive first, reflective later.",
            "love_language": "Physical touch and words of affirmation.",
            "lifestyle": "Creative pursuits, music, art, values aesthetic experiences.",
            "relationship_values": "Craves emotional intensity and deep reassurance.",
            "humor_and_play": "Passionate storyteller, animated and engaging.",
        },
    },
    {
        "email": "iris@example.com",
        "username": "iris",
        "password": "password123",
        "profile": {
            "age": 30, "gender": "female", "looking_for": "male",
            "communication_style": "Balanced communicator, adapts style based on situation and person.",
            "attachment_style": "Secure attachment with healthy relationship patterns.",
            "partner_preferences": "Looking for someone flexible, emotionally stable, and values balance.",
            "values": "Values balance, flexibility, and emotional stability.",
        },
        "traits": {
            "openness": "Moderately open, shares when the relationship feels safe.",
            "emotional_style": "Well-regulated, handles emotions with maturity.",
            "social_energy": "Ambivert, comfortable in most settings.",
            "conflict_approach": "Calm and measured, seeks compromise.",
            "love_language": "Quality time and shared activities.",
            "lifestyle": "Well-rounded, balances work, hobbies, and social life.",
            "relationship_values": "Seeks an equal partner, mutual support and respect.",
            "humor_and_play": "Warm humor, enjoys shared laughs over daily moments.",
        },
    },
    {
        "email": "jack@example.com",
        "username": "jack",
        "password": "password123",
        "profile": {
            "age": 36, "gender": "male", "looking_for": "female",
            "communication_style": "Direct and action-oriented, prefers practical solutions over lengthy discussions.",
            "attachment_style": "Dismissive-avoidant, values independence and self-reliance.",
            "partner_preferences": "Seeks someone independent, low-maintenance, and respects autonomy.",
            "values": "Values independence, self-reliance, and personal freedom.",
        },
        "traits": {
            "openness": "Reserved, shares personal details only when necessary.",
            "emotional_style": "Stoic exterior, processes emotions privately.",
            "social_energy": "Independent, enjoys solo activities and small-group settings.",
            "conflict_approach": "Avoids unnecessary conflict, pragmatic when engaged.",
            "love_language": "Acts of service and practical support.",
            "lifestyle": "Self-directed, fitness-oriented, values freedom and efficiency.",
            "relationship_values": "Needs significant independence within a partnership.",
            "humor_and_play": "Deadpan humor, appreciates sarcasm and understatement.",
        },
    },
    {
        "email": "kate@example.com",
        "username": "kate",
        "password": "password123",
        "profile": {
            "age": 28, "gender": "female", "looking_for": "male",
            "communication_style": "Nurturing and supportive, naturally creates warm and safe conversations.",
            "attachment_style": "Secure attachment with strong caregiving tendencies.",
            "partner_preferences": "Looking for someone who appreciates care, values family, and emotional warmth.",
            "values": "Values family, care, and creating warm loving relationships.",
        },
        "traits": {
            "openness": "Open and inviting, makes others feel comfortable sharing.",
            "emotional_style": "Warm and nurturing, feels deeply for those she cares about.",
            "social_energy": "Moderate, energized by close relationships over large gatherings.",
            "conflict_approach": "Seeks harmony, sometimes avoids difficult topics to keep peace.",
            "love_language": "Acts of service and physical affection.",
            "lifestyle": "Home-oriented, loves cooking, family gatherings, cozy routines.",
            "relationship_values": "Prioritizes emotional warmth, consistency, and building a home together.",
            "humor_and_play": "Gentle, nurturing humor, laughs easily.",
        },
    },
    {
        "email": "leo@example.com",
        "username": "leo",
        "password": "password123",
        "profile": {
            "age": 34, "gender": "male", "looking_for": "female",
            "communication_style": "Confident and assertive, speaks mind clearly while respecting others.",
            "attachment_style": "Secure attachment with strong sense of self.",
            "partner_preferences": "Seeks someone confident, ambitious, and values mutual growth.",
            "values": "Values confidence, ambition, and mutual personal growth.",
        },
        "traits": {
            "openness": "Confident in sharing views, welcomes constructive challenge.",
            "emotional_style": "Grounded, handles emotions with composure and clarity.",
            "social_energy": "Extroverted leader, comfortable taking charge in group settings.",
            "conflict_approach": "Direct but respectful, seeks resolution through honest dialogue.",
            "love_language": "Words of affirmation and quality time.",
            "lifestyle": "Ambitious, fitness-focused, values achievement and discipline.",
            "relationship_values": "Wants an equal partner who challenges and inspires growth.",
            "humor_and_play": "Confident humor, enjoys good-natured competition.",
        },
    },
    {
        "email": "maya@example.com",
        "username": "maya",
        "password": "password123",
        "profile": {
            "age": 26, "gender": "female", "looking_for": "any",
            "communication_style": "Creative and expressive, uses metaphors and stories to communicate.",
            "attachment_style": "Secure with artistic temperament, values emotional expression.",
            "partner_preferences": "Looking for someone creative, open-minded, and appreciates art.",
            "values": "Values creativity, self-expression, and artistic pursuits.",
        },
        "traits": {
            "openness": "Extremely open, draws from art and emotion to express herself.",
            "emotional_style": "Rich emotional landscape, expresses through creative outlets.",
            "social_energy": "Thrives in creative and artistic communities.",
            "conflict_approach": "Processes conflict through journaling and creative expression.",
            "love_language": "Gift-giving and creative acts of affection.",
            "lifestyle": "Art-centric, values beauty, museums, music, and self-expression.",
            "relationship_values": "Seeks a creative partner who appreciates beauty and depth.",
            "humor_and_play": "Quirky and imaginative, loves absurdist humor.",
        },
    },
    {
        "email": "noah@example.com",
        "username": "noah",
        "password": "password123",
        "profile": {
            "age": 37, "gender": "male", "looking_for": "female",
            "communication_style": "Calm and measured, thinks before speaking and values thoughtful dialogue.",
            "attachment_style": "Secure attachment with philosophical mindset.",
            "partner_preferences": "Seeks someone intellectually curious, calm, and values deep thinking.",
            "values": "Values wisdom, intellectual curiosity, and philosophical discussions.",
        },
        "traits": {
            "openness": "Intellectually open, emotionally selective about what he reveals.",
            "emotional_style": "Calm and contemplative, processes through reflection.",
            "social_energy": "Prefers meaningful conversations over social chatter.",
            "conflict_approach": "Philosophical, seeks to understand before judging.",
            "love_language": "Deep conversation and shared intellectual exploration.",
            "lifestyle": "Reads extensively, enjoys nature walks and quiet evenings.",
            "relationship_values": "Seeks intellectual companionship and mutual curiosity.",
            "humor_and_play": "Thoughtful wit, enjoys irony and intellectual humor.",
        },
    },
    {
        "email": "olivia@example.com",
        "username": "olivia",
        "password": "password123",
        "profile": {
            "age": 25, "gender": "female", "looking_for": "male",
            "communication_style": "Enthusiastic and energetic, brings positive energy to conversations.",
            "attachment_style": "Secure attachment with extroverted personality.",
            "partner_preferences": "Looking for someone energetic, social, and values shared experiences.",
            "values": "Values social connection, shared experiences, and positive energy.",
        },
        "traits": {
            "openness": "Very open, shares experiences and stories freely and enthusiastically.",
            "emotional_style": "Upbeat and expressive, wears emotions visibly.",
            "social_energy": "Highly extroverted, thrives in large groups and new environments.",
            "conflict_approach": "Optimistic approach, tries to find the positive in disagreements.",
            "love_language": "Quality time and shared adventures.",
            "lifestyle": "Active social calendar, fitness, travel, always planning something fun.",
            "relationship_values": "Wants a partner in adventure, someone to explore life with.",
            "humor_and_play": "High energy, loves pranks, memes, and spontaneous fun.",
        },
    },
]


def seed_database():
    """Create fake users with profiles."""
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        auth_service = AuthService(db)
        created_count = 0

        for user_data in SAMPLE_PROFILES:
            existing_user = auth_service.get_user_by_email(user_data["email"])
            if existing_user:
                print(f"  User {user_data['username']} already exists, skipping...")
                continue

            user = auth_service.create_user(
                email=user_data["email"],
                username=user_data["username"],
                password=user_data["password"]
            )

            session = Session(user_id=user.id)
            db.add(session)
            db.commit()
            db.refresh(session)

            profile = Profile(
                session_id=session.id,
                user_id=user.id,
                age=user_data["profile"].get("age"),
                gender=user_data["profile"].get("gender"),
                looking_for=user_data["profile"].get("looking_for"),
                communication_style=user_data["profile"]["communication_style"],
                attachment_style=user_data["profile"]["attachment_style"],
                partner_preferences=user_data["profile"]["partner_preferences"],
                values=user_data["profile"]["values"],
                metrics=user_data.get("traits", {}),
                raw_data=user_data["profile"],
            )
            db.add(profile)
            db.commit()

            created_count += 1
            print(f"  Created user: {user_data['username']}")

        print(f"\n  Seed completed! Created {created_count} users with profiles.")

    except Exception as e:
        print(f"  Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
