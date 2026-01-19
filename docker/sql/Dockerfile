# /docker/sql/Dockerfile

FROM alpine:latest

# Install SQLite3
RUN apk add --no-cache sqlite

# Create data directory
RUN mkdir -p /data

# Copy the company database
COPY company.db /data/company.db

# Create backup copy for state resets
RUN cp /data/company.db /data/company.db.original

# Set working directory
WORKDIR /data

# Ensure database files are readable
RUN chmod 644 /data/company.db /data/company.db.original

# The environment is now ready to execute SQL commands via sqlite3
