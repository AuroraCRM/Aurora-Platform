from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from aurora_platform.config import settings


class AzureKeyVault:
    """Integração com o Azure Key Vault para gerenciamento de segredos."""

    def __init__(self):
        self.vault_url = settings.AZURE_KEY_VAULT_URI
        if self.vault_url:
            self.credential = DefaultAzureCredential()
            self.client = SecretClient(
                vault_url=self.vault_url, credential=self.credential
            )
        else:
            self.client = None

    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Recupera um segredo do Azure Key Vault.

        Args:
            secret_name: Nome do segredo

        Returns:
            str: Valor do segredo ou None se não encontrado
        """
        if not self.client:
            return None

        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception:
            return None

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Armazena um segredo no Azure Key Vault.

        Args:
            secret_name: Nome do segredo
            secret_value: Valor do segredo

        Returns:
            bool: True se o segredo foi armazenado com sucesso
        """
        if not self.client:
            return False

        try:
            self.client.set_secret(secret_name, secret_value)
            return True
        except Exception:
            return False
