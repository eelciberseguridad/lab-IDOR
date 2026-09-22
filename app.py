from flask import Flask, request, session, redirect, render_template_string, jsonify

app = Flask(__name__)
app.secret_key = "clave-laboratorio-burp"

usuarios = {
    "EEL CIBERSEGURIDAD": {
        "password": "1234",
        "documento": 1001
    },
    "CLIENTE B": {
        "password": "5678",
        "documento": 1002
    }
}

documentos = {
    1001: {
        "propietario": "EEL CIBERSEGURIDAD",
        "contenido": "INFORME CONFIDENCIAL 1001 - EEL CIBERSEGURIDAD"
    },
    1002: {
        "propietario": "CLIENTE B",
        "contenido": "INFORME CONFIDENCIAL 1002 - CLIENTE B"
    }
}

LOGIN = """
<h1>LABORATORIO API</h1>
<h2>Acceso al sistema</h2>

<form method="POST">
    <p>Usuario</p>
    <input name="usuario">

    <p>Contraseña</p>
    <input name="password" type="password">

    <br><br>
    <button type="submit">INGRESAR</button>
</form>
"""

PANEL = """
<h1>Panel privado</h1>

<p>Usuario autenticado:
<strong>{{ usuario }}</strong>
</p>

<button onclick="verDocumento()">
VER MI DOCUMENTO
</button>

<br><br>

<pre id="resultado"></pre>

<script>
async function verDocumento() {
    const respuesta = await fetch("/api/documento", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "documento": {{ documento }}
        })
    });

    const datos = await respuesta.json();

    document.getElementById("resultado").textContent =
        JSON.stringify(datos, null, 2);
}
</script>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")

        if (
            usuario in usuarios
            and usuarios[usuario]["password"] == password
        ):
            session["usuario"] = usuario
            return redirect("/panel")

        return "Credenciales incorrectas", 401

    return LOGIN


@app.route("/panel")
def panel():
    if "usuario" not in session:
        return redirect("/")

    usuario = session["usuario"]

    return render_template_string(
        PANEL,
        usuario=usuario,
        documento=usuarios[usuario]["documento"]
    )


@app.route("/api/documento", methods=["POST"])
def api_documento():
    if "usuario" not in session:
        return jsonify({
            "error": "Usuario no autenticado"
        }), 401

    datos = request.get_json(silent=True) or {}
    doc_id = datos.get("documento")

    if doc_id not in documentos:
        return jsonify({
            "error": "Documento inexistente"
        }), 404

    # VULNERABILIDAD INTENCIONAL DEL LABORATORIO:
    # existe una sesión válida, pero el backend NO comprueba
    # que el documento solicitado pertenezca al usuario autenticado.
    return jsonify({
        "documento": doc_id,
        "propietario": documentos[doc_id]["propietario"],
        "contenido": documentos[doc_id]["contenido"]
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
