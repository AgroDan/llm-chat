import json
import os

from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    stream_with_context,
    url_for,
)

from config import get_config, save_config
from providers import list_models, stream_chat

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True)
    if not data or "messages" not in data:
        return jsonify({"error": "Invalid request"}), 400
    messages = data["messages"]
    cfg = get_config()

    provider = cfg["provider"]
    model = cfg["model"]
    system_prompt = cfg["system_prompt"]
    base_url = cfg.get("base_url", "")

    if provider == "anthropic":
        api_key = cfg.get("anthropic_api_key", "")
    elif provider == "openai":
        api_key = cfg.get("openai_api_key", "")
    else:
        api_key = ""

    def generate():
        try:
            for chunk in stream_chat(provider, api_key, base_url, model, system_prompt, messages):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/models")
def models():
    cfg = get_config()
    provider = request.args.get("provider") or cfg["provider"]
    base_url = request.args.get("base_url") or cfg.get("base_url", "")
    api_key = request.args.get("api_key") or (
        cfg.get("anthropic_api_key", "") if provider == "anthropic"
        else cfg.get("openai_api_key", "") if provider == "openai"
        else ""
    )
    return jsonify(list_models(provider, api_key, base_url))


@app.route("/admin/login", methods=["POST"])
def admin_login():
    password = request.form.get("password", "")
    cfg = get_config()
    if password == cfg["admin_password"]:
        session["admin"] = True
        return redirect(url_for("admin"))
    return redirect(url_for("admin", error="1"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    cfg = get_config()

    if request.method == "POST":
        if not session.get("admin"):
            return redirect(url_for("admin"))
        new_cfg = {
            "provider": request.form.get("provider", cfg["provider"]),
            "openai_api_key": request.form.get("openai_api_key", ""),
            "anthropic_api_key": request.form.get("anthropic_api_key", ""),
            "base_url": request.form.get("base_url", ""),
            "model": request.form.get("model", cfg["model"]),
            "system_prompt": request.form.get("system_prompt", cfg["system_prompt"]),
        }
        new_password = request.form.get("admin_password", "").strip()
        if new_password:
            new_cfg["admin_password"] = new_password
        save_config(new_cfg)
        return redirect(url_for("admin", saved="1"))

    return render_template(
        "admin.html",
        logged_in=session.get("admin", False),
        config=cfg,
        error=request.args.get("error"),
        saved=request.args.get("saved"),
    )


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")
