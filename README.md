# README.md

En el repo está todo lo que hice para crear la polls app de la documeantación oficial de Django más un par de cosas más que le agregué, y dejo las instrucciones de como desplegarla en docker con postgres en un servidor linux.

## deployment en docker

Para crear una imagen a partir de la aplicación django creada lo primero que tenemos que hacer es generar un requirements.txt a partir de todas las dependencias que instalamos en nuestro entorno virtual, esto se hace con:
```
pip freeze > requirements.txt
```
Una vez que corramos este comando vamos a tener todas las dependencias que necesitamos instalar en nuestro contenedor.

Lo siguiente es crear un archivo Dockerfile que se basa en la imagen de python alojada en dockerhub, los comandos ENV son buenas prácticas para evitar procesamiento innecesario, el comando workdir es para establecer el directorio en el contenedor, una vez hecho esto copiamos los requerimientos al directorio de trabajo y corremos el pip install -r para instalarlos, una vez instaladas todas las dependencias copiamos nuestro proyecto dentro del contenedor, cabe destacar que todos estos archivos tienen que estar dentro de la carpeta outer del proyecto, es decir, la que tiene el archivo _manage.py_. Solo para organizarme en el repo las dejé afuera.

```
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/]
CMD python manage.py migrate ; python manage.py runserver 0.0.0.0:8000 --insecure
```
El docker compose para desplegarlo con postgres y ngninx proxy manager es este:

```
version: "3.9"
   
services:
  pollsdb:
    image: postgres
    container_name: pollsdb
    volumes:
      - ./data/db:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - 5433:5432
  pollsweb:
    image: samucancld/pollsapp:1.2
    container_name: pollsweb
    volumes:
      - .:/code
    ports:
      - "7777:8000"
    environment:
      - POSTGRES_NAME=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - DB_ALIAS=pollsdb
      - LOCAL_HOST=localhost # private ip
      - PUBLIC_DOMAIN=yourdomain #public ip or public domain
      - SEC_PUBLIC_DOMAIN=yourseconddomain # another domain, optional
      - TZ=yourtimezone
    depends_on:
      - pollsdb
networks:
  default:
    name: nginxpm_default
    external: true
```

Le agregué varias variables de entorno para que sea más facil de desplegar

Y eso es todo, ahora podemos correr docker-compose up -d y se van a levantar los dos contenedores y vamos a tener nuestra app de django desplegada en docker que conversa con el contenedor de docker, dentro de la red del reverse proxy para hacerla pública. Si queremos agregar cosas en la db podemos entrar en la consola interactiva del contenedor y crear un superusuario
```
python3 manage.py createsuperuser
```
Con el usuario que creemos tenemos acceso al admin panel de la aplicación y todo lo que generemos en al db va a tener persistencia en nuestro sv. Más adelante voy a ver si puedo hacer que se cree un superuser por defecto o con un par de variables de entorno más que se pasen en el yaml pero por ahora eso es todo.

Para aceptar POST requests con un reverse proxy que traduce https a http tuve que configurar en setting.py
```
CSRF_TRUSTED_ORIGINS = ["https://yourdomain.com", "https://www.yourdomain.com"]
```
si no me tiraba error de cross site request forgery