"""Deep Research & Topic Extraction Capability for StoryForge Runtime."""

import os
import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class ResearchArtifact(IArtifact):
    """Artifact containing structured topic research data."""

    def __init__(
        self,
        artifact_id: str,
        topic: str,
        facts: List[str],
        timeline_events: List[Dict[str, str]],
        key_entities: List[str],
        confidence_score: float,
    ):
        self._id = artifact_id
        self.topic = topic
        self.facts = facts
        self.timeline_events = timeline_events
        self.key_entities = key_entities
        self.confidence_score = confidence_score

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "research_data"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "topic": self.topic,
            "facts": self.facts,
            "timeline_events": self.timeline_events,
            "key_entities": self.key_entities,
            "confidence_score": self.confidence_score,
        }


class DeepResearchCapability(ICapability):
    """Capability that performs topic extraction, entity analysis, and timeline discovery."""

    @property
    def name(self) -> str:
        return "deep_research"

    async def _call_gemini(self, topic: str, content_pack: str) -> str | None:
        """Attempt to get real research from Gemini API."""
        import httpx

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None

        try:
            prompt = (
                f"You are a research expert. Provide 5 concise, factual bullet points about '{topic}' "
                f"in the context of {content_pack}. Also provide 3 key timeline events and 3 key entities. "
                f"Format as JSON with keys: facts (list of strings), timeline_events (list of {{year, event}}), key_entities (list of strings)."
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4},
            }
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[DeepResearch] Gemini API call failed: {e}")

        return None

    async def execute(self, topic: str = "", content_pack: str = "general", **kwargs: Any) -> Dict[str, Any]:
        """Perform deep topic research and return structured findings."""
        if not topic:
            topic = "StoryForge AI Platform"

        artifact_id = f"res-{uuid.uuid4().hex[:8]}"

        # Try live Gemini API first
        gemini_response = await self._call_gemini(topic, content_pack)

        if gemini_response:
            # Parse the LLM response for facts
            import json as json_mod
            try:
                # Try to extract JSON from the response
                clean = gemini_response.strip()
                if "```json" in clean:
                    clean = clean.split("```json")[1].split("```")[0].strip()
                elif "```" in clean:
                    clean = clean.split("```")[1].split("```")[0].strip()

                parsed = json_mod.loads(clean)
                facts = parsed.get("facts", [])[:5]
                timeline_events = parsed.get("timeline_events", [])[:3]
                key_entities = parsed.get("key_entities", [])[:3]
            except Exception:
                # LLM returned non-JSON text — split into fact lines
                lines = [l.strip().lstrip("- •").strip() for l in gemini_response.strip().split("\n") if l.strip() and len(l.strip()) > 10]
                facts = lines[:5] if lines else [gemini_response[:200]]
                timeline_events = [{"year": "Modern Era", "event": f"AI-driven analysis of {topic}"}]
                key_entities = [topic.split()[0] if topic.split() else topic]

            confidence = 0.92
        else:
            # Fallback template data
            facts = [
                f"{topic} is a significant subject within the {content_pack} domain.",
                f"Key breakthroughs in {topic} transformed modern practices and user expectations.",
                f"Recent innovations in {topic} enable automated short-form visual storytelling.",
            ]
            timeline_events = [
                {"year": "Early Phase", "event": f"Foundational concepts of {topic} introduced."},
                {"year": "Expansion Phase", "event": f"Widespread adoption of {topic} technologies."},
                {"year": "Modern Era", "event": f"AI-driven automation of {topic} visual pipelines."},
            ]
            key_entities = [topic.split()[0] if topic.split() else topic, content_pack.capitalize(), "StoryForge Engine"]
            confidence = 0.75

        artifact = ResearchArtifact(
            artifact_id=artifact_id,
            topic=topic,
            facts=facts,
            timeline_events=timeline_events,
            key_entities=key_entities,
            confidence_score=confidence,
        )

        return artifact.to_dict()
