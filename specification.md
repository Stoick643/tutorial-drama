
A... SPECIFICATION

***

### ## Project Specification: The Narrative Learning Engine

#### ### 1. Vision & Goal
To create an interactive, web-based learning platform that teaches technical subjects (like Redis, Git, Docker) through engaging, narrative-driven tutorials. The goal is to make learning code feel like playing a game or reading a story, dramatically increasing user engagement and knowledge retention.

---
#### ### 2. Core Features
* **Narrative-Driven Content:** Tutorials are presented as dialogues or stories in various styles (e.g., detective, sci-fi).
* **Multi-Topic & Multi-Style:** The platform is architected to support numerous topics and thematic "skins."
* **Interactive Code Execution:** Users can run code directly in the browser and get instant feedback from a sandboxed environment.
* **Decoupled Architecture:** Content (JSON), presentation (HTML/CSS), and logic (Python) are separate, allowing for scalability.

---
#### ### 3. Technical Architecture
* **Backend:** Python with **FastAPI**.
* **Frontend:** **Jinja2** for templating, with standard HTML, CSS, and JavaScript.
* **Content Format:** **JSON** files, structured to support multiple narrative styles per lesson.
* **Content Storage:** **Flat files** managed within a **Git repository** ("content-as-code").
* **Executor/Grader Service:** A separate microservice that uses **Docker** to create secure, isolated environments for running and verifying user code.
* **Deployment:** Git-based deployment to a cloud platform like **Render**.



---
#### ### 4. Content Strategy
* **Initial Topics:**
    * Redis
    * Git
    * Docker
    * Python
    * DevOps
    * SQL
* **Initial Styles:**
 q

---
#### ### 5. Phased Development Plan (Roadmap)
1.  **Phase 1 (MVP - Crawl):** Build the core FastAPI application with the Jinja2 template engine. Implement the first tutorial (**Redis**) with one style (**Detective Noir**). Use a simple, shared Redis sandbox for the interactive challenges.
2.  **Phase 2 (Scale - Walk):** Develop the generic, Docker-based **Executor/Grader Service**. Add a second tutorial topic (**Git** or **SQL**) to prove the multi-topic architecture.
3.  **Phase 3 (Enrich - Run):** Add multiple new **styles** for existing tutorials. Begin development of user accounts for progress tracking.


B... EXAMPLE 
Here is a complete example for the first real lesson of the Redis tutorial, covering both the raw text and its final JSON format.

-----

### \#\# a) Tutorial as Text (Detective Noir Style)

**Title: The Ephemeral Lead**

**Concept:** Using Strings for basic key-value storage (`SET`, `GET`) and setting an expiry (`SETEX`).

**(The scene opens in Detective Indecks' dark office. The phone rings.)**

**Detective Indecks:** "Indecks."

**REDIS:** "Got a new lead for you, detective. A shadowy figure, `user789`. We need to track them, but only when they're active. We can't waste resources tailing them when they go dark."

**Detective Indecks:** "So I need a way to put a temporary tag on them. What's the tool?"

**REDIS:** "The simplest tool in the box. A basic key-value pair. You give me a key, like `online:user789`, and a value, like 'active'. My `SET` command handles it. If you need to check the status, you just ask me with `GET online:user789`."

**Detective Indecks:** "But you said temporary. What if I forget to remove the tag? The lead goes cold, but my board still says they're active. Sloppy work."

**REDIS:** "That's why you don't use `SET`. You use `SETEX`—SET with Expiry. You give me the key, the number of seconds to keep the lead alive, and the value. For example: `SETEX online:user789 300 "active"`. In 5 minutes (300 seconds), that record vanishes. No loose ends. No sloppy work."

**Detective Indecks:** "Clean. I like it. Let's put it to the test."

-----

### **Your Assignment (The Challenge):**

A new person of interest, `user456`, just came online. Mark their status as 'online' but make sure the lead goes cold (expires) in exactly 2 minutes (120 seconds).

**Hint:** You need the command that sets a key with an expiry time, all in one clean operation.

-----

### \#\# b) Text Transformed into JSON Format

Here is how the above text and challenge would be structured in your `tutorials/redis/01_strings.json` file.

```json
{
  "tutorial": "Redis Basics",
  "module": 1,
  "scene": 1,
  "technical_concept": "Using Strings for basic key-value storage with SET, GET, and SETEX for expiry.",
  "code_example": {
    "language": "redis-cli",
    "code": "SETEX online:user789 300 \"active\""
  },
  "challenge": {
    "task": "A new person of interest, `user456`, just came online. Mark their status as 'online' but make sure the lead goes cold (expires) in exactly 2 minutes (120 seconds).",
    "hint": "You need the command that sets a key with an expiry time, all in one clean operation.",
    "check": {
      "command": "TTL online:user456",
      "expected_output_type": "integer_greater_than",
      "expected_output_value": 110 
    }
  },
  "styles": [
    {
      "name": "detective_noir",
      "title": "The Ephemeral Lead",
      "dialogue": [
        {
          "character": "Detective Indecks",
          "line": "Indecks."
        },
        {
          "character": "REDIS",
          "line": "Got a new lead for you, detective. A shadowy figure, `user789`. We need to track them, but only when they're active. We can't waste resources tailing them when they go dark."
        },
        {
          "character": "Detective Indecks",
          "line": "So I need a way to put a temporary tag on them. What's the tool?"
        },
        {
          "character": "REDIS",
          "line": "The simplest tool in the box. A basic key-value pair. You give me a key, like `online:user789`, and a value, like 'active'. My `SET` command handles it. If you need to check the status, you just ask me with `GET online:user789`."
        },
        {
          "character": "Detective Indecks",
          "line": "But you said temporary. What if I forget to remove the tag? The lead goes cold, but my board still says they're active. Sloppy work."
        },
        {
          "character": "REDIS",
          "line": "That's why you don't use `SET`. You use `SETEX`—SET with Expiry. You give me the key, the number of seconds to keep the lead alive, and the value. For example: `SETEX online:user789 300 \"active\"`. In 5 minutes (300 seconds), that record vanishes. No loose ends. No sloppy work."
        },
        {
          "character": "Detective Indecks",
          "line": "Clean. I like it. Let's put it to the test."
        }
      ]
    }
  ]
}
```


C... FILE STRUCTURE

/redi-tutorial-project
├── /app
│   └── main.py
├── /static
│   ├── styles.css
│   └── interactive.js
├── /templates
│   └── tutorial_template.html
└── /tutorials
    └── /redis
        ├── 00_setup.json
        └── 01_strings.json