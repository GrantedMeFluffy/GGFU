from setuptools import setup, find_packages

setup(
    name="gguf_model_chat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "llama-cpp-python>=0.2.0",
        "numpy>=1.21.0",
        "streamlit>=1.28.0",
    ],
    author="Replit User",
    author_email="user@example.com",
    description="A Streamlit application for chatting with GGUF language models",
    keywords="gguf, llm, chat, streamlit",
    url="https://github.com/yourusername/gguf-model-chat",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)