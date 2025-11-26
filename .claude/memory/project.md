# Project Memory

## Last Updated
2024-11-26

## Project Overview
- **Name**: Saca-visitas
- **Type**: [pendiente definir]
- **Stack**: [pendiente definir]
- **Started**: 2024-11-26

## Key Decisions

### Architecture
| Date | Decision | Rationale | Made By |
|------|----------|-----------|---------|
| 2024-11-26 | Implementar sistema de agentes Claude Code | Mejor organización, escalación humana obligatoria, testing visual | Human |

### Technology Choices
| Technology | Purpose | Why Chosen | Alternatives Rejected |
|------------|---------|------------|----------------------|
| Opus model | Agentes de pensamiento profundo (architect, critic, explorer, memory) | Mayor capacidad de razonamiento | Sonnet (menos profundo) |
| Sonnet model | Agentes de ejecución (coder, tester, stuck) | Balance velocidad/calidad | Haiku (muy limitado) |
| Playwright MCP | Testing visual | Screenshots reales, verificación visual | Testing manual |

### Patterns & Conventions
| Area | Convention | Example |
|------|------------|---------|
| Agentes | Archivos .md en .claude/agents/ | .claude/agents/coder.md |
| Memoria | Archivo en .claude/memory/ | .claude/memory/project.md |

## Mistakes & Lessons

### Bugs Fixed
| Date | Bug | Root Cause | Solution | Prevention |
|------|-----|------------|----------|------------|
| - | - | - | - | - |

### Failed Approaches
| Date | What We Tried | Why It Failed | Lesson |
|------|---------------|---------------|--------|
| - | - | - | - |

## User Preferences

### Code Style
- [pendiente definir]

### Communication
- Usuario prefiere español
- Explicaciones claras y directas
- Gusta de diagramas ASCII

### Priorities
- Agentes que superen limitaciones de la IA
- Sistema robusto con escalación humana
- Sin fallbacks ni workarounds

## Ongoing Issues

### Known Bugs
| Issue | Status | Workaround |
|-------|--------|------------|
| - | - | - |

### Technical Debt
| Debt | Impact | Plan |
|------|--------|------|
| - | - | - |

## External Dependencies

### APIs
| API | Purpose | Credentials Location | Rate Limits |
|-----|---------|---------------------|-------------|
| - | - | - | - |

### Services
| Service | Purpose | Config |
|---------|---------|--------|
| Playwright MCP | Testing visual | .mcp.json |

## Session History

### Recent Sessions
| Date | What Was Done | Outcome |
|------|---------------|---------|
| 2024-11-26 | Creación sistema de agentes | 7 agentes implementados: architect, critic, explorer, memory, coder, tester, stuck |

## Agents Implemented

### Core Agents (7)
| Agent | Role | Model | Purpose |
|-------|------|-------|---------|
| architect | Visionario | opus | Diseña arquitectura, ve el futuro |
| critic | Cuestionador | opus | Desafía decisiones, encuentra fallas |
| explorer | Investigador | opus | Explora código antes de modificar |
| memory | Memoria | opus | Recuerda entre sesiones |
| coder | Implementador | sonnet | Escribe código |
| tester | Verificador | sonnet | Testing visual con Playwright |
| stuck | Escalador | sonnet | Consulta al humano |

### Quality Agents (4)
| Agent | Role | Model | Purpose |
|-------|------|-------|---------|
| security | Guardian | opus | Audita seguridad, encuentra vulnerabilidades |
| debugger | Detective | opus | Encuentra causa raíz de bugs |
| reviewer | Revisor | opus | Code review antes de merge |
| performance | Optimizador | opus | Identifica y resuelve cuellos de botella |

### Domain Agents (6)
| Agent | Role | Model | Purpose |
|-------|------|-------|---------|
| frontend | Artista UI | opus | HTML, CSS, React, Vue, UI/UX, responsive |
| backend | Servidor | opus | Node.js, APIs, REST, GraphQL, auth |
| database | Datos | opus | PostgreSQL, MySQL, queries, migrations |
| data-sync | Puente | opus | Excel↔DB, Access↔DB, ETL, fotos/OLE |
| devops | Infra | opus | Docker, CI/CD, GitHub Actions, cloud |
| api-designer | Contratos | opus | OpenAPI, REST design, documentación |

### Summary
- **Total Agents**: 17
- **Opus Model**: 14 agents
- **Sonnet Model**: 3 agents

### Registry
- Archivo: `.claude/agents-registry.json`
- Funcionalidad: Routing automático por keywords, workflows predefinidos

## Agent Sources
- security, debugger, reviewer, performance: Basados en mejores prácticas de:
  - [wshobson/agents](https://github.com/wshobson/agents)
  - [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
  - [vanzan01/claude-code-sub-agent-collective](https://github.com/vanzan01/claude-code-sub-agent-collective)

## Notes
- Sistema diseñado para compensar debilidades tanto del humano como de la IA
- Todos los agentes de "pensamiento" usan Opus para razonamiento profundo
- Escalación obligatoria al humano via stuck agent - NO FALLBACKS
