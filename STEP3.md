# Step 3: Matching System

## Overview

Implemented a simple matching system that shows up to 5 daily candidates based on profile compatibility.

## Features

### Backend

1. **Profile-User Link**
   - Added `user_id` to profiles table
   - Profiles now linked to both session and user
   - Migration handles existing data

2. **Matching Service**
   - Simple deterministic matching algorithm
   - Compares profiles based on:
     - Values (30% weight)
     - Partner preferences (30% weight)
     - Communication style (20% weight)
     - Attachment style (20% weight)
   - Returns match score (0.0-1.0) and explanation

3. **New Endpoints**
   - `GET /api/v1/users/{user_id}/profile` - Get user's profile
   - `GET /api/v1/users/{user_id}/matches` - Get matches (max 5)

4. **Seed Data**
   - Script creates 15 fake users with diverse profiles
   - Each user has complete profile data
   - Run: `cd apps/api && python seed_data.py`

### Frontend

1. **Matches Page** (`/matches`)
   - Displays up to 5 matches
   - Shows match score and explanation
   - Displays profile traits
   - "Start Chat" button (placeholder)

2. **Navigation**
   - Link to matches appears when profile is ready
   - Easy navigation between chat and matches

## API Endpoints

### GET /api/v1/users/{user_id}/profile

Get profile for a specific user.

**Response:**
```json
{
  "communication_style": "Direct and honest...",
  "attachment_style": "Secure attachment...",
  "partner_preferences": "Looking for...",
  "values": "Values authenticity..."
}
```

### GET /api/v1/users/{user_id}/matches

Get matches for a user (requires authentication).

**Query Parameters:**
- `limit` (optional): Max results, default 5

**Response:**
```json
{
  "matches": [
    {
      "user_id": "uuid",
      "username": "alice",
      "profile": {
        "communication_style": "...",
        "attachment_style": "...",
        "partner_preferences": "...",
        "values": "..."
      },
      "match_score": 0.85,
      "match_explanation": "You both value authenticity..."
    }
  ],
  "total": 5
}
```

## Matching Algorithm

### Score Calculation

```python
score = (
    values_similarity * 0.3 +
    preferences_similarity * 0.3 +
    communication_similarity * 0.2 +
    attachment_similarity * 0.2
)
```

### Text Similarity

Uses Jaccard similarity on meaningful words (4+ characters):
- Extracts words from both texts
- Calculates intersection / union
- Returns 0.0 to 1.0

### Explanation Generation

Based on high-scoring dimensions:
- "shared core values"
- "similar partner preferences"
- "compatible communication styles"
- "similar attachment patterns"

## Database Schema

### profiles table (updated)

```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- NEW
    communication_style TEXT,
    attachment_style TEXT,
    partner_preferences TEXT,
    values TEXT,
    raw_data JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX ix_profiles_user_id ON profiles(user_id);
```

## Testing

### Backend Tests (10 new tests)

```bash
cd apps/api
pytest tests/test_matches.py -v
```

Tests cover:
- ✅ Get user profile
- ✅ Profile not found
- ✅ Matches require auth
- ✅ Empty matches when no profile
- ✅ Get matches success
- ✅ Excludes self from matches
- ✅ Max 5 results
- ✅ Only own matches
- ✅ Match explanation exists
- ✅ Match score validation

### Frontend Tests (10 new tests)

```bash
cd apps/web
npm test tests/pages/matches.test.tsx
```

Tests cover:
- ✅ Redirects if not authenticated
- ✅ Shows loading state
- ✅ Displays matches
- ✅ Shows match scores
- ✅ Shows explanations
- ✅ Shows profile info
- ✅ Shows chat buttons
- ✅ Empty state
- ✅ Error handling
- ✅ User info display

## Seed Data

### Running the Seed Script

```bash
cd apps/api
python seed_data.py
```

### Sample Users

Creates 15 users with diverse profiles:
- alice, bob, carol, david, emma
- frank, grace, henry, iris, jack
- kate, leo, maya, noah, olivia

Each has:
- Unique communication style
- Attachment type
- Partner preferences
- Core values

All users have password: `password123`

## Usage

### 1. Apply Migration

```bash
cd apps/api
alembic upgrade head
```

### 2. Seed Data

```bash
python seed_data.py
```

### 3. Start Services

```bash
cd ../..
make up
```

### 4. Test Flow

1. Register/login at http://localhost:3000/assistant
2. Complete profile (answer 5+ questions)
3. Click "Смотреть совпадения"
4. View your matches at http://localhost:3000/matches

## File Structure

```
apps/
├── api/
│   ├── alembic/versions/
│   │   └── 006_add_user_id_to_profiles.py
│   ├── app/
│   │   ├── models/
│   │   │   └── profile.py (updated)
│   │   ├── schemas/
│   │   │   └── matches.py (new)
│   │   ├── services/
│   │   │   ├── matching_service.py (new)
│   │   │   └── profile_service.py (updated)
│   │   └── routers/
│   │       └── matches.py (new)
│   ├── tests/
│   │   └── test_matches.py (new)
│   └── seed_data.py (new)
└── web/
    ├── src/
    │   ├── app/
    │   │   ├── assistant/page.tsx (updated)
    │   │   └── matches/page.tsx (new)
    │   └── lib/
    │       └── api.ts (updated)
    └── tests/pages/
        └── matches.test.tsx (new)
```

## Statistics

- **Backend**: 10 new tests (41 total)
- **Frontend**: 10 new tests (36 total)
- **Total**: 77 tests ✅
- **New files**: 6
- **Updated files**: 6
- **Lines of code**: ~1,200

## Next Steps (Not in Step 3)

Future enhancements could include:
- AI-powered matching with embeddings
- Real-time chat functionality
- Match preferences/filters
- Like/pass actions
- Match history
- Notifications

## Notes

- Matching is deterministic (same results each time)
- No AI/ML used yet (simple text similarity)
- Authentication required for all match endpoints
- Users can only see their own matches
- Profiles must be complete to appear in matches
