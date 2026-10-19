# Refactor: eliminar archivo de comando heredado security-review

**Fecha:** 2026-10-19 11:18
**Tipo:** Refactor
**Requisitos:** ninguno

## Qué se hizo

Se eliminó el archivo de comando heredado `.claude/commands/security-review.md` tras verificar que la migración del procedimiento de auditoría al formato de skill actual (`.claude/skills/security-review/SKILL.md`) está completa y funcional.

Esta acción finaliza la migración iniciada en el commit e827922, eliminando la duplicación de definiciones y alineando completamente el mecanismo de invocación con el formato actual de procedimientos del proyecto.

## Qué se modificó

### `.claude/commands/security-review.md` (eliminado)

```
Status: DELETED
Motivo: Comando heredado duplicado; skill equivalente disponible en `.claude/skills/security-review/SKILL.md`
```

El contenido se conserva íntegramente en la skill, sin pérdida funcional.

## Por qué

CLAUDE.md línea 174-176 prohíbe explícitamente nuevos archivos en `.claude/commands/` (formato heredado):

> "No meter procedimientos en este archivo ni crear archivos en `.claude/commands/` (formato heredado). Un procedimiento nuevo es una skill en `.claude/skills/<nombre>/SKILL.md`"

La presencia de ambas definiciones con el mismo nombre crease ambigüedad. Aunque Claude Code prevalece la skill, eliminar el archivo heredado refuerza las convenciones del proyecto y simplifica la mantenibilidad.

## Validaciones previas

- ✅ Skill intacta y funcional: `.claude/skills/security-review/SKILL.md`
- ✅ Contenido idéntico entre skill y comando (sin instrucciones únicas en el comando)
- ✅ Regla de proyecto confirmada: CLAUDE.md línea 174-176
- ✅ Cambio único: `git status --short` muestra solo `D .claude/commands/security-review.md`

## Notas

Ningún documento de `docs/` se ve afectado. La funcionalidad de `/security-review` continúa disponible e invocará la skill actual.
