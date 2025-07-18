# brestic

Un potente wrapper para 'restic' que simplifica la gestión de tus backups a través de la línea de comandos.

`brestic` nace de la necesidad de automatizar y simplificar las operaciones más comunes de `restic`, permitiendo gestionar complejas políticas de retención y múltiples fuentes de backup con comandos de una sola línea.

![Bash Shell](https://img.shields.io/badge/Shell-Bash-blue?style=for-the-badge&logo=gnu-bash)

## Características Principales

-   **Sintaxis Simple y Unificada**: Olvídate de recordar las complejas banderas de `restic`. Usa comandos intuitivos como `brestic b mi_backup` para hacer un backup o `brestic ls mi_backup` para listar snapshots.
-   **Gestión por Archivos de Configuración**: Organiza tus backups por proyectos o máquinas. Cada archivo de configuración contiene el repositorio, la contraseña y las fuentes de datos.
-   **Múltiples Fuentes de Backup**: Define varios directorios para respaldar dentro de un mismo archivo de configuración, cada uno con sus propias etiquetas y exclusiones.
-   **Políticas de Retención Avanzadas**: Automatiza la limpieza de snapshots antiguos con comandos simples pero potentes:
    -   `clean-monthly`: Limpia backups antiguos pero conserva un archivo histórico de los días 1 y 15 de cada mes.
    -   `clean-by-day`: Borra de forma masiva todos los backups más antiguos que un número de meses determinado, ideal para cumplir con políticas de retención estrictas.
-   **Interfaz Interactiva**: Comandos como `d` (borrar) o `r` (restaurar) te presentan un menú para que elijas el snapshot sobre el que quieres actuar, evitando errores.
-   **Robusto y Seguro**: Incluye mecanismos de desbloqueo automático para operaciones largas y pide siempre confirmación antes de realizar operaciones destructivas.

## Requisitos

Antes de usar `brestic`, asegúrate de tener instalado:

1.  **`restic`**: La herramienta de backup subyacente.
2.  **`jq`**: Una herramienta de línea de comandos para procesar JSON. `brestic` la usa para analizar la salida de `restic`.
3.  **Un backend configurado**: Debes tener un lugar donde guardar tus backups, ya sea una ruta local, un servidor SFTP o un proveedor en la nube configurado a través de `rclone`.

El propio script incluye un comando para facilitar la instalación en sistemas basados en Debian:
```bash
brestic install
```

## Instalación

1.  **Clona el repositorio** en una ubicación de tu elección (por ejemplo, en `/opt`):
    ```bash
    git clone https://github.com/tu_usuario/brestic.git /opt/brestic
    ```

2.  **Crea un enlace simbólico** para que el comando `brestic` esté disponible en todo el sistema:
    ```bash
    sudo ln -s /opt/brestic/brestic /usr/local/bin/brestic
    ```

3.  **Asegúrate de que el script tiene permisos de ejecución**:
    ```bash
    sudo chmod +x /usr/local/bin/brestic
    ```

¡Listo! Ahora puedes usar el comando `brestic` desde cualquier lugar de tu terminal.

## Configuración

El corazón de `brestic` son sus archivos de configuración. Estos se almacenan en `~/.config/brestic/`. Puedes tener tantos como necesites (uno para tu portátil, otro para un servidor, etc.).

Para crear tu primera configuración, ejecuta:
```bash
brestic e mi_servidor
```
Esto abrirá un archivo de texto vacío con tu editor de línea de comandos predeterminado (`nano` por defecto).

### Ejemplo de Archivo de Configuración

Aquí tienes un ejemplo completo para un archivo llamado `mi_servidor`.

```bash
# ~/.config/brestic/mi_servidor

# --- Repositorio de Destino ---
# Puede ser una ruta local (/mnt/backups/restic) o un backend de rclone.
SERVER="rclone:nas:backups/servidor_web"

# --- Contraseña del Repositorio ---
# ¡Asegúrate de que sea una contraseña segura!
PASS="mi_contraseña_muy_segura_aqui"


# --- Fuentes de Backup ---
# Puedes tener varias líneas SOURCE. Cada una se ejecutará como un comando
# de backup independiente, permitiendo diferentes etiquetas y exclusiones.

# Respalda el directorio web, etiquétalo como 'web' y excluye los logs.
SOURCE="/var/www --tag web --exclude='**/logs/*.log'"

# Respalda la base de datos, etiquetándola como 'db'.
SOURCE="/var/lib/mysql --tag db"

# Respalda la configuración del sistema.
SOURCE="/etc --tag config"
```

## Uso y Comandos

La ayuda completa siempre está disponible con `brestic -h` o `brestic --help`.

```text
brestic v1.1.0 (Unified Logic)
Un potente wrapper para 'restic' que simplifica la gestión de backups.

-------------------------------------------------------------------------------
Uso: brestic <COMANDO> <CONFIG_NAME> [ARGUMENTOS...]
-------------------------------------------------------------------------------
COMANDOS POR CATEGORÍA

  Gestión de Configuraciones:
  e <config_name>               Edita o crea un archivo de configuración.
  c                             Lista todos los archivos de configuración.
  install                       Instala/actualiza restic en sistemas Debian.

  Operaciones Básicas del Repositorio:
  i <config_name>               Inicializa el repositorio.
  b <config_name>               Realiza un backup.
  r <config_name>               Restaura interactivamente un snapshot.
  d, rm <config_name>           Borra un snapshot seleccionado interactivamente.
  u <config_name>               Desbloquea el repositorio (útil para errores).
  dd <config_name>              Ejecuta 'prune' para limpiar datos no referenciados.

  Listado y Búsqueda:
  ls <config_name>              Lista todos los snapshots.
  lsl <config_name>             Lista archivos del último snapshot.
  lss <config_name>             Lista archivos de un snapshot seleccionado.

  Limpieza y Mantenimiento Avanzado:
  clean-monthly <config> <meses> Elimina día a día, conservando los días 1 y 15 (no toca el último mes).
  clean-by-day <config> <meses>  Elimina día a día, empezando desde hace X meses (no toca el último mes).
```

### Ejemplo de Flujo de Trabajo

1.  **Crear y editar la configuración `webserver`**:
    ```bash
    brestic e webserver
    ```
    *(Pega el contenido del ejemplo anterior y guárdalo)*

2.  **Inicializar el repositorio por primera vez**:
    ```bash
    brestic i webserver
    ```

3.  **Realizar el primer backup**:
    ```bash
    brestic b webserver
    ```

4.  **Listar los snapshots creados**:
    ```bash
    brestic ls webserver
    ```

5.  **Restaurar un backup de forma interactiva**:
    ```bash
    brestic r webserver
    ```

6.  **Limpiar snapshots antiguos de forma segura**:
    Imagina que quieres borrar todo lo que tenga más de 6 meses, pero conservando los días 1 y 15 de cada mes como archivo histórico.
    ```bash
    brestic clean-monthly webserver 6
    ```

## Automatización con Cron

`brestic` es ideal para ser ejecutado con `cron`. Aquí tienes un ejemplo de una configuración `crontab` para automatizar backups y limpieza.

Edita tu crontab con `crontab -e` y añade las siguientes líneas:

```crontab
# ----------------------------------------------------------------
# Ejemplo de Crontab para brestic
# ----------------------------------------------------------------

# Realiza un backup completo cada día a las 02:30 AM.
30 2 * * * /usr/local/bin/brestic b webserver >> /var/log/brestic.log 2>&1

# Ejecuta una limpieza mensual cada domingo a las 04:30 AM.
# Borra todo lo que tenga más de 12 meses, conservando los días 1 y 15.
30 4 * * 0 /usr/local/bin/brestic clean-monthly webserver 12 >> /var/log/brestic.log 2>&1
```
**Nota**: El `>> /var/log/brestic.log 2>&1` es muy importante para redirigir toda la salida (tanto la normal como los errores) a un archivo de log, evitando que `cron` te envíe correos electrónicos.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Contribuir

¡Las contribuciones son bienvenidas! Si encuentras un bug o tienes una idea para mejorar `brestic`, por favor, abre un "issue" en GitHub.
