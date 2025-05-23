# **CENTINELA**
by Joaquín Romero (c), 2025  
## Seguimiento automático de los cambios de ciertos valores en una página de Crowdfunding mediante Web Scrapping  
  
## Descripción general  
  
Aplicación de escritorio para Windows que se aloja en la bandeja del sistema y se ejecuta en segundo plano
Realiza Web Scrapping cada n minutos de un intervalo prefijado por el usuario y extrae información cuantitavia de una página Web de Crowdfunding (Verkami).
  
## Instalación  
1. *Instalar Python*: Asegurarse de que Python esté instalado en el PC. Puedes descargar e instalar Python desde el sitio web oficial de Python.
2. *Descomprimir ficheros del proyecto*: Esto incluye todos los ficheros y estrcutura de carpetas necesaria para la ejecución de la aplicación.
3. *Crear un entorno virtual*: En la carpeta del proyecto descomprimido, crear un nuevo entorno virtual ejecutando el comando:
~~~
    c:\mi_usuario\Centinela\>  python -m venv .venv
~~~


4. *Activar el entorno virtual*:
    - En Windows se hace mediante el siguiente comando:
~~~
    c:\mi_usuario\Centinela\>  .venv\Scripts\activate 
~~~

Tras la activación, el prompt del sistema cambiará mostrando el nombre del entorno virtual entre paréntesis '(.venv)' delante del prompt:
~~~
    (.venv) c:\mi_usuario\Centinela\>  _ 
~~~

5. *Instalar dependencias*: Ejecutar el siguiente comando instalará en el entorno virtual de la aplicación todos los módulos y librerías que ésta necesita:
~~~
    (.venv) c:\mi_usuario\Centinela\>  pip install -r requirements.txt
~~~


## Ejecución  
Ejecutar en la línea de comandos:
~~~
    (.venv) c:\mi_usuario\Centinela\>  python app/main.py
~~~



