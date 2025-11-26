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

| Agent | Role | Model | Purpose |
|-------|------|-------|---------|
| architect | Visionario | opus | Diseña arquitectura, ve el futuro |
| critic | Cuestionador | opus | Desafía decisiones, encuentra fallas |
| explorer | Investigador | opus | Explora código antes de modificar |
| memory | Memoria | opus | Recuerda entre sesiones |
| coder | Implementador | sonnet | Escribe código |
| tester | Verificador | sonnet | Testing visual con Playwright |
| stuck | Escalador | sonnet | Consulta al humano |

## Notes
- Sistema diseñado para compensar debilidades tanto del humano como de la IA
- Todos los agentes de "pensamiento" usan Opus para razonamiento profundo
- Escalación obligatoria al humano via stuck agent - NO FALLBACKS
