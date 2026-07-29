/**
 * StoryForge MongoDB Document Collection Schemas
 */

export interface IScriptSceneDoc {
  sceneNumber: number;
  heading: string;
  narrationText: string;
  visualPrompt: string;
  cameraDirection: string;
  estimatedDurationSeconds: number;
  speakerId?: string;
}

export interface IScriptRevisionDoc {
  id: string;
  projectId: string;
  storyId: string;
  version: number;
  scenes: IScriptSceneDoc[];
  totalWordCount: number;
  estimatedTotalDurationSeconds: number;
  llmModelUsed: string;
  createdAt: string;
}

export interface IStoryboardFrameDoc {
  frameId: string;
  sceneNumber: number;
  imagePrompt: string;
  videoPrompt?: string;
  generatedImageUrl?: string;
  generatedVideoUrl?: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  qualityScore?: number;
  notes?: string;
}

export interface IStoryboardDoc {
  id: string;
  projectId: string;
  scriptRevisionId: string;
  frames: IStoryboardFrameDoc[];
  createdAt: string;
  updatedAt: string;
}

export interface IWorkflowTrajectoryDoc {
  id: string;
  projectId: string;
  executionId: string;
  steps: {
    stepId: string;
    capabilityName: string;
    status: 'success' | 'failed' | 'running';
    inputData: Record<string, unknown>;
    outputData: Record<string, unknown>;
    errorTraceback?: string;
    startedAt: string;
    completedAt?: string;
  }[];
  createdAt: string;
}
