# Checklist técnico detallado — Security Audit Read-Only v2

## 1. Scope y capacidad
- Arquitectura real.
- Servicios realmente utilizados.
- Permisos disponibles.
- Capacidades/licenciamiento relevantes.
- Restricciones conocidas.
- Diferenciar control faltante, no disponible, no verificado y no aplicable.

## 2. Azure Functions / APIs
- Authentication/authorization, Anonymous/Function/Admin, Entra ID/Easy Auth.
- JWT issuer/audience/scopes/roles.
- IDOR/BOLA.
- Endpoints públicos/administrativos.
- Function Keys.
- Managed Identity/RBAC.
- SQL injection, command injection, SSRF, path traversal, XSS.
- Upload, MIME, extensiones, rutas y temporales.
- Rate limiting, throttling, timeouts, errores y logs.
- HTTPS/TLS/CORS/runtime/settings/secrets.

## 3. Frontend / Static Web App
- Auth, rutas, API exposure.
- Variables públicas y `.env`.
- Source maps.
- Tokens/cookies.
- XSS, CSRF cuando aplique, clickjacking, open redirect.
- CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, frame-ancestors.
- CORS.

## 4. Azure Storage
- Public/anonymous access.
- allowBlobPublicAccess.
- Shared Key/SAS/User Delegation SAS.
- Managed Identity/RBAC.
- HTTPS/minimum TLS.
- Soft delete/versioning/lifecycle.
- Logging y exposición de URLs.
- No asumir que Shared Key es inseguro sin contexto.

## 5. Base de datos
- Entra ID/Managed Identity/SQL auth.
- Usuarios/roles/mínimo privilegio.
- Connection strings/secrets.
- Firewall/public access/Private Endpoint/TLS/cifrado.
- SQL injection y queries parametrizadas.
- PII/logs/privilegios excesivos.

## 6. Secretos
Buscar sin mostrar valores: passwords, API keys, tokens, Bearer, connection strings, SAS, client secrets, certificados, private keys, `.env`, workflows y Git history.
Preferir metadata sobre recuperar valores.

## 7. Git History
Revisar commits, ramas, tags, archivos eliminados y secretos históricos.
Usar inspección (`git log`, `git show`, `git diff`, `git show <commit>:<file>`).
No reset, clean, checkout/switch mutante, rebase, stash, cherry-pick, commit, merge ni push.

## 8. Dependencias
Revisar requirements/lockfiles, versiones, vulnerabilidades, abandonadas, transitivas, innecesarias y versiones sin fijar.
No instalar scanners ni actualizar dependencias.
Si una herramienta existente usa red, aplicar pre-flight.

## 9. Código
Injection, XSS/CSRF/SSRF, autorización, IDOR/BOLA, path traversal, upload, datos sensibles, criptografía y errores.

## 10. Entra ID / RBAC
Apps, scopes, roles, service principals, Managed Identity, secrets, certificados, federated credentials, OIDC, expiración y privilegios.
Evaluar Owner/Contributor/User Access Administrator, scope e herencia.

## 11. Key Vault
RBAC vs Access Policies, Managed Identity, metadata de secretos/certificados, expiración, logging, soft delete, purge protection, red y Private Endpoint.
Nunca mostrar valores.

## 12. Networking
Public access, Private Endpoint, VNet, NSG, firewall, IP restrictions, trusted services, DNS, TLS, puertos y endpoints innecesarios.
No recomendar automáticamente trusted services: evaluar contexto y política corporativa.

## 13. Application Insights / Logging
Requests, dependencies, exceptions y traces.
Buscar passwords, tokens, connection strings, PII, documentos, identificación, datos bancarios y Authorization headers.

## 14. GitHub Actions / CI-CD
Revisar solo capacidades realmente disponibles:
- triggers;
- permissions;
- GITHUB_TOKEN;
- secrets;
- Azure Login;
- OIDC/federated credentials;
- service principals;
- acciones de terceros;
- versiones;
- scripts;
- variables;
- artefactos;
- forks/pull requests;
- expression injection.

No asumir disponibilidad de GitHub Advanced Security ni controles exclusivos de planes superiores. Si no están disponibles, registrar Limitación de plataforma y no vulnerabilidad.

## 15. SOC/EDR
Correlacionar proceso, argumentos, destino, protocolo, payload, archivo, contexto y propósito.
No clasificar automáticamente como amenaza por palabras como `ssh`, `tunnel` o por redirecciones.
Nunca modificar comandos para ocultarlos del EDR.

## 16. Producción
Distinguir observación, consulta, interacción no mutante, prueba activa y explotación.
Esta skill solo realiza observación/consulta y operaciones inequívocamente no mutantes.
No hacer pruebas activas contra producción.

## 17. Limitaciones
Indicar qué no se pudo comprobar, por qué, impacto sobre la conclusión y alternativa de verificación.

## 18. Cierre
Indicar claramente:
- verificado;
- no verificado;
- hallazgo;
- recomendación;
- limitación;
- no aplicable;
- dependencia de licencia/capacidad.
