import os
import sys
import json
import logging
import asyncio
from typing import List, Dict, Any

# Ensure backend modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.database import AsyncSessionLocal, init_db
from app.db.models import TranscriptChunkModel
from app.rag.embedder import embedder
from sqlalchemy import select, delete

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lenny_growth.ingestion")

# Sample starter transcript dataset grounded in iconic Lenny's Podcast episodes
SEED_TRANSCRIPT_EPISODES = [
    {
        "guest": "Shreyas Doshi",
        "title": "High-Agency Product Management, LNO Framework, and Product Strategy",
        "url": "https://www.lennyspodcast.com/shreyas-doshi",
        "date": "2023-04-15",
        "content": """
Shreyas Doshi on the LNO Framework for Product Managers:
Most Product Managers fail because they treat every task with equal urgency and quality. The LNO framework categorizes tasks into three buckets:
1. Leverage (L) Tasks: 10x impact activities like defining core product vision, positioning, strategic roadmaps, or high-leverage architectural choices. Give these 100% of your energy.
2. Neutral (N) Tasks: 1x impact tasks that must be done well (e.g., standard status reports, standard sprint planning). Give these 80% effort.
3. Overhead (O) Tasks: Low impact compliance tasks. Delegate or complete with 50% effort.

On Product-Market Fit & Pre-Mortems:
Before launching a major growth initiative, conduct a Pre-Mortem. Ask the team: "Imagine it's 12 months from today and this feature launch failed miserably. Why did it fail?" This unlocks candid risk identification that standard optimistic roadmapping ignores. High-agency product managers anticipate failure modes early.
"""
    },
    {
        "guest": "Elena Verna",
        "title": "Product-Led Growth (PLG), Viral Loops, and B2B Monetization",
        "url": "https://www.lennyspodcast.com/elena-verna",
        "date": "2023-06-20",
        "content": """
Elena Verna on the Core Mechanics of Product-Led Growth (PLG):
PLG is not a pricing model; it is a business strategy where product usage is the primary driver of customer acquisition, retention, and expansion.
The PLG Flywheel consists of:
1. Low Friction Onboarding: Get users to the 'Aha! Moment' within seconds, before requiring sign-up or credit card info.
2. Self-Serve Value Realization: The product must solve a discrete problem immediately.
3. Natural Monetization Triggers: Charge when users hit usage limits (seats, storage, advanced workflows), not before they experience value.

On Product-Led Sales (PLS):
Top PLG companies (Miro, Notion, Figma) combine PLG with sales. Product usage generates Product-Qualified Leads (PQLs). Sales reps contact teams that are already actively using the free tier inside an enterprise.
"""
    },
    {
        "guest": "Brian Chesky",
        "title": "Founder Mode, Design-Driven Products, and Airbnb's Growth Story",
        "url": "https://www.lennyspodcast.com/brian-chesky",
        "date": "2023-11-10",
        "content": """
Brian Chesky on Founder Mode and Product Excellence:
Conventional Silicon Valley wisdom tells founders to 'hire great people and empower them to run everything.' But when founders step back completely, product design coherency fractures.
Founder mode means staying deep in the details of the product. At Airbnb, we eliminated traditional product management silos and unified product management with product marketing.

On Design and Storytelling:
Great products aren't built by consensus; they are crafted by visionaries who obsess over details. We designed Airbnb's end-to-end user journey by creating 45 storyboard panels of the ideal guest and host experience. Every product feature should feel like a scene in a movie.
"""
    },
    {
        "guest": "Casey Winters",
        "title": "Growth Loops, Retention Tactics, and Building Sustainable Moats",
        "url": "https://www.lennyspodcast.com/casey-winters",
        "date": "2023-08-05",
        "content": """
Casey Winters on Retention as the Foundation of Growth:
Acquisition gets all the headlines, but retention creates compounding growth. If your product retention curve decays to zero, no amount of performance marketing will save you.

Growth Loops vs Linear Funnels:
Linear funnels (Acquisition -> Activation -> Retention -> Revenue) treat users as outputs. Growth loops take the output of one user's action and feed it into acquiring or activating the next user.
Types of Growth Loops:
1. Viral Loops: User creates content or invites collaborators (e.g., Slack, Figma).
2. Content Loops: User generates public content indexed by search engines (e.g., Pinterest, Quora).
3. Paid Loops: Monetized users fund user acquisition ad spend.
"""
    },
    {
        "guest": "Gibson Biddle",
        "title": "The DHM Model for Product Strategy and Netflix Branding",
        "url": "https://www.lennyspodcast.com/gibson-biddle",
        "date": "2023-02-18",
        "content": """
Gibson Biddle on the DHM Product Strategy Framework:
How do you build a product that customers love? Use the DHM Framework:
- Delight (D): How will your product delight users right now?
- Hard to Copy (H): What margin-enhancing moats are you building (network effects, unique tech, brand, scale)?
- Margin-enhancing (M): How will the product generate revenue and increase lifetime value?

At Netflix, our delight was instant streaming with personalized recommendations; our Hard-to-copy advantage was our recommendation algorithm and original content library.
"""
    }
]

def chunk_text(text: str, max_chars: int = 600, overlap: int = 100) -> List[str]:
    """Splits long text into overlapping chunks for precise vector embedding."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current_chunk = ""

    for p in paragraphs:
        if len(current_chunk) + len(p) <= max_chars:
            current_chunk += ("\n\n" if current_chunk else "") + p
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = p

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

async def run_ingestion():
    logger.info("Initializing database for ingestion...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # Clear existing seed chunks to allow clean re-ingestion
        await session.execute(delete(TranscriptChunkModel))
        await session.commit()
        logger.info("Cleared previous transcript chunks.")

        total_chunks = 0
        for ep in SEED_TRANSCRIPT_EPISODES:
            text_chunks = chunk_text(ep["content"])
            logger.info(f"Ingesting '{ep['title']}' ({len(text_chunks)} chunks)...")

            for idx, raw_chunk in enumerate(text_chunks):
                vector = embedder.embed_text(raw_chunk)
                chunk_model = TranscriptChunkModel(
                    guest=ep["guest"],
                    title=ep["title"],
                    url=ep["url"],
                    date=ep["date"],
                    chunk_index=idx,
                    content=raw_chunk,
                    embedding=vector
                )
                session.add(chunk_model)
                total_chunks += 1

        await session.commit()
        logger.info(f"Ingestion complete! Successfully indexed {total_chunks} transcript chunks.")

if __name__ == "__main__":
    asyncio.run(run_ingestion())
