const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface UserRegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface SessionCreateResponse {
  session_id: string;
  status: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  thinking?: string | null;
  created_at: string;
}

export interface StartConversationResponse {
  messages: Message[];
}

export interface ProfileTraits {
  openness: string | null;
  emotional_style: string | null;
  social_energy: string | null;
  conflict_approach: string | null;
  love_language: string | null;
  lifestyle: string | null;
  relationship_values: string | null;
  humor_and_play: string | null;
}

export interface ProfileSnapshot {
  age: number | null;
  gender: string | null;
  metrics: ProfileTraits | null;
  communication_style: string | null;
  attachment_style: string | null;
  partner_preferences: string | null;
  values: string | null;
}

export interface PhotoInfo {
  id: string;
  url: string;
  vibe_description: string | null;
  vibe_tags: string[] | null;
}

export interface ProfileViewData {
  age: number | null;
  gender: string | null;
  metrics: ProfileTraits | null;
  communication_style: string | null;
  attachment_style: string | null;
  partner_preferences: string | null;
  values: string | null;
  vibe_tags: string[] | null;
  photos: PhotoInfo[];
}

export interface PhotoResponse {
  id: string;
  user_id: string;
  filename: string;
  original_name: string;
  vibe_description: string | null;
  vibe_tags: string[] | null;
  order: number;
  created_at: string;
}

export interface PhotoUploadResponse {
  photo: PhotoResponse;
  message: string;
}

export interface SendMessageResponse {
  user_message: Message;
  assistant_message: Message;
  profile_ready: boolean;
  profile_snapshot: ProfileSnapshot | null;
  intent: string | null;
  profile_view: ProfileViewData | null;
}

export interface Profile {
  id: string;
  session_id: string;
  age: number | null;
  gender: string | null;
  looking_for: string | null;
  communication_style: string | null;
  attachment_style: string | null;
  partner_preferences: string | null;
  values: string | null;
  metrics: ProfileTraits | null;
  created_at: string;
  updated_at: string;
}

export interface MatchProfile {
  age: number | null;
  gender: string | null;
  communication_style: string | null;
  attachment_style: string | null;
  partner_preferences: string | null;
  values: string | null;
}

export interface FullUserProfile {
  id: string;
  session_id: string;
  age: number | null;
  gender: string | null;
  looking_for: string | null;
  communication_style: string | null;
  attachment_style: string | null;
  partner_preferences: string | null;
  values: string | null;
  metrics: ProfileTraits | null;
  vibe_tags: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface Match {
  user_id: string;
  username: string;
  profile: MatchProfile;
  match_score: number;
  match_explanation: string;
}

export interface MatchListResponse {
  matches: Match[];
  total: number;
}

export interface LikeStatus {
  liked: boolean;
  mutual: boolean;
}

export interface AccessCheck {
  can_message: boolean;
  reason: string;
}

export interface SubscriptionStatus {
  active: boolean;
  plan: string | null;
  expires_at: string | null;
  free_chats_remaining: number;
}

export interface ConversationSummary {
  id: string;
  other_user_id: string;
  other_username: string;
  access_reason: string;
  last_message: string | null;
  last_message_at: string | null;
  created_at: string;
}

export interface DirectMessage {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  created_at: string;
}

export interface AdvisorResponse {
  answer: string;
}

export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  async register(data: UserRegisterRequest): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  }

  async login(data: UserLoginRequest): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async getCurrentUser(): Promise<UserResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/me`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to get current user');
    }

    return response.json();
  }

  async getOrCreateSession(): Promise<SessionCreateResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/assistant/session`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get session: ${response.statusText}`);
    }

    return response.json();
  }

  async createSession(): Promise<SessionCreateResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/assistant/session`, {
      method: 'POST',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }

    return response.json();
  }

  async startConversation(sessionId: string): Promise<StartConversationResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/assistant/session/${sessionId}/start`,
      {
        method: 'POST',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to start conversation: ${response.statusText}`);
    }

    return response.json();
  }

  async sendMessage(sessionId: string, content: string): Promise<SendMessageResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/assistant/session/${sessionId}/message`,
      {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ content }),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }

    return response.json();
  }

  async getMessages(sessionId: string): Promise<Message[]> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/assistant/session/${sessionId}/messages`,
      {
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get messages: ${response.statusText}`);
    }

    return response.json();
  }

  async getProfile(sessionId: string): Promise<Profile> {
    const response = await fetch(`${this.baseUrl}/api/v1/profile/${sessionId}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get profile: ${response.statusText}`);
    }

    return response.json();
  }

  async getMatches(userId: string): Promise<MatchListResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/users/${userId}/matches`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get matches: ${response.statusText}`);
    }

    return response.json();
  }

  async getUserProfile(userId: string): Promise<FullUserProfile> {
    const response = await fetch(`${this.baseUrl}/api/v1/users/${userId}/profile`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get user profile: ${response.statusText}`);
    }

    return response.json();
  }

  // --- Likes ---

  async likeUser(targetUserId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/likes/${targetUserId}`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Failed to like');
    }
  }

  async unlikeUser(targetUserId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/likes/${targetUserId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to unlike');
    }
  }

  async getLikeStatus(targetUserId: string): Promise<LikeStatus> {
    const response = await fetch(`${this.baseUrl}/api/v1/likes/${targetUserId}/status`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get like status');
    return response.json();
  }

  // --- Subscription ---

  async getSubscriptionStatus(): Promise<SubscriptionStatus> {
    const response = await fetch(`${this.baseUrl}/api/v1/subscription`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get subscription');
    return response.json();
  }

  // --- Conversations ---

  async checkAccess(targetUserId: string): Promise<AccessCheck> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations/${targetUserId}/access`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to check access');
    return response.json();
  }

  async startConversationWith(targetUserId: string): Promise<ConversationSummary> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations/${targetUserId}`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Cannot start conversation');
    }
    return response.json();
  }

  async listConversations(): Promise<ConversationSummary[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to list conversations');
    return response.json();
  }

  async getConversationMessages(conversationId: string): Promise<DirectMessage[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations/${conversationId}/messages`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get messages');
    return response.json();
  }

  async sendDirectMessage(conversationId: string, content: string): Promise<DirectMessage> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error('Failed to send message');
    return response.json();
  }

  async askAdvisor(conversationId: string, question: string): Promise<AdvisorResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations/${conversationId}/advisor`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ question }),
    });
    if (!response.ok) throw new Error('Failed to get advice');
    return response.json();
  }

  // --- Photos ---

  async uploadPhoto(file: File): Promise<PhotoUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const headers: HeadersInit = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}/api/v1/photos/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Failed to upload photo');
    }
    return response.json();
  }

  async getPhotos(): Promise<PhotoResponse[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/photos`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get photos');
    return response.json();
  }

  async getUserPhotos(userId: string): Promise<PhotoResponse[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/photos/user/${userId}`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to get user photos');
    return response.json();
  }

  async deletePhoto(photoId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/photos/${photoId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to delete photo');
  }

  getPhotoUrl(photoId: string): string {
    return `${this.baseUrl}/api/v1/photos/${photoId}/file`;
  }
}

export const apiClient = new ApiClient();
