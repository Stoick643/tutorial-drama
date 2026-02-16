# /docker/llm/Dockerfile
# ABOUTME: Grader image for LLM internals tutorial.
# ABOUTME: Contains real tokenizer, embedding similarity, API caller, and validators.

FROM python:3.12-alpine

# Install curl for API call lessons
RUN apk add --no-cache curl

# Install Python packages
RUN pip install --no-cache-dir tiktoken numpy

# Create data directory
RUN mkdir -p /data /scripts

# Copy pre-computed embeddings
COPY embeddings.json /data/embeddings.json

# Copy all Python scripts
COPY llm_dispatch.py /scripts/llm_dispatch.py
COPY call_llm.py /scripts/call_llm.py
COPY tokenize_text.py /scripts/tokenize_text.py
COPY compute_similarity.py /scripts/compute_similarity.py
COPY validate_api_request.py /scripts/validate_api_request.py

# Create executable entry points
RUN echo '#!/bin/sh' > /usr/local/bin/llm-dispatch && \
    echo 'cd /scripts && python llm_dispatch.py "$@"' >> /usr/local/bin/llm-dispatch && \
    chmod +x /usr/local/bin/llm-dispatch

RUN echo '#!/bin/sh' > /usr/local/bin/tokenize-text && \
    echo 'cd /scripts && python -c "from tokenize_text import tokenize; import sys; print(tokenize(open(sys.argv[1]).read().strip()))" "$@"' >> /usr/local/bin/tokenize-text && \
    chmod +x /usr/local/bin/tokenize-text

RUN echo '#!/bin/sh' > /usr/local/bin/compute-similarity && \
    echo 'cd /scripts && python -c "from compute_similarity import compute; import sys; print(compute(open(sys.argv[1]).read().strip()))" "$@"' >> /usr/local/bin/compute-similarity && \
    chmod +x /usr/local/bin/compute-similarity

RUN echo '#!/bin/sh' > /usr/local/bin/call-llm && \
    echo 'cd /scripts && python -c "from call_llm import call_llm; import sys; print(call_llm(open(sys.argv[1]).read().strip()))" "$@"' >> /usr/local/bin/call-llm && \
    chmod +x /usr/local/bin/call-llm

RUN echo '#!/bin/sh' > /usr/local/bin/call-llm-json && \
    echo 'cd /scripts && python -c "from call_llm import call_llm_from_json; import sys; print(call_llm_from_json(open(sys.argv[1]).read().strip()))" "$@"' >> /usr/local/bin/call-llm-json && \
    chmod +x /usr/local/bin/call-llm-json

RUN echo '#!/bin/sh' > /usr/local/bin/validate-api-request && \
    echo 'cd /scripts && python validate_api_request.py "$@"' >> /usr/local/bin/validate-api-request && \
    chmod +x /usr/local/bin/validate-api-request

WORKDIR /workspace
