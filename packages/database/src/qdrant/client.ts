/**
 * StoryForge Qdrant Vector Search Schemas & Constants
 */

export const QDRANT_COLLECTIONS = {
  STORY_KNOWLEDGE: 'story_knowledge',
  SCRIPT_CHUNKS: 'script_chunks',
  CONTENT_PACK_EMBEDDINGS: 'content_pack_embeddings',
};

export interface IVectorPayload {
  projectId?: string;
  packName?: string;
  sourceType: 'document' | 'script' | 'web_research';
  textChunk: string;
  metadata: Record<string, unknown>;
  createdAt: string;
}

export interface IQdrantSearchResult {
  id: string;
  score: number;
  payload: IVectorPayload;
}
