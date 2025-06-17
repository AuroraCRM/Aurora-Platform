# src/aurora/utils/validators.py

import re
from typing import Optional

def validate_cnpj(cnpj: str) -> bool:
    """
    Valida um CNPJ.
    
    Args:
        cnpj: CNPJ a ser validado
        
    Returns:
        bool: True se o CNPJ for válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    peso = 5
    for i in range(12):
        soma += int(cnpj[i]) * peso
        peso = 9 if peso == 2 else peso - 1
    
    digito1 = 11 - (soma % 11)
    digito1 = 0 if digito1 > 9 else digito1
    
    # Verifica o primeiro dígito verificador
    if int(cnpj[12]) != digito1:
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    peso = 6
    for i in range(13):
        soma += int(cnpj[i]) * peso
        peso = 9 if peso == 2 else peso - 1
    
    digito2 = 11 - (soma % 11)
    digito2 = 0 if digito2 > 9 else digito2
    
    # Verifica o segundo dígito verificador
    return int(cnpj[13]) == digito2

def sanitize_input(input_str: Optional[str]) -> Optional[str]:
    """
    Sanitiza uma string de entrada para prevenir injeção de código.
    
    Args:
        input_str: String a ser sanitizada
        
    Returns:
        str: String sanitizada
    """
    if input_str is None:
        return None
    
    # Remove caracteres potencialmente perigosos
    sanitized = re.sub(r'[<>&\'"]', '', input_str)
    
    # Limita o tamanho da string
    return sanitized[:1000]  # Limita a 1000 caracteres

def validate_email(email: str) -> bool:
    """
    Valida um endereço de e-mail.
    
    Args:
        email: E-mail a ser validado
        
    Returns:
        bool: True se o e-mail for válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Valida um número de telefone.
    
    Args:
        phone: Telefone a ser validado
        
    Returns:
        bool: True se o telefone for válido, False caso contrário
    """
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', phone)
    
    # Verifica se tem entre 10 e 15 dígitos
    return 10 <= len(phone) <= 15