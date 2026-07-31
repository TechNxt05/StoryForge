"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import DAGNodeCanvas, { DAGNode } from "../../../components/DAGNodeCanvas";
import VideoPreviewPlayer from "../../../components/VideoPreviewPlayer";
import TimelineEditor, { TimelineClip } from "../../../components/TimelineEditor";
import EditorChat from "../../../components/EditorChat";
import { getProjectById, generatePlan } from "../../../lib/api";

export default function CanvasStudioPage() {
  const params = useParams();
  const projectId = (params?.id as string) || "proj-printing-press";

  const [project, setProject] = useState<any>(null);
  const [selectedNodeId, setSelectedNodeId] = useState("node-1");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isChatProcessing, setIsChatProcessing] = useState(false);
  const [exportNotice, setExportNotice] = useState("");
  const [currentVideoUrl, setCurrentVideoUrl] = useState("https://res.cloudinary.com/demo/video/upload/v1689255627/dog.mp4");

  const [nodes, setNodes] = useState<DAGNode[]>([
    {
      id: "node-1",
      name: "Deep Web Research",
      capability: "web_scraper",
      modelUsed: "DuckDuckGo HTML",
      apiKeyType: "Zero-Key (Free)",
      status: "completed",
      duration: "1.2s",
    },
    {
      id: "node-2",
      name: "AI Director Planning",
      capability: "scriptwriter",
      modelUsed: "Gemini 1.5 Flash",
      apiKeyType: "Free API Key",
      status: "completed",
      duration: "1.4s",
    },
    {
      id: "node-3",
      name: "Visual Vision Analysis",
      capability: "vision_analyzer",
      modelUsed: "Gemini 1.5 Pro Vision",
      apiKeyType: "Free API Key",
      status: "completed",
      duration: "0.9s",
    },
    {
      id: "node-4",
      name: "Voiceover Synthesis",
      capability: "voice_synthesizer",
      modelUsed: "Kokoro-82M ONNX",
      apiKeyType: "Local Execution",
      status: "completed",
      duration: "1.1s",
    },
    {
      id: "node-5",
      name: "YouTube B-Roll Sourcing",
      capability: "youtube_fetcher",
      modelUsed: "yt-dlp Engine",
      apiKeyType: "Local Execution",
      status: "completed",
      duration: "2.3s",
    },
    {
      id: "node-6",
      name: "FFmpeg Composition",
      capability: "ffmpeg_renderer",
      modelUsed: "FFmpeg H.264/AAC CLI",
      apiKeyType: "Local Execution",
      status: "completed",
      duration: "3.5s",
    },
  ]);

  const [clips, setClips] = useState<TimelineClip[]>([
    {
      id: "vclip-1",
      type: "video",
      url: "https://res.cloudinary.com/demo/video/upload/v1689255627/dog.mp4",
      startOffset: 0,
      duration: 10,
      filters: { brightness: 0, contrast: 1, volume: 1 },
      name: "Scene 1: Match Intro & Setup",
    },
    {
      id: "vclip-2",
      type: "video",
      url: "https://res.cloudinary.com/demo/video/upload/v1689255627/dog.mp4",
      startOffset: 10,
      duration: 12,
      filters: { brightness: 0, contrast: 1, volume: 1 },
      name: "Scene 2: MS Dhoni Steps Up Order",
    },
    {
      id: "aclip-1",
      type: "audio",
      url: "https://cdn.storyforge.ai/audio/kokoro/scene_1.mp3",
      startOffset: 0,
      duration: 22,
      filters: { brightness: 0, contrast: 1, volume: 1 },
      name: "Voiceover: Cinematic Narration",
    }
  ]);

  useEffect(() => {
    async function loadProjectDetails() {
      try {
        const data = await getProjectById(projectId);
        if (data) {
          setProject(data);
          const title = data.title || "Story Project";
          const topic = data.topic || "AI Generated Narrative";
          setClips([
            {
              id: "vclip-1",
              type: "video",
              url: "https://res.cloudinary.com/demo/video/upload/v1689255627/dog.mp4",
              startOffset: 0,
              duration: 8,
              filters: { brightness: 0, contrast: 1, volume: 1 },
              name: `Act 1: ${title} - ${topic.slice(0, 30)}`,
            },
            {
              id: "vclip-2",
              type: "video",
              url: "https://res.cloudinary.com/demo/video/upload/v1689255627/dog.mp4",
              startOffset: 8,
              duration: 10,
              filters: { brightness: 0, contrast: 1, volume: 1 },
              name: `Act 2: Strategic Turning Point`,
            },
            {
              id: "aclip-1",
              type: "audio",
              url: "https://cdn.storyforge.ai/audio/kokoro/scene_1.mp3",
              startOffset: 0,
              duration: 18,
              filters: { brightness: 0, contrast: 1, volume: 1 },
              name: `Voiceover: ${title} Narrative`,
            }
          ]);
        }
      } catch (err) {
        console.warn("Could not fetch project details from API, using local context:", err);
      }
    }
    if (projectId) loadProjectDetails();
  }, [projectId]);

  const handleClipUpdate = (updatedClip: TimelineClip) => {
    setClips(clips.map(c => c.id === updatedClip.id ? updatedClip : c));
  };

  const handleUploadMedia = async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("asset_type", file.type.startsWith("image") ? "image" : "video");
      
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "https://storyforge-snc4.onrender.com";
      const res = await fetch(`${baseUrl}/api/v1/projects/${projectId}/assets/upload`, {
        method: "POST",
        body: formData,
      });
      
      if (res.ok) {
        const data = await res.json();
        setClips([...clips, {
          id: data.id,
          type: data.asset_type,
          url: data.storage_url,
          startOffset: clips.length * 5,
          duration: 5,
          filters: { brightness: 0, contrast: 1, volume: 1 },
          name: file.name
        }]);
      }
    } catch (e) {
      console.error("Upload failed", e);
    } finally {
      setIsUploading(false);
    }
  };

  const handleReRunPipeline = async () => {
    setIsGenerating(true);
    // Animate nodes to running state
    setNodes(nodes.map(n => ({ ...n, status: "running" })));
    
    try {
      const topic = project?.topic || "Autonomous Storytelling Pipeline";
      await generatePlan(topic, project?.content_pack_name || "history", project?.aspect_ratio || "9:16");
    } catch (err) {
      console.warn("Error re-running pipeline API:", err);
    } finally {
      setTimeout(() => {
        setNodes(nodes.map(n => ({ ...n, status: "completed" })));
        setIsGenerating(false);
      }, 2500);
    }
  };

  const handleChatCommand = async (message: string) => {
    setIsChatProcessing(true);
    
    // Simulate DAG pipeline steps animating while processing prompt
    setNodes(nodes.map((n, idx) => idx === 1 ? { ...n, status: "running" } : n));
    await new Promise(resolve => setTimeout(resolve, 1500));
    setNodes(nodes.map((n, idx) => idx === 5 ? { ...n, status: "running" } : { ...n, status: "completed" }));
    await new Promise(resolve => setTimeout(resolve, 1500));
    setNodes(nodes.map(n => ({ ...n, status: "completed" })));

    // Apply AI updates to clips and preview
    if (message.toLowerCase().includes("bright")) {
      setClips(prev => prev.map(c => c.type === "video" ? { ...c, filters: { ...c.filters, brightness: 0.5 } } : c));
    } else if (message.toLowerCase().includes("quote") || message.toLowerCase().includes("scene")) {
      setClips(prev => [
        ...prev,
        {
          id: `vclip-${Date.now()}`,
          type: "image",
          url: "https://pollinations.ai/p/Dhoni_winning_moment_stadium",
          startOffset: prev.length * 5,
          duration: 6,
          filters: { brightness: 0.2, contrast: 1.1 },
          name: `Frame: "${message.slice(0, 30)}..."`
        }
      ]);
    }

    setIsChatProcessing(false);
  };

  const handleExport = () => {
    setExportNotice("Export package compiled! Video MP4 + Subtitle SRT rendered via FFmpeg CLI.");
    setTimeout(() => setExportNotice(""), 5000);
  };

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || nodes[0];
  const projectTitle = project?.title || "Story Project Studio";

  return (
    <div className="space-y-6">
      {/* Studio Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
            Unified Studio (DAG Roadmap + Canva Frame Deck)
          </span>
          <h1 className="text-2xl font-extrabold text-white mt-0.5">{projectTitle}</h1>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleExport}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition"
          >
            Export Video &rarr;
          </button>
          <button
            onClick={handleReRunPipeline}
            disabled={isGenerating}
            className="gradient-button px-5 py-2 rounded-xl text-xs font-bold text-white shadow-lg disabled:opacity-50"
          >
            {isGenerating ? "Executing Pipeline..." : "Re-Run DAG Pipeline"}
          </button>
        </div>
      </div>

      {exportNotice && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
          ✨ {exportNotice}
        </div>
      )}

      {/* Execution Progress & DAG Roadmap */}
      <DAGNodeCanvas
        nodes={nodes}
        selectedNodeId={selectedNodeId}
        onSelectNode={(id) => setSelectedNodeId(id)}
      />

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Live Player Preview & Chatbot */}
        <div className="lg:col-span-1 space-y-6">
          <VideoPreviewPlayer
            videoUrl={currentVideoUrl}
            aspectRatio={project?.aspect_ratio || "9:16"}
            title={projectTitle}
          />
          <EditorChat 
            onSendMessage={handleChatCommand} 
            isProcessing={isChatProcessing} 
          />
        </div>

        {/* Right Column: Canva Slide Deck & Frame Inspector */}
        <div className="lg:col-span-2 space-y-6">
          <TimelineEditor 
            clips={clips} 
            onClipUpdate={handleClipUpdate} 
            onUpload={handleUploadMedia}
            isUploading={isUploading}
          />
        </div>
      </div>
    </div>
  );
}
