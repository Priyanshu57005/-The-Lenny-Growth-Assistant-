# Product Requirement Document (PRD): The Lenny Growth Assistant

## 1. Product Objective
The Lenny Growth Assistant is a full-stack, AI-powered conversational application designed to provide product managers, growth leads, and startup founders with immediate, grounded advice sourced directly from *Lenny's Podcast* and newsletter transcripts. It turns hundreds of hours of high-signal interviews into an actionable copilot capable of answering strategic questions, writing long-form essays, and generating live interactive visual artifacts.

## 2. Target User & Problem Statement
- **Target User**: Product Managers (PMs), VP of Growth, Founders, Product Operations.
- **Problem Statement**: Growth leaders spend hours searching through disparate articles and podcast episodes to find tactical advice on topics like Product-Market Fit, PLG onboarding, retention loops, and LNO task prioritization. Generic AI chatbots hallucinate frameworks or give generic advice ungrounded in real industry leader experience.

## 3. Core Capabilities & User Flows

### Flow A: Grounded Knowledge Q&A
1. User starts a new chat session.
2. User asks: "What is Shreyas Doshi's advice on product-market fit pre-mortems?"
3. Agent Router classifies query as `KNOWLEDGE_QNA` -> triggers RAG vector retrieval.
4. Assistant generates a response citing Shreyas Doshi and episode details.
5. Expandable source cards display the exact transcript text snippets and match score.

### Flow B: Ship 30 for 30 Essay Generation
1. User asks: "Write a Ship 30 essay on PLG monetization triggers."
2. Agent Router classifies query as `SHIP30_ESSAY` -> dispatches `Ship30Skill`.
3. System retrieves Elena Verna transcript knowledge and generates a ~1,250-word structured essay with strong hook, skimmable headings, bold sub-bullets, and actionable takeaways.

### Flow C: HTML & Markdown Artifact Generation
1. User asks: "Create an interactive HTML pricing table component artifact."
2. Agent Router dispatches `ArtifactGeneratorSkill`.
3. System outputs a clean conversational summary in chat while opening the Artifact Canvas side-by-side.
4. User previews rendered HTML inside an isolated sandbox iframe or views raw code, copies, or downloads it.

## 4. Success Metrics
- **Grounding Fidelity**: >95% of strategic claims backed by explicit source citations.
- **Zero Hallucination Rate**: 100% acknowledgment of missing context when retrieval score is below similarity threshold.
- **Session Isolation**: 0% leakage of message context between distinct chat sessions.
- **Response Latency**: <3s to initial stream/response using local Ollama or cloud providers.

## 5. Scope & Trade-offs
- **In-Scope**: PostgreSQL RAG vector storage, Ollama/Anthropic/OpenAI provider switching, Ship 30 skill, side-by-side HTML/MD canvas, HTML security sandbox.
- **Out-of-Scope (v1)**: User multi-tenant authentication logins (sessions are currently anonymous per client device).

## 6. Risks & Mitigation Strategies
| Risk | Mitigation |
|------|------------|
| Ollama model missing on evaluator machine | Auto-fallback to Anthropic/OpenAI or clear diagnostic health indicator in UI |
| Malicious script execution in AI HTML | Enforce strict iframe sandbox (`allow-scripts` without `allow-same-origin`) and CSP meta tags |
| Database offline | Fallback embedded SQLite engine ensures evaluator can test app instantly |
