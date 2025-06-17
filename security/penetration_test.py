#!/usr/bin/env python3
"""
Script para realizar testes de penetração automatizados na API Aurora-Platform.
Este script deve ser executado periodicamente para identificar vulnerabilidades.
"""

import requests
import json
import sys
import argparse
import logging
import time
import random
import string
import re
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("penetration_test.log")
    ]
)
logger = logging.getLogger(__name__)

class PenetrationTester:
    """Classe para realizar testes de penetração na API."""
    
    def __init__(self, base_url: str, username: str = None, password: str = None):
        """
        Inicializa o testador de penetração.
        
        Args:
            base_url: URL base da API
            username: Nome de usuário para autenticação
            password: Senha para autenticação
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        self.vulnerabilities = []
        
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """
        Executa todos os testes de penetração.
        
        Returns:
            List[Dict]: Lista de vulnerabilidades encontradas
        """
        logger.info(f"Iniciando testes de penetração em {self.base_url}")
        
        # Testes de autenticação
        self.test_authentication()
        
        # Testes de injeção
        self.test_sql_injection()
        self.test_xss_vulnerabilities()
        self.test_command_injection()
        
        # Testes de configuração
        self.test_security_headers()
        self.test_cors_configuration()
        self.test_ssl_configuration()
        
        # Testes de autorização
        self.test_authorization_bypass()
        self.test_privilege_escalation()
        
        # Testes de rate limiting
        self.test_rate_limiting()
        
        # Testes de vazamento de informações
        self.test_information_disclosure()
        
        logger.info(f"Testes concluídos. {len(self.vulnerabilities)} vulnerabilidades encontradas.")
        return self.vulnerabilities
    
    def authenticate(self) -> bool:
        """
        Autentica na API.
        
        Returns:
            bool: True se a autenticação foi bem-sucedida
        """
        if not self.username or not self.password:
            logger.warning("Credenciais não fornecidas. Pulando autenticação.")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/token",
                data={"username": self.username, "password": self.password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                logger.info("Autenticação bem-sucedida")
                return True
            else:
                logger.warning(f"Falha na autenticação: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro durante autenticação: {str(e)}")
            return False
    
    def add_vulnerability(self, name: str, severity: str, description: str, endpoint: str = None, details: Any = None):
        """
        Adiciona uma vulnerabilidade à lista.
        
        Args:
            name: Nome da vulnerabilidade
            severity: Severidade (Critical, High, Medium, Low, Info)
            description: Descrição da vulnerabilidade
            endpoint: Endpoint afetado
            details: Detalhes adicionais
        """
        vulnerability = {
            "name": name,
            "severity": severity,
            "description": description,
            "endpoint": endpoint,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.vulnerabilities.append(vulnerability)
        logger.warning(f"Vulnerabilidade encontrada: {name} ({severity}) - {description}")
    
    def test_authentication(self):
        """Testa vulnerabilidades de autenticação."""
        logger.info("Testando vulnerabilidades de autenticação")
        
        # Teste de força bruta
        self._test_brute_force_protection()
        
        # Teste de senhas fracas
        self._test_weak_passwords()
        
        # Teste de tokens JWT
        self._test_jwt_vulnerabilities()
    
    def _test_brute_force_protection(self):
        """Testa proteção contra força bruta."""
        if not self.username:
            return
        
        # Tenta fazer login várias vezes com senha incorreta
        failed_attempts = 0
        max_attempts = 10
        
        for i in range(max_attempts):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/auth/token",
                    data={"username": self.username, "password": "wrong_password"}
                )
                
                if response.status_code == 429:
                    # Bloqueio detectado
                    logger.info("Proteção contra força bruta detectada")
                    return
                
                failed_attempts += 1
                time.sleep(0.5)  # Pequeno delay para não sobrecarregar
            except Exception:
                continue
        
        if failed_attempts >= max_attempts:
            self.add_vulnerability(
                name="Falta de proteção contra força bruta",
                severity="High",
                description="A API não implementa proteção contra ataques de força bruta",
                endpoint="/api/v1/auth/token",
                details={"attempts": failed_attempts}
            )
    
    def _test_weak_passwords(self):
        """Testa aceitação de senhas fracas."""
        # Lista de senhas fracas comuns
        weak_passwords = ["123456", "password", "admin", "qwerty", "welcome"]
        
        # Tenta criar um usuário com senha fraca
        for password in weak_passwords:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json={
                        "username": f"test_user_{random.randint(1000, 9999)}",
                        "email": f"test{random.randint(1000, 9999)}@example.com",
                        "password": password
                    }
                )
                
                if response.status_code == 201 or response.status_code == 200:
                    self.add_vulnerability(
                        name="Aceitação de senhas fracas",
                        severity="Medium",
                        description=f"A API aceita senhas fracas como '{password}'",
                        endpoint="/api/v1/auth/register",
                        details={"password": password}
                    )
                    break
            except Exception:
                continue
    
    def _test_jwt_vulnerabilities(self):
        """Testa vulnerabilidades em tokens JWT."""
        if not self.token:
            return
        
        # Verifica se o token tem assinatura
        parts = self.token.split(".")
        if len(parts) != 3:
            self.add_vulnerability(
                name="Token JWT mal formado",
                severity="Critical",
                description="O token JWT não segue o formato padrão",
                details={"token_parts": len(parts)}
            )
            return
        
        # Verifica algoritmo none
        try:
            import base64
            header = json.loads(self._base64url_decode(parts[0]))
            if header.get("alg") == "none":
                self.add_vulnerability(
                    name="JWT com algoritmo 'none'",
                    severity="Critical",
                    description="O token JWT usa o algoritmo 'none', o que permite falsificação de tokens",
                    details={"header": header}
                )
        except Exception:
            pass
    
    def test_sql_injection(self):
        """Testa vulnerabilidades de injeção SQL."""
        logger.info("Testando vulnerabilidades de injeção SQL")
        
        # Payloads de injeção SQL
        payloads = [
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
            "' UNION SELECT username, password FROM users --",
            "1; SELECT * FROM information_schema.tables"
        ]
        
        # Endpoints para testar
        endpoints = [
            "/api/v1/clientes",
            "/api/v1/leads",
            "/api/v1/clientes/cnpj"
        ]
        
        for endpoint in endpoints:
            for payload in payloads:
                try:
                    # Teste em parâmetros de consulta
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        params={"q": payload, "filter": payload}
                    )
                    
                    # Verifica se a resposta contém indicadores de SQL
                    if self._check_sql_error_patterns(response.text):
                        self.add_vulnerability(
                            name="Possível injeção SQL",
                            severity="Critical",
                            description="A resposta contém indicadores de erro SQL",
                            endpoint=endpoint,
                            details={"payload": payload, "response": response.text[:200]}
                        )
                        break
                    
                    # Teste em corpo JSON
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={"search": payload, "filter": payload}
                    )
                    
                    if self._check_sql_error_patterns(response.text):
                        self.add_vulnerability(
                            name="Possível injeção SQL",
                            severity="Critical",
                            description="A resposta contém indicadores de erro SQL",
                            endpoint=endpoint,
                            details={"payload": payload, "response": response.text[:200]}
                        )
                        break
                except Exception:
                    continue
    
    def _check_sql_error_patterns(self, text: str) -> bool:
        """
        Verifica se o texto contém padrões de erro SQL.
        
        Args:
            text: Texto a ser verificado
            
        Returns:
            bool: True se encontrar padrões de erro SQL
        """
        patterns = [
            r"SQL syntax",
            r"ORA-[0-9]{5}",
            r"MySQL error",
            r"SQL Server error",
            r"PostgreSQL error",
            r"SQLite3::",
            r"SQLSTATE\[[0-9A-Z]{5}\]"
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def test_xss_vulnerabilities(self):
        """Testa vulnerabilidades XSS."""
        logger.info("Testando vulnerabilidades XSS")
        
        # Payloads XSS
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        # Endpoints para testar
        endpoints = [
            "/api/v1/clientes",
            "/api/v1/leads"
        ]
        
        for endpoint in endpoints:
            for payload in payloads:
                try:
                    # Teste em parâmetros de consulta
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        params={"q": payload, "name": payload}
                    )
                    
                    # Verifica se o payload foi refletido na resposta
                    if payload in response.text:
                        self.add_vulnerability(
                            name="Possível XSS refletido",
                            severity="High",
                            description="O payload XSS foi refletido na resposta",
                            endpoint=endpoint,
                            details={"payload": payload}
                        )
                        break
                    
                    # Teste em corpo JSON
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={"name": payload, "description": payload}
                    )
                    
                    if response.status_code == 201 or response.status_code == 200:
                        # Verifica se o payload foi armazenado
                        get_response = self.session.get(f"{self.base_url}{endpoint}")
                        if payload in get_response.text:
                            self.add_vulnerability(
                                name="Possível XSS armazenado",
                                severity="Critical",
                                description="O payload XSS foi armazenado e refletido em outra página",
                                endpoint=endpoint,
                                details={"payload": payload}
                            )
                            break
                except Exception:
                    continue
    
    def test_command_injection(self):
        """Testa vulnerabilidades de injeção de comandos."""
        logger.info("Testando vulnerabilidades de injeção de comandos")
        
        # Payloads de injeção de comandos
        payloads = [
            "$(whoami)",
            "`whoami`",
            "| whoami",
            "; whoami",
            "& whoami",
            "&& whoami",
            "|| whoami",
            "> /tmp/test"
        ]
        
        # Endpoints para testar
        endpoints = [
            "/api/v1/clientes",
            "/api/v1/leads",
            "/api/v1/clientes/cnpj"
        ]
        
        for endpoint in endpoints:
            for payload in payloads:
                try:
                    # Teste em parâmetros de consulta
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        params={"q": payload, "filter": payload}
                    )
                    
                    # Verifica se a resposta contém indicadores de execução de comando
                    if self._check_command_execution_patterns(response.text):
                        self.add_vulnerability(
                            name="Possível injeção de comandos",
                            severity="Critical",
                            description="A resposta contém indicadores de execução de comandos",
                            endpoint=endpoint,
                            details={"payload": payload, "response": response.text[:200]}
                        )
                        break
                    
                    # Teste em corpo JSON
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={"search": payload, "filter": payload}
                    )
                    
                    if self._check_command_execution_patterns(response.text):
                        self.add_vulnerability(
                            name="Possível injeção de comandos",
                            severity="Critical",
                            description="A resposta contém indicadores de execução de comandos",
                            endpoint=endpoint,
                            details={"payload": payload, "response": response.text[:200]}
                        )
                        break
                except Exception:
                    continue
    
    def _check_command_execution_patterns(self, text: str) -> bool:
        """
        Verifica se o texto contém padrões de execução de comandos.
        
        Args:
            text: Texto a ser verificado
            
        Returns:
            bool: True se encontrar padrões de execução de comandos
        """
        patterns = [
            r"uid=\d+\(\w+\)",  # Saída de whoami/id
            r"root:",  # Saída de /etc/passwd
            r"Directory of",  # Saída de dir (Windows)
            r"Volume in drive",  # Saída de dir (Windows)
            r"total \d+",  # Saída de ls -l
            r"[drwx-]{10}",  # Permissões de arquivo Unix
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def test_security_headers(self):
        """Testa cabeçalhos de segurança HTTP."""
        logger.info("Testando cabeçalhos de segurança HTTP")
        
        try:
            response = self.session.get(self.base_url)
            headers = response.headers
            
            # Cabeçalhos de segurança importantes
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                "X-XSS-Protection": "1; mode=block",
                "Content-Security-Policy": None,  # Qualquer valor é aceitável
                "Strict-Transport-Security": None,  # Qualquer valor é aceitável
                "Referrer-Policy": None,  # Qualquer valor é aceitável
            }
            
            for header, expected_value in security_headers.items():
                if header not in headers:
                    self.add_vulnerability(
                        name=f"Cabeçalho {header} ausente",
                        severity="Medium",
                        description=f"O cabeçalho de segurança {header} não está presente na resposta",
                        details={"headers": dict(headers)}
                    )
                elif expected_value is not None:
                    if isinstance(expected_value, list):
                        if headers[header] not in expected_value:
                            self.add_vulnerability(
                                name=f"Cabeçalho {header} com valor incorreto",
                                severity="Medium",
                                description=f"O cabeçalho {header} tem valor '{headers[header]}', esperado um de {expected_value}",
                                details={"headers": dict(headers)}
                            )
                    elif headers[header] != expected_value:
                        self.add_vulnerability(
                            name=f"Cabeçalho {header} com valor incorreto",
                            severity="Medium",
                            description=f"O cabeçalho {header} tem valor '{headers[header]}', esperado '{expected_value}'",
                            details={"headers": dict(headers)}
                        )
        except Exception as e:
            logger.error(f"Erro ao testar cabeçalhos de segurança: {str(e)}")
    
    def test_cors_configuration(self):
        """Testa configuração de CORS."""
        logger.info("Testando configuração de CORS")
        
        try:
            # Testa com origem permitida
            response = self.session.options(
                f"{self.base_url}/api/v1/clientes",
                headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"}
            )
            
            # Verifica se CORS está configurado corretamente
            if "Access-Control-Allow-Origin" in response.headers:
                # Testa com origem não permitida
                response = self.session.options(
                    f"{self.base_url}/api/v1/clientes",
                    headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "GET"}
                )
                
                if "Access-Control-Allow-Origin" in response.headers:
                    if response.headers["Access-Control-Allow-Origin"] == "*":
                        self.add_vulnerability(
                            name="CORS configurado para permitir qualquer origem",
                            severity="Medium",
                            description="A configuração de CORS permite requisições de qualquer origem",
                            details={"headers": dict(response.headers)}
                        )
                    elif response.headers["Access-Control-Allow-Origin"] == "http://evil.com":
                        self.add_vulnerability(
                            name="CORS não valida origens corretamente",
                            severity="High",
                            description="A configuração de CORS permite requisições de origens não confiáveis",
                            details={"headers": dict(response.headers)}
                        )
        except Exception as e:
            logger.error(f"Erro ao testar configuração de CORS: {str(e)}")
    
    def test_ssl_configuration(self):
        """Testa configuração SSL/TLS."""
        logger.info("Testando configuração SSL/TLS")
        
        if not self.base_url.startswith("https://"):
            self.add_vulnerability(
                name="HTTPS não utilizado",
                severity="Critical",
                description="A API não utiliza HTTPS para comunicação segura",
                details={"url": self.base_url}
            )
            return
        
        try:
            # Tenta conexão com TLS 1.0 (inseguro)
            import ssl
            import socket
            
            hostname = self.base_url.split("//")[1].split("/")[0]
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            
            with socket.create_connection((hostname, 443)) as sock:
                try:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        self.add_vulnerability(
                            name="TLS 1.0 habilitado",
                            severity="High",
                            description="O servidor aceita conexões com TLS 1.0, que é considerado inseguro",
                            details={"hostname": hostname}
                        )
                except ssl.SSLError:
                    # TLS 1.0 não suportado (comportamento correto)
                    pass
        except Exception as e:
            logger.error(f"Erro ao testar configuração SSL/TLS: {str(e)}")
    
    def test_authorization_bypass(self):
        """Testa bypass de autorização."""
        logger.info("Testando bypass de autorização")
        
        # Endpoints protegidos
        protected_endpoints = [
            "/api/v1/clientes",
            "/api/v1/leads"
        ]
        
        # Salva o token atual
        original_token = self.token
        original_headers = self.session.headers.copy()
        
        # Remove o token de autenticação
        self.token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        for endpoint in protected_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code != 401 and response.status_code != 403:
                    self.add_vulnerability(
                        name="Bypass de autorização",
                        severity="Critical",
                        description=f"Endpoint protegido {endpoint} acessível sem autenticação",
                        endpoint=endpoint,
                        details={"status_code": response.status_code}
                    )
            except Exception:
                continue
        
        # Restaura o token
        self.token = original_token
        self.session.headers = original_headers
    
    def test_privilege_escalation(self):
        """Testa escalação de privilégios."""
        logger.info("Testando escalação de privilégios")
        
        # Endpoints administrativos
        admin_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/settings"
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    self.add_vulnerability(
                        name="Possível escalação de privilégios",
                        severity="Critical",
                        description=f"Endpoint administrativo {endpoint} acessível com usuário comum",
                        endpoint=endpoint,
                        details={"status_code": response.status_code}
                    )
            except Exception:
                continue
    
    def test_rate_limiting(self):
        """Testa proteção contra abuso de taxa de requisições."""
        logger.info("Testando proteção contra abuso de taxa de requisições")
        
        # Endpoint para testar
        endpoint = "/api/v1/clientes"
        
        # Faz várias requisições em paralelo
        num_requests = 50
        responses = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._make_request, endpoint) for _ in range(num_requests)]
            responses = [future.result() for future in futures]
        
        # Verifica se alguma requisição foi limitada (429 Too Many Requests)
        if 429 not in [r.status_code for r in responses if r]:
            self.add_vulnerability(
                name="Falta de proteção contra abuso de taxa",
                severity="Medium",
                description=f"O endpoint {endpoint} não implementa limitação de taxa após {num_requests} requisições",
                endpoint=endpoint,
                details={"num_requests": num_requests}
            )
    
    def _make_request(self, endpoint: str) -> Optional[requests.Response]:
        """
        Faz uma requisição para um endpoint.
        
        Args:
            endpoint: Endpoint para requisição
            
        Returns:
            Response: Objeto de resposta ou None em caso de erro
        """
        try:
            return self.session.get(f"{self.base_url}{endpoint}")
        except Exception:
            return None
    
    def test_information_disclosure(self):
        """Testa vazamento de informações sensíveis."""
        logger.info("Testando vazamento de informações sensíveis")
        
        # Endpoints para testar
        endpoints = [
            "/",
            "/api",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        
        # Padrões sensíveis
        sensitive_patterns = [
            r"password\s*=\s*['\"]([^'\"]+)['\"]",
            r"secret\s*=\s*['\"]([^'\"]+)['\"]",
            r"api[_-]?key\s*=\s*['\"]([^'\"]+)['\"]",
            r"connectionstring\s*=\s*['\"]([^'\"]+)['\"]",
            r"(mongodb|redis|postgres|mysql)://[^\s]+",
            r"-----BEGIN (RSA|DSA|EC|PGP) PRIVATE KEY-----"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    # Verifica se há informações sensíveis na resposta
                    for pattern in sensitive_patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        if matches:
                            self.add_vulnerability(
                                name="Vazamento de informações sensíveis",
                                severity="Critical",
                                description=f"O endpoint {endpoint} expõe informações sensíveis",
                                endpoint=endpoint,
                                details={"pattern": pattern, "matches_count": len(matches)}
                            )
                            break
            except Exception:
                continue
    
    def _base64url_decode(self, input: str) -> str:
        """
        Decodifica uma string base64url.
        
        Args:
            input: String base64url
            
        Returns:
            str: String decodificada
        """
        import base64
        padding = '=' * (4 - (len(input) % 4))
        return base64.urlsafe_b64decode(input + padding).decode('utf-8')
    
    def generate_report(self, output_file: str = "penetration_test_report.json") -> None:
        """
        Gera um relatório dos testes de penetração.
        
        Args:
            output_file: Arquivo de saída para o relatório
        """
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target": self.base_url,
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "critical": len([v for v in self.vulnerabilities if v["severity"] == "Critical"]),
                "high": len([v for v in self.vulnerabilities if v["severity"] == "High"]),
                "medium": len([v for v in self.vulnerabilities if v["severity"] == "Medium"]),
                "low": len([v for v in self.vulnerabilities if v["severity"] == "Low"]),
                "info": len([v for v in self.vulnerabilities if v["severity"] == "Info"])
            },
            "vulnerabilities": self.vulnerabilities
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Relatório gerado em {output_file}")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Ferramenta de teste de penetração para Aurora-Platform")
    parser.add_argument("--url", required=True, help="URL base da API")
    parser.add_argument("--username", help="Nome de usuário para autenticação")
    parser.add_argument("--password", help="Senha para autenticação")
    parser.add_argument("--output", default="penetration_test_report.json", help="Arquivo de saída para o relatório")
    
    args = parser.parse_args()
    
    tester = PenetrationTester(args.url, args.username, args.password)
    
    if args.username and args.password:
        tester.authenticate()
    
    tester.run_all_tests()
    tester.generate_report(args.output)

if __name__ == "__main__":
    main()