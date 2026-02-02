#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  EndeeSync - Docker Startup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH.${NC}"
    exit 1
fi

echo -e "${BLUE}Building and starting containers...${NC}"
docker-compose up --build -d

echo -e "\n${GREEN}✓ System is running!${NC}"
echo -e "${GREEN}frontend/Backend: http://localhost:8000${NC}"
echo -e "${GREEN}Endee Server:     http://localhost:8080${NC}"
echo -e "${BLUE}Logs follow (Press Ctrl+C to stop trailing logs)...${NC}\n"

docker-compose logs -f
