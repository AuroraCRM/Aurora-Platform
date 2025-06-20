#!/usr/bin/env python3
"""
Script para verificar e atualizar dependências do projeto Aurora-Platform.
Este script verifica vulnerabilidades conhecidas e atualiza pacotes automaticamente.
"""

import subprocess
import json
import sys
import os
import re
import argparse
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("dependency_update.log")],
)
logger = logging.getLogger(__name__)


class DependencyUpdater:
    """Classe para gerenciar atualizações de dependências."""

    def __init__(
        self, requirements_file: str, auto_update: bool = False, create_pr: bool = False
    ):
        """
        Inicializa o atualizador de dependências.

        Args:
            requirements_file: Caminho para o arquivo requirements.txt
            auto_update: Se True, atualiza automaticamente as dependências
            create_pr: Se True, cria um PR com as atualizações
        """
        self.requirements_file = requirements_file
        self.auto_update = auto_update
        self.create_pr = create_pr
        self.dependencies = {}
        self.vulnerabilities = []
        self.updates_available = []

    def load_dependencies(self) -> Dict[str, str]:
        """
        Carrega as dependências do arquivo requirements.txt.

        Returns:
            Dict: Mapeamento de pacotes para versões
        """
        try:
            with open(self.requirements_file, "r") as f:
                lines = f.readlines()

            # Parse requirements.txt
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Remove comentários inline
                line = line.split("#")[0].strip()

                # Parse package and version
                match = re.match(
                    r"^([a-zA-Z0-9_\-\.]+)([<>=!~]+)([a-zA-Z0-9_\-\.]+).*$", line
                )
                if match:
                    package, operator, version = match.groups()
                    self.dependencies[package] = {
                        "version": version,
                        "operator": operator,
                    }
                else:
                    # Sem versão específica
                    package = line.split("[")[0]  # Remove extras como [crypto]
                    self.dependencies[package] = {"version": "latest", "operator": "=="}

            logger.info(
                f"Carregadas {len(self.dependencies)} dependências de {self.requirements_file}"
            )
            return self.dependencies
        except Exception as e:
            logger.error(f"Erro ao carregar dependências: {str(e)}")
            return {}

    def check_vulnerabilities(self) -> List[Dict]:
        """
        Verifica vulnerabilidades nas dependências usando safety.

        Returns:
            List: Lista de vulnerabilidades encontradas
        """
        try:
            # Instala safety se necessário
            self._ensure_tool_installed("safety")

            # Executa safety check
            result = subprocess.run(
                ["safety", "check", "--json", "-r", self.requirements_file],
                capture_output=True,
                text=True,
            )

            # Parse output
            if result.returncode == 0:
                logger.info("Nenhuma vulnerabilidade encontrada")
                return []

            try:
                vulnerabilities = json.loads(result.stdout)
                self.vulnerabilities = vulnerabilities
                logger.warning(f"Encontradas {len(vulnerabilities)} vulnerabilidades")
                return vulnerabilities
            except json.JSONDecodeError:
                logger.error("Erro ao analisar saída do safety")
                return []
        except Exception as e:
            logger.error(f"Erro ao verificar vulnerabilidades: {str(e)}")
            return []

    def check_updates(self) -> List[Dict]:
        """
        Verifica atualizações disponíveis para as dependências.

        Returns:
            List: Lista de atualizações disponíveis
        """
        try:
            # Instala pip-review se necessário
            self._ensure_tool_installed("pip-review")

            # Executa pip-review
            result = subprocess.run(
                ["pip-review", "--raw"], capture_output=True, text=True
            )

            updates = []
            for line in result.stdout.splitlines():
                if "=>" in line:
                    package, versions = line.split(" ", 1)
                    current_version, new_version = versions.split(" => ")
                    updates.append(
                        {
                            "package": package,
                            "current_version": current_version,
                            "new_version": new_version.rstrip(),
                        }
                    )

            self.updates_available = updates
            logger.info(f"Encontradas {len(updates)} atualizações disponíveis")
            return updates
        except Exception as e:
            logger.error(f"Erro ao verificar atualizações: {str(e)}")
            return []

    def update_dependencies(self, only_vulnerable: bool = True) -> bool:
        """
        Atualiza as dependências.

        Args:
            only_vulnerable: Se True, atualiza apenas pacotes vulneráveis

        Returns:
            bool: True se as atualizações foram bem-sucedidas
        """
        if not self.auto_update:
            logger.info("Atualização automática desativada")
            return False

        try:
            packages_to_update = []

            # Identifica pacotes para atualizar
            if only_vulnerable:
                # Extrai nomes de pacotes vulneráveis
                vulnerable_packages = set()
                for vuln in self.vulnerabilities:
                    if isinstance(vuln, list) and len(vuln) >= 2:
                        vulnerable_packages.add(vuln[0])
                    elif isinstance(vuln, dict) and "package" in vuln:
                        vulnerable_packages.add(vuln["package"])

                # Filtra atualizações para pacotes vulneráveis
                for update in self.updates_available:
                    if update["package"] in vulnerable_packages:
                        packages_to_update.append(update["package"])
            else:
                # Atualiza todos os pacotes com atualizações disponíveis
                packages_to_update = [
                    update["package"] for update in self.updates_available
                ]

            if not packages_to_update:
                logger.info("Nenhum pacote para atualizar")
                return True

            # Atualiza os pacotes
            logger.info(
                f"Atualizando {len(packages_to_update)} pacotes: {', '.join(packages_to_update)}"
            )

            for package in packages_to_update:
                subprocess.run(["pip", "install", "--upgrade", package], check=True)

            # Atualiza o arquivo requirements.txt
            self._update_requirements_file(packages_to_update)

            logger.info("Pacotes atualizados com sucesso")

            # Cria PR se necessário
            if self.create_pr:
                self._create_pull_request(packages_to_update)

            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar dependências: {str(e)}")
            return False

    def _update_requirements_file(self, updated_packages: List[str]) -> None:
        """
        Atualiza o arquivo requirements.txt com as novas versões.

        Args:
            updated_packages: Lista de pacotes atualizados
        """
        try:
            # Obtém as versões atuais dos pacotes
            package_versions = {}
            for package in updated_packages:
                result = subprocess.run(
                    ["pip", "show", package], capture_output=True, text=True
                )

                for line in result.stdout.splitlines():
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        package_versions[package] = version
                        break

            # Lê o arquivo requirements.txt
            with open(self.requirements_file, "r") as f:
                lines = f.readlines()

            # Atualiza as versões
            new_lines = []
            for line in lines:
                original_line = line
                line = line.strip()
                if not line or line.startswith("#"):
                    new_lines.append(original_line)
                    continue

                # Remove comentários inline
                code_part = line.split("#")[0].strip()
                comment_part = (
                    line[len(code_part) :] if len(line) > len(code_part) else ""
                )

                # Parse package
                match = re.match(r"^([a-zA-Z0-9_\-\.]+).*$", code_part)
                if match:
                    package = match.group(1)
                    if package in package_versions:
                        new_version = package_versions[package]
                        new_line = f"{package}>={new_version}{comment_part}\n"
                        new_lines.append(new_line)
                        logger.info(f"Atualizando {package} para >={new_version}")
                    else:
                        new_lines.append(original_line)
                else:
                    new_lines.append(original_line)

            # Escreve o arquivo atualizado
            with open(self.requirements_file, "w") as f:
                f.writelines(new_lines)

            logger.info(f"Arquivo {self.requirements_file} atualizado")
        except Exception as e:
            logger.error(f"Erro ao atualizar arquivo requirements.txt: {str(e)}")

    def _create_pull_request(self, updated_packages: List[str]) -> None:
        """
        Cria um Pull Request com as atualizações.

        Args:
            updated_packages: Lista de pacotes atualizados
        """
        try:
            # Verifica se git está disponível
            subprocess.run(["git", "--version"], check=True, capture_output=True)

            # Cria branch
            branch_name = (
                f"dependency-updates-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)

            # Adiciona alterações
            subprocess.run(["git", "add", self.requirements_file], check=True)

            # Commit
            commit_message = f"Atualiza dependências: {', '.join(updated_packages)}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # Push
            subprocess.run(
                ["git", "push", "--set-upstream", "origin", branch_name], check=True
            )

            logger.info(f"Branch {branch_name} criada e enviada para o repositório")
            logger.info(
                "Crie um Pull Request manualmente ou configure a API do GitHub para criação automática"
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar comando git: {e.stderr}")
        except Exception as e:
            logger.error(f"Erro ao criar Pull Request: {str(e)}")

    def _ensure_tool_installed(self, tool: str) -> None:
        """
        Garante que uma ferramenta está instalada.

        Args:
            tool: Nome da ferramenta
        """
        try:
            # Verifica se a ferramenta está instalada
            subprocess.run([tool, "--version"], capture_output=True)
        except FileNotFoundError:
            logger.info(f"Instalando {tool}...")
            subprocess.run(["pip", "install", tool], check=True)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Gerenciador de dependências para Aurora-Platform"
    )
    parser.add_argument(
        "--requirements", default="requirements.txt", help="Arquivo de requisitos"
    )
    parser.add_argument(
        "--auto-update",
        action="store_true",
        help="Atualiza automaticamente dependências vulneráveis",
    )
    parser.add_argument(
        "--update-all",
        action="store_true",
        help="Atualiza todas as dependências, não apenas vulneráveis",
    )
    parser.add_argument(
        "--create-pr",
        action="store_true",
        help="Cria um Pull Request com as atualizações",
    )

    args = parser.parse_args()

    updater = DependencyUpdater(
        requirements_file=args.requirements,
        auto_update=args.auto_update or args.update_all,
        create_pr=args.create_pr,
    )

    # Carrega dependências
    updater.load_dependencies()

    # Verifica vulnerabilidades
    vulnerabilities = updater.check_vulnerabilities()

    # Verifica atualizações disponíveis
    updates = updater.check_updates()

    # Atualiza dependências se necessário
    if args.auto_update or args.update_all:
        updater.update_dependencies(only_vulnerable=not args.update_all)

    # Exibe resumo
    print("\n=== Resumo ===")
    print(f"Dependências analisadas: {len(updater.dependencies)}")
    print(f"Vulnerabilidades encontradas: {len(vulnerabilities)}")
    print(f"Atualizações disponíveis: {len(updates)}")

    if vulnerabilities:
        print("\n⚠️ VULNERABILIDADES ENCONTRADAS ⚠️")
        for vuln in vulnerabilities:
            if isinstance(vuln, list) and len(vuln) >= 3:
                print(f"- {vuln[0]} {vuln[1]}: {vuln[2]}")
            elif isinstance(vuln, dict):
                print(
                    f"- {vuln.get('package')} {vuln.get('vulnerable_spec')}: {vuln.get('advisory')}"
                )

    if updates:
        print("\nAtualizações disponíveis:")
        for update in updates:
            print(
                f"- {update['package']}: {update['current_version']} -> {update['new_version']}"
            )


if __name__ == "__main__":
    main()
