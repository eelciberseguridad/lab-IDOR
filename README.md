# EEL CIBERSEGURIDAD — Laboratorio IDOR en una API con Burp Suite

Laboratorio práctico y deliberadamente vulnerable para aprender a identificar una falla **IDOR (Insecure Direct Object Reference)** utilizando **Burp Suite**.

> ⚠️ **ADVERTENCIA:** este laboratorio tiene fines exclusivamente educativos y de capacitación en ciberseguridad. Debe ejecutarse únicamente en equipos, máquinas virtuales y entornos propios, controlados o expresamente autorizados.

## Objetivo

La aplicación autentica correctamente a un usuario, pero contiene intencionalmente una falla de autorización.

El objetivo es iniciar sesión como **EEL CIBERSEGURIDAD**, consultar el documento asignado y utilizar Burp Suite para observar la petición que la aplicación realiza en segundo plano hacia una API. Después modificaremos únicamente el identificador del documento para comprobar si el backend verifica que el recurso solicitado realmente pertenece al usuario autenticado.

El laboratorio permite comprender la diferencia entre **autenticación** y **autorización**.

---

## Estructura del repositorio

```text
lab-IDOR/
├── README.md
├── app.py
└── requirements.txt
```

---

## Requisitos

- Kali Linux o un entorno de laboratorio equivalente.
- Python 3.
- Flask.
- Burp Suite.
- Git para clonar el repositorio.

### Instalar Flask en Kali Linux

Una opción es instalar el paquete de Kali:

```bash
sudo apt update
sudo apt install python3-flask -y
```

El repositorio también incluye `requirements.txt` para quienes prefieran utilizar un entorno virtual de Python.

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

Durante la demostración se inicia sesión **únicamente como EEL CIBERSEGURIDAD**.

La contraseña de CLIENTE B se incluye porque ambos usuarios forman parte del laboratorio controlado, pero **no se utiliza para obtener su documento durante la prueba**.

---

## 1. Clonar el repositorio

Abrir una terminal en Kali Linux y ejecutar:

```bash
git clone https://github.com/eelciberseguridad/lab-IDOR.git
```

Entrar en la carpeta:

```bash
cd lab-IDOR
```

Comprobar su contenido:

```bash
ls
```

Deberían aparecer:

```text
README.md
app.py
requirements.txt
```

---

## 2. Ejecutar la aplicación

El archivo principal del laboratorio es:

```text
app.py
```

Ejecutar:

```bash
python3 app.py
```

El servidor quedará disponible localmente en:

```text
http://127.0.0.1:5000
```

Dejar esta terminal abierta durante todo el laboratorio.

### Si el puerto 5000 está ocupado

Comprobar qué proceso lo está utilizando:

```bash
sudo lsof -i :5000
```

Detener el servidor anterior antes de volver a ejecutar `app.py`.

---

## 3. Abrir Burp Suite

Abrir otra terminal y ejecutar:

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

Dejar:

```text
Intercept is OFF
```

Esto permite que las peticiones continúen normalmente mientras Burp las registra.

Después seleccionar:

```text
Open browser
```

---

## 4. Abrir el laboratorio

Desde el navegador integrado de Burp ingresar a:

```text
http://127.0.0.1:5000
```

Aparecerá la pantalla de acceso.

---

## 5. Iniciar sesión

Utilizar exclusivamente:

```text
Usuario: EEL CIBERSEGURIDAD
Contraseña: 1234
```

Presionar:

```text
INGRESAR
```

La aplicación abrirá el panel privado.

---

## 6. Consultar nuestro documento

Presionar:

```text
VER MI DOCUMENTO
```

La aplicación devolverá:

```text
INFORME CONFIDENCIAL 1001 - EEL CIBERSEGURIDAD
```

## 7. Descubrir la petición con Burp Suite

Volver a Burp Suite y entrar en:

```text
Proxy → HTTP history
```

Buscar:

```text
POST /api/documento
```

Seleccionar esa petición.

En el cuerpo aparecerá:

```json
{"documento":1001}
```

Aunque el identificador no aparece en la URL del navegador, Burp permite observar que la aplicación lo está enviando a la API.

---

## 8. Enviar la petición a Repeater

Hacer clic derecho sobre:

```text
POST /api/documento
```

Seleccionar:

```text
Send to Repeater
```

Abrir:

```text
Repeater
```

Primero dejar la petición original:

```json
{"documento":1001}
```

Presionar:

```text
Send
```

El servidor debe responder:

```text
HTTP/1.1 200 OK
```

y devolver el documento perteneciente a **EEL CIBERSEGURIDAD**.

Hasta este punto el comportamiento es correcto.

---

## 9. Probar el control de autorización

Seguimos autenticados como:

```text
EEL CIBERSEGURIDAD
```

No cerramos sesión.

No iniciamos sesión como CLIENTE B.

No utilizamos la contraseña de CLIENTE B.

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

## 10. Resultado

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

La sesión continúa perteneciendo a **EEL CIBERSEGURIDAD**, pero el backend permite acceder al documento perteneciente a **CLIENTE B** simplemente modificando el identificador enviado a la API.

---

## ¿Qué está fallando?

La aplicación comprueba que existe una sesión autenticada.

También comprueba que el documento solicitado existe.

Pero no comprueba:

```text
¿El usuario autenticado está autorizado
para acceder a este documento?
```

En nuestro ejemplo:

```text
Usuario autenticado: EEL CIBERSEGURIDAD
Documento solicitado: 1002
Propietario del documento: CLIENTE B
```

El servidor debería rechazar la solicitud.

Una implementación correcta podría responder:

```text
HTTP/1.1 403 Forbidden
```

---

## Autenticación y autorización

**Autenticación:** determina quién es el usuario.

**Autorización:** determina a qué recursos puede acceder ese usuario.

En este laboratorio la autenticación funciona: el sistema sabe que la sesión pertenece a **EEL CIBERSEGURIDAD**.

Lo que falla es la autorización.

---

## ¿Qué papel cumple Burp Suite?

Burp Suite no crea la vulnerabilidad.

Permite observar la comunicación entre el navegador y el servidor, descubrir peticiones que no necesariamente aparecen en la barra de direcciones, enviarlas a **Repeater**, modificar sus parámetros y analizar cómo responde el backend.

En este laboratorio descubrimos:

```json
{"documento":1001}
```

y comprobamos qué ocurre al solicitar:

```json
{"documento":1002}
```

manteniendo exactamente la misma sesión autenticada.

---

## Uso responsable

Este proyecto fue desarrollado exclusivamente para aprendizaje, demostración y capacitación en seguridad web.

No debe utilizarse para realizar pruebas sobre sistemas de terceros sin autorización expresa.

El objetivo es comprender cómo funciona una vulnerabilidad, cómo identificarla y por qué los controles de autorización deben implementarse siempre en el servidor.

---

**EEL CIBERSEGURIDAD**  
*Laboratorio educativo de seguridad web y análisis con Burp Suite.*
