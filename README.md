# brestic

Un potente wrapper para 'restic' que simplifica la gestión de tus backups a través de la línea de comandos, ahora con notificaciones integradas y navegación interactiva.

`brestic` nace de la necesidad de automatizar y simplificar las operaciones más comunes de `restic`, permitiendo gestionar complejas políticas de retención, múltiples fuentes de backup y recibir alertas en tiempo real en tu móvil.

![Bash Shell](https://img.shields.io/badge/Shell-Bash-blue?style=for-the-badge&logo=gnu-bash)
![Version](https://img.shields.io/badge/Version-v2.0.0-green?style=for-the-badge)

## Características Principales

-   **Notificaciones Multi-canal**: Recibe confirmaciones de tus backups en **ntfy** y **Telegram** automáticamente. Soporta formato Markdown para mayor legibilidad.
-   **Sintaxis Unificada v2.0**: Comandos simplificados y potentes para gestionar el ciclo de vida completo del dato.
-   **Navegación Interactiva**: 
    -   `nav`: Explora tus backups como si fueran carpetas locales usando `fzf`.
    -   `diff`: Compara visualmente qué ha cambiado entre dos snapshots.
-   **Gestión por Archivos de Configuración**: Organiza tus backups por proyectos. Cada archivo en `~/.config/brestic/` es un perfil independiente.
-   **Políticas de Limpieza Inteligentes**: 
    -   `[N]m`: Limpieza avanzada que conserva hitos históricos (días 1 y 15) de meses pasados.
    -   `clp`: Aplica políticas personalizadas definidas directamente en tu archivo de configuración.
-   **Robusto**: Gestión de bloqueos automática (`unlock`) y validación de integridad de datos.

## Requisitos

1.  **`restic`**: La herramienta de backup principal.
2.  **`jq`**: Para procesar metadatos de los snapshots.
3.  **`fzf`**: (Opcional pero recomendado) Para la navegación interactiva y selección de archivos.
4.  **`curl`**: Para el envío de notificaciones.

Instalación rápida en Debian/Ubuntu:
```bash
brestic install
```

## Instalación

1.  **Clona el repositorio**:
    ```bash
    git clone https://github.com/tu_usuario/brestic.git /opt/brestic
    ```
2.  **Enlace simbólico**:
    ```bash
    sudo ln -s /opt/brestic/brestic /usr/local/bin/brestic
    sudo chmod +x /usr/local/bin/brestic
    ```

## Configuración

Crea o edita un perfil con: `brestic e mi_servidor`.

### Ejemplo de Configuración Completa (v2.0.0)

```bash
# ~/.config/brestic/mi_servidor

# --- Destino y Seguridad ---
SERVER="rclone:drive:backups/web"
PASS="tu_contrasena_segura"

# --- Notificaciones (Opcional) ---
# ntfy.sh o servidor propio
NTFY_URL_SERVER="https://ntfy.sh/tu_topico_secreto"
NTFY_USER="usuario"
NTFY_PASS="password"

# Telegram Bot
TELEGRAM_TOKEN="123456:ABC-DEF..."
TELEGRAM_ID="tu_id_de_usuario"

# --- Fuentes de Backup ---
SOURCE="/var/www --tag web --exclude='**/cache/*'"
SOURCE="/home/user/documentos --tag docs"

# --- Política de Retención Personalizada (comando 'clp') ---
KEEP="--keep-daily 7 --keep-weekly 4 --keep-monthly 6"
```

## Uso y Comandos

### Gestión y Operaciones
| Comando | Descripción |
| :--- | :--- |
| `b <config>` | **Backup**: Ejecuta las fuentes y envía notificaciones. |
| `ls <config>` | Lista snapshots del repositorio. |
| `m <config>` | Monta el repositorio en `~/brestic`. |
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

## Automatización con Cron

Al usar `brestic` en cron, ya no necesitas revisar logs constantemente gracias a las notificaciones:

```crontab
# Backup diario a las 03:00 AM
00 3 * * * /usr/local/bin/brestic b mi_servidor

# Limpieza y mantenimiento cada domingo a las 05:00 AM
00 5 * * 0 /usr/local/bin/brestic clp mi_servidor && /usr/local/bin/brestic dd mi_servidor
```

## Notas de la Versión 2.0.0
- **Formato de Notificación**: El nombre **Brestic** aparecerá en negrita en Telegram y ntfy.
- **Seguridad**: Se han añadido banderas `-euo pipefail` para máxima fiabilidad en scripts automáticos.
- **Mejora en `b`**: El comando de backup ahora itera correctamente sobre múltiples líneas `SOURCE` notificando cada éxito individualmente.

## Licencia
MIT © 2024-2025. Contribuciones bienvenidas vía PR.
