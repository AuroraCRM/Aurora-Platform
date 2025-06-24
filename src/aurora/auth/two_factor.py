# src/aurora/auth/two_factor.py
import pyotp
import qrcode
import io
import base64
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field
from fastapi import HTTPException, status # Importar para usar em exceções

class TwoFactorSetup(BaseModel):
    secret: str
    qrcode_uri: str
    message: str

class TwoFactorVerify(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, description="Código de 6 dígitos do autenticador")


class TwoFactorAuth:
    """
    Gerencia a lógica de Autenticação de Dois Fatores (2FA) usando senhas de uso único (TOTP).
    """
    def __init__(self):
        # Em um cenário real, este dicionário seria substituído por uma tabela no banco de dados.
        # Mapeia user_id para a chave secreta 2FA do usuário.
        self.user_secrets: Dict[str, str] = {}
        
        # Mapeia user_id para uma lista de códigos de backup de uso único.
        self.user_backup_codes: Dict[str, List[str]] = {}
        # Mapeia user_id para o status de ativação do 2FA
        self.user_2fa_enabled_status: Dict[str, bool] = {} # Adicionado para rastrear se 2FA está habilitado


    def generate_secret(self) -> str:
        """Gera uma nova chave secreta para configuração do 2FA."""
        return pyotp.random_base32()

    def get_provisioning_uri(self, user_id: str, issuer_name: str) -> str:
        """
        Gera a URI de provisionamento para ser exibida como um QR Code no app autenticador.
        Também salva o segredo gerado internamente.
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
            return False # ou levantar uma HTTPException se o segredo não existir

        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    async def setup_2fa_for_user(self, user: Dict[str, Any]) -> TwoFactorSetup:
        """
        Gera um novo segredo 2FA para o usuário e um QR code URI para setup.
        Este método é chamado pelo endpoint /2fa/setup.
        """
        username = user["username"]
        if self.user_2fa_enabled_status.get(username): # Verifica se 2FA já está ativo
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA já configurado e ativo para este usuário. Desative primeiro para reconfigurar.",
            )
        
        # Re-usa get_provisioning_uri que já gera e armazena o secret
        totp_uri = self.get_provisioning_uri(user_id=username, issuer_name="AuroraCRM")

        # Gerar o QR code como imagem base64
        img = qrcode.make(totp_uri)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qrcode_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        qrcode_uri = f"data:image/png;base64,{qrcode_base64}"

        return TwoFactorSetup(
            secret=self.user_secrets[username], # Retorna o secret gerado
            qrcode_uri=qrcode_uri,
            message="Escaneie este QR Code com seu aplicativo autenticador e depois ative o 2FA."
        )

    async def enable_2fa_for_user(self, user: Dict[str, Any], code: str) -> bool:
        """
        Ativa o 2FA para um usuário após verificar o código.
        Este método é chamado pelo endpoint /2fa/enable.
        """
        username = user["username"]
        secret = self.user_secrets.get(username)

        if not secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum segredo 2FA configurado para este usuário. Faça o setup primeiro.",
            )

        if self.user_2fa_enabled_status.get(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA já está ativado para este usuário.",
            )

        if self.verify_code(username, code):
            self.user_2fa_enabled_status[username] = True
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código 2FA inválido.",
            )

    async def disable_2fa_for_user(self, user: Dict[str, Any]) -> bool:
        """
        Desativa o 2FA para um usuário.
        Este método é chamado pelo endpoint /2fa/disable.
        """
        username = user["username"]
        if not self.user_2fa_enabled_status.get(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA não está ativado para este usuário.",
            )
        
        self.user_2fa_enabled_status[username] = False
        self.user_secrets.pop(username, None) # Remover o segredo também
        return True

    async def verify_2fa_login(self, username: str, code: str) -> bool:
        """
        Verifica um código 2FA para um usuário durante o processo de login.
        Este método é chamado pelo endpoint /token/2fa.
        """
        if not self.user_2fa_enabled_status.get(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Autenticação de dois fatores não ativada para este usuário.",
            )

        if self.verify_code(username, code):
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código de autenticação de dois fatores inválido.",
            )