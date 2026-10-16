#!/usr/bin/env python3
"""
PreToolUse security gate — project scope (v3.2).

Copia funcional del guardrail global para proyectos que clonen esta plantilla.
Cuando ambos hooks coexisten (global + proyecto), se ejecutan los dos y prevalece
la decision mas restrictiva (deny > ask > allow/defer).

Logica identica al hook global pretool-security-gate.py. Ver ese archivo para
la documentacion completa del contrato de entrada/salida y las decisiones de diseno.

LIMITACION DE PLATAFORMA: un hook que falla o agota el timeout NO bloquea la
llamada a la herramienta (fail-open). Este gate es defensa en profundidad, no
un limite de seguridad duro. EDR/XDR y el modelo de aprobacion humana son los
controles autoritativos.
"""

import json
import re
import sys


def _load_event():
    try:
        raw = sys.stdin.buffer.read()
    except Exception:
        try:
            raw = sys.stdin.read().encode("utf-8", "replace")
        except Exception:
            return None
    try:
        return json.loads(raw.decode("utf-8-sig", "replace"))
    except Exception:
        return None


def _emit(decision=None, reason=None, context=None):
    hso = {"hookEventName": "PreToolUse"}
    if decision:
        hso["permissionDecision"] = decision
    if reason:
        hso["permissionDecisionReason"] = reason
    if context:
        hso["additionalContext"] = context
    sys.stdout.write(json.dumps({"hookSpecificOutput": hso}))
    sys.exit(0)


def _silent():
    sys.exit(0)


HIGH_IMPACT = [
    (r"(?i)\bSet-MpPreference\b[^\n]*-Disable\w*\s+\$?true", "Disables Microsoft Defender protection"),
    (r"(?i)\b(Add|Set)-MpPreference\b[^\n]*-Exclusion(Path|Process|Extension)\b", "Adds a Defender exclusion"),
    (r"(?i)\bSet-MpPreference\b[^\n]*-DisableRealtimeMonitoring", "Disables Defender real-time monitoring"),
    (r"(?i)\b(Stop-Service|Set-Service|sc(\.exe)?\s+(stop|config))\b[^\n]*\b(WinDefend|Sense|WdNisSvc)\b", "Stops/alters a Defender/EDR service"),
    (r"(?i)\bnetsh\s+advfirewall\s+set\b[^\n]*\b(off|disable)\b", "Disables the Windows Firewall"),
    (r"(?i)\bSet-NetFirewallProfile\b[^\n]*-Enabled\s+False", "Disables a firewall profile"),
    (r"(?i)(^|[\\/\s;&|'\"])(mimikatz|invoke-mimikatz|rubeus|certipy(-ad)?|crackmapexec|secretsdump(\.py)?|impacket-\w+|bloodhound|sharphound)\b", "Offensive/credential-access tool"),
    (r"/dev/tcp/\d", "Bash /dev/tcp reverse-shell pattern"),
    (r"(?i)New-Object\s+System\.Net\.Sockets\.TCPClient", "PowerShell TCP reverse-shell pattern"),
    (r"(?i)\bn(c|cat)\b[^\n]*\s(-e|--exec|--sh-exec)\b", "netcat/ncat command execution (reverse shell)"),
    (r"(?i)\bsocat\b[^\n]*\bEXEC\b", "socat EXEC (command execution over socket)"),
    (r"(?i)(^|[\\/\s;&|'\"])(ngrok|chisel|frpc|frps|gost|zrok|bore)\b", "Network tunnel tool"),
    (r"(?i)\bcloudflared\b[^\n]*\btunnel\b", "Cloudflare tunnel"),
    (r"\bssh\b[^\n]*\s-[RLD]\b", "SSH port forwarding / SOCKS tunnel (-R/-L/-D)"),
    (r"(?i)\bplink\b[^\n]*\s-[RLD]\b", "PuTTY plink port forwarding / tunnel"),
    (r"(?i)\breg(\.exe)?\s+(add|delete)\b[^\n]*\\(Run|RunOnce)\b", "Autorun registry persistence"),
    (r"(?i)\b(New|Set)-ItemProperty\b[^\n]*\\CurrentVersion\\Run", "Autorun registry persistence"),
    (r"\brm\s+-rf\s+(/|~|\$HOME)(\s|$)", "Recursive delete of a root/home path"),
    (r"(?i)\bRemove-Item\b[^\n]*\b-Recurse\b[^\n]*\b-Force\b[^\n]*[A-Za-z]:\\(\s|\"|')*(\*)?\s*$", "Recursive force-delete of a drive root"),
]

SENSITIVE = [
    (r"(?i)\baz\s+keyvault\s+secret\s+(show|download|list|get)\b", "Reads Key Vault secret material"),
    (r"(?i)\bGet-AzKeyVaultSecret\b", "Reads Key Vault secret material"),
    (r"(?i)\baz\s+staticwebapp\s+secrets\b", "Reads/sets Static Web App secrets"),
    (r"(?i)--deployment-token\b", "Uses a deployment token"),
    (r"(?i)\bgh\s+secret\b", "Reads/sets GitHub Actions secrets"),
    (r"(?i)\baz\s+role\s+assignment\s+(create|delete)\b", "Changes Azure RBAC"),
    (r"(?i)\bNew-AzRoleAssignment\b|\bRemove-AzRoleAssignment\b", "Changes Azure RBAC"),
    (r"(?i)\baz\s+ad\s+(app|sp)\s+credential\b", "Manages Entra app/SP credentials"),
    (r"(?i)\b(schtasks(\.exe)?\s+/create|New-ScheduledTask|Register-ScheduledTask)\b", "Creates a scheduled task (possible persistence)"),
    (r"(?i)[\"'\s=]([A-Za-z]:[\\/][^\s\"']*\.(pem|pfx|p12|key))\b", "References a private-key/certificate file"),
    (r"(?i)\bid_rsa\b", "References an SSH private key"),
]

WRITE_ASK = [
    (r"(?i)\bgit\s+push\b", "git push to a remote"),
    (r"(?i)\bgit\s+reset\s+--hard\b", "git reset --hard (discards changes)"),
    (r"(?i)\bgit\s+clean\s+-[a-wyz]*f", "git clean -f (deletes untracked files)"),
    (r"(?i)\baz\s+[\w-]+(\s+[\w-]+)*\s+(delete|purge|remove)\b", "Destructive Azure operation"),
    (r"(?i)\b(Remove|Stop|Restart)-Az\w+\b", "Destructive/stateful Azure operation"),
]

HTTP_MUTATING = r"(?i:(-X|--request)\s+(POST|PUT|PATCH|DELETE)\b)|(?i:-Method\s+(POST|PUT|PATCH|DELETE)\b)"
READONLY_POST_ALLOWLIST = [
    r"registry\.npmjs\.org/-/npm/v1/security/advisories/bulk",
    r"registry\.npmjs\.org/-/npm/v1/security/audits",
]


def classify(cmd):
    for pat, why in HIGH_IMPACT:
        if re.search(pat, cmd):
            return ("deny", why)
    for pat, why in SENSITIVE:
        if re.search(pat, cmd):
            return ("ask", why)
    for pat, why in WRITE_ASK:
        if re.search(pat, cmd):
            return ("ask", why)
    if re.search(HTTP_MUTATING, cmd):
        if not any(re.search(a, cmd) for a in READONLY_POST_ALLOWLIST):
            return ("ask", "Mutating HTTP request (write by default)")
    return (None, None)


def main():
    event = _load_event()
    if not event:
        _silent()

    tool = str(event.get("tool_name", ""))
    if tool not in ("Bash", "PowerShell"):
        _silent()

    inp = event.get("tool_input") or {}
    cmd = str(inp.get("command", "")) if isinstance(inp, dict) else ""
    if not cmd.strip():
        _silent()

    decision, why = classify(cmd)
    if decision == "deny":
        _emit(
            "deny",
            reason=("Blocked by security guardrail: %s. High-impact / remote-access / "
                    "evasion pattern. If legitimate authorized work, state the tool, "
                    "reason, expected effect and authorization scope." % why),
            context=("Security guardrail: HIGH IMPACT (%s). Do not retry a reworded "
                     "or obfuscated variant." % why),
        )
    if decision == "ask":
        _emit(
            "ask",
            reason=("Security guardrail requests confirmation: %s. Confirm intended "
                    "and in scope." % why),
            context=("Security guardrail: %s. Prefer simplest auditable equivalent; "
                     "do not print secrets." % why),
        )
    _silent()


if __name__ == "__main__":
    main()
