import logging
from typing import List, Dict, Optional
from app.schemas.schemas import SourceCitation
from app.services.llm import llm_factory

logger = logging.getLogger("lenny_growth.skills.ship30")

SHIP30_SYSTEM_PROMPT = """You are a master digital writer trained in the Ship 30 for 30 framework, writing an authoritative, highly actionable long-form growth essay.

Your writing MUST strictly adhere to the following Ship 30 for 30 architecture:
1. WORD COUNT: Aim for approximately 1,250 words of rich, comprehensive content.
2. HOOK: Open with a compelling, magnetic line or 2-sentence paragraph that instantly grabs product/growth professionals.
3. NARRATIVE PROGRESSION: Move logically from Problem Statement -> Mindset Shift -> Tactical Framework -> Real-World Execution -> Key Takeaway.
4. SKIMMABLE FORMATTING: Use crisp H2 and H3 subheadings, numbered lists, bullet points, and single-sentence paragraphs.
5. EMPHASIS: Use **selective bolding** on high-impact terms and metrics to guide skimmers.
6. GROUNDING & CITATIONS: Every strategic framework, metric, or advice MUST be explicitly grounded in the retrieved transcript knowledge provided. Reference guests by name (e.g., "As Shreyas Doshi notes..." or "Brian Chesky highlights...").
7. NO HALLUCINATIONS: If the retrieved transcripts do not contain enough specific data for a section, acknowledge the boundary honestly.

Structure your essay with these main sections:
# [Magnetic Title]

> **The 30-Second Summary**: 2-3 bullet point core thesis.

## 1. The Core Challenge & Mindset Shift
## 2. Proven Frameworks from Product Leaders
## 3. Step-by-Step Tactical Execution Guide
## 4. Common Pitfalls & Mistakes to Avoid
## 5. The Ultimate Takeaway for Growth & PM Leaders
"""

class Ship30Skill:
    def __init__(self):
        self.name = "Ship 30 for 30 Essay Generator"

    async def execute(
        self,
        topic_request: str,
        citations: List[SourceCitation],
        conversation_history: List[Dict[str, str]],
        provider_override: Optional[str] = None
    ) -> str:
        # Build context from citations
        if citations:
            context_blocks = []
            for i, c in enumerate(citations, 1):
                context_blocks.append(f"--- SOURCE [{i}]: Guest: {c.guest} | Episode: {c.title} ---\n{c.snippet}\n")
            knowledge_context = "\n".join(context_blocks)
        else:
            knowledge_context = "No specific transcript sources retrieved for this topic."

        prompt = f"""Write a comprehensive Ship 30 for 30 style essay on the following topic requested by the user:

USER REQUEST:
"{topic_request}"

RETRIEVED LENNY PODCAST TRANSCRIPT KNOWLEDGE:
{knowledge_context}

INSTRUCTIONS:
Generate the full ~1,250-word Ship 30 for 30 essay following all formatting, structure, and transcript grounding rules.
"""

        essay, provider_used = await llm_factory.generate_with_fallback(
            prompt=prompt,
            system_prompt=SHIP30_SYSTEM_PROMPT,
            conversation_history=conversation_history,
            temperature=0.6,
            provider_override=provider_override
        )
        logger.info(f"Ship30Skill generated essay using provider '{provider_used}' ({len(essay.split())} words)")
        return essay

ship30_skill = Ship30Skill()
