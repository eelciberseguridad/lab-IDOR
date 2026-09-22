# EEL CIBERSEGURIDAD — Laboratorio IDOR en una API con Burp Suite

Laboratorio práctico y deliberadamente vulnerable para aprender a identificar una falla **IDOR (Insecure Direct Object Reference)** utilizando **Burp Suite**.

> ⚠️ **ADVERTENCIA:** este laboratorio tiene fines exclusivamente educativos y de capacitación en ciberseguridad. Debe ejecutarse únicamente en equipos, máquinas virtuales y entornos propios, controlados o expresamente autorizados.

## Objetivo

La aplicación autentica correctamente a un usuario, pero contiene intencionalmente una falla de autorización.

El objetivo es iniciar sesión como **EEL CIBERSEGURIDAD**, consultar el documento asignado y utilizar Burp Suite para observar la petición que la aplicación realiza en segundo plano hacia una API.

Después modificaremos únicamente el identificador del documento para comprobar si el backend verifica que el recurso solicitado realmente pertenece al usuario autenticado.

La idea central del laboratorio es comprender la diferencia entre **autenticación** y **autorización**.

---

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

---

## Credenciales del laboratorio

La aplicación contiene dos usuarios de prueba.

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

Durante la demostración iniciaremos sesión **únicamente como EEL CIBERSEGURIDAD**.

La contraseña de CLIENTE B se incluye porque ambos usuarios forman parte de este laboratorio controlado, pero **no se utiliza para obtener su documento durante la prueba**.

---

## 1. Descargar el laboratorio

Desde una terminal:

```bash
git clone https://github.com/eelciberseguridad/laboratorio-IDOR.git
```

Entrar en la carpeta:

```bash
cd laboratorio-IDOR
```

Comprobar los archivos:

```bash
ls
```

---

## 2. Ejecutar la aplicación

El archivo principal del laboratorio es:

```text
aplicación.py
```

Ejecutarlo con:

```bash
python3 aplicación.py
```

El servidor quedará disponible localmente en:

```text
http://127.0.0.1:5000
```

Dejar esta terminal abierta mientras se realiza la práctica.

> Si el puerto 5000 ya está ocupado, puede comprobarse qué proceso lo utiliza con `sudo lsof -i :5000`.

---

## 3. Abrir Burp Suite

Abrir otra terminal:

```bash
burpsuite
```

Seleccionar:

```text
Temporary project
→ Next
→ Use Burp defaults
→ Start Burp
```

Ir a:

```text
Proxy → Intercept
```

y dejar:

```text
Intercept is OFF
```

Esto permite que las peticiones continúen normalmente mientras Burp las registra en el historial.

Seleccionar:

```text
Open browser
```

---

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

Presionar:

```text
INGRESAR
```

La aplicación abrirá el panel privado del usuario.

---

## 5. Consultar el documento

Presionar:

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

Esto significa que necesitamos observar qué comunicación está realizando la aplicación en segundo plano.

---

## 6. Analizar la petición con Burp Suite

Volver a Burp Suite y entrar en:

```text
Proxy → HTTP history
```

Buscar la petición:

```text
POST /api/documento
```

Seleccionarla.

En el cuerpo de la petición aparecerá:

```json
{"documento":1001}
```

Aunque el identificador no era visible en la URL, el navegador lo estaba enviando a la API mediante una petición HTTP.

---

## 7. Enviar la petición a Repeater

Hacer clic derecho sobre:

```text
POST /api/documento
```

y seleccionar:

```text
Send to Repeater
```

Abrir:

```text
Repeater
```

Primero enviar la petición sin modificarla:

```json
{"documento":1001}
```

Presionar:

```text
Send
```

El servidor responderá:

```text
HTTP/1.1 200 OK
```

y devolverá el documento perteneciente a **EEL CIBERSEGURIDAD**.

Hasta este punto, el comportamiento es correcto.

---

## 8. Probar el control de autorización

Seguimos autenticados como:

```text
EEL CIBERSEGURIDAD
```

No cerramos sesión.

No iniciamos sesión como CLIENTE B.

No utilizamos su contraseña.

No modificamos nuestra cookie de sesión.

En Repeater cambiamos únicamente:

```json
{"documento":1001}
```

por:

```json
{"documento":1002}
```

Presionamos nuevamente:

```text
Send
```

---

## 9. Resultado

La aplicación vulnerable responde:

```text
HTTP/1.1 200 OK
```

y devuelve información similar a:

```json
{
  "contenido": "INFORME CONFIDENCIAL 1002 - CLIENTE B",
  "documento": 1002,
  "propietario": "CLIENTE B"
}
```

La vulnerabilidad quedó demostrada.

La sesión continúa perteneciendo a **EEL CIBERSEGURIDAD**, pero el backend permitió acceder a un recurso perteneciente a **CLIENTE B** simplemente modificando la referencia enviada a la API.

---

## ¿Qué está fallando?

La aplicación comprueba que existe una sesión autenticada.

También comprueba que el documento solicitado existe.

Sin embargo, no realiza la comprobación fundamental:

```text
¿El usuario autenticado está autorizado
para acceder a este documento?
```

En este caso:

```text
Usuario autenticado: EEL CIBERSEGURIDAD
Documento solicitado: 1002
Propietario: CLIENTE B
```

El servidor debería rechazar la petición.

Una implementación correcta podría responder:

```text
HTTP/1.1 403 Forbidden
```

---

## Autenticación vs. autorización

Este laboratorio permite visualizar claramente dos conceptos diferentes.

**Autenticación:** determina quién es el usuario.

**Autorización:** determina a qué recursos puede acceder ese usuario.

En nuestro laboratorio la autenticación funciona: el servidor sabe que la sesión pertenece a **EEL CIBERSEGURIDAD**.

Lo que falla es la autorización: el servidor no comprueba que el documento solicitado pertenezca al usuario autenticado.

---

## ¿Qué papel cumple Burp Suite?

Burp Suite no crea la vulnerabilidad.

Nos permite observar la comunicación entre el navegador y el servidor, descubrir peticiones que no necesariamente aparecen en la barra de direcciones, enviarlas a **Repeater**, modificar sus parámetros y analizar cómo responde el backend.

En este laboratorio permitió descubrir que la aplicación enviaba:

```json
{"documento":1001}
```

y comprobar qué sucedía al solicitar:

```json
{"documento":1002}
```

manteniendo exactamente la misma sesión autenticada.

---

## Estructura del repositorio

```text
laboratorio-IDOR/
├── LÉAME.md
├── aplicación.py
└── requisitos.txt
```

---

## Uso responsable

Este proyecto fue desarrollado para aprendizaje, demostración y capacitación en seguridad web.

No debe utilizarse para realizar pruebas sobre sistemas de terceros sin autorización expresa.

El objetivo es comprender cómo funciona una vulnerabilidad, cómo identificarla y por qué los controles de autorización deben implementarse siempre en el servidor.

---

**EEL CIBERSEGURIDAD**  
*Laboratorio educativo de seguridad web y análisis con Burp Suite.*
