# Controles de seguridad a nivel de proyecto — Fase 6

**Fecha:** 2026-10-16 18:00
**Tipo:** Configuración

## Qué se hizo

Se añadieron controles de seguridad a nivel de proyecto que complementan los guardrails globales v3.2
instalados en `~/.claude/`. Los controles son estrictamente aditivos: no modifican, reemplazan
ni debilitan ningún archivo global.

## Qué se modificó

### Archivos nuevos

- `.claude/hooks/session-start.py` — hook SessionStart de proyecto; emite recordatorio de
  postura de seguridad (pnpm, changelog, tokens, CLAUDE.md).
- `.claude/hooks/pretool-gate.py` — hook PreToolUse de proyecto; gate idéntico al global para
  Bash/PowerShell: bloquea operaciones HIGH_IMPACT (tampering Defender, herramientas ofensivas,
  port-forwarding SSH), solicita confirmación para WRITE (git push --force, az role assignment,
  etc.).
- `.claude/skills/security-safe-command-execution/SKILL.md` — skill de 21 secciones para
  clasificación READ/TEST/WRITE/SENSITIVE/HIGH IMPACT; copia local del skill global.
- `.claude/skills/security-audit-readonly/SKILL.md` — skill de auditoría estrictamente
  solo-lectura (Azure + GitHub + código); único write permitido: `docs/security/audit.md`.
- `.claude/skills/security-audit-readonly/checklist-tecnico.md` — 18 secciones de cobertura
  técnica (Functions, Frontend, Storage, DB, Secretos, Git History, Dependencias, Código,
  RBAC, Key Vault, Networking, Logging, CI/CD, SOC/EDR, Producción, Limitaciones, Cierre).
- `.claude/skills/security-audit-readonly/informe.md` — plantilla normativa del informe final
  (secciones A–I).
- `.claude/commands/security-review.md` — slash command `/security-review` que activa el skill
  de auditoría.

### Archivos modificados

- `.claude/settings.json` — eliminados 4 patrones de pnpm del allow (pnpm install ejecuta
  lifecycle scripts arbitrarios); añadidas 5 reglas deny (rm -rf /, ~, $HOME;
  git push --force; git push -f); añadido bloque `hooks` con SessionStart y PreToolUse
  apuntando al intérprete Python absoluto (`C:\Users\farias\AppData\Local\Programs\Python\
  Python312\python.exe`), no al alias de Microsoft Store.
- `CLAUDE.md` — añadido aviso sobre el alias de Microsoft Store en hooks: cómo verificar la
  ruta real en un equipo nuevo y cómo corregirla si es necesario.
- `.gitignore` — añadidos `__pycache__/` y `*.pyc` en la sección Cache (los hooks Python
  generan bytecode al compilarse; no debe commitarse).

## Por qué

El repositorio ya contaba con guardrails globales v3.2. Este cambio lleva los mismos controles
al nivel de proyecto para que cualquier miembro del equipo que clone el repo herede la postura
de seguridad sin depender de su configuración global personal.

El alcance fue revisado en T-01 a T-20 y autorizado explícitamente por el usuario antes de
ejecutar cualquier modificación.

## Notas de implementación

- Orden de evaluación confirmado: (1) PreToolUse hook → emite allow/ask/deny/defer;
  (2) permissions.deny evaluado después; gana la restricción más estricta.
- `onFailure: "block"` mantenido desactivado (requiere Claude Code ≥ v2.1.295; verificar
  antes de activar).
- T-20 (prueba de integración real end-to-end en Claude Code) pendiente de autorización
  separada: abrir una sesión nueva en este proyecto y confirmar que ambos hooks se ejecutan.
