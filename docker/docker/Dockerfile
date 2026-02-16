# /docker/docker/Dockerfile
# ABOUTME: Grader image for Docker tutorials.
# ABOUTME: Contains mock docker CLI, Dockerfile validator, and Compose validator.

FROM python:3.12-alpine

# Install PyYAML for compose validation
RUN pip install --no-cache-dir pyyaml

# Install mock docker CLI
COPY mock_docker.sh /usr/local/bin/docker
RUN chmod +x /usr/local/bin/docker

# Install validators
COPY validate_dockerfile.py /usr/local/bin/validate-dockerfile
COPY validate_compose.py /usr/local/bin/validate-compose
RUN chmod +x /usr/local/bin/validate-dockerfile /usr/local/bin/validate-compose

# Create working directory for user input
RUN mkdir -p /workspace
WORKDIR /workspace

# The environment is now ready to:
# - Simulate docker CLI commands (mock_docker.sh)
# - Validate Dockerfiles (validate_dockerfile.py)
# - Validate docker-compose.yml (validate_compose.py)
