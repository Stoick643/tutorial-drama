# LLM Internals Tutorial — Curriculum & Build Plan

## Overview
- **Target:** IT professionals who want to understand how LLMs work under the hood
- **Lessons:** 6
- **Narrative Styles:** Sci-Fi + Office Comedy
- **Grading:** Hybrid — real API calls, real tokenizer, validators
- **API Provider:** Moonshot (primary), Deepseek shown as code example
- **API Key:** Server-side (`LLM_API_KEY` env var) — students never need their own

## Pedagogical Design

### Learning Principles Applied
| Principle | Application |
|-----------|-------------|
| **Concrete Before Abstract** | Lesson 00: see LLM respond FIRST, explain theory AFTER |
| **Scaffolding** | Each lesson builds on the previous one |
| **Zone of Proximal Development** | Challenges just beyond current ability |
| **Flow State** | Clear goals, immediate feedback, sense of control |
| **Bloom's Taxonomy** | Progress from Experience → Understand → Apply → Analyze |
| **Immediate Feedback** | Real-time grading on every submission |
| **Narrative Motivation** | Story creates emotional investment in learning |

### Bloom's Taxonomy Progression
```
Lesson 00: Experience   — "See it work" (wow moment, real API call)
Lesson 01: Understand   — "How does it read?" (see tokenization happen)
Lesson 02: Understand   — "How does it know meaning?" (see similarity scores)
Lesson 03: Apply        — "Can I build a request?" (construct API JSON)
Lesson 04: Apply        — "Can I call it myself?" (write curl command)
Lesson 05: Analyze      — "How do real systems work?" (build enhanced prompt + RAG)
```

### Engagement Curve
```
Engagement
  ↑
  │         ★ 04 (real API call you built!)
  │       ★ 05 (build what ChatGPT actually does)
  │     ★ 03 (construct full request)
  │ ★ 00 (wow! it talks!)
  │   ★ 01 ★ 02 (understanding deepens)
  └──────────────────────→ Lessons
```
Lessons 01-02 are more theoretical — engagement maintained through real interactive
tools (tokenizer, similarity) and strong narrative. Lessons 03-05 ramp up with
creation and real API calls.

## Lessons

### 00 — Your First Conversation With an LLM
- **Bloom Level:** Experience (concrete before abstract)
- **Concept:** What IS an LLM? Student experiences it first, then we explain: transformer architecture (high level), weights, training vs inference, model sizes (7B, 70B, 405B).
- **Real-World:** Why different models exist — speed vs quality vs cost tradeoff.
- **Student Experience:** Type any question → see real LLM response → dialogue explains what just happened under the hood. "Wow" moment first, theory second.
- **Challenge:** Type a question to the LLM. Real call to Moonshot API.
- **Grading:** Real API call. Any valid question gets a response. Success = LLM responded.
- **Key Insight:** "That response was generated token-by-token by a neural network with billions of parameters. Let's find out how."

### 01 — Tokenization: How LLMs Read
- **Bloom Level:** Understand
- **Concept:** How text becomes numbers. BPE (Byte Pair Encoding), token limits, context windows. Why "strawberry" is tricky. Why tokens ≠ words. Why emojis cost more tokens.
- **Real-World:** Why API pricing is per-token. Why context window size matters (4K vs 128K).
- **Student Experience:** Type any text → see actual token splits and IDs → count matches expected.
- **Challenge:** Tokenize a specific sentence using real tokenizer, predict/verify token count.
- **Grading:** Real tiktoken in container. Show actual splits, compare token count.
- **Builds On:** Lesson 00 — "Remember that response? Every word in it was a token."

### 02 — Embeddings: How LLMs Understand Meaning
- **Bloom Level:** Understand
- **Concept:** How meaning becomes math. Vector space, semantic similarity, cosine distance. Words with similar meaning = nearby vectors. "King - Man + Woman ≈ Queen."
- **Real-World:** How search engines, RAG, and recommendations work under the hood.
- **Student Experience:** Pick two sentences → see similarity score → understand why.
- **Challenge:** Compute similarity between sentences with pre-loaded embeddings.
- **Grading:** Python + numpy with pre-computed embeddings baked into image.
- **Builds On:** Lesson 01 — "Tokens are IDs, but embeddings give them MEANING."

### 03 — Anatomy of a Call: Building the Request
- **Bloom Level:** Apply
- **Concept:** Full flow: User prompt → system prompt + context → tokenize → inference → sample (temperature, top-p) → detokenize → response. What each parameter does.
- **Real-World:** Why same prompt gives different answers (temperature). Why responses get cut off (max_tokens). How to control creativity vs precision.
- **Student Experience:** Construct a complete API request JSON by hand.
- **Challenge:** Build JSON with model, messages array (system + user roles), temperature, max_tokens.
- **Grading:** JSON validator — check structure, required fields, valid parameter ranges.
- **Builds On:** Lessons 00-02 — "You've seen the response, the tokens, the meaning. Now build the request that makes it all happen."

### 04 — The API Layer: Calling It For Real
- **Bloom Level:** Apply
- **Concept:** Same model, different channels: Chat UI, CLI (Claude Code), Java SDK, curl/REST. The OpenAI-compatible API format that Moonshot, Deepseek, and many others use.
- **Real-World:** One standard format, many providers. Show Java code example, Deepseek endpoint as alternative.
- **Student Experience:** Write a curl command → real API call to Moonshot → see actual response.
- **Challenge:** Write a working curl command that calls Moonshot API with proper headers and JSON body.
- **Grading:** Validate curl structure + execute real API call. Show actual LLM response.
- **Builds On:** Lesson 03 — "You built the JSON. Now send it."

### 05 — Enhanced Prompts & RAG: What Really Happens
- **Bloom Level:** Analyze / Create
- **Concept:** What happens BEFORE your prompt hits the model: system prompts (persona, rules, guardrails), context injection (RAG — retrieve relevant docs, inject into prompt), tool/function calling. The user types "What's our refund policy?" but the real prompt includes the entire policy document.
- **Real-World:** How ChatGPT, Claude, and enterprise AI assistants actually work behind the scenes. Why RAG beats fine-tuning for most use cases.
- **Student Experience:** Build an enhanced prompt with system + retrieved context + user query → call API → see how context changes the response.
- **Challenge:** Construct a full enhanced prompt JSON with system message, retrieved context, and user query. Real API call shows the difference.
- **Grading:** JSON validator for structure + real API call to show quality difference.
- **Builds On:** Everything — "Now you know what's really happening when you chat with an AI."

## Build Plan

### Step 1: Docker Image (`docker/llm/Dockerfile`)
- Base: `python:3.12-alpine`
- Install: tiktoken, numpy, curl
- Add scripts:
  - `tokenize-text` — tokenize input, show splits + count + IDs
  - `compute-similarity` — cosine similarity with pre-loaded embeddings
  - `validate-api-request` — check JSON structure for API calls
  - `call-llm` — make real API call to Moonshot, return response
- Add data:
  - `embeddings.json` — pre-computed sentence embeddings for lesson 02
- **No Java in image** — Java code shown as example in lesson text, curl does actual calls
- Estimated size: ~200 MB

### Step 2: Wire into docker_manager.py
- Add `"llm": "grader-image-llm"` to GRADER_IMAGES
- Add `_build_command` for llm language
- Pass `LLM_API_KEY` env var to container at runtime
- Add container reset logic

### Step 3: Write 6 Lesson JSON Files
- Each with Sci-Fi + Office Comedy styles
- All lessons use multiline input (questions, text, JSON, curl commands)

### Step 4: Update Homepage
- Activate LLM card on index.html

### Step 5: Test
- Test each lesson end-to-end
- Test real Moonshot API calls for lessons 00, 04, 05
- Test graceful behavior if API is temporarily unavailable

## API Key Management
- Environment variable: `LLM_API_KEY`
- Passed to grader container at runtime (not baked into image)
- All lessons use real API (00, 04, 05 directly; 01-03 use local tools)
- Moonshot API: `https://api.moonshot.cn/v1/chat/completions`
- Deepseek API: `https://api.deepseek.com/v1/chat/completions` (shown as code example in lesson 04)

## Narrative Styles

### 🚀 Sci-Fi
- LLM = alien intelligence / ship's computer awakening
- Tokens = alien alphabet / signal encoding
- Embeddings = star map coordinates (similar meanings = nearby stars)
- API call = transmission to the intelligence
- Enhanced prompt = mission briefing before transmission
- Characters: Commander, Ship AI (ARIA), Science Officer

### 💼 Office Comedy
- LLM = the new AI intern who just joined the team
- Tokens = how the intern reads your emails (word by word, sometimes weirdly)
- Embeddings = the intern's filing system ("these go in the same drawer")
- API call = sending a formal memo to the AI department
- Enhanced prompt = the manager's briefing before the intern meets a client
- Characters: Manager, AI Intern (Alex), Skeptical Senior Dev (Sam)
