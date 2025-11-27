#!/bin/bash

# Claude Agents Elite - Installation Script
# Usage: ./install.sh /path/to/your/project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Target directory (argument or current directory)
TARGET_DIR="${1:-.}"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         Claude Agents Elite - Installation                ║"
echo "║                   17 Specialized Agents                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}Error: Directory '$TARGET_DIR' does not exist${NC}"
    exit 1
fi

# Convert to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo -e "${YELLOW}Installing to: ${TARGET_DIR}${NC}"
echo ""

# Check if .claude already exists
if [ -d "$TARGET_DIR/.claude" ]; then
    echo -e "${YELLOW}Warning: .claude directory already exists${NC}"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Installation cancelled${NC}"
        exit 1
    fi
    rm -rf "$TARGET_DIR/.claude"
fi

# Copy .claude directory
echo -e "${BLUE}Copying agents...${NC}"
cp -r "$REPO_DIR/.claude" "$TARGET_DIR/"

# Create memory directory if it doesn't exist
mkdir -p "$TARGET_DIR/.claude/memory"

# Initialize project memory
if [ ! -f "$TARGET_DIR/.claude/memory/project.md" ]; then
    echo -e "${BLUE}Initializing project memory...${NC}"
    cat > "$TARGET_DIR/.claude/memory/project.md" << 'EOF'
# Project Memory

## Last Updated
$(date +%Y-%m-%d)

## Project Overview
- **Name**: [Project Name]
- **Type**: [Web App/API/CLI/etc.]
- **Stack**: [Technologies used]
- **Started**: $(date +%Y-%m-%d)

## Key Decisions

### Architecture
| Date | Decision | Rationale | Made By |
|------|----------|-----------|---------|

### Technology Choices
| Technology | Purpose | Why Chosen | Alternatives Rejected |
|------------|---------|------------|----------------------|

## Mistakes & Lessons

### Bugs Fixed
| Date | Bug | Root Cause | Solution | Prevention |
|------|-----|------------|----------|------------|

## User Preferences

### Code Style
- [To be defined]

### Communication
- [To be defined]

## Notes
- Claude Agents Elite system installed
- 17 specialized agents available
- Escalation via stuck agent mandatory
EOF
fi

# Count agents
AGENT_COUNT=$(ls -1 "$TARGET_DIR/.claude/agents/"*.md 2>/dev/null | wc -l)

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Installation Complete!                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BLUE}Location:${NC} $TARGET_DIR/.claude/"
echo -e "  ${BLUE}Agents:${NC}   $AGENT_COUNT agents installed"
echo ""
echo -e "  ${YELLOW}Agents by category:${NC}"
echo -e "    Core:    architect, critic, explorer, memory, coder, tester, stuck"
echo -e "    Quality: security, debugger, reviewer, performance"
echo -e "    Domain:  frontend, backend, database, data-sync, devops, api-designer"
echo ""
echo -e "  ${YELLOW}Next steps:${NC}"
echo -e "    1. Run 'claude' in your project directory"
echo -e "    2. The agents will be automatically loaded"
echo -e "    3. Start with: 'memory, recall project context'"
echo ""
echo -e "  ${BLUE}Documentation:${NC} $REPO_DIR/README.md"
echo ""
