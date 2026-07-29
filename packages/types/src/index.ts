/**
 * StoryForge Shared TypeScript Type Definitions
 */

export type ProjectStatus = 'draft' | 'planning' | 'generating' | 'rendering' | 'completed' | 'failed';
export type AspectRatio = '9:16' | '16:9' | '1:1';

export interface IProject {
  id: string;
  workspaceId: string;
  creatorId: string;
  title: string;
  topic: string;
  contentPackName: string;
  aspectRatio: AspectRatio;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
}

export interface IDAGNode {
  id: string;
  name: string;
  capability: string;
  status: 'completed' | 'running' | 'pending' | 'failed';
  duration: string;
}
