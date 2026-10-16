#!/usr/bin/env python3
"""
SessionStart hook — project scope (complementa el guardrail global v3.2).

Emite un recordatorio breve de las reglas clave del proyecto al iniciar sesión.
No duplica la política global (que ya inyecta el hook global de SessionStart).
No puede bloquear sesiones: el exit code no se evalúa en SessionStart.
"""

import json
import os
import sys

REMINDER = (
    "PROJECT SECURITY POSTURE:\n"
    "- Skill requerido antes de comandos sensibles: security-safe-command-execution\n"
    "- Gestor de paquetes: pnpm (v11). pnpm install requiere aprobacion manual\n"
    "- Cambios: registrar en changelog/ y actualizar docs/ en la misma sesion\n"
    "- Tokens: nunca en .mcp.json; usar ${VARIABLE} con el valor en .env.local\n"
    "- Lee CLAUDE.md antes de actuar\n"
)


def _read_cwd():
    try:
        event = json.load(sys.stdin)
        if isinstance(event, dict):
            return event.get("cwd") or ""
    except Exception:
        pass
    return ""


def main():
    try:
        sys.stdout.write(REMINDER)
        cwd = _read_cwd()
        if cwd and os.path.isfile(os.path.join(cwd, "CLAUDE.md")):
            sys.stdout.write("- Project policy: %s\n" % os.path.join(cwd, "CLAUDE.md"))
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
