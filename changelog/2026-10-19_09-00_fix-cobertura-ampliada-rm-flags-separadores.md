# Fix: cobertura ampliada de rm destructivo — flags, ${HOME} y separadores

**Fecha:** 2026-10-19 09:00
**Tipo:** Fix

## Qué se hizo

Se amplió la cobertura del patrón HIGH_IMPACT `rm -rf` en el hook de proyecto `pretool-gate.py`
para cubrir variantes de flags, la notación `${HOME}` con llaves y separadores de comandos sin
espacio. Adicionalmente, se portó la corrección de S-FP-5 (barra final) al hook global
`pretool-security-gate.py`, donde la brecha original permanecía sin corregir.

El análisis estático S-FP-6 identificó 11 falsos negativos en el hook de proyecto y 3 en el
hook global. Esta intervención los reduce a 3 limitaciones estructurales documentadas (ver sección
de limitaciones), que requieren un parser semántico o lookahead multi-token para resolverse.

## Qué se modificó

### `.claude/hooks/pretool-gate.py` — línea 71 (hook de proyecto)

```diff
-    (r"\brm\s+-rf\s+(/+|~/|~|\$HOME/|\$HOME)(\s|$)", "Recursive delete of filesystem root or home directory"),
+    (r"\brm\s+-(?:[a-z]*r[a-z]*f|[a-z]*f[a-z]*r)[a-z]*(?:\s+--\S+)*\s+(/+|~/|~|\$(?:HOME|\{HOME\})/?)(\s|[;&|]|$)", "Recursive delete of filesystem root or home directory"),
```

Nuevos casos cubiertos respecto a S-FP-5:

| Caso | Antes | Después |
|---|---|---|
| `rm -fr /` (flags invertidos) | SILENT | DENY |
| `rm -rfv /` (flag verbose) | SILENT | DENY |
| `rm -fvr ~/` (permutación aleatoria) | SILENT | DENY |
| `rm -rf --no-preserve-root /` | SILENT | DENY |
| `rm -rf ${HOME}/` (notación con llaves) | SILENT | DENY |
| `rm -rf ${HOME}` | SILENT | DENY |
| `rm -rf /;echo done` (semicolon sin espacio) | SILENT | DENY |
| `rm -rf ~/;echo done` | SILENT | DENY |
| `rm -rf /&&rm /tmp` | SILENT | DENY |

Sin falsos positivos introducidos (rutas específicas como `~/proyecto/tmp`, `$HOME/proyecto`,
`${HOME}/files`, `/usr/local/bin`, `/tmp/builddir` siguen siendo SILENT).

Estructura del nuevo patrón (con comentarios):

```
\brm\s+                          # comando rm + espacio
-(?:                              # flag group con -
  [a-z]*r[a-z]*f|               #   r antes de f: -rf, -rfv, -rvf…
  [a-z]*f[a-z]*r                #   f antes de r: -fr, -fvr…
)[a-z]*                          # flags adicionales opcionales
(?:\s+--\S+)*                    # opciones --long-option antes del target
\s+                              # espacio antes del target
(/+|~/|~|\$(?:HOME|\{HOME\})/?) # target: raíz, home, $HOME o ${HOME}
(\s|[;&|]|$)                    # separador: espacio, ; & | o fin de cadena
```

### `C:\Users\farias\.claude\hooks\pretool-security-gate.py` — línea 104 (hook global)

Puerto mínimo de S-FP-5 únicamente. No se portaron las mejoras de flags ni `${HOME}`.
El mensaje original se conserva sin cambios.

```diff
-    (r"\brm\s+-rf\s+(/|~|\$HOME)(\s|$)", "Recursive delete of a root/home path"),
+    (r"\brm\s+-rf\s+(/+|~/|~|\$HOME/|\$HOME)(\s|$)", "Recursive delete of a root/home path"),
```

### Archivos NO modificados

- `.claude/settings.json` (proyecto): sin cambios.
- `C:\Users\farias\.claude\settings.json` (global): sin cambios.
- Ningún otro archivo de configuración global de Claude Code.

## Pruebas ejecutadas

Runner de pruebas aislado (`sfp7_test_runner.py` en scratchpad de sesión): las cadenas de
comandos se procesaron exclusivamente como input de texto a la función `classify()` de cada
hook, nunca como comandos de shell.

| Etapa | Hook proyecto | Hook global | Total |
|---|---|---|---|
| Baseline (antes de cambios) | 23/34 | 6/9 | 29/43 |
| Tras edit proyecto | 34/34 | 6/9 | 40/43 |
| Tras port global | 34/34 | 9/9 | **43/43** |

## Limitaciones documentadas (fuera de alcance)

Las siguientes variantes permanecen como SILENT en ambos hooks. Se documentan aquí para
trazabilidad; su corrección requiere un parser semántico o lookahead multi-token:

| Variante | Motivo |
|---|---|
| `rm -r -f /` | Flags separados; el patrón requiere un único token `-rf`/`-fr` |
| `rm -rf -- /` | Bare end-of-options marker `--` no cubierto por `(?:\s+--\S+)*` |
| `rm -rf "$HOME"` / `'~'` | Variables entre comillas; el quote escapa la detección |
| Flags mayúsculas `-RF` | Patrón case-sensitive para flags; `(?i)` no aplicado |

Las limitaciones del hook global son más amplias: flags alternativas (`-fr`, `-rfv`) y
`${HOME}` siguen siendo SILENT ahí por diseño (solo se portó S-FP-5).

## Por qué

El análisis estático S-FP-6 confirmó que el patrón de S-FP-5 cubría las formas más directas
(`rm -rf /`, `rm -rf ~/`) pero no las variantes habituales que un modelo de lenguaje podría
generar (`rm -fr /`, `rm -rfv /`, `rm -rf ${HOME}`). La ampliación reduce la superficie de
evasión accidental sin introducir falsos positivos en rutas específicas.

El hook global no recibió las mejoras de S-FP-7 porque cualquier cambio en archivos fuera del
proyecto requiere autorización separada y un alcance más conservador.
