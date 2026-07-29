/**
 * StoryForge PostgreSQL Schema & Entity Definitions
 */

export interface IUserEntity {
  id: string;
  email: string;
  hashedPassword?: string;
  fullName: string;
  avatarUrl?: string;
  role: 'admin' | 'creator' | 'viewer';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface IWorkspaceEntity {
  id: string;
  name: string;
  slug: string;
  ownerId: string;
  settingsJson?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface IProjectEntity {
  id: string;
  workspaceId: string;
  creatorId: string;
  title: string;
  topic: string;
  contentPackName: string;
  status: 'draft' | 'planning' | 'generating' | 'rendering' | 'completed' | 'failed';
  metadataJson?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface IStoryEntity {
  id: string;
  projectId: string;
  title: string;
  synopsis: string;
  durationTargetSeconds: number;
  aspectRatio: '9:16' | '16:9' | '1:1';
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface IAssetEntity {
  id: string;
  projectId: string;
  assetType: 'image' | 'video' | 'audio' | 'subtitle' | 'document';
  providerName: string;
  storageUrl: string;
  fileSizeBytes: number;
  mimeType: string;
  metadataJson?: Record<string, unknown>;
  createdAt: string;
}

export interface ISubscriptionEntity {
  id: string;
  workspaceId: string;
  planTier: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'canceled' | 'past_due';
  monthlyTokenQuota: number;
  tokensUsedCurrentPeriod: number;
  currentPeriodStart: string;
  currentPeriodEnd: string;
}

export interface IAuditLogEntity {
  id: string;
  workspaceId: string;
  userId: string;
  action: string;
  resourceType: string;
  resourceId: string;
  detailsJson?: Record<string, unknown>;
  createdAt: string;
}
