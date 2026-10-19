# Fix: reglas deny trailing-slash y migración de security-review a skills/

**Fecha:** 2026-10-19 10:00
**Tipo:** Configuración / Fix
**Commit:** e827922cb517ced813366f485114daef65f6554f

## Qué se hizo

Se cerraron tres brechas en `permissions.deny` del proyecto (S-FP-9B) y se migró el
procedimiento de auditoría de seguridad al formato de skill actual. Adicionalmente se
portó la mejora de patrones S-FP-7 al hook global (cambio local, fuera del repositorio).

## Qué se modificó

### `.claude/settings.json` — en commit e827922

Añadidas 3 reglas `deny` exactas para variantes con barra final no cubiertas:

```json
"Bash(rm -rf //)",
"Bash(rm -rf ~/)",
"Bash(rm -rf $HOME/)"
```

`permissions.deny` usa coincidencia de cadena exacta: `rm -rf ~/` no era reconocida
por la regla preexistente `Bash(rm -rf ~)` porque el slash final no forma parte del
patrón. Las tres variantes ya eran bloqueadas por el hook (regex S-FP-7), pero no
por la capa de UI de `permissions.deny`. Se añaden como defensa adicional en esa capa.

No es posible usar wildcards (`Bash(rm -rf ~*)`) sin crear falsos positivos en rutas
de subdirectorio legítimas.

### `.claude/skills/security-review/SKILL.md` (nuevo) — en commit e827922

Skill creada en el formato actual (`.claude/skills/<nombre>/SKILL.md` con frontmatter
`name:` + `description:`), equivalente funcional del comando legacy
`.claude/commands/security-review.md`. Invoca el skill `security-audit-readonly` con
las mismas instrucciones: lectura previa de `checklist-tecnico.md` e `informe.md` y
generación del informe en `docs/security/audit.md`. Auditoría estrictamente de solo
lectura.

El archivo original `.claude/commands/security-review.md` se conserva deliberadamente
mientras la invocación funcional de la nueva skill no esté verificada (ver Limitaciones).

### `C:\Users\farias\.claude\hooks\pretool-security-gate.py` línea 104 — fuera del repositorio

Cambio local al hook global, **no incluido en el commit e827922**. Puerto mínimo de la
mejora S-FP-7 al hook global. El patrón anterior solo cubría la forma `-rf` con
separador `(\s|$)`. El nuevo patrón cubre todas las permutaciones de flags (`-fr`,
`-rfv`, `-fvr`, etc.) y separadores sin espacio (`;`, `&&`, `|`), igual que el hook
de proyecto desde S-FP-7.

```diff
-    (r"\brm\s+-rf\s+(/+|~/|~|\$HOME/|\$HOME)(\s|$)", "Recursive delete of a root/home path"),
+    (r"\brm\s+-(?:[a-z]*r[a-z]*f|[a-z]*f[a-z]*r)[a-z]*(?:\s+--\S+)*\s+(/+|~/|~|\$(?:HOME|\{HOME\})/?)(\s|[;&|]|$)", "Recursive delete of a root/home path"),
```

## Pruebas ejecutadas

Runner de pruebas aislado (`sfp7_test_runner.py` en scratchpad de sesión). Las cadenas
de comandos se procesaron exclusivamente como input de texto a la función `classify()`
de cada hook, nunca como comandos de shell.

| Hook | Casos | Resultado |
|---|---|---|
| Proyecto (`pretool-gate.py`) | 34 | 34/34 PASS |
| Global (`pretool-security-gate.py`) | 15 (incluye 6 nuevos GN) | 15/15 PASS |
| **Total** | **49** | **49/49 PASS** |

Las 34 pruebas del proyecto cubren: regresiones (R-1..R-9), nuevas permutaciones de
flags (F-1..F-5), notación `${HOME}` (G-1..G-3), separadores sin espacio (H-1..H-3),
rutas específicas sin falso positivo (S-1..S-11) y limitaciones documentadas (L-1..L-3).
Las 15 pruebas globales cubren: regresiones S-FP-5 (GR-1..GR-6), nuevas permutaciones
S-FP-9B (GN-1..GN-6) y rutas específicas sin falso positivo (GS-1..GS-3).

**Nota:** el runner verifica `classify()` únicamente. No se probaron `main()`, `_emit()`,
el parsing JSON de stdin ni el protocolo completo del hook.

## Limitaciones

- **Invocación funcional de `/security-review` no verificada.** No se ha comprobado en
  una sesión real de Claude Code que la nueva skill sea la que se cargue al invocar
  `/security-review`. La verificación requeriría abrir una sesión, invocar el skill y
  cancelar inmediatamente antes de que comience la auditoría.

- **`.claude/commands/security-review.md` conservado deliberadamente.** Hasta que la
  invocación end-to-end de la skill esté verificada, el comando legacy permanece como
  fallback. Su eliminación requiere autorización separada.

- **Cambio al hook global fuera de git.** La actualización de
  `pretool-security-gate.py` es un cambio local en la máquina del usuario y no está
  versionado en este repositorio. Cualquier reinstalación o nuevo equipo requeriría
  aplicar el mismo diff manualmente.

- **Limitaciones estructurales conocidas del patrón rm (ambos hooks):** `rm -r -f /`
  (flags separados), `rm -rf -- /` (end-of-options marker), `rm -rf "$HOME"` (variable
  entre comillas) y flags en mayúsculas `-RF` permanecen como SILENT. Su corrección
  requiere un parser semántico o lookahead multi-token.

## Por qué

`permissions.deny` proporciona una capa de bloqueo temprano en la UI de Claude Code,
antes de que el hook PreToolUse se ejecute. Aunque el hook ya cubría estas variantes,
la ausencia de las reglas en `deny` dejaba una diferencia observable entre ambas capas.
La adición es mínima, exacta y sin riesgo de falsos positivos.

La migración de `commands/` a `skills/` cumple la regla de CLAUDE.md que prohíbe
nuevos archivos en el directorio `commands/` (formato heredado) y alinea el mecanismo
de invocación con el resto de procedimientos del proyecto.
