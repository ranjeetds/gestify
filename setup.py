"""
Setup script for Gestify
"""

from setuptools import setup, find_packages
import os

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gestify',
    version='2.0.0',
    author='Gestify Contributors',
    author_email='',
    description='AI-Powered Hand Gesture Control for macOS/Linux/Windows',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ranjeetds/gestify',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'opencv-python>=4.8.0',
        'mediapipe>=0.10.0',
        'numpy>=1.24.0',
        'pyautogui>=0.9.50',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'gestify=gestify_lib.__main__:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

