from setuptools import setup, find_packages

setup(
    name="aurora",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.0",
        "pydantic>=1.8.0",
        "python-dotenv>=0.19.0",
        "redis>=4.0.0",
        "azure-keyvault-secrets>=4.3.0",
        "azure-identity>=1.7.0",
        "qrcode>=7.3.1",
        "pyotp>=2.6.0",
        "pillow>=9.0.0",  # Dependência do qrcode
        "setuptools>=58.0.0",  # Explicitamente requerido
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2",
        ],
    },
    python_requires=">=3.8",
)