import logging
import re
from typing import List, Dict, Optional
from app.services.llm.base import BaseLLMProvider

logger = logging.getLogger("lenny_growth.llm.mock")

class MockGroundedProvider(BaseLLMProvider):
    """
    Offline Demo/Fallback Provider that synthesizes rich grounded responses from retrieved transcript context.
    Ensures zero-downtime demonstration even when Ollama is offline and Cloud API keys are unconfigured.
    """
    @property
    def provider_name(self) -> str:
        return "demo"

    @property
    def model_name(self) -> str:
        return "grounded-demo-v1"

    async def check_health(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7
    ) -> str:
        prompt_lower = prompt.lower()
        
        # Check if prompt contains Ship 30 request
        if "ship 30" in prompt_lower or "ship30" in prompt_lower or "essay" in prompt_lower:
            return """# The Ultimate Product-Led Growth & Onboarding Playbook

> **The 30-Second Summary**: 
> - Sustainable growth is built on immediate self-serve value realization, not high-friction sales funnels.
> - Categorize PM focus using Shreyas Doshi's LNO framework: 10x leverage tasks demand 100% focus.
> - Monetization triggers should fire naturally when users hit usage expansion thresholds.

## 1. The Core Challenge & Mindset Shift
In traditional software sales, companies locked products behind gated demos and credit card walls. Today's top product-led companies (**Miro**, **Notion**, **Figma**) flip this model: user activation comes first, monetization follows.

As **Elena Verna** emphasizes, Product-Led Growth (PLG) is not merely a pricing strategy—it is an end-to-end company flywheel where the product itself drives acquisition, retention, and expansion.

## 2. Proven Frameworks from Product Leaders

### The LNO Prioritization Framework (**Shreyas Doshi**)
Product leaders frequently burn out by treating every task with equal priority. The **LNO Framework** categorizes workloads:
1. **Leverage (L) Tasks**: 10x impact activities (e.g. core onboarding flows, positioning, architecture).
2. **Neutral (N) Tasks**: 1x standard impact tasks (e.g. routine status updates, sprint hygiene).
3. **Overhead (O) Tasks**: Low impact compliance tasks. Delegate or complete with minimum viable effort.

### Growth Loops vs Linear Funnels (**Casey Winters**)
Linear funnels treat users as static outputs. Sustainable growth requires **Growth Loops**, where output from one active user automatically feeds input into acquiring the next user (via viral collaboration or content loops).

## 3. Step-by-Step Tactical Execution Guide
1. **Remove Friction in Onboarding**: Deliver the 'Aha! Moment' within 30 seconds of user registration.
2. **Conduct Pre-Mortems**: Before major launches, ask the team: *"Imagine it is 12 months from today and this launch failed. Why did it fail?"*
3. **Align Monetization with Usage**: Charge users when they hit organic capacity limits (seats, workspace limits, advanced integrations).

## 4. The Ultimate Takeaway for Growth Leaders
Focus relentlessly on retention curves. As **Casey Winters** notes, if your retention curve decays to zero, performance marketing spend is wasted money. Prioritize high-leverage product work that creates compounding user value.
"""

        # Check if prompt contains HTML artifact request
        if any(kw in prompt_lower for kw in ["html", "ui mockup", "artifact", "css", "pricing table", "dashboard"]):
            return """I've generated the requested interactive HTML SaaS Pricing Table component artifact. You can view, preview, and copy the full component in the Artifact Canvas beside this chat.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS Pricing Component</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent: #3b82f6;
            --text: #f8fafc;
            --text-muted: #94a3b8;
        }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--bg-color);
            color: var(--text);
            padding: 2rem;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h2 { font-size: 1.75rem; margin-bottom: 0.5rem; }
        p.subtitle { color: var(--text-muted); margin-bottom: 2rem; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.5rem;
            width: 100%;
            max-width: 900px;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid #334155;
            border-radius: 1rem;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, border-color 0.2s;
        }
        .card:hover { transform: translateY(-4px); border-color: var(--accent); }
        .card.popular { border: 2px solid var(--accent); position: relative; }
        .badge {
            position: absolute;
            top: -12px;
            right: 20px;
            background: var(--accent);
            color: white;
            font-size: 0.75rem;
            padding: 2px 10px;
            border-radius: 12px;
            font-weight: 600;
        }
        .price { font-size: 2.25rem; font-weight: 700; margin: 1rem 0; }
        .btn {
            background: var(--accent);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: auto;
            transition: background 0.2s;
        }
        .btn:hover { background: #2563eb; }
        ul { list-style: none; padding: 0; margin: 1rem 0; color: var(--text-muted); font-size: 0.9rem; }
        li { margin-bottom: 0.5rem; display: flex; align-items: center; }
        li::before { content: "✓"; color: var(--accent); margin-right: 0.5rem; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Flexible Pricing for Growth Teams</h2>
    <p class="subtitle">Choose the plan that fits your product operations stage</p>
    <div class="grid">
        <div class="card">
            <h3>Starter</h3>
            <div class="price">$29<span style="font-size: 1rem; color: #94a3b8;">/mo</span></div>
            <ul>
                <li>Up to 3 Product Managers</li>
                <li>Basic Transcript Search</li>
                <li>Standard RAG Grounding</li>
            </ul>
            <button class="btn">Start Free Trial</button>
        </div>
        <div class="card popular">
            <div class="badge">MOST POPULAR</div>
            <h3>Pro Growth</h3>
            <div class="price">$79<span style="font-size: 1rem; color: #94a3b8;">/mo</span></div>
            <ul>
                <li>Unlimited PM Seats</li>
                <li>Ship 30 Essay Generator</li>
                <li>HTML & MD Artifact Canvas</li>
                <li>Priority Local/Cloud LLMs</li>
            </ul>
            <button class="btn">Get Started</button>
        </div>
    </div>
</body>
</html>
```
"""

        # Grounded Q&A response synthesized from prompt context
        citations_found = re.findall(r"Guest: ([^\n|]+)", prompt)
        guest_list = ", ".join(set(citations_found)) if citations_found else "Shreyas Doshi and Elena Verna"

        return f"""### Grounded Product Management Guidance

Based on insights from **{guest_list}** in Lenny's Podcast transcripts:

1. **The LNO Prioritization Framework**:
   - **Leverage (L) Tasks**: 10x high-impact strategic activities (vision, core onboarding, positioning). Allocate **100%** energy to these.
   - **Neutral (N) Tasks**: 1x standard impact tasks (routine status updates, sprint planning). Give **80%** effort.
   - **Overhead (O) Tasks**: Low-impact compliance tasks. Complete with **50%** effort or delegate.

2. **Conducting Pre-Mortems**:
   - High-agency PMs anticipate failure modes early. Before launching a major growth feature, ask the team: *"Assume it is 12 months from today and this launch failed. What went wrong?"*

3. **Product-Led Growth (PLG) Execution**:
   - Focus on getting users to the 'Aha! Moment' immediately before imposing friction or paywalls. Monetize when users hit natural capacity limits.

*(Generated via Grounded Synthesis Engine. To use live LLM models, start Ollama locally via `ollama run llama3.2` or set ANTHROPIC_API_KEY / OPENAI_API_KEY in `.env`)*
"""
