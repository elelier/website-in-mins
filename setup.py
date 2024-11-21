from setuptools import setup, find_packages

setup(
    name="website-in-mins",
    version="2.0.0",
    description="FrontPage Rapid - Generador de páginas web profesionales",
    packages=find_packages(include=["app", "app.*"]),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "fastapi-limiter",
        "fastapi-security",
        "uvicorn>=0.24.0",
        "jinja2>=3.1.2",
        "pydantic>=2.4.2",
        "pydantic-settings>=2.0.3",
        "rcssmin>=1.1.1",
        "pillow>=10.1.0",
        "httpx>=0.25.1",
        "python-multipart>=0.0.6",
        "python-jose",
        "passlib[bcrypt]",
        "email-validator>=2.1.0",
        "bcrypt>=4.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
        ]
    }
)
