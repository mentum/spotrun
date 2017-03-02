from setuptools import setup, find_packages
import re


version = ''
with open('spotrun/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

setup(
    name='spotrun',
    author='mentum',
    url='https://github.com/mentum/spotrun',
    version=version,
    packages=find_packages(),
    license='MIT',
    description='Run tasks on EC2 spot instances',
    entry_points={
        'console_scripts': [
            'spotrun=spotrun.main:main'
        ]
    },
    install_requires=[
        "boto3==1.4.4",
        "marshmallow==2.13.0",
        "paramiko==2.1.2"
    ]
)
