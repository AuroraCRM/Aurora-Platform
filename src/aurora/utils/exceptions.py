# src/aurora/utils/exceptions.py

class CRMServiceError(Exception):
    """Exceção base para erros na camada de serviço do CRM."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Podemos adicionar outras exceções customizadas aqui no futuro
