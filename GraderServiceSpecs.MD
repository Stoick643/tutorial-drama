Here is a project description for the grader-service for future reference.

## Project Description: Grader Service
The Grader Service is a standalone, backend microservice designed to function as a universal code execution engine. Its sole purpose is to receive code submissions via an API, run the code in a secure and isolated sandboxed environment, and return the output and a pass/fail verdict. It acts as the "backstage crew" for the main tutorial-drama learning platform.

Licensed by Google

## Current Status
Architecture: The service is a FastAPI application, architected to be a stateless, private web service.

Core Logic: It has a working /grade endpoint that accepts a JSON payload containing the language, user code, and validation logic.

Isolation Technology: It uses Docker to create sandboxed environments. The container management logic is designed to use a container pooling strategy for high performance.

Language Support: The service is fully implemented for its first language: Redis. It uses a pre-built Docker image with redis-cli to execute and validate Redis commands.

Testing: The service has been successfully tested in isolation using curl and has been integrated with the main tutorial-drama application.

## Anticipated Scope
The service is designed to be a generic and scalable platform. The anticipated scope includes:

Multi-Language Support: The immediate next step is to add support for SQL (via SQLite). Future planned languages include Git, Docker (using a simulator), Python, and general Bash/Shell scripting.

Advanced Grading Logic: The current grading mechanism is basic. The scope includes developing a more robust "grading dispatcher" that can handle more complex validation types (e.g., checking for partial string matches, evaluating numeric ranges, or checking multi-line output).

Resource Management: As the service scales, the scope includes implementing more sophisticated container pool management, such as dynamically scaling the number of warm containers based on traffic.

Security Hardening: Implementing stricter security policies, such as running containers with minimal privileges and setting tighter resource limits (CPU, memory) to prevent abuse.