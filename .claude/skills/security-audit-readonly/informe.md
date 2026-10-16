# Formato del informe final — Security Audit Read-Only v2

## Quick Wins
Solo controles aplicables, disponibles, de bajo riesgo y respaldados por evidencia.

| Control | Evidencia actual | Acción recomendada | Disponibilidad | Prioridad |
|---|---|---|---|---|

## Hardening Azure
```text
Servicio:
Configuración:
Estado actual:
Estado recomendado:
Aplicabilidad:
Disponibilidad/licencia:
Limitación:
Prioridad:
Riesgo:
```

## Plan de remediación
### 1. Inmediatas
### 2. Corto plazo
### 3. Mediano plazo

Las acciones deben ser aplicables al entorno actual o marcarse como dependientes de capacidad/licencia.

# A. Arquitectura actual
Diagrama y descripción solo de componentes encontrados.

# B. Controles de seguridad actuales
Qué existe, cómo funciona y evidencia.

# C. Hallazgos
```text
ID:
Componente:
Severidad:
Descripción:
Evidencia:
Estado:
Riesgo:
Impacto potencial:
Recomendación:
Aplicabilidad:
Dependencia de licencia/capacidad:
Limitación:
Prioridad:
Esfuerzo estimado:
```

# D. Quick Wins
Medidas rápidas, aplicables y de bajo riesgo.

# E. Hardening de Azure
Configuraciones recomendadas y aplicabilidad real.

# F. Seguridad del código
Vulnerabilidades y recomendaciones.

# G. Seguridad de CI/CD
GitHub Actions, OIDC, Azure Login, permisos y controles realmente disponibles.

# H. Plan de remediación
1. Inmediatas
2. Corto plazo
3. Mediano plazo

# I. Estado final
| Control | Estado actual | Recomendación | Aplicabilidad | Disponibilidad | Prioridad |
|---|---|---|---|---|---|

## Estados permitidos
Confirmado · Probable · No verificado · No aplicable · Limitación de plataforma · Limitación de acceso

## Regla contra falsos positivos
No declarar vulnerabilidad únicamente por nombres de herramientas, palabras como `ssh`/`tunnel`, paquetes con nombres sensibles, redirecciones o una alerta EDR aislada. Correlacionar proceso, argumentos, destino, protocolo, payload, archivo, contexto, propósito y resultado.

## Regla de capacidad
Si un control no puede aplicarse por licencia, plan, permisos o disponibilidad:
- no presentarlo como fallo;
- documentarlo como limitación;
- proponer alternativa disponible si existe.

## Finalización
Indicar qué fue verificado, qué no, qué depende de licencia/capacidad, qué no aplica y qué requiere autorización posterior.

**Auditoría completada en modo estrictamente solo lectura. No se realizaron cambios.**

Informe guardado en `docs/security/audit.md`.
