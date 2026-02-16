# LLM Tutorial — Detailed Lesson Plans

Each lesson follows this structure:
1. **Hook** — grab attention, connect to previous lesson
2. **Concept** — introduce the idea through narrative dialogue
3. **Demonstration** — show it working (code example)
4. **Challenge** — student does it themselves
5. **Feedback** — instant result + "what just happened" reflection

---

## Lesson 00 — Your First Conversation With an LLM

### Learning Objective
Student experiences an LLM responding to their question, then understands (at high level) what just happened.

### Prerequisites
None — this is the entry point.

### Lesson Flow

| Phase | Duration | What Happens |
|-------|----------|-------------|
| **Hook** | 1 min | Dialogue sets the scene. Sci-Fi: "We've detected a signal from an alien intelligence." Office: "HR says our new intern is... artificial." |
| **Concept (light)** | 2 min | Minimal explanation: "An LLM is a program that predicts the next word. It was trained on massive amounts of text. Let's just talk to it." Deliberately vague — we explain details in later lessons. |
| **Demo** | 1 min | Code example shows a simple question and response. |
| **Challenge** | 2 min | Student types ANY question. Real API call to Moonshot. Real response appears. |
| **Reflection** | 2 min | Dialogue reacts to what happened: "That response had 47 tokens. It took 0.8 seconds. The model has 200 billion parameters. What does any of that mean? That's what we'll find out." |

### Challenge Details
- **Input:** Any text (free-form question)
- **Grading:** Real API call to Moonshot. Success = non-empty response returned.
- **Validation type:** `user_output_contains` — response must contain at least 10 characters.
- **What student sees:** Their question + the LLM's actual response.

### Key Teaching Moments
- LLMs generate text, they don't "know" things
- The response came from a server via an API (not magic)
- Teaser: "Every word in that response was predicted one at a time — we'll see how in the next lesson"

### Narrative Notes
- **Sci-Fi:** Commander sends first transmission to alien intelligence (ARIA). Response comes back. Science Officer is amazed. "It understood us?"
- **Office Comedy:** Manager asks the new AI intern (Alex) a question. Alex responds eloquently. Senior Dev Sam is suspicious. "It's just autocomplete on steroids."

---

## Lesson 01 — Tokenization: How LLMs Read

### Learning Objective
Student understands that LLMs don't read words — they read tokens. Student can tokenize text and predict approximate token counts.

### Prerequisites
Lesson 00 — student has seen an LLM respond.

### Lesson Flow

| Phase | Duration | What Happens |
|-------|----------|-------------|
| **Hook** | 1 min | "Remember that response from lesson 00? The LLM didn't read your question as words. It read it as tokens. Let's see what that means." |
| **Concept** | 3 min | Dialogue explains: tokens ≠ words. "Hello world" = 2 tokens, but "tokenization" = 3 tokens. BPE algorithm (simplified): common pairs get merged. Show why "strawberry" is tricky — the model sees ["str", "aw", "berry"]. |
| **Demo** | 1 min | Code example: `tokenize("Hello, how are you?")` → shows splits + IDs + count. |
| **Challenge** | 2 min | Student types a sentence → real tiktoken tokenizes it → shows token splits, IDs, and total count. |
| **Reflection** | 1 min | "Your sentence was X tokens. API pricing is per token. A 128K context window means 128,000 tokens — roughly a 300-page book." |

### Challenge Details
- **Input:** Any text string (e.g., "The quick brown fox jumps over the lazy dog")
- **Grading:** Real tiktoken tokenization. Show splits and count.
- **Validation type:** `user_output_contains` — output must contain "tokens" (the tokenizer script always includes the count).
- **What student sees:** Token splits (e.g., ["The", " quick", " brown", ...]), token IDs, total count.

### Key Teaching Moments
- Tokens ≠ words (spaces, punctuation, subwords)
- Different languages tokenize differently (Chinese: 1 character ≈ 1 token, English: 1 word ≈ 1-2 tokens)
- This is why LLMs have token limits, not word limits
- API costs are per token — now you can estimate costs

### Narrative Notes
- **Sci-Fi:** Science Officer analyzes the alien signal. "Commander, the intelligence doesn't process our language directly. It breaks it into fragments — tokens." Shows signal decomposition on screen.
- **Office Comedy:** Manager writes an email to Alex. Sam explains: "It doesn't read your email like you do. It chops it into weird pieces. Watch." Shows tokenized email. Manager: "Why did it split 'quarterly' into three pieces?!"

---

## Lesson 02 — Embeddings: How LLMs Understand Meaning

### Learning Objective
Student understands that tokens become vectors (lists of numbers) that encode meaning, and that similar meanings = nearby vectors.

### Prerequisites
Lesson 01 — student knows about tokens.

### Lesson Flow

| Phase | Duration | What Happens |
|-------|----------|-------------|
| **Hook** | 1 min | "Tokens are just IDs — numbers. But how does the LLM know that 'happy' and 'joyful' mean similar things? The answer: embeddings." |
| **Concept** | 3 min | Dialogue explains: each token gets converted to a vector (list of hundreds of numbers). Similar meanings = nearby vectors in space. Analogy: city coordinates — Paris and London are closer to each other than to Tokyo. "King - Man + Woman ≈ Queen" as the classic example. |
| **Demo** | 1 min | Code example: compute similarity between "The cat sat on the mat" and "A feline rested on the rug" → 0.92 (very similar). Compare with "The stock market crashed" → 0.13 (not similar). |
| **Challenge** | 2 min | Student picks/types two sentences → compute cosine similarity → see the score. |
| **Reflection** | 1 min | "This is how search engines find relevant results without exact keyword matches. This is how RAG works — finding relevant documents for your question. We'll get to that in lesson 05." |

### Challenge Details
- **Input:** Two sentences (or pick from predefined list for reliable grading).
- **Grading:** Python + numpy computes cosine similarity with pre-computed embeddings.
- **Validation type:** `user_output_contains` — output must contain "similarity" with a score.
- **Pre-computed embeddings:** ~20 sentences baked into the Docker image covering various topics (animals, tech, food, weather, etc.)

### Key Teaching Moments
- Embeddings capture MEANING, not just spelling
- Similar concepts cluster together in vector space
- This is the foundation of semantic search and RAG
- Dimensions: real embeddings have 768-3072 dimensions (not just 2D)

### Narrative Notes
- **Sci-Fi:** Science Officer maps the intelligence's "meaning space." "Commander, I've plotted how ARIA organizes concepts. Look — 'star' and 'sun' are almost at the same coordinates. But 'star' and 'celebrity' are far apart. It understands context!"
- **Office Comedy:** Sam draws a map on the whiteboard. "Think of Alex's brain like a city. 'Budget' and 'finances' live on the same street. 'Budget' and 'sandwich' live in different neighborhoods. That's how it knows what you mean."

---

## Lesson 03 — Anatomy of a Call: Building the Request

### Learning Objective
Student can construct a complete LLM API request JSON with all required parameters, and understands what each parameter controls.

### Prerequisites
Lessons 00-02 — student understands tokens, embeddings, and has seen the LLM respond.

### Lesson Flow

| Phase | Duration | What Happens |
|-------|----------|-------------|
| **Hook** | 1 min | "You've talked to the LLM, seen its tokens, explored its meaning space. Now let's look under the hood: what does the actual request look like?" |
| **Concept** | 3 min | Dialogue walks through the full request structure: `model` (which LLM), `messages` array (roles: system, user, assistant), `temperature` (0=deterministic, 1=creative), `max_tokens` (response length limit), `top_p` (nucleus sampling). Explain the flow: your JSON → tokenize → neural network → sample next token → repeat → detokenize → response JSON. |
| **Demo** | 2 min | Full API request JSON shown with annotations explaining each field. |
| **Challenge** | 3 min | Student writes a complete API request JSON: model, messages with system + user roles, temperature, max_tokens. |
| **Reflection** | 1 min | "You just built what every LLM application sends behind the scenes. ChatGPT, Claude Code, Siri — they all construct this JSON. In the next lesson, you'll actually send it." |

### Challenge Details
- **Input:** Multi-line JSON (textarea).
- **Grading:** JSON validator checks:
  - Valid JSON syntax
  - Has `model` field (string)
  - Has `messages` array with at least 2 messages
  - Has message with `role: "system"` and `content`
  - Has message with `role: "user"` and `content`
  - Has `temperature` (number, 0-2 range)
  - Has `max_tokens` (integer, > 0)
- **Validation type:** `exact_match` — validator returns "PASS" or specific error.

### Key Teaching Moments
- The `messages` array is a conversation history — context matters
- `system` role sets behavior ("You are a helpful assistant" vs "You are a pirate")
- `temperature` controls randomness — 0 for code, 0.7 for creative writing
- `max_tokens` prevents runaway costs — always set a limit
- This is the OpenAI-compatible format used by Moonshot, Deepseek, and many others

### Narrative Notes
- **Sci-Fi:** Commander learns the "transmission protocol" to communicate with ARIA. Each field is a different part of the signal. Temperature = "how creative should the intelligence be in its interpretation?"
- **Office Comedy:** Manager learns the proper memo format for the AI department. "You can't just yell 'Hey Alex!' across the office. There's a protocol." Sam shows the JSON. "This is the memo template. system = job description, user = your request, temperature = how much creative freedom you give the intern."

---

## Lesson 04 — The API Layer: Calling It For Real

### Learning Objective
Student can make a real API call to an LLM using curl, and understands that different interfaces (curl, Java, Python, Chat UI) all use the same format.

### Prerequisites
Lesson 03 — student can construct the API request JSON.

### Lesson Flow

| Phase | Duration | What Happens |
|-------|----------|-------------|
| **Hook** | 1 min | "You built the JSON. Now let's SEND it. For real." |
| **Concept** | 3 min | Dialogue explains: the same JSON works everywhere. Show side by side: curl command, Java HttpClient code, Python requests code. All send the same JSON to the same endpoint. Mention: Moonshot uses OpenAI-compatible format, so does Deepseek — just change the URL. |
| **Demo** | 2 min | Full curl command with headers, JSON body, and expected response structure. Plus Java code example (for reference, not executed). |
| **Challenge** | 3 min | Student writes a curl command. Real API call to Moonshot. Real response shown. |
| **Reflection** | 1 min | "You just did what every AI application does. ChatGPT's web UI, Claude Code's terminal, a Java microservice — they all make this same call. The interface is different, the API is the same." |

### Challenge Details
- **Input:** Multi-line curl command (textarea).
- **Grading:**
  1. Validate curl syntax (contains required elements: URL, Content-Type header, Authorization header, JSON body)
  2. Execute real API call to Moonshot
  3. Show actual LLM response
- **Validation type:** `user_output_contains` — response must contain actual LLM output.
- **API key:** Injected by container from `LLM_API_KEY` env var. Student uses placeholder `$LLM_API_KEY` in their curl command.

### Key Teaching Moments
- One API format, many providers (Moonshot, Deepseek, OpenAI-compatible)
- One API format, many clients (curl, Java, Python, JavaScript)
- Show Java code: `HttpClient` + `HttpRequest` example (not executed, for reference)
- Show Deepseek endpoint as alternative (same format, different URL)
- Streaming vs non-streaming responses
- Response structure: `choices[0].message.content`

### Narrative Notes
- **Sci-Fi:** Commander sends the first "live transmission" to ARIA using the protocol they learned. Real response comes back. Crew cheers. "We have two-way communication!"
- **Office Comedy:** Manager finally sends the formal memo to Alex. Real response comes back. Manager is impressed. Sam: "Congrats, you just did what our entire AI platform does. Except our platform does it 10,000 times a day."

---

## Lesson 05 — Enhanced Prompts & RAG: What Really Happens

### Learning Objective
Student understands that production AI systems enhance the user's prompt before sending it to the LLM — adding system prompts, retrieved context (RAG), and instructions. Student can build an enhanced prompt.

### Prerequisites
All previous lessons — student understands the full pipeline.

### Lesson Flow

| Phase | Duration | What Happens |
|-------|----------|-------------|
| **Hook** | 1 min | "When you type 'What's our refund policy?' into a company chatbot, you think it just sends that to the LLM. It doesn't. Let me show you what REALLY gets sent." |
| **Concept** | 4 min | Dialogue reveals the real prompt: system message (persona + rules + guardrails) + retrieved context (the actual refund policy document, pulled from a database using embeddings from lesson 02!) + user's question. This is RAG: Retrieve relevant docs → Augment the prompt → Generate response. Also: tool/function calling concept. |
| **Demo** | 2 min | Side by side: what the user typed vs what actually gets sent to the LLM. The real prompt is 10x longer. Show how context injection dramatically improves response quality. |
| **Challenge** | 3 min | Student builds a full enhanced prompt JSON: system message (persona + rules), retrieved context (provided), user query. Real API call shows the response. Then compare with bare prompt (no context) — see the quality difference. |
| **Reflection** | 2 min | "Now you know the full picture. From tokens to vectors to API calls to enhanced prompts. Every AI product you use — ChatGPT, Claude, Copilot — does exactly this. You can build this yourself." |

### Challenge Details
- **Input:** Multi-line JSON (textarea) with messages array:
  - system: persona + rules + context
  - user: question
- **Grading:**
  1. JSON validator checks structure (system message with context, user message)
  2. Real API call with enhanced prompt → show response
  3. (Bonus in output) Show what bare prompt would produce for comparison
- **Validation type:** `exact_match` — validator returns "PASS" for structure, then API response shown.
- **Provided context:** A sample "company refund policy" document that the student must include in the system message.

### Key Teaching Moments
- Users see a simple chat box, but the real prompt is huge
- RAG connects to lesson 02 (embeddings) — "Remember similarity scores? That's how the system finds the right documents"
- System prompt = persona + rules + guardrails (prevents hallucination, stays on topic)
- This is why AI chatbots can answer about YOUR company's data without being retrained
- RAG vs fine-tuning: RAG is cheaper, faster to update, and works for most use cases

### Narrative Notes
- **Sci-Fi:** Commander discovers ARIA doesn't just receive their message — the ship's computer adds a "mission briefing" (system prompt) and "intelligence reports" (retrieved context) before transmitting. "We thought we were talking directly to the intelligence. We weren't. The ship was augmenting our signal." Commander builds the full transmission manually.
- **Office Comedy:** Manager discovers that when they email Alex, Sam's team adds a "briefing packet" before passing it on. "You think Alex reads your email? First, we attach the employee handbook, the relevant policy docs, and a note saying 'don't make stuff up.'" Manager: "So Alex never saw my raw email?" Sam: "Nobody sends raw prompts to production. That's lesson one of AI engineering."
