# Docker Tutorial — Curriculum

## Overview
- **Target:** Complete Docker beginners
- **Lessons:** 6
- **Narrative Styles:** Fairy Tale 🧙 + Flirting/Romance 💘
- **Core Mental Model:** Dockerfile → Image → Container (like .java → .class → JVM)
- **Grading Approach:** Hybrid — simulator for CLI commands, real validation for Dockerfiles and Compose files

## Lessons

### 00 — The Container Idea
- **Concept:** Why containers exist. The three-step process: Dockerfile → Image → Container.
- **Real-World:** "Works on my machine" problem — containers guarantee consistency.
- **Challenge:** Simulator — `docker --version`
- **Key Takeaway:** Containers are lightweight, portable, reproducible environments.

### 01 — Running Containers
- **Concept:** `docker run`, `docker ps`, `docker stop` — using existing images.
- **Real-World:** Spin up nginx or postgres in seconds, no installation.
- **Challenge:** Simulator — `docker run nginx`
- **Key Takeaway:** You can use containers immediately, before ever writing a Dockerfile.

### 02 — Your First Dockerfile
- **Concept:** `FROM`, `RUN`, `CMD` — writing the recipe.
- **Real-World:** Packaging a Node.js or Python app for deployment.
- **Challenge:** Write a Dockerfile — grader validates required instructions.
- **Key Takeaway:** A Dockerfile is just a text recipe that builds an image.

### 03 — Building & Layering
- **Concept:** `COPY`, `WORKDIR`, `EXPOSE`, image layers, build caching.
- **Real-World:** Why rebuilds are fast — layer reuse. Optimizing build order.
- **Challenge:** Write a Dockerfile with more instructions — grader validates.
- **Key Takeaway:** Order matters. Each instruction creates a cached layer.

### 04 — Volumes & Ports
- **Concept:** `-v` for persistent data, `-p` for port mapping, networking basics.
- **Real-World:** Database that survives container restarts. Exposing an API to the world.
- **Challenge:** Simulator — run with `-v` and `-p` flags.
- **Key Takeaway:** Containers are ephemeral by default. Volumes and ports connect them to the real world.

### 05 — Compose: Multi-Container Apps
- **Concept:** `docker-compose.yml`, services, networks, linking containers.
- **Real-World:** Web app + PostgreSQL database running together — what you'd actually deploy.
- **Challenge:** Write a docker-compose.yml — grader validates structure and services.
- **Key Takeaway:** Real apps are multiple containers working together. Compose makes that easy.

## Narrative Styles

### 🧙 Fairy Tale
- Dockerfile = magic recipe / spell scroll
- Image = enchanted blueprint
- Container = summoned creature
- Volumes = treasure chests that persist between summons
- Compose = assembling your party of creatures
- Characters: The Wizard, the Apprentice, talking animals, etc.

### 💘 Flirting / Romance
- Dockerfile = dating profile
- Image = your ideal type
- Container = the actual date
- Volumes = moving your stuff into their place
- Compose = moving in together
- Characters: Flirty narrators, awkward first dates, love interests

## Technical Implementation

### Docker Image (`docker/docker/Dockerfile`)
- Alpine-based image with:
  - Mock `docker` CLI script (bash) for simulator lessons
  - Dockerfile parser/validator (Python or bash) for lessons 02-03
  - YAML validator for lesson 05

### Grading Strategy
| Lesson | Type | Validation |
|--------|------|------------|
| 00 | Simulator | Output contains version string |
| 01 | Simulator | Output contains expected run/ps output |
| 02 | Dockerfile validation | Check for FROM, RUN, CMD |
| 03 | Dockerfile validation | Check for COPY, WORKDIR, EXPOSE + above |
| 04 | Simulator | Output contains port/volume mapping |
| 05 | YAML validation | Check for services, image/build, ports |
