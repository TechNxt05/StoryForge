/**
 * StoryForge Redis Cache & Key Helpers
 */

export const REDIS_KEYS = {
  userSession: (userId: string) => `session:user:${userId}`,
  rateLimit: (ipOrUser: string) => `ratelimit:${ipOrUser}`,
  projectState: (projectId: string) => `project:state:${projectId}`,
  taskProgress: (taskId: string) => `task:progress:${taskId}`,
  contentPackCache: (packName: string) => `cache:pack:${packName}`,
};

export interface ITaskProgressCache {
  taskId: string;
  projectId: string;
  stepName: string;
  percentComplete: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  message: string;
  updatedAt: string;
}
