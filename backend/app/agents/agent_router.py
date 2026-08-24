import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.retriever import retriever
from app.skills.ship30 import ship30_skill
from app.skills.artifact_gen import artifact_generator_skill
from app.services.llm import llm_factory
from app.schemas.schemas import SourceCitation

logger = logging.getLogger("lenny_growth.agent.router")

ROUTER_CLASSIFICATION_PROMPT = """Analyze the user's latest input message and classify it into EXACTLY ONE of the following 4 routes:

1. SHIP30_ESSAY: User asks to write/generate a "Ship 30", "Ship 30 for 30", or long-form essay / article about growth/PM.
2. ARTIFACT_GEN: User asks to create an HTML/CSS layout, component, UI design, dashboard, diagram, PRD document, template, or visual artifact.
3. KNOWLEDGE_QNA: User asks a product management, growth, metrics, hiring, leadership, or startup advice question that should be answered using transcript knowledge.
4. DIRECT: User message is a greeting, meta-question, or simple chit-chat (e.g. "hi", "who are you?", "help").

Output ONLY the category name string (SHIP30_ESSAY, ARTIFACT_GEN, KNOWLEDGE_QNA, or DIRECT). Do not add any extra text or punctuation.
"""

GROUNDED_ANSWER_SYSTEM_PROMPT = """You are The Lenny Growth Assistant, an AI expert grounded strictly in Lenny Rachitsky's Podcast and Newsletter transcripts.

YOUR ABSOLUTE MANDATE FOR GROUNDED ANSWERS:
1. Base your answer ONLY on the provided TRANSCRIPT CONTEXT below.
2. CITATIONS: Attribute key points to specific guests and episodes (e.g., "According to Elena Verna...", "As Shreyas Doshi shares in his episode...").
3. BOUNDARIES / NO HALLUCINATION: If the provided transcript context does NOT contain enough relevant information to answer the user's question, you MUST explicitly acknowledge this limitation. Say:
   "Based on the available Lenny's Podcast transcript database, I couldn't find specific discussion on [topic]. Here is what the transcripts do cover regarding related concepts..."
4. FORMATTING: Use clean markdown, bold terms, bullet points, and actionable takeaways.
"""

class AgentRouter:
    def __init__(self):
        pass

    async def classify_route(self, message: str, provider_override: Optional[str] = None) -> str:
        msg_lower = message.lower()
        
        # Fast rule-based heuristics
        if "ship 30" in msg_lower or "ship30" in msg_lower or "write an essay on" in msg_lower:
            return "SHIP30_ESSAY"
        if any(kw in msg_lower for kw in ["html", "ui mockup", "artifact", "css", "pricing table", "dashboard layout", "component"]):
            return "ARTIFACT_GEN"
        if msg_lower in ["hi", "hello", "hey", "who are you", "help", "what can you do"]:
            return "DIRECT"

        # LLM classification fallback
        try:
            res, _ = await llm_factory.generate_with_fallback(
                prompt=f"User Message: '{message}'",
                system_prompt=ROUTER_CLASSIFICATION_PROMPT,
                temperature=0.0,
                provider_override=provider_override
            )
            route = res.strip().upper()
            if route in ["SHIP30_ESSAY", "ARTIFACT_GEN", "KNOWLEDGE_QNA", "DIRECT"]:
                return route
        except Exception as e:
            logger.warning(f"LLM router classification failed: {e}. Defaulting to KNOWLEDGE_QNA.")
        
        return "KNOWLEDGE_QNA"

    async def process_user_message(
        self,
        user_message: str,
        db_session: AsyncSession,
        conversation_history: List[Dict[str, str]],
        provider_override: Optional[str] = None
    ) -> Tuple[str, str, List[SourceCitation], Optional[Dict[str, Any]]]:
        """
        Processes message through router -> retrieval -> specialized skill/grounded answerer.
        Returns tuple: (response_text, agent_route, citations_list, artifact_dict_or_none)
        """
        route = await self.classify_route(user_message, provider_override)
        logger.info(f"Agent Router classified query '{user_message[:30]}...' -> Route: {route}")

        # Step 1: Perform RAG retrieval for relevant routes
        citations: List[SourceCitation] = []
        if route in ["KNOWLEDGE_QNA", "SHIP30_ESSAY", "ARTIFACT_GEN"]:
            citations = await retriever.retrieve(user_message, db_session)

        # Step 2: Route execution
        artifact_payload = None

        if route == "SHIP30_ESSAY":
            essay_text = await ship30_skill.execute(user_message, citations, conversation_history, provider_override)
            return essay_text, route, citations, None

        elif route == "ARTIFACT_GEN":
            summary_text, art_type, title, content = await artifact_generator_skill.execute(
                user_message, citations, conversation_history, provider_override
            )
            artifact_payload = {
                "artifact_type": art_type,
                "title": title,
                "content": content
            }
            return summary_text, route, citations, artifact_payload

        elif route == "KNOWLEDGE_QNA":
            # Check if empty or low score retrieval
            if not citations or (citations and citations[0].score < 0.25):
                grounded_prompt = f"""USER QUESTION:
"{user_message}"

RETRIEVED TRANSCRIPT CONTEXT:
No sufficiently relevant transcript chunks were found in the knowledge base (all similarity scores below threshold).

INSTRUCTIONS:
Politely inform the user that Lenny's podcast transcript database does not contain specific coverage of this question. Provide high-level context if related product concepts are known, but explicitly clarify the boundary. Do NOT fabricate quotes or invent episodes.
"""
            else:
                context_str = "\n\n".join([
                    f"--- CITATION [{i+1}]: Guest: {c.guest} | Episode: {c.title} (Relevance Score: {c.score}) ---\n{c.snippet}"
                    for i, c in enumerate(citations)
                ])
                grounded_prompt = f"""USER QUESTION:
"{user_message}"

RETRIEVED TRANSCRIPT CONTEXT:
{context_str}

INSTRUCTIONS:
Answer the user's question clearly, grounded strictly in the retrieved transcript context above. Cite the guest speakers and episode titles when referencing their advice.
"""

            response_text, _ = await llm_factory.generate_with_fallback(
                prompt=grounded_prompt,
                system_prompt=GROUNDED_ANSWER_SYSTEM_PROMPT,
                conversation_history=conversation_history,
                temperature=0.5,
                provider_override=provider_override
            )
            return response_text, route, citations, None

        else:  # DIRECT / General conversation
            direct_prompt = f"User says: '{user_message}'. Respond as The Lenny Growth Assistant, a helpful AI expert on product management, growth strategies, and startup scaling."
            response_text, _ = await llm_factory.generate_with_fallback(
                prompt=direct_prompt,
                system_prompt="You are The Lenny Growth Assistant, a friendly and sharp product management AI copilot.",
                conversation_history=conversation_history,
                temperature=0.7,
                provider_override=provider_override
            )
            return response_text, route, [], None

agent_router = AgentRouter()
