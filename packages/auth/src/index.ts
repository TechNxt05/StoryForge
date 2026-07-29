/**
 * StoryForge Auth Package Shared Definitions & Utilities
 */

export interface IAuthUser {
  id: string;
  email: string;
  fullName: string;
  role: 'admin' | 'creator' | 'viewer';
}

export interface IAuthSession {
  user: IAuthUser;
  token: string;
  expiresAt: number;
}

export const AUTH_ROLES = {
  ADMIN: 'admin',
  CREATOR: 'creator',
  VIEWER: 'viewer',
} as const;
