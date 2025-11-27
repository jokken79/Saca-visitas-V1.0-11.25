# Workflows Guide

Esta guia describe los workflows predefinidos y como usarlos.

## Workflows Disponibles

### 1. new_feature - Nueva Funcionalidad

**Cuando usar:** Implementar una funcionalidad completamente nueva.

**Agentes involucrados:**
```
memory -> architect -> critic -> explorer -> coder -> reviewer -> tester
```

**Flujo:**
1. `memory` recuerda decisiones y contexto previo
2. `architect` disena la solucion a alto nivel
3. `critic` cuestiona el diseno y busca fallas
4. `explorer` investiga codigo existente relacionado
5. `coder` implementa la funcionalidad
6. `reviewer` revisa el codigo
7. `tester` verifica visualmente

**Ejemplo de uso:**
```
"Necesito agregar autenticacion con Google OAuth"
```

---

### 2. bug_fix - Corregir Bug

**Cuando usar:** Hay un error que necesita ser corregido.

**Agentes involucrados:**
```
memory -> debugger -> explorer -> coder -> tester
```

**Flujo:**
1. `memory` verifica si este bug ha ocurrido antes
2. `debugger` analiza el error y encuentra la causa raiz
3. `explorer` investiga codigo relacionado
4. `coder` implementa la correccion
5. `tester` verifica que el bug esta corregido

**Ejemplo de uso:**
```
"Los usuarios no pueden hacer login, reciben error 500"
```

---

### 3. data_migration - Migracion de Datos

**Cuando usar:** Mover datos entre sistemas (Excel, Access, bases de datos).

**Agentes involucrados:**
```
memory -> data-sync -> database -> tester
```

**Flujo:**
1. `memory` recuerda decisiones previas sobre datos
2. `data-sync` disena e implementa la migracion
3. `database` optimiza queries y esquema
4. `tester` verifica que los datos migraron correctamente

**Ejemplo de uso:**
```
"Necesito migrar 5000 registros de Excel a PostgreSQL, incluyendo fotos"
```

---

### 4. api_development - Desarrollo de API

**Cuando usar:** Disenar e implementar una API.

**Agentes involucrados:**
```
memory -> api-designer -> critic -> backend -> security -> tester
```

**Flujo:**
1. `memory` recuerda patrones de API usados
2. `api-designer` crea especificacion OpenAPI
3. `critic` revisa el diseno de la API
4. `backend` implementa los endpoints
5. `security` audita la seguridad
6. `tester` prueba los endpoints

**Ejemplo de uso:**
```
"Crear API REST para gestion de productos con CRUD completo"
```

---

### 5. frontend_feature - Funcionalidad Frontend

**Cuando usar:** Implementar algo en la interfaz de usuario.

**Agentes involucrados:**
```
memory -> frontend -> reviewer -> tester -> performance
```

**Flujo:**
1. `memory` recuerda patrones de UI usados
2. `frontend` implementa componentes y estilos
3. `reviewer` revisa el codigo
4. `tester` verifica visualmente
5. `performance` optimiza rendimiento

**Ejemplo de uso:**
```
"Crear un dashboard con graficos interactivos"
```

---

### 6. deployment - Despliegue

**Cuando usar:** Desplegar a produccion o staging.

**Agentes involucrados:**
```
memory -> security -> devops -> tester
```

**Flujo:**
1. `memory` recuerda configuraciones previas
2. `security` audita antes del deploy
3. `devops` configura y ejecuta deployment
4. `tester` verifica que todo funciona

**Ejemplo de uso:**
```
"Deploy a produccion con Docker en AWS"
```

---

### 7. optimization - Optimizacion

**Cuando usar:** Mejorar rendimiento de la aplicacion.

**Agentes involucrados:**
```
memory -> performance -> database -> frontend -> backend
```

**Flujo:**
1. `memory` recuerda optimizaciones previas
2. `performance` identifica cuellos de botella
3. `database` optimiza queries
4. `frontend` optimiza bundle y renderizado
5. `backend` optimiza endpoints

**Ejemplo de uso:**
```
"La pagina de productos tarda 5 segundos en cargar"
```

---

## Como Invocar Workflows

### Opcion 1: Mencion directa
```
"Usa el workflow de bug_fix para resolver este error"
```

### Opcion 2: Descripcion natural
```
"Hay un bug en el login" -> Claude detecta y usa bug_fix
```

### Opcion 3: Paso a paso
```
"Primero invoca a debugger para analizar, luego a coder para corregir"
```

## Crear Workflows Personalizados

Edita `.claude/agents-registry.json`:

```json
{
  "workflows": {
    "templates": {
      "mi_workflow": {
        "description": "Descripcion de mi workflow",
        "steps": ["agent1", "agent2", "agent3"]
      }
    }
  }
}
```

## Tips

1. **Siempre empieza con `memory`** - Evita repetir errores
2. **Termina con `tester`** - Verifica todo visualmente
3. **Usa `critic` para decisiones importantes** - Encuentra fallas antes
4. **`stuck` es tu amigo** - Cuando hay dudas, pregunta al humano
