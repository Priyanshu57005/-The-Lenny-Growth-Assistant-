import logging
import re
from typing import List, Dict, Optional, Tuple
from app.schemas.schemas import SourceCitation
from app.services.llm import llm_factory

logger = logging.getLogger("lenny_growth.skills.artifact_gen")

ARTIFACT_SYSTEM_PROMPT = """You are an expert Frontend Engineer and Technical Document Designer.
Your task is to generate clean, high-quality Markdown or standalone HTML/CSS artifacts based on the user's request and transcript context.

RULES FOR HTML ARTIFACTS:
1. Output MUST be valid, self-contained HTML (including standard <!DOCTYPE html>, <html>, <head> with embedded CSS <style>, and <body>).
2. Use modern, beautiful SaaS UI styling (flexbox/grid, dark mode or clean light theme, custom CSS variables, rounded corners, subtle shadows, Google fonts if linked).
3. Do NOT include external script tags from unauthorized CDNs. Embedded inline JavaScript for light interactivity (e.g. tab switching, dark mode toggle, counter, calculator) is allowed.
4. Wrap your output in a markdown block labeled ```html or ```markdown.

RULES FOR MARKDOWN ARTIFACTS:
1. Output structured, beautifully formatted Markdown with headers, tables, bullet points, callout blockquotes, and code blocks.
2. Wrap your output in ```markdown.
"""

class ArtifactGeneratorSkill:
    def __init__(self):
        self.name = "Artifact Generator Skill"

    def extract_artifact_from_text(self, text: str) -> Tuple[str, str, str]:
        """
        Parses LLM output to extract artifact type, title, and clean content code block.
        Returns (artifact_type, title, content)
        """
        # Search for ```html ... ``` block
        html_match = re.search(r"```html\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if html_match:
            html_content = html_match.group(1).strip()
            # Extract title from <title> tag or default
            title_match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE)
            title = title_match.group(1) if title_match else "Interactive HTML Component"
            return "html", title, html_content

        # Search for ```markdown ... ``` block
        md_match = re.search(r"```markdown\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if md_match:
            md_content = md_match.group(1).strip()
            # Extract first H1 heading for title
            h1_match = re.search(r"^#\s+(.*)", md_content, re.MULTILINE)
            title = h1_match.group(1) if h1_match else "Growth Document Artifact"
            return "markdown", title, md_content

        # Fallback: Check if response starts with <html> or <!DOCTYPE
        if "<html>" in text.lower() or "<!doctype html>" in text.lower():
            return "html", "Generated HTML Artifact", text.strip()

        # Default fallback to markdown artifact
        lines = text.strip().split("\n")
        title = lines[0].replace("#", "").strip() if lines and lines[0].startswith("#") else "Growth Artifact"
        return "markdown", title, text.strip()

    async def execute(
        self,
        user_request: str,
        citations: List[SourceCitation],
        conversation_history: List[Dict[str, str]],
        provider_override: Optional[str] = None
    ) -> Tuple[str, str, str, str]:
        """
        Executes artifact generation.
        Returns (assistant_chat_summary, artifact_type, title, artifact_content)
        """
        context_str = ""
        if citations:
            context_str = "TRANSCRIPT CONTEXT:\n" + "\n".join([f"- {c.guest} on '{c.title}': {c.snippet}" for c in citations])

        prompt = f"""Generate an artifact requested by the user:

USER REQUEST:
"{user_request}"

{context_str}

If the user asks for a UI layout, preview, interactive component, dashboard, or design mockup, generate an HTML/CSS artifact.
If the user asks for a framework doc, checklist, PRD, roadmap, or markdown report, generate a Markdown artifact.

Provide a short 2-sentence conversational summary in your main text, followed by the full artifact code block.
"""

        full_output, provider_used = await llm_factory.generate_with_fallback(
            prompt=prompt,
            system_prompt=ARTIFACT_SYSTEM_PROMPT,
            conversation_history=conversation_history,
            temperature=0.4,
            provider_override=provider_override
        )

        art_type, title, content = self.extract_artifact_from_text(full_output)
        
        # Clean chat summary (strip the code block from the main message body)
        summary = re.sub(r"```(html|markdown)?[\s\S]*?```", "", full_output).strip()
        if not summary:
            summary = f"I've generated the requested {art_type.upper()} artifact: **{title}**. You can view and interact with it in the Artifact Panel."

        return summary, art_type, title, content

artifact_generator_skill = ArtifactGeneratorSkill()
