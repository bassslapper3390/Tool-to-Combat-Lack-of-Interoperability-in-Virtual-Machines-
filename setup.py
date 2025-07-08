from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vm-interop",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for VM format conversion and migration analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vm-interop",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.4.0",
        "pandas>=1.5.0",
        "scapy>=2.5.0",
        "paramiko>=3.0.0",
        "psutil>=5.9.0",
        "python-socketio>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "vm-interop=vm_interop.gui:main",
        ],
    },
) 