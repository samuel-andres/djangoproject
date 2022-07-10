# Primer proyecto en Django siguiendo la documentación oficial

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
COPY . /code/
```

Ahora, para que todo salga bien hay que crear la imagen en un SO con kernel de linux, el docker de windows es una porquería, así que si necesitamos hacemos un zip del proyecto completo y lo pasamos a nuestro servidor linux.

Ya en nuestro servidor, lo que tenemos que hacer para correr la app es usar docker compose, para esto creamos un archivo llamado docker-compose.yaml en nuestro directorio outer que tiene lo siguiente:
- version: la versión de docker-compose
- services: vamos a configurar dos servicios a partir de dos imagenes distintas, la aplicación web a partir del dockerfile que creamos, y la db de postgres a partir de la imagen de postgres que está en dockerhub
- dentro de la db indicamos la imagen de postgres, si queremos la última versión no hace falta indicar ningún tag, y creamos un volumen para tener persistencia en la base de datos, este se mapea como servidor/contenedor, es decir en este caso le estamos diciendo que en nuesstro directorio outer, en el directorio data y dentro en el directorio db se va a guardar la db de postgres, bindeada al directorio var lib postgresql data dentro del contenedor, luego le pasamos algunas variables de entorno (que tenemos que asegurarnos de configurar igual en el archivo settings.py de nuestra aplicación django y por último bindeamos los puertos para el contenedor (la sintaxis es puertolocal:puertocontenedor), en este caso yo le puse otro puerto porque ya tengo corriendo otra instancia de postgres en el puerto default 5432
- eso es todo para el contenedor de postgres, ahora para el contenedor de nuestra app tenemos que setear el parámetro build en el directorio actual para que cree la imagen a partir del Dockerfile que creamos, y corremos las migraciones de la aplicación y lanzamos el servidor, esto para que cada vez que despleguemos el contenedor no tengamos que entrar a su shell y hacerlo manualmente, mapeamos el directorio actual al directorio code del contenedor que es donde va a estar todo el código src de la app y bindeamos nuestro puertp 7777 al 8000 del contenedor (esto no hace falta, yo lo hice porque en el 8000 tengo portainer), las variables de entorno son las de postgres para setear en el settings.py y por último el parámetro depends_on hace que se corra después del contenedor de postgres
```
version: "3.9"
   
services:
  db:
    image: postgres
    volumes:
      - ./data/db:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - 5433:5433
  web:
    build: .
    command: bash -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/code
    ports:
      - "7777:8000"
    environment:
      - POSTGRES_NAME=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    depends_on:
      - db

```

En settings.py la configuración de la db es la siguiente:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    }
}
```
Para que esto funcione tenemos que importar os al principio del archivo. Y eso es todo, ahora podemos correr docker-compose up -d y se van a levantar los dos contenedores y vamos a tener nuestra app de django desplegada en docker que conversa con el contenedor de docker. Si queremos agregar cosas en la db podemos entrar en la consola interactiva del contenedor y crear un superusuario
```
python3 manage.py createsuperuser
```
Con el usuario que creemos tenemos acceso al admin panel de la aplicación y todo lo que generemos en al db va a tener persistencia en nuestro sv. Más adelante voy a ver si puedo hacer que se cree un superuser por defecto o con un par de variables de entorno que se pasen en el docker compose yaml pero por ahora eso es todo.
