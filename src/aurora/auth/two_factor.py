# src/aurora/auth/two_factor.py
import pyotp
from typing import Dict, List, Optional

class TwoFactorAuth:
    """
    Gerencia a lógica de Autenticação de Dois Fatores (2FA) usando senhas de uso único (TOTP).
    """
    def __init__(self):
        # Em um cenário real, este dicionário seria substituído por uma tabela no banco de dados.
        # Mapeia user_id para a chave secreta 2FA do usuário.
        self.user_secrets: Dict[str, str] = {}
        
        # CORREÇÃO: Adiciona a anotação de tipo explícita para o dicionário.
        # Mapeia user_id para uma lista de códigos de backup de uso único.
        self.user_backup_codes: Dict[str, List[str]] = {}

    def generate_secret(self) -> str:
        """Gera uma nova chave secreta para configuração do 2FA."""
        return pyotp.random_base32()

    def get_provisioning_uri(self, user_id: str, issuer_name: str) -> str:
        """
        Gera a URI de provisionamento para ser exibida como um QR Code no app autenticador.
        """
        secret = self.generate_secret()
        self.user_secrets[user_id] = secret
        
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name=issuer_name
        )

    def verify_code(self, user_id: str, code: str) -> bool:
        """
        Verifica se um código TOTP fornecido é válido para um usuário.
        """
        secret = self.user_secrets.get(user_id)
        if not secret:
            return False
            
        totp = pyotp.TOTP(secret)
        return totp.verify(code)