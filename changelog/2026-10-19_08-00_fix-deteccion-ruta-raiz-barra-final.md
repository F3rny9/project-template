# Fix: detección de rutas raíz/home con barra final en rm -rf

**Fecha:** 2026-10-19 08:00
**Tipo:** Fix
**Commit:** ef89e63

## Qué se hizo

Se corrigió una brecha en la regla HIGH_IMPACT del hook de proyecto `pretool-gate.py` que
permitía que `rm -rf ~/`, `rm -rf $HOME/` y `rm -rf //` pasaran en silencio en lugar de
bloquearse. La expresión regular no cubría el carácter de barra final (`/`) inmediatamente
después del target, porque el grupo de cierre `(\s|$)` requería espacio o fin de cadena pero
el slash adicional fallaba ambas condiciones.

## Qué se modificó

### `.claude/hooks/pretool-gate.py` — línea 71

```diff
-    (r"\brm\s+-rf\s+(/|~|\$HOME)(\s|$)", ...)
+    (r"\brm\s+-rf\s+(/+|~/|~|\$HOME/|\$HOME)(\s|$)", ...)
```

Cambios respecto a la versión anterior (Fase 6):
- `/` → `/+`: detecta también `//` (doble barra de raíz).
- Añadida alternativa `~/`: cubre `rm -rf ~/` con barra final explícita.
- Añadida alternativa `\$HOME/`: cubre `rm -rf $HOME/` con barra final explícita.
- Mensaje actualizado a "Recursive delete of filesystem root or home directory".

### Pruebas ejecutadas

22 casos de prueba verificados (decisiones deny, ask y silencio). Ninguna regresión en el
comportamiento anterior. Los casos clave nuevos:

| Caso | Antes | Después |
|---|---|---|
| `rm -rf ~/` | SILENT (brecha) | DENY |
| `rm -rf $HOME/` | SILENT (brecha) | DENY |
| `rm -rf //` | SILENT (brecha) | DENY |
| `rm -rf ~/proyecto/tmp` | SILENT | SILENT (sin falso positivo) |

## Por qué

La brecha fue identificada en el análisis estático T-20 (S-FP-4) y confirmada mediante pruebas
de unidad (S-FP-5). Un comando `rm -rf ~/` elimina el directorio home completo con la misma
consecuencia que `rm -rf ~`; la barra final es una variación sintáctica equivalente que el
patrón original no anticipaba.
