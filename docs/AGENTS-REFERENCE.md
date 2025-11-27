# Agents Reference

Referencia rapida de todos los agentes del sistema.

## Quick Reference

| Agente | Categoria | Modelo | Invocar cuando... |
|--------|-----------|--------|-------------------|
| architect | core | opus | Inicio de proyecto, cambios estructurales |
| critic | core | opus | ANTES de implementar cambios importantes |
| explorer | core | opus | ANTES de modificar codigo existente |
| memory | core | opus | AL INICIO de sesion, antes de decisiones |
| coder | core | sonnet | Para implementar tareas del todo list |
| tester | core | sonnet | DESPUES de cada implementacion |
| stuck | core | sonnet | Cuando hay problemas o dudas |
| security | quality | opus | ANTES de deploy, datos sensibles, auth |
| debugger | quality | opus | Errores, tests fallando, bugs |
| reviewer | quality | opus | DESPUES de coder, ANTES de merge |
| performance | quality | opus | App lenta, memoria alta, escalabilidad |
| frontend | domain | opus | UI, componentes, estilos, responsive |
| backend | domain | opus | APIs, servidor, auth, endpoints |
| database | domain | opus | SQL, queries, migrations, esquemas |
| data-sync | domain | opus | Excel, Access, CSV, ETL, fotos |
| devops | domain | opus | Docker, CI/CD, deploy, cloud |
| api-designer | domain | opus | OpenAPI, REST design, contratos |

## Tools por Agente

### Herramientas disponibles:

| Tool | Descripcion |
|------|-------------|
| Read | Leer archivos |
| Write | Crear archivos |
| Edit | Modificar archivos |
| Glob | Buscar archivos por patron |
| Grep | Buscar contenido en archivos |
| Bash | Ejecutar comandos |
| Task | Invocar otros agentes |

### Distribucion:

```
architect:    Read, Glob, Grep, WebSearch, Task
critic:       Read, Glob, Grep, Task
explorer:     Read, Glob, Grep, Bash, Task
memory:       Read, Write, Edit, Glob, Grep
coder:        Read, Write, Edit, Glob, Grep, Bash, Task
tester:       Task, Read, Bash
stuck:        AskUserQuestion, Read, Bash, Glob, Grep
security:     Read, Grep, Glob, Bash, Task
debugger:     Read, Write, Edit, Bash, Glob, Grep, Task
reviewer:     Read, Write, Edit, Glob, Grep, Task
performance:  Read, Write, Edit, Bash, Glob, Grep, Task
frontend:     Read, Write, Edit, Glob, Grep, Bash, Task
backend:      Read, Write, Edit, Glob, Grep, Bash, Task
database:     Read, Write, Edit, Glob, Grep, Bash, Task
data-sync:    Read, Write, Edit, Glob, Grep, Bash, Task
devops:       Read, Write, Edit, Glob, Grep, Bash, Task
api-designer: Read, Write, Edit, Glob, Grep, Task
```

## Keywords para Routing

El registry usa estas keywords para routing automatico:

### Core
- architect: arquitectura, diseno, estructura, sistema
- critic: cuestionar, validar, alternativas, problemas
- explorer: explorar, buscar, investigar, dependencias
- memory: recordar, decisiones, historia, contexto

### Quality
- security: seguridad, vulnerabilidad, owasp, xss, injection
- debugger: bug, error, debug, crash, exception
- reviewer: review, calidad, refactor, clean, solid
- performance: rendimiento, lento, optimizar, cache

### Domain
- frontend: react, vue, css, html, ui, componente
- backend: node, api, rest, graphql, servidor
- database: sql, postgres, mysql, query, migration
- data-sync: excel, access, csv, import, sync, foto
- devops: docker, ci, cd, deploy, cloud, aws
- api-designer: openapi, swagger, api design, contrato

## Escalacion

**TODOS** los agentes deben invocar a `stuck` cuando:
- Encuentran un error inesperado
- No pueden completar la tarea
- Necesitan tomar una decision que requiere contexto humano
- Hay multiples soluciones validas
- Algo no funciona como esperaban

## Integracion entre Agentes

```
architect <-> critic      (arquitectura validada)
explorer  <-> coder       (contexto antes de codigo)
coder     <-> reviewer    (codigo revisado)
coder     <-> tester      (codigo verificado)
*         <-> stuck       (escalacion a humano)
*         <-> memory      (contexto persistente)
```
