# EEL CIBERSEGURIDAD — Laboratorio IDOR en una API con Burp Suite

Laboratorio práctico y deliberadamente vulnerable para aprender a identificar una falla **IDOR (Insecure Direct Object Reference)** utilizando **Burp Suite**.

> ⚠️ **Uso educativo:** ejecutá este laboratorio únicamente en equipos, máquinas virtuales y entornos propios o expresamente autorizados.

## Objetivo

La aplicación autentica correctamente a un usuario, pero contiene intencionalmente una falla de autorización.

El objetivo es iniciar sesión como **EEL CIBERSEGURIDAD**, consultar el documento asignado y observar con Burp Suite la petición que la aplicación realiza a la API. Luego se modifica únicamente el identificador del documento para comprobar si el backend verifica que el recurso pertenece al usuario autenticado.

## Requisitos

- Kali Linux o un entorno de laboratorio equivalente.
- Python 3.
- Flask.
- Burp Suite.

Si Flask no está instalado:

```bash
sudo apt update
sudo apt install python3-flask -y
```

## Credenciales de prueba

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

Durante la demostración se inicia sesión **únicamente como EEL CIBERSEGURIDAD**. La contraseña de CLIENTE B no se utiliza para obtener su documento.

## 1. Descargar y entrar al proyecto

```bash
git clone <URL-DE-TU-REPOSITORIO>
cd lab-idor-api-burpsuite
```

Si descargaste el proyecto como ZIP, descomprimilo y abrí una terminal dentro de la carpeta.

## 2. Ejecutar la aplicación

```bash
python3 app.py
```

El servidor quedará disponible en:

```text
http://127.0.0.1:5000
```

Dejá esa terminal abierta.

## 3. Abrir Burp Suite

En otra terminal:

```bash
burpsuite
```

Seleccioná:

```text
Temporary project → Next → Use Burp defaults → Start Burp
```

En:

```text
Proxy → Intercept
```

dejá:

```text
Intercept is OFF
```

Después seleccioná **Open browser**.

## 4. Iniciar sesión

Desde el navegador integrado de Burp ingresá a:

```text
http://127.0.0.1:5000
```

Utilizá:

```text
Usuario: EEL CIBERSEGURIDAD
Contraseña: 1234
```

Presioná **INGRESAR**.

## 5. Consultar el documento

En el panel presioná:

```text
VER MI DOCUMENTO
```

La aplicación devolverá el documento `1001`, perteneciente a EEL CIBERSEGURIDAD.

La URL continúa siendo:

```text
http://127.0.0.1:5000/panel
```

El identificador del documento no aparece en la barra de direcciones.

## 6. Descubrir la petición

En Burp Suite entrá en:

```text
Proxy → HTTP history
```

Buscá:

```text
POST /api/documento
```

En el cuerpo de la petición aparecerá:

```json
{"documento":1001}
```

## 7. Enviar a Repeater

Hacé clic derecho sobre la petición y seleccioná:

```text
Send to Repeater
```

Entrá en **Repeater** y presioná **Send** sin modificar nada.

El servidor debe responder `200 OK` y devolver el documento `1001`.

## 8. Probar el control de autorización

Sin cerrar sesión y sin modificar la cookie, cambiá únicamente:

```json
{"documento":1001}
```

por:

```json
{"documento":1002}
```

Presioná nuevamente **Send**.

La aplicación vulnerable responderá `200 OK` y devolverá información perteneciente a **CLIENTE B**.

## Resultado

La autenticación funciona: el servidor sabe que la sesión pertenece a **EEL CIBERSEGURIDAD**.

La autorización falla: el backend permite consultar un documento perteneciente a otro usuario porque no verifica la propiedad del recurso solicitado.

En una implementación correcta, una petición de EEL CIBERSEGURIDAD al documento `1002` debería ser rechazada, por ejemplo, con:

```text
403 Forbidden
```

## ¿Qué demuestra el laboratorio?

Burp Suite no crea la vulnerabilidad. Permite observar la comunicación entre el navegador y el servidor, enviar una petición a Repeater, modificarla y comprobar cómo responde el backend.

La enseñanza central es distinguir:

**Autenticación:** ¿quién es el usuario?

**Autorización:** ¿a qué recursos puede acceder ese usuario?

En este laboratorio la primera funciona y la segunda falla.

---

**EEL CIBERSEGURIDAD**  
Laboratorio educativo de seguridad web.
