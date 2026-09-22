# EEL CIBERSEGURIDAD — Laboratorio IDOR en una API con Burp Suite

Laboratorio práctico y deliberadamente vulnerable para aprender a identificar una falla **IDOR (Insecure Direct Object Reference)** utilizando **Burp Suite**.

> ⚠️ **ADVERTENCIA:** este laboratorio tiene fines exclusivamente educativos y de capacitación en ciberseguridad. Debe ejecutarse únicamente en equipos, máquinas virtuales y entornos propios, controlados o expresamente autorizados.

## Objetivo

La aplicación autentica correctamente a un usuario, pero contiene intencionalmente una falla de autorización.

El objetivo es iniciar sesión como **EEL CIBERSEGURIDAD**, consultar el documento asignado y utilizar Burp Suite para observar la petición que la aplicación realiza en segundo plano hacia una API. Después modificaremos únicamente el identificador del documento para comprobar si el backend verifica que el recurso solicitado realmente pertenece al usuario autenticado.

Este laboratorio permite comprender claramente la diferencia entre **autenticación** y **autorización**.

## Requisitos

- Kali Linux o un entorno de laboratorio equivalente.
- Python 3.
- Flask.
- Burp Suite.
- Git, si se desea clonar el repositorio.

Para instalar Flask en Kali Linux:

```bash
sudo apt update
sudo apt install python3-flask -y
```

También puede instalarse desde `requirements.txt` en un entorno virtual de Python.

## Credenciales del laboratorio

### Usuario principal

```text
Usuario: EEL CIBERSEGURIDAD
Contraseña: 1234
Documento asignado: 1001
```

### Segundo usuario

```text
Usuario: CLIENTE B
Contraseña: 5678
Documento asignado: 1002
```

Durante la demostración se inicia sesión **únicamente como EEL CIBERSEGURIDAD**. La contraseña de CLIENTE B forma parte del laboratorio, pero no se utiliza para obtener su documento durante la prueba.

## 1. Descargar el laboratorio

```bash
git clone https://github.com/eelciberseguridad/laboratorio-IDOR.git
cd laboratorio-IDOR
```

Comprobar los archivos:

```bash
ls
```

La estructura debe ser:

```text
laboratorio-IDOR/
├── README.md
├── app.py
└── requirements.txt
```

## 2. Ejecutar la aplicación

El archivo principal es:

```text
app.py
```

Ejecutarlo con:

```bash
python3 app.py
```

El servidor quedará disponible en:

```text
http://127.0.0.1:5000
```

Dejar esa terminal abierta durante la práctica.

Si el puerto 5000 estuviera ocupado:

```bash
sudo lsof -i :5000
```

## 3. Abrir Burp Suite

En otra terminal:

```bash
burpsuite
```

Seleccionar:

```text
Temporary project → Next → Use Burp defaults → Start Burp
```

Ir a:

```text
Proxy → Intercept
```

y dejar:

```text
Intercept is OFF
```

Después seleccionar **Open browser**.

## 4. Iniciar sesión

Desde el navegador integrado de Burp ingresar a:

```text
http://127.0.0.1:5000
```

Utilizar:

```text
Usuario: EEL CIBERSEGURIDAD
Contraseña: 1234
```

Presionar **INGRESAR**.

## 5. Consultar el documento

En el panel presionar:

```text
VER MI DOCUMENTO
```

La aplicación devolverá:

```text
INFORME CONFIDENCIAL 1001 - EEL CIBERSEGURIDAD
```

La dirección del navegador continuará siendo:

```text
http://127.0.0.1:5000/panel
```

El identificador `1001` no aparece en la barra de direcciones.

## 6. Descubrir la petición con Burp Suite

Ir a:

```text
Proxy → HTTP history
```

Buscar:

```text
POST /api/documento
```

En el cuerpo de la petición aparecerá:

```json
{"documento":1001}
```

Burp permite observar que el navegador está enviando este identificador a la API aunque no aparezca en la barra de direcciones.

## 7. Enviar la petición a Repeater

Hacer clic derecho sobre `POST /api/documento` y seleccionar:

```text
Send to Repeater
```

Abrir **Repeater**.

Enviar primero la petición original:

```json
{"documento":1001}
```

Presionar **Send**.

El servidor debe responder:

```text
HTTP/1.1 200 OK
```

y devolver el documento perteneciente a **EEL CIBERSEGURIDAD**.

## 8. Probar el control de autorización

Seguimos autenticados como **EEL CIBERSEGURIDAD**.

No cerramos sesión, no iniciamos sesión como CLIENTE B, no utilizamos su contraseña y no modificamos nuestra cookie de sesión.

En Repeater cambiamos únicamente:

```json
{"documento":1001}
```

por:

```json
{"documento":1002}
```

Presionamos nuevamente **Send**.

## 9. Resultado

La aplicación vulnerable responde:

```text
HTTP/1.1 200 OK
```

y devuelve:

```json
{
  "contenido": "INFORME CONFIDENCIAL 1002 - CLIENTE B",
  "documento": 1002,
  "propietario": "CLIENTE B"
}
```

La vulnerabilidad quedó demostrada.

La sesión continúa perteneciendo a **EEL CIBERSEGURIDAD**, pero el backend permite acceder al documento de **CLIENTE B** simplemente modificando la referencia enviada a la API.

## ¿Qué está fallando?

La aplicación comprueba que existe una sesión autenticada y que el documento solicitado existe, pero no verifica si el usuario autenticado está autorizado para acceder a ese documento.

Una implementación correcta debería rechazar la solicitud al documento `1002` realizada desde la sesión de EEL CIBERSEGURIDAD, por ejemplo:

```text
HTTP/1.1 403 Forbidden
```

## Autenticación vs. autorización

**Autenticación:** determina quién es el usuario.

**Autorización:** determina a qué recursos puede acceder ese usuario.

En este laboratorio la autenticación funciona. El sistema sabe que la sesión pertenece a **EEL CIBERSEGURIDAD**.

Lo que falla es la autorización.

## ¿Qué papel cumple Burp Suite?

Burp Suite no crea la vulnerabilidad. Permite observar la comunicación entre el navegador y el servidor, descubrir peticiones que no necesariamente aparecen en la URL, enviarlas a **Repeater**, modificar parámetros y analizar cómo responde el backend.

## Uso responsable

Este proyecto fue desarrollado exclusivamente para aprendizaje, demostración y capacitación en seguridad web. No debe utilizarse para realizar pruebas sobre sistemas de terceros sin autorización expresa.

---

**EEL CIBERSEGURIDAD**  
*Laboratorio educativo de seguridad web y análisis con Burp Suite.*
