export interface User {
  id: number;
  email: string;
  handle: string;
  display_name: string;
  bio: string;
  avatar?: string | null;
  banner?: string | null;
  reputation_score: number;
  created_at: string;
  is_staff: boolean;
  is_superuser: boolean;
  profile?: {
    location: string;
    website: string;
    pronouns: string;
    updated_at: string;
  };
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials {
  email: string;
  handle: string;
  password: string;
  display_name?: string;
}

export interface AuthResponse {
  token: string;
}

export type UserRole = 'guest' | 'user' | 'staff' | 'admin';

export function getUserRole(user: User | null): UserRole {
  if (!user) return 'guest';
  if (user.is_superuser) return 'admin';
  if (user.is_staff) return 'staff';
  return 'user';
}