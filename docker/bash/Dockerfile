# /docker/bash/Dockerfile

FROM alpine:latest

# Install bash and common tools
RUN apk add --no-cache bash coreutils findutils grep sed gawk

# Create workspace with sample files for lessons
RUN mkdir -p /workspace/subdir /workspace/logs

# server.log for grep lessons (lesson 02)
RUN printf '2024-01-15 10:23:01 error connection refused from 192.168.1.50\n\
2024-01-15 10:23:15 info server started on port 8080\n\
2024-01-15 10:24:02 warning disk space low\n\
2024-01-15 10:25:33 ERROR timeout waiting for response\n\
2024-01-15 10:26:01 info request processed successfully\n\
2024-01-15 10:27:45 error connection reset by peer\n\
2024-01-15 10:28:00 info health check passed\n' > /workspace/server.log

# access.log for pipe lessons (lesson 03) - 6 unique lines after sort|uniq
RUN printf '192.168.1.10 GET /index.html 200\n\
10.0.0.5 GET /about.html 200\n\
192.168.1.10 GET /index.html 200\n\
10.0.0.5 POST /api/data 201\n\
192.168.1.20 GET /style.css 200\n\
10.0.0.5 GET /about.html 200\n\
192.168.1.30 GET /contact.html 404\n\
192.168.1.40 GET /login.html 200\n\
192.168.1.30 GET /contact.html 404\n' > /workspace/access.log

# Some .tmp files for xargs lesson (lesson 04)
RUN touch /workspace/junk1.tmp /workspace/junk2.tmp /workspace/subdir/junk3.tmp

# Set working directory
WORKDIR /workspace

# Default shell is bash
CMD ["/bin/bash"]
