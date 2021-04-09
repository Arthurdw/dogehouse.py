import re
from distutils.core import setup
from os import path

with open('dogehouse/config.py') as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

this_dir = path.abspath(path.dirname(__file__))

with open(path.join(this_dir, "README.rst"), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dogehouse',
    packages=["dogehouse", "dogehouse.utils", "dogehouse.ext"],
    version=version,
    license='MIT',
    description='A Python wrapper for the Dogehouse API.',
    project_urls={
        "Documentation": "https://dogehouse.arthurdw.com",
    },
    long_description=long_description,
    author='Arthurdw',
    author_email='mail@arthurdw.com',
    url='https://github.com/Arthurdw/dogehouse.py',
    download_url=f'https://github.com/Arthurdw/dogehouse.py/archive/{version}.tar.gz',
    keywords=["dogehouse"],
    install_requires=[
        "websockets",
        "python-dateutil"],
    extras_require={
        "telemetry": ["python-socketio[asyncio_client]"]
    },
    classifiers=[
        # Development statuses:
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha'
        'Development Status :: 4 - Beta'
        # Development Status :: 5 - Production/Stable
        # Development Status :: 6 - Mature
        # Development Status :: 7 - Inactive
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
