"""
Setup configuration for Sougui AI Chatbot
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sougui-ai-chatbot",
    version="2.0.0",
    author="Sougui Team",
    author_email="support@sougui.tn",
    description="Chatbot IA avancé pour l'analyse business de Sougui",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sougui/ai-chatbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Business/Industry",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sougui-ai=main:main",
        ],
    },
)
