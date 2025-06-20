# apply-patches.ps1

# 1) Patch para security.py
$securityPatch = @"
--- a/src/aurora/middleware/security.py
+++ b/src/aurora/middleware/security.py
@@ -100,9 +100,12 @@ class SecurityHeadersMiddleware(BaseHTTPMiddleware):
-            # Remove cabeçalhos sensíveis
-            response.headers.pop("server", None)
-            response.headers.pop("x-powered-by", None)
+            # Remove cabeçalhos sensíveis de forma compatível com MutableHeaders
+            if "server" in response.headers:
+                del response.headers["server"]
+            if "x-powered-by" in response.headers:
+                del response.headers["x-powered-by"]
"@

# 2) Patch para servico_crm.py
$crmPatch = @"
--- a/src/aurora/services/servico_crm.py
+++ b/src/aurora/services/servico_crm.py
@@ -45,7 +45,11 @@ def _mapear_dados_api_para_cliente(self, dados_api: Dict[str, Any]) -> ClienteCreate:
-        cnpj_limpo = dados_api.get("cnpj", "")
+        # Adaptamos ao formato da integração CNPJ: taxId e company.name
+        raw_cnpj = dados_api.get("taxId", "")
+        cnpj_limpo = raw_cnpj.replace(".", "").replace("/", "").replace("-", "")
@@ -54,8 +58,11 @@ def _mapear_dados_api_para_cliente(self, dados_api: Dict[str, Any]) -> ClienteCreate:
-        dados_mapeados = {
-            "cnpj": cnpj_limpo,
-            "razao_social": dados_api.get("razao_social"),
-            "nome_fantasia": dados_api.get("nome_fantasia"),
+        empresa = dados_api.get("company", {})
+        dados_mapeados = {
+            "cnpj": cnpj_limpo,
+            "razao_social": empresa.get("name"),
+            "nome_fantasia": empresa.get("tradeName"),
"@

# 3) Salva os patches em disco
$securityPatch | Out-File -Encoding UTF8 security.patch
$crmPatch      | Out-File -Encoding UTF8 crm.patch

# 4) Aplica os patches
git apply .\security.patch
git apply .\crm.patch

# 5) (Opcional) Limpa os arquivos de patch
Remove-Item .\security.patch, .\crm.patch
