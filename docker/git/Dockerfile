# /docker/git/Dockerfile

FROM alpine:latest

# Install git
RUN apk add --no-cache git

# Create and initialize a repository
RUN mkdir /repo && cd /repo && git init && git config user.email "test@test.com" && git config user.name "Test"

# Set working directory
WORKDIR /repo

# The environment is now ready to execute git commands
