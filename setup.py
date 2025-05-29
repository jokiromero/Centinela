import os
from setuptools import setup, find_packages

fichero = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(fichero) as reqsfile:
    requeridos = reqsfile.read().splitlines()

paquetes = find_packages()
print(f"{paquetes=}")

setup(
    name="Centinela",
    version="1.2.20250529",
    author="Joaquín Romero",
    author_email="joki.romero@gmail.com",
    description="Seguimiento por Web Scrapping del importe recaudado en un Crowdfunding de Verkami",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license="GPL-3.0-or-later",
    url="https://github.com/jokiromero/Centinela",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "GPL-3.0-or-later",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Desktop Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
    ],
    python_requires=">=3.8",
    install_requires=requeridos,
    scripts=["centinela.main.py",],
    # py_modules=["config.py", "datos_persistentes.py", "scrapper_verkami.py", "tools.py"],
    packages=paquetes,
    include_package_data=True,  # incluir todos los ficheros del proyecto seiguiendo lo indicado en MANIFIEST.in
)
