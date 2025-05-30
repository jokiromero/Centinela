<h1 align="center">
    <span>Centinela</span>
  <img width="auto" height="50px" src="https://github.com/jokiromero/centinela/images/ojo_abierto.png"/>
</h1>

[//]: # (# **CENTINELA**)
by Joaquín Romero (c), 2025  
## Seguimiento automático de los cambios de ciertos valores en una página de Crowdfunding mediante Web Scrapping  
  
## ✨ Descripción general  
  
Aplicación de escritorio para Windows que se aloja en la bandeja del sistema y se ejecuta en segundo plano.
Realiza Web Scrapping cada 'n' minutos de un intervalo prefijado por el usuario y extrae información cuantitativa de una página Web de Crowdfunding (Verkami).
  
##  🧩 Primera instalación  
1. *Instalar Python*: Asegurarse de que Python esté instalado en el PC. Puedes descargar e instalar Python desde el sitio web oficial de Python.
2. *Crear un entorno virtual*: Este entorno virtual será donde instalaremos el paquete de la aplicación y todas sus dependencias de forma que podrá ejecutarse de manera aislada del resto de aplicaciones y paquetes Python que tengamos instalados en nuestro PC. Puede estar ubicado en cualquier ruta, pero recomendamos en 'c:\users\mi_suario\.centinela', siendo '.centinela' el nombre de dicho entorno. Para crear el entorno virtual usaremos el comando: 
~~~
   c:\users\mi_usuario\>  python -m venv .centinela
~~~

3. Activar el entorno virtual*:
    - En Windows se hace mediante el siguiente comando:
~~~
    c:\users\mi_usuario\>  .centinela\Scripts\activate 
~~~

Tras la activación, el prompt del sistema cambiará mostrando el nombre del entorno virtual entre paréntesis '(.venv)' delante del prompt:
~~~
    (.centinela) c:\users\mi_usuario\>  _ 
~~~

Cuando no se vaya a usar, podrá desactivarse mediante el comando ` .centinela\Scripts\deactivate `

4*Instalar el paquete del proyecto*: Este paquete consiste en un fichero denominado `centinela-<version>.tar.gz` (comprimido ZIP/WinRAR) que contiene todos los ficheros que forman el paquete de aplicación y las librerías necesarias para su funcionamiento. Este paquete está disponible en la carpeta 'dist' del repositorio de Ceninela en GitHub.com. Para instalar este paquete tiene dos opciones: 
- _Opción 1_: Partir de una copia del fichero del paquete disponible en su repositorio clonado local mediante: 
~~~
    (.centinela) c:\users\mi_usuario\>  pip install miRutaRepo/Centinela/dist/<nombre_fichero.tar.gz>
~~~
d- Opción 2: Descargar una copia del fichero del paquete directamente desde GitHub.com y luego instalarlo mediante:
~~~
    (.centinela) c:\users\mi_usuario\>  curl --remote-name 
    
    (.centinela) c:\users\mi_usuario\>  pip install miRutaRepo/Centinela/dist/<nombre_fichero.tar.gz>
~~~




5. *Instalar dependencias*: Ejecutar el siguiente comando instalará en el entorno virtual de la aplicación todos los módulos y librerías que ésta necesita:
~~~
    (.centinela) c:\users\mi_usuario\Centinela\>  pip install -r requirements.txt
~~~


## 📜 Ejecución  
Ejecutar en la línea de comandos:
~~~
    (.venv) c:\users\mi_usuario\Centinela\>  python -m app.main
~~~

🤝🌟🔧💻

