#!/bin/sh
# ABOUTME: Mock Docker CLI that simulates docker commands for tutorial lessons.
# ABOUTME: Returns realistic output for common docker commands without needing real Docker.

COMMAND="$1"
SUBCOMMAND="$2"
shift 2 2>/dev/null
ARGS="$@"

case "$COMMAND" in
    --version)
        echo "Docker version 24.0.7, build afdd53b"
        ;;
    --help)
        echo "Usage:  docker [OPTIONS] COMMAND"
        echo ""
        echo "A self-sufficient runtime for containers"
        echo ""
        echo "Common Commands:"
        echo "  run         Create and run a new container"
        echo "  ps          List containers"
        echo "  images      List images"
        echo "  pull        Download an image from a registry"
        echo "  build       Build an image from a Dockerfile"
        echo "  stop        Stop running containers"
        echo "  rm          Remove containers"
        ;;
    info)
        echo "Client: Docker Engine - Community"
        echo " Version:    24.0.7"
        echo " Context:    default"
        echo ""
        echo "Server: Docker Engine - Community"
        echo " Containers: 3"
        echo "  Running: 2"
        echo "  Paused:  0"
        echo "  Stopped: 1"
        echo " Images: 5"
        echo " Server Version: 24.0.7"
        echo " Storage Driver: overlay2"
        echo " Operating System: Alpine Linux v3.19"
        echo " Architecture: x86_64"
        ;;
    run)
        case "$SUBCOMMAND" in
            hello-world|"--name"*"hello-world"*)
                echo ""
                echo "Hello from Docker!"
                echo "This message shows that your installation appears to be working correctly."
                echo ""
                echo "To generate this message, Docker took the following steps:"
                echo " 1. The Docker client contacted the Docker daemon."
                echo " 2. The Docker daemon pulled the \"hello-world\" image from the Docker Hub."
                echo " 3. The Docker daemon created a new container from that image."
                echo " 4. The Docker daemon streamed that output to the Docker client."
                echo ""
                echo "For more examples and ideas, visit:"
                echo " https://docs.docker.com/get-started/"
                ;;
            nginx|"--name"*"nginx"*|"-d"*|"-p"*)
                # Handle various flag combinations for nginx
                CONTAINER_ID="a1b2c3d4e5f6"
                if echo "$SUBCOMMAND $ARGS" | grep -q "nginx"; then
                    echo "$CONTAINER_ID"
                    echo "Unable to find image 'nginx:latest' locally"
                    echo "latest: Pulling from library/nginx"
                    echo "Digest: sha256:abc123def456..."
                    echo "Status: Downloaded newer image for nginx:latest"
                    echo "$CONTAINER_ID"
                else
                    echo "$CONTAINER_ID"
                fi
                ;;
            postgres*|"-e"*)
                CONTAINER_ID="b2c3d4e5f6a7"
                echo "$CONTAINER_ID"
                ;;
            alpine*|busybox*)
                echo "Hello from Alpine!"
                ;;
            *)
                echo "Unable to find image '$SUBCOMMAND' locally"
                echo "Error: pull access denied for $SUBCOMMAND, repository does not exist"
                exit 1
                ;;
        esac
        ;;
    ps)
        if [ "$SUBCOMMAND" = "-a" ] || [ "$SUBCOMMAND" = "--all" ]; then
            echo "CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS                     PORTS     NAMES"
            echo "a1b2c3d4e5f6   nginx     \"/docker-entrypoint.…\"   2 minutes ago   Up 2 minutes               80/tcp    web-server"
            echo "b2c3d4e5f6a7   postgres  \"docker-entrypoint.s…\"   5 minutes ago   Up 5 minutes               5432/tcp  my-database"
            echo "c3d4e5f6a7b8   alpine    \"/bin/sh\"                10 minutes ago  Exited (0) 8 minutes ago             relaxed_pike"
        else
            echo "CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS     NAMES"
            echo "a1b2c3d4e5f6   nginx     \"/docker-entrypoint.…\"   2 minutes ago   Up 2 minutes   80/tcp    web-server"
            echo "b2c3d4e5f6a7   postgres  \"docker-entrypoint.s…\"   5 minutes ago   Up 5 minutes   5432/tcp  my-database"
        fi
        ;;
    images)
        echo "REPOSITORY   TAG       IMAGE ID       CREATED        SIZE"
        echo "nginx        latest    a8758716bb6a   2 weeks ago    187MB"
        echo "postgres     15        3b1a7a6b3b1a   3 weeks ago    379MB"
        echo "alpine       latest    c1aabb73d233   4 weeks ago    7.38MB"
        echo "hello-world  latest    d2c94e258dcb   8 months ago   13.3kB"
        ;;
    pull)
        IMAGE="${SUBCOMMAND:-unknown}"
        echo "Using default tag: latest"
        echo "latest: Pulling from library/$IMAGE"
        echo "a2abf6c4d29d: Pull complete"
        echo "b8d5e9c1a3f2: Pull complete"
        echo "c7e4f8d2b1a0: Pull complete"
        echo "Digest: sha256:abc123def456789..."
        echo "Status: Downloaded newer image for $IMAGE:latest"
        echo "docker.io/library/$IMAGE:latest"
        ;;
    build)
        echo "Sending build context to Docker daemon  2.048kB"
        echo "Step 1/3 : FROM python:3.12-slim"
        echo " ---> a1b2c3d4e5f6"
        echo "Step 2/3 : COPY . /app"
        echo " ---> Using cache"
        echo " ---> b2c3d4e5f6a7"
        echo "Step 3/3 : CMD [\"python\", \"app.py\"]"
        echo " ---> c3d4e5f6a7b8"
        echo "Successfully built c3d4e5f6a7b8"
        echo "Successfully tagged my-app:latest"
        ;;
    stop)
        echo "${SUBCOMMAND:-container}"
        ;;
    rm)
        echo "${SUBCOMMAND:-container}"
        ;;
    *)
        echo "docker: '$COMMAND' is not a docker command."
        echo "See 'docker --help'"
        exit 1
        ;;
esac
