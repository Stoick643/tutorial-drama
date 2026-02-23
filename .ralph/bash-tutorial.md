# Bash Tutorial - Build Complete Tutorial

## Goals
- Create 8 bash lessons (00-07) with Survival Adventure + Heist/Spy narrative styles
- Create Docker grader image for bash
- Wire up grading in docker_manager.py + subprocess_manager.py
- Add bash card to index.html and menu support

## Checklist
- [x] Study existing lesson JSON format (redis/sql lessons as reference)
- [x] Study existing docker grader images
- [x] Study docker_manager.py and subprocess_manager.py patterns
- [x] Create tutorials/bash/ directory
- [x] Create lesson 00 - Where Am I? (pwd, ls, cd, mkdir) - graded
- [x] Create lesson 01 - Creating & Destroying (touch, cat, rm, cp/mv) - graded
- [x] Create lesson 02 - Finding Needles (grep, find) - graded
- [x] Create lesson 03 - The Pipe Revolution (|, head/tail, sort/uniq) - graded
- [x] Create lesson 04 - Power Pipes: xargs (xargs, find|xargs, complex pipelines) - graded
- [x] Create lesson 05 - Text Surgery (sed, awk) - graded
- [x] Create lesson 06 - The Toolbelt (chmod, curl/wget, history, alias, top) - chat mode
- [x] Create lesson 07 - Your First Script (#!/bin/bash, variables, read, script) - graded multiline
- [x] Create docker/bash/Dockerfile
- [x] Wire up docker_manager.py
- [x] Wire up subprocess_manager.py
- [x] Add bash card to index.html
- [x] Update README.md and Roadmap.md

## Verification
- Docker image `grader-image-bash` builds successfully
- Lesson 00: `mkdir camp && ls -d camp` → "camp" ✓
- Lesson 01: `echo SOS > signal.txt && cp signal.txt backup.txt` → validation "SOS\nSOS" ✓
- Lesson 02: `grep -i ERROR server.log` → contains "error" and "connection" ✓
- Lesson 03: `cat access.log | sort | uniq | wc -l` → contains "6" ✓
- Lesson 04: `find . -name "*.tmp" | xargs rm` → validation finds no .tmp files ✓
- Lesson 05: `awk '{print $1}' access.log | sort | uniq -c` → contains "192.168" and "10.0" ✓
- Lesson 06: chat mode, no grading ✓
- Lesson 07: multiline script creates mysite/, outputs "index.html", "style.css", "Done!" ✓
- All 8 JSON files parse correctly
- docker_manager.py: GRADER_IMAGES, _build_command, return_container updated
- subprocess_manager.py: workspace init, _execute_bash, _reset_state, sanitization updated

## Notes
- All work completed in the pre-loop phase
- Narrative styles: Survival Adventure + Heist/Spy
- Lessons 00-05, 07 graded; lesson 06 chat mode
- Pipe focus in lessons 03-04 (xargs is the star)
- Lesson 07 finale: write a bash script (multiline)
