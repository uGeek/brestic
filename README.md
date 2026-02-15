# brestic

Un potente wrapper para 'restic' que simplifica la gestión de tus backups a través de la línea de comandos, ahora con notificaciones integradas, navegación interactiva y **explorador web profesional**.

`brestic` nace de la necesidad de automatizar y simplificar las operaciones más comunes de `restic`, permitiendo gestionar complejas políticas de retención, múltiples fuentes de backup y recibir alertas en tiempo real en tu móvil.

![Bash Shell](https://img.shields.io/badge/Shell-Bash-blue?style=for-the-badge&logo=gnu-bash)
![Python](https://img.shields.io/badge/Python-3.x-yellow?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Web-Flask-lightgrey?style=for-the-badge&logo=flask)
![Version](https://img.shields.io/badge/Version-v2.1.0-green?style=for-the-badge)

## 🚀 Características Principales

-   **Notificaciones Multi-canal**: Recibe confirmaciones de tus backups en **ntfy** y **Telegram** automáticamente. Soporta formato Markdown para mayor legibilidad.
-   **PyBrestic (Explorador Web)**: Nueva interfaz gráfica en Flask para navegar por tus snapshots, previsualizar archivos y realizar restauraciones desde el navegador.
-   **Sintaxis Unificada v2.1**: Comandos simplificados y potentes para gestionar el ciclo de vida completo del dato.
-   **Navegación Interactiva CLI**: 
    -   `nav`: Explora tus backups como si fueran carpetas locales usando `fzf`.
    -   `diff`: Compara visualmente qué ha cambiado entre dos snapshots.
-   **Gestión por Archivos de Configuración**: Organiza tus backups por proyectos. Cada archivo en `~/.config/brestic/` es un perfil independiente.
-   **Políticas de Limpieza Inteligentes**: 
    -   `[N]m`: Limpieza avanzada que conserva hitos históricos (días 1 y 15) de meses pasados.
    -   `clp`: Aplica políticas personalizadas definidas directamente en tu archivo de configuración.
-   **Robusto**: Gestión de bloqueos automática (`unlock`) y validación de integridad de datos.

## 📋 Requisitos

1.  **`restic`**: La herramienta de backup principal.
2.  **`jq`**: Para procesar metadatos de los snapshots.
3.  **`fzf`**: Para la navegación interactiva y selección de archivos en terminal.
4.  **`Python 3 & Flask`**: Necesarios para el explorador web (`pybrestic.py`).
    ```bash
    pip install flask
    ```

Instalación rápida de dependencias en Debian/Ubuntu:
```bash
brestic install
sudo apt install jq fzf python3-flask
```

## ⚙️ Instalación

1.  **Clona el repositorio**:
    ```bash
    git clone https://github.com/tu_usuario/brestic.git /opt/brestic
    ```
2.  **Enlace simbólico**:
    ```bash
    sudo ln -s /opt/brestic/brestic /usr/local/bin/brestic
    sudo chmod +x /usr/local/bin/brestic
    ```

## 🛠 Configuración

Crea o edita un perfil con: `brestic e mi_servidor`.

### Ejemplo de Configuración Completa (v2.1.0)

```bash
# ~/.config/brestic/mi_servidor

# --- Destino y Seguridad ---
SERVER="rclone:drive:backups/web"
PASS="tu_contrasena_segura"

# --- Notificaciones (Opcional) ---
NTFY_URL_SERVER="https://ntfy.sh/tu_topico_secreto"
TELEGRAM_TOKEN="123456:ABC-DEF..."
TELEGRAM_ID="tu_id_de_usuario"

# --- Fuentes de Backup ---
SOURCE="/var/www --tag web --exclude='**/cache/*'"
SOURCE="/home/user/documentos --tag docs"

# --- Política de Retención Personalizada (comando 'clp') ---
KEEP="--keep-daily 7 --keep-weekly 4 --keep-monthly 6"
```

## 📖 Uso y Comandos

### Gestión y Operaciones
| Comando | Descripción |
| :--- | :--- |
| `b <config>` | **Backup**: Ejecuta las fuentes y envía notificaciones. |
| `ls <config>` | Lista snapshots del repositorio. |
| `m <config>` | **Montaje Simple**: Monta el repositorio en `~/brestic`. |
| `mw <config>` | **Montaje Web**: Monta el repo e inicia el navegador Flask (PyBrestic). |
| `nav <config>`| Navega por los archivos del backup con `fzf` (requiere `m`). |
| `diff <config>`| Compara dos snapshots seleccionados visualmente. |
| `u <config>` | Desbloquea el repositorio tras un fallo. |

### Limpieza y Retención
| Comando | Descripción |
| :--- | :--- |
| `cl <config>` | Política estándar (30d, 4w, 12m, 2y). |
| `clp <config>` | Aplica la variable `$KEEP` del archivo de config. |
| `3m <config>` | Borra snapshots de más de 3 meses, conservando días 1 y 15. |
| `date-YYYY-MM-DD` | Borra snapshots de una fecha específica. |
| `word-TEXTO` | Borra snapshots que contengan un texto en su ruta. |

---

## 🌐 PyBrestic: Explorador de Archivos Web

El comando `brestic mw <config>` levanta una interfaz web potente que permite interactuar con tus backups sin usar la terminal.

### Funcionalidades:
- **Navegación Visual**: Explora la estructura de directorios de tus snapshots montados.
- **Previsualización**: Ver contenido de archivos de texto, logs y otros formatos compatibles.
- **Restauración Inteligente**: Descarga o restaura archivos y carpetas directamente a tu máquina local.
- **Seguridad**: Acceso protegido mediante credenciales (Configurables en `pybrestic.py`).
  - *Usuario por defecto*: `admin`
  - *Password por defecto*: `brestic2024`

### ¿Cómo funciona?
Al lanzar `mw`, el script monta el repositorio restic en segundo plano, espera un tiempo prudencial (definido por `PYBRESTIC_SLEEP`) para que los archivos sean legibles, y arranca el servidor Flask en el puerto `5000`.

---

## ⏰ Automatización con Cron

Aprovecha las notificaciones para estar al tanto de tus copias automáticas:

```crontab
# Backup diario a las 03:00 AM
00 3 * * * /usr/local/bin/brestic b mi_servidor

# Limpieza y mantenimiento cada domingo a las 05:00 AM
00 5 * * 0 /usr/local/bin/brestic clp mi_servidor && /usr/local/bin/brestic dd mi_servidor
```

## 📝 Notas de la Versión 2.1.0
- **Integración PyBrestic**: Se ha unificado el navegador web con la lógica de montaje de restic.
- **Lanzamiento Paralelo**: El comando `mw` gestiona procesos en segundo plano para no bloquear el terminal.
- **Mejora en Notificaciones**: El nombre **Brestic** ahora utiliza formato Markdown para destacar en dispositivos móviles.

## 📄 Licencia
MIT © 2024-2025. Contribuciones bienvenidas vía Pull Request.
