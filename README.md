<h1 align="center">
   <img width="auto" height="35px" src="https://github.com/jokiromero/Centinela/blob/master/centinela/images/ojo_abierto.png"/>
   <p><font size="18px">Centinela</font></p>
</h1>
<p align="center"><font size="2"><i>by Joaquín Romero (c), 2025</i></font></p>
<h1 align="center">Seguimiento automático de los cambios de ciertos valores en una página de Crowdfunding mediante Web Scrapping</h1>

 
<hr />

## ✨ Descripción general  
Aplicación de escritorio para Windows que se aloja en la bandeja del sistema y se ejecuta en segundo plano.
Realiza Web Scrapping cada 'n' minutos de un intervalo prefijado por el usuario y extrae información cuantitativa de una página Web de Crowdfunding (Verkami).
  
##  🧩 Primera instalación  
1. *Instalar Python*: Asegurarse de que Python esté instalado en el PC. Puedes descargar e instalar Python desde el sitio web oficial de Python.
2. *Crear un entorno virtual*: Este entorno virtual será donde instalaremos el paquete de la aplicación y todas sus dependencias de forma que podrá ejecutarse de manera aislada del resto de aplicaciones y paquetes Python que tengamos instalados en nuestro PC. Puede estar ubicado en cualquier ruta, pero recomendamos en 'c:\users\mi_suario\.centinela', siendo '.centinela' el nombre de dicho entorno. Para crear el entorno virtual usaremos el comando: 
~~~
   c:\users\mi_usuario\>  python -m venv .centinela
~~~

3. *Activar el entorno virtual*:
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
- Opción 2: Descargar una copia del fichero del paquete directamente desde GitHub.com y luego instalarlo mediante:
~~~
    (.centinela) c:\users\mi_usuario\>  curl --remote-name https://raw.githubusercontent.com/jokiromero/Centinela/master/dist/centinela-<version>.tar.gz" 
    (.centinela) c:\users\mi_usuario\>  pip install miRutaRepo/Centinela/dist/centinela-<version>.tar.gz>
~~~
(donde `<version>` debe ser sustituido por los dígitos que identifican la versión de que se trate. Por ejemplo `centinela-1.3`)

## 📜 Ejecución  
Ejecutar en la línea de comandos:
~~~
    (.centinela) c:\users\mi_usuario\>  python -m centinela.main
~~~

Nótese que siempre que esté activado el entorno virtual donde hayamos instalado el paquete, no importará en qué directorio nos eoncontremos ya que la aplicación se ejecutará dentro del entorno virtual y ésta no tienen ninguna dependencia fuera del mismo (no realiza ininguna referencia a una carpeta que no forme parte de su árbol de carpetas)

## 🔧 Instalación sucesiva (actualizaciones):

Los pasos que hay que dar son los siguientes:
1. *Activar el entorno virtual*
2. *Desistalar la versión previa*

~~~
    (.centinela) c:\users\mi_usuario\>  pip uninstall centinela 
~~~
En algunos casos, este paso no es necesario y la propia reinstalación del nuevo paquete sustituye al anterior.

4. *Instalar la nueva versión*:

Repetir el procedimiento ya explicado según usemos un paquete local o tengamos que descargar el paquete desde GitHub.com
 






🤝🌟💻

