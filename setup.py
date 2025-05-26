import os
from setuptools import setup, find_packages

fichero = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(fichero) as reqsfile:
    requeridos = reqsfile.read().splitlines()

setup(
    name="Centinela",
    version="1.0.0",
    author="Joaquín Romero",
    author_email="joki.romero@gmail.com",
    description="Seguimiento por Web Scrapping del importe recaudado en un Crowdfunding de Verkami",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/tu-usuario/mi-aplicacion",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: Free for non-commercial use',
        "Operating System :: Microsoft :: Windows",
        "Topic :: Desktop Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
    ],
    python_requires=">=3.8",
    install_requires=requeridos,
    packages=find_packages(),
    # packages=["app",],
    include_package_data=True,  # incluir todos los ficheros del proyecto seiguiendo lo indicado en MANIFIEST.in

)
