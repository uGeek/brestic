import os
import time
import datetime
import re
import shutil
import unicodedata
from flask import Flask, render_template_string, jsonify, request, Response, send_file
from functools import wraps

app = Flask(__name__)

# --- CONFIGURACIÓN ---
CONFIG_DIR = os.path.expanduser("~/.config/brestic")
MOUNT_BASE = os.path.expanduser("~/brestic")
USER_AUTH = "admin"
PASS_AUTH = "brestic2024"

# --- SEGURIDAD ---
def check_auth(username, password):
    return username == USER_AUTH and password == PASS_AUTH

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response('No autorizado', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

# --- UTILIDADES ---

def format_snapshot_date(name):
    try:
        dt_str = name.split('+')[0].split('.')[0]
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except: return name

# --- RUTAS API ---

@app.route('/')
@requires_auth
def index():
    configs = [f for f in os.listdir(CONFIG_DIR) if os.path.isfile(os.path.join(CONFIG_DIR, f))]
    return render_template_string(HTML_TEMPLATE, configs=configs)

@app.route('/api/config/<name>', methods=['GET', 'POST'])
@requires_auth
def manage_config(name):
    path = os.path.join(CONFIG_DIR, name)
    if request.method == 'POST':
        content = request.json.get('content')
        with open(path, 'w', encoding='utf-8') as f: f.write(content)
        return jsonify({"status": "saved"})
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f: return jsonify({"content": f.read()})
    return jsonify({"content": ""})

# Ruta para descarga (Attachment)
@app.route('/api/download/<path:subpath>')
@requires_auth
def download(subpath):
    full_path = os.path.join(MOUNT_BASE, subpath)
    if os.path.isfile(full_path):
        return send_file(full_path, as_attachment=True, download_name=os.path.basename(full_path))
    return jsonify({"error": "No es un archivo"}), 404

# Ruta para previsualización (Inline)
@app.route('/api/view/<path:subpath>')
@requires_auth
def view_file(subpath):
    full_path = os.path.join(MOUNT_BASE, subpath)
    if os.path.isfile(full_path):
        # Detectar si es texto para forzar encoding utf-8 en el navegador si es necesario
        return send_file(full_path, as_attachment=False)
    return jsonify({"error": "No es un archivo"}), 404

@app.route('/api/browse/<path:subpath>')
@requires_auth
def browse(subpath):
    full_path = os.path.join(MOUNT_BASE, subpath)
    if not os.path.exists(full_path):
        return jsonify({"error": "Ruta no encontrada"}), 404

    items = []
    try:
        path_parts = subpath.strip('/').split('/')
        is_snapshot_list = (len(path_parts) == 2 and path_parts[0] == "tags")

        for entry in os.scandir(full_path):
            try:
                info = entry.stat()
                items.append({
                    "name": entry.name,
                    "display_name": format_snapshot_date(entry.name) if is_snapshot_list else entry.name,
                    "is_dir": entry.is_dir(),
                    "size": f"{info.st_size / (1024*1024):.2f} MB" if not entry.is_dir() else "-",
                    "mode": oct(info.st_mode)[-3:],
                    "mtime": time.strftime('%d/%m/%Y %H:%M', time.localtime(info.st_mtime))
                })
            except: continue
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        return jsonify({"items": items, "current_path": subpath})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/restore', methods=['POST'])
@requires_auth
def restore():
    data = request.json
    subpath = data.get('path')
    target_path = data.get('target')
    source_full_path = os.path.join(MOUNT_BASE, subpath.strip('/'))

    try:
        if os.path.isdir(source_full_path):
            shutil.copytree(source_full_path, target_path, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(source_full_path, target_path)
        return jsonify({"status": "ok", "msg": f"Restaurado en: {target_path}"})
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>pyBrestic Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #0b0b0d; color: #d1d1d1; font-family: 'Inter', sans-serif; }
        .sidebar { height: 100vh; background: #121214; border-right: 1px solid #222; padding: 20px; position: fixed; width: 18%; }
        .main-content { margin-left: 18%; padding: 40px; }
        .card { background: #18181b; border: 1px solid #2a2a2c; border-radius: 12px; }
        .config-link { cursor: pointer; padding: 12px; border-radius: 10px; display: block; color: #888; text-decoration: none; margin-bottom: 5px; }
        .config-link.active { background: #4f46e5; color: white; }
        .table { color: #d1d1d1; }
        .search-box { background: #000; border: 1px solid #333; color: #fff; border-radius: 8px; padding: 10px 15px; width: 100%; margin-bottom: 20px; outline: none; }
        #loading-overlay { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; justify-content:center; align-items:center; flex-direction:column; }
        textarea.form-control { background: #000; color: #10b981; font-family: 'Fira Code', monospace; border: 1px solid #333; }
        
        /* Modal Preview */
        #preview-container { background: #111; border: 1px solid #444; border-radius: 10px; max-height: 80vh; overflow: auto; padding: 20px; color: #00ff41; }
        .preview-img { max-width: 100%; height: auto; display: block; margin: auto; }
        .preview-audio { width: 100%; margin-top: 20px; }
        .preview-text { white-space: pre-wrap; font-family: 'Fira Code', monospace; font-size: 13px; }
        iframe { width: 100%; height: 70vh; border: none; background: white; }
    </style>
</head>
<body>
<div id="loading-overlay">
    <div class="spinner-border text-primary mb-3"></div>
    <h5 id="loading-text">Copiando archivos...</h5>
</div>

<!-- MODAL PREVIEW -->
<div class="modal fade" id="previewModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-xl">
        <div class="modal-content bg-dark border-secondary">
            <div class="modal-header border-secondary">
                <h5 class="modal-title text-white" id="previewTitle">Vista previa</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" id="previewBody">
                <!-- El contenido se inyecta aquí -->
            </div>
        </div>
    </div>
</div>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-2 sidebar">
            <h4 class="mb-4 text-white fw-bold"><i class="fas fa-bolt text-primary me-2"></i> pyBrestic</h4>
            {% for c in configs %}
            <a class="config-link" onclick="selectConfig('{{c}}', this)"><i class="far fa-file-code me-2"></i> {{c}}</a>
            {% endfor %}
        </div>

        <div class="col-md-10 main-content">
            <div id="dashboard" style="display:none;">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 id="config-title" class="fw-bold h3 m-0 text-white">---</h2>
                    <div class="btn-group">
                        <button class="btn btn-outline-light btn-sm" onclick="editConfig()">Config</button>
                        <button class="btn btn-primary btn-sm" onclick="initExplorer()">Tags</button>
                    </div>
                </div>

                <div id="browser-view" class="card p-4 shadow-sm">
                    <nav aria-label="breadcrumb"><ol class="breadcrumb mb-4" id="browser-breadcrumb"></ol></nav>
                    <input type="text" id="fileSearch" class="search-box" placeholder="🔍 Buscar archivos (ignore acentos, puntos y mayúsculas)..." onkeyup="filterFiles()">

                    <table class="table table-dark table-hover align-middle">
                        <thead>
                            <tr class="text-muted small">
                                <th width="50">ICONO</th>
                                <th>NOMBRE</th>
                                <th>TAMAÑO</th>
                                <th>MODO</th>
                                <th>MODIFICADO</th>
                                <th class="text-center">ACCIONES</th>
                            </tr>
                        </thead>
                        <tbody id="file-list"></tbody>
                    </table>
                </div>

                <div id="editor-view" style="display:none;" class="card p-4">
                    <textarea id="config-editor-area" class="form-control" rows="20"></textarea>
                    <div class="mt-4">
                        <button class="btn btn-success" onclick="saveConfig()">Guardar</button>
                        <button class="btn btn-dark ms-2" onclick="hideEditor()">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let activeConfig = "";
let allItems = [];
let currentPathGlobal = "";
const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));

function showLoading(show, text="Procesando...") { 
    document.getElementById('loading-text').innerText = text;
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none'; 
}

function selectConfig(name, el) {
    activeConfig = name;
    document.querySelectorAll('.config-link').forEach(l => l.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('config-title').innerText = name;
    initExplorer();
}

function initExplorer() { hideEditor(); navigateTo('tags'); }

async function navigateTo(relPath) {
    showLoading(true, "Leyendo...");
    currentPathGlobal = relPath;
    const res = await fetch(`/api/browse/${relPath}`);
    const data = await res.json();
    showLoading(false);
    if(data.error) { alert(data.error); return; }
    allItems = data.items;
    updateBreadcrumbs(relPath);
    renderFiles(data.items);
    document.getElementById('fileSearch').value = "";
}

function updateBreadcrumbs(path) {
    const bread = document.getElementById('browser-breadcrumb');
    bread.innerHTML = '<li class="breadcrumb-item"><a href="#" onclick="initExplorer()">Raíz</a></li>';
    let parts = path.split('/').filter(x => x && x!=='tags');
    let acc = "tags";
    parts.forEach((p) => { acc += "/" + p; bread.innerHTML += `<li class="breadcrumb-item"><a href="#" onclick="navigateTo('${acc}')">${p}</a></li>`; });
}

function cleanStr(str) { return str.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase().replace(/\\./g, ""); }
function filterFiles() { const val = cleanStr(document.getElementById('fileSearch').value); renderFiles(allItems.filter(item => cleanStr(item.display_name).includes(val))); }

function renderFiles(items) {
    const list = document.getElementById('file-list');
    list.innerHTML = "";
    if(currentPathGlobal !== "tags") {
        let parts = currentPathGlobal.split('/'); parts.pop();
        list.innerHTML += `<tr onclick="navigateTo('${parts.join('/')}')" style="cursor:pointer"><td class="text-center"><i class="fas fa-level-up-alt text-warning"></i></td><td colspan="5" class="text-muted small">.. (Atrás)</td></tr>`;
    }

    items.forEach(item => {
        const icon = item.is_dir ? '<i class="fas fa-folder text-warning"></i>' : '<i class="far fa-file-alt text-info"></i>';
        const fullItemPath = `${currentPathGlobal}/${item.name}`;
        
        let actions = item.is_dir 
            ? `<button class="btn btn-sm btn-dark me-1" onclick="navigateTo('${fullItemPath}')">Abrir</button>`
            : `<button class="btn btn-sm btn-outline-info me-1" onclick="openPreview('${fullItemPath}', '${item.name}')"><i class="fas fa-eye"></i></button>
               <a href="/api/download/${fullItemPath}" class="btn btn-sm btn-success me-1"><i class="fas fa-download"></i></a>`;
        
        if (currentPathGlobal.split('/').filter(x=>x).length >= 3) {
            actions += `<button class="btn btn-sm btn-outline-warning" onclick="requestRestore('${fullItemPath}')"><i class="fas fa-undo"></i></button>`;
        }

        list.innerHTML += `<tr>
            <td class="text-center" style="cursor:pointer" onclick="${item.is_dir ? `navigateTo('${fullItemPath}')` : `openPreview('${fullItemPath}', '${item.name}')`}">${icon}</td>
            <td style="cursor:pointer" onclick="${item.is_dir ? `navigateTo('${fullItemPath}')` : `openPreview('${fullItemPath}', '${item.name}')`}" class="${item.is_dir ? 'fw-bold' : ''}">${item.display_name}</td>
            <td>${item.size}</td><td><code>${item.mode}</code></td><td>${item.mtime}</td>
            <td class="text-center">${actions}</td></tr>`;
    });
}

function openPreview(path, name) {
    const ext = name.split('.').pop().toLowerCase();
    const url = `/api/view/${path}`;
    const body = document.getElementById('previewBody');
    document.getElementById('previewTitle').innerText = name;
    body.innerHTML = '<div class="text-center"><div class="spinner-border text-primary"></div></div>';
    previewModal.show();

    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) {
        body.innerHTML = `<img src="${url}" class="preview-img">`;
    } else if (['mp3', 'wav', 'ogg', 'm4a'].includes(ext)) {
        body.innerHTML = `<div class="text-center"><i class="fas fa-music fa-4x mb-3 text-primary"></i><audio controls autoplay class="preview-audio"><source src="${url}" type="audio/mpeg"></audio></div>`;
    } else if (['html', 'htm'].includes(ext)) {
        body.innerHTML = `<iframe src="${url}"></iframe>`;
    } else if (['txt', 'md', 'json', 'csv', 'log', 'py', 'js', 'css', 'sh', 'yaml', 'yml', 'conf'].includes(ext)) {
        fetch(url).then(r => r.text()).then(text => {
            body.innerHTML = `<div id="preview-container"><pre class="preview-text">${text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre></div>`;
        });
    } else {
        body.innerHTML = `<div class="text-center p-5"><h5>No hay vista previa disponible para .${ext}</h5><a href="/api/download/${path}" class="btn btn-success mt-3">Descargar archivo</a></div>`;
    }
}

function requestRestore(fullPath) {
    const parts = fullPath.split('/').filter(x=>x);
    const originalPath = "/" + parts.slice(3).join('/');
    const target = prompt(`¿Restaurar en?\\n${originalPath}`, originalPath);
    if(!target) return;
    showLoading(true, "Restaurando...");
    fetch('/api/restore', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ path: fullPath, target: target }) })
    .then(res => res.json()).then(data => { showLoading(false); alert(data.msg || data.error); });
}

async function editConfig() {
    const res = await fetch(`/api/config/${activeConfig}`); 
    const data = await res.json();
    document.getElementById('config-editor-area').value = data.content;
    document.getElementById('editor-view').style.display = 'block'; 
    document.getElementById('browser-view').style.display = 'none';
}

async function saveConfig() {
    const content = document.getElementById('config-editor-area').value;
    await fetch(`/api/config/${activeConfig}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({content}) });
    alert("Guardado.");
}
function hideEditor() { document.getElementById('editor-view').style.display = 'none'; document.getElementById('browser-view').style.display = 'block'; }
</script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
