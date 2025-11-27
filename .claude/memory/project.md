# Project Memory - Claude Agents Elite

## Last Updated
2024-11-26

## Project Overview
- **Name**: Claude Agents Elite
- **Type**: Agent System / Template Repository
- **Stack**: Markdown agents for Claude Code
- **Started**: 2024-11-26

## Key Decisions

### Architecture
| Date | Decision | Rationale | Made By |
|------|----------|-----------|---------|
| 2024-11-26 | 17 agentes organizados en 3 categorias | Balance entre cobertura y eficiencia | Human + AI |
| 2024-11-26 | Opus para pensamiento, Sonnet para ejecucion | Optimizar calidad vs velocidad | Human + AI |
| 2024-11-26 | Registry JSON para routing automatico | Facilitar seleccion de agentes | Human + AI |

### Technology Choices
| Technology | Purpose | Why Chosen | Alternatives Rejected |
|------------|---------|------------|----------------------|
| Opus model | Agentes de analisis (14) | Mayor capacidad de razonamiento | Sonnet (menos profundo) |
| Sonnet model | Agentes de ejecucion (3) | Balance velocidad/calidad | Haiku (muy limitado) |
| JSON registry | Routing y workflows | Facil de modificar y extender | YAML (menos compatible) |

### Patterns & Conventions
| Area | Convention | Example |
|------|------------|---------|
| Agentes | Archivos .md en .claude/agents/ | architect.md |
| Memoria | project.md en .claude/memory/ | Este archivo |
| Templates | .claude/templates/ | new-agent.md |
| Documentacion | docs/ | WORKFLOWS.md |

## Agent Categories

### Core (7 agents)
- architect, critic, explorer, memory (Opus)
- coder, tester, stuck (Sonnet)

### Quality (4 agents)
- security, debugger, reviewer, performance (all Opus)

### Domain (6 agents)
- frontend, backend, database, data-sync, devops, api-designer (all Opus)

## Notes
- Sistema disenado para maxima calidad y eficiencia
- Escalacion humana obligatoria via stuck agent
- Sin fallbacks ni workarounds permitidos
- Registry permite routing automatico por keywords
- Workflows predefinidos para tareas comunes
