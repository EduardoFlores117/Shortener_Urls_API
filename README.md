Para evitar conflictos entre paquetes, se recomienda activar un entorno virtual con el siguiente comando:

En Windows: venv\Scripts\activate
En Mac/Linux: source venv/bin/activate

Instalar dependencias pip install -r requirements.txt

Para poner en marcha el servidor, simplemente ejecuta el siguiente comando en la terminal:
python manage.py runserver

Esto iniciará el servidor en la dirección http://127.0.0.1:8000, desde donde se podrán realizar todas las operaciones disponibles en la API.

Para explorar los endpoints disponibles y probar cada funcionalidad de manera interactiva, puedes acceder a la documentación de Swagger en la siguiente dirección:

👉 http://127.0.0.1:8000/swagger/

Desde ahí, podrás ver todos los métodos disponibles, los parámetros requeridos y ejemplos de respuestas.

🔑 Acceso y Autenticación
Para poder acortar URLs, cada usuario debe estar registrado en el sistema.

Si ya tienes una cuenta, puedes iniciar sesión enviando una solicitud POST a:

/api/auth/login/

Credenciales de Prueba:

Usuario: juanito@gmail.com
Contraseña: juanito1234

Usuario: anael@gmail.com
Contraseña: anael1234

Usuario: pedro@gmail.com
Contraseña: pedro1234

superusuario:
Usuario: admin@gmail.com
Contraseña: root1234

Al iniciar sesión, recibirás un token JWT, el cual deberás incluir en cada petición autenticada bajo el encabezado:

Authorization: Bearer <tu_token>

Si deseas registrarte con una cuenta nueva, puedes hacerlo mediante la siguiente solicitud POST:

api/auth/register/

Cuando desees cerrar sesión, solo necesitas enviar una petición POST a: api/auth/logout/ o quitar tu tokenm del encabezado Authorization



En el endopoint de /api/urls/bulk-upload/ podras subir multiples URL para acortar y puede elegir si como respuesta de esa soolicitud un json o file, si es json ahi mismo te dan las URL acortadas, pero si es file, puedes dercagr el archivo.

es decir:

{
  "urls": [
    "string"
  ],
  "response_type": "json"
}


O


{
  "urls": [
    "string"
  ],
  "response_type": "file"
}





