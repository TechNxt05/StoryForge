"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import VideoPreviewPlayer from "../../../components/VideoPreviewPlayer";
import TimelineEditor, { TimelineClip } from "../../../components/TimelineEditor";
import EditorChat from "../../../components/EditorChat";
import { getProjectById } from "../../../lib/api";

export default function CanvasStudioPage() {
  const params = useParams();
  const projectId = (params?.id as string) || "proj-printing-press";

  const [project, setProject] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isChatProcessing, setIsChatProcessing] = useState(false);
  const [exportNotice, setExportNotice] = useState("");

  const [clips, setClips] = useState<TimelineClip[]>([
    {
      id: "vclip-1",
      type: "video",
      url: "https://res.cloudinary.com/demo/video/upload/dog.mp4",
      startOffset: 0,
      duration: 10,
      filters: { brightness: 0, contrast: 1, volume: 1 },
      name: "Scene 1: Introduction",
    },
    {
      id: "aclip-1",
      type: "audio",
      url: "https://cdn.storyforge.ai/audio/kokoro/scene_1.mp3",
      startOffset: 0,
      duration: 10,
      filters: { brightness: 0, contrast: 1, volume: 1 },
      name: "Voiceover: Hook",
    }
  ]);

  useEffect(() => {
    async function loadProjectDetails() {
      try {
        const data = await getProjectById(projectId);
        if (data) setProject(data);
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
          startOffset: clips.length * 2,
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

  const handleChatCommand = async (message: string) => {
    setIsChatProcessing(true);
    // In a real implementation, we send this to the iterative refinement API
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulate an AI tweaking the brightness based on the prompt
    if (message.toLowerCase().includes("bright")) {
      setClips(prev => prev.map(c => c.type === "video" ? { ...c, filters: { ...c.filters, brightness: 0.5 } } : c));
    }
    setIsChatProcessing(false);
  };

  const handleExport = () => {
    setExportNotice("Export package compiling... Generating FFmpeg Filtergraph from Timeline.");
    setTimeout(() => setExportNotice(""), 5000);
  };

  const projectTitle = project?.title || "Story Project Studio";

  return (
    <div className="space-y-6">
      {/* Studio Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
            Mini Canva Studio Editor
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
        </div>
      </div>

      {exportNotice && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
          ✨ {exportNotice}
        </div>
      )}

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Editor Chat & Player */}
        <div className="lg:col-span-1 space-y-6">
          <VideoPreviewPlayer
            aspectRatio={project?.aspect_ratio || "9:16"}
            title={projectTitle}
          />
          <EditorChat 
            onSendMessage={handleChatCommand} 
            isProcessing={isChatProcessing} 
          />
        </div>

        {/* Right Column: Mini Canva Timeline Editor */}
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
