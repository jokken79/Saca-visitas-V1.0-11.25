# Example Session

Este es un ejemplo de como se usa el sistema de agentes en una sesion real.

## Escenario: Crear API de productos

**Usuario:** "Necesito crear una API REST para gestionar productos con CRUD completo"

---

### Paso 1: Memory recuerda contexto

```
Claude invoca: memory

MEMORY REPORT:
- Proyecto usa Node.js + Express
- Base de datos: PostgreSQL
- Patron de API establecido: /api/v1/resource
- Autenticacion: JWT
- Errores previos: Faltaban validaciones en endpoints similares
```

---

### Paso 2: API Designer crea especificacion

```
Claude invoca: api-designer

API DESIGN SPECIFICATION:

Endpoints:
GET    /api/v1/products        - Listar productos (paginado)
GET    /api/v1/products/:id    - Obtener producto
POST   /api/v1/products        - Crear producto
PATCH  /api/v1/products/:id    - Actualizar producto
DELETE /api/v1/products/:id    - Eliminar producto

OpenAPI spec creada en: docs/openapi/products.yaml
```

---

### Paso 3: Critic revisa el diseno

```
Claude invoca: critic

CRITICAL ANALYSIS:

Strengths:
- Sigue patrones REST establecidos
- Consistente con otras APIs del proyecto

Critical Questions:
1. Que pasa si se elimina un producto con ordenes activas?
2. Se necesita soft delete o hard delete?
3. Quien puede crear/eliminar productos? (roles)

Recommendation: DISCUSS
Necesita decision humana sobre reglas de negocio.
```

---

### Paso 4: Stuck escala al humano

```
Claude invoca: stuck

HUMAN DECISION NEEDED:

Question: "El critico identifico preguntas importantes sobre la API de productos"

Options:
1. Soft delete (marcar como inactivo)
2. Hard delete (eliminar completamente)
3. Soft delete + validacion de ordenes activas

Tu eleccion?
```

**Usuario elige:** "Opcion 3 - Soft delete con validacion"

---

### Paso 5: Backend implementa

```
Claude invoca: backend

BACKEND IMPLEMENTATION:

Files created:
- src/routes/products.ts
- src/controllers/productController.ts
- src/services/productService.ts
- src/validators/productValidator.ts

Soft delete implementado con campo deleted_at
Validacion de ordenes activas antes de eliminar
```

---

### Paso 6: Security audita

```
Claude invoca: security

SECURITY AUDIT:

Checklist:
[x] Input validation - Zod schemas implemented
[x] Authentication - JWT required on all endpoints
[x] Authorization - Admin role required for create/delete
[x] SQL injection - Parameterized queries used
[x] Rate limiting - Applied to all endpoints

Security Score: 95/100
Minor: Agregar logging de acciones administrativas
```

---

### Paso 7: Tester verifica

```
Claude invoca: tester

VISUAL TEST REPORT:

Tests executed:
[PASS] GET /api/v1/products - Returns 200 with paginated list
[PASS] POST /api/v1/products - Creates product, returns 201
[PASS] GET /api/v1/products/:id - Returns single product
[PASS] PATCH /api/v1/products/:id - Updates product
[PASS] DELETE /api/v1/products/:id - Soft deletes product
[PASS] DELETE product with orders - Returns 400 error

All tests passing!
```

---

### Paso 8: Memory guarda contexto

```
Claude invoca: memory

MEMORY UPDATED:

Decision recorded:
- Products API usa soft delete con validacion de ordenes
- Patron establecido para futuras APIs similares

Session recorded:
- API de productos completada exitosamente
- 6 endpoints creados
- Security audit: 95/100
```

---

## Resultado Final

API de productos completamente funcional con:
- CRUD completo
- Soft delete con validacion
- Seguridad auditada
- Tests pasando
- Documentacion OpenAPI
- Contexto guardado para futuras sesiones
