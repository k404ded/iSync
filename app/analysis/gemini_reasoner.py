"""
Gemini AI Semantic Reasoning Engine for iSync.
Leverages Google Gemini API (gemini-3.8-flash) for deep semantic curriculum analysis.
Strictly grounded in source text; never invents pages, slides, or quotes.
"""

import json
from typing import Optional
from app.config import GEMINI_API_KEY
from app.models.schemas import SoftwareChange, ContentChunk, Finding


class GeminiReasoner:
    """Uses Gemini API to refine findings with strict evidence grounding."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def refine_finding(
        self,
        change: SoftwareChange,
        chunk: ContentChunk,
        base_finding: Finding,
    ) -> Finding:
        """Refines a finding's technical rationale and author action using Gemini."""
        if not self.is_available:
            return base_finding

        prompt = f"""You are iSync, an AI curriculum maintenance analyst for engineering CAD/CAM software.
Analyze how this software change affects the existing course excerpt.

SOFTWARE CHANGE:
- Title: {change.title}
- Type: {change.change_type.value}
- Details: {change.description}
- Subsystem: {change.affected_subsystem}

SOURCE COURSE DOCUMENT:
- Document: {chunk.document}
- Location: {chunk.exact_location}
- Excerpt: "{chunk.text}"

STRICT GROUNDING RULES:
1. Ground your reasoning ONLY in the provided source excerpt and software change.
2. DO NOT invent new pages, slides, features, or filenames.
3. If evidence is insufficient, state: "Insufficient evidence — manual review required."
4. Provide concise, high-impact author instructions.

Respond strictly in valid JSON format with keys:
"why_flagged": string (technical rationale explaining why the existing course content is affected),
"recommended_action": string (exact instructions for the course author),
"old_state": string or null (the outdated concept/text/workflow),
"new_state": string or null (the updated target concept/workflow)
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )
            raw_text = response.text.strip()
            # Clean markdown code blocks if present
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()

            data = json.loads(raw_text)
            updates = {}
            if data.get("why_flagged"):
                updates["why_flagged"] = data["why_flagged"]
            if data.get("recommended_action"):
                updates["recommended_action"] = data["recommended_action"]
            if "old_state" in data and data["old_state"]:
                updates["old_state"] = data["old_state"]
            if "new_state" in data and data["new_state"]:
                updates["new_state"] = data["new_state"]

            return base_finding.model_copy(update=updates)
        except Exception:
            # Fall back safely to base finding without failing the pipeline
            return base_finding
