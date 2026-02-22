# MineVision Dashboard

Dashboard full-stack en Python Dash para visualización de datos de operaciones mineras.

---

## Contenido

- [Requisitos](#requisitos)
- [Windows — CMD o PowerShell](#windows--cmd-o-powershell)
- [Windows — Git Bash con make](#windows--git-bash-con-make)
- [Ubuntu / Linux](#ubuntu--linux)
- [Comandos make (referencia)](#comandos-make-referencia)
- [Páginas del dashboard](#páginas-del-dashboard)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## Requisitos

| Herramienta | Versión mínima | Enlace |
|---|---|---|
| Python | 3.10+ | https://www.python.org/downloads/ |
| pip | incluido con Python | — |
| make (opcional) | cualquiera | ver sección correspondiente |

> **Windows:** durante la instalación de Python marcar **"Add Python to PATH"**

Verificar que Python esté instalado:
```
python --version
```

---

## Windows — CMD o PowerShell

> Opción más simple. No necesita `make`.

### CMD (símbolo del sistema)

```bat
:: Abrir CMD en la carpeta del proyecto y ejecutar:

setup.bat       <- crea .venv/ e instala todas las dependencias
run.bat         <- activa el venv y lanza la app
```

### PowerShell

```powershell
# Solo la primera vez (habilitar ejecución de scripts):
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego:
.\setup.ps1     # crea .venv/ e instala dependencias
.\run.ps1       # lanza la app
```

### Manual (sin scripts)

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app.py
```

Abrir en el navegador: **http://localhost:8050**
Detener: `Ctrl + C`

---

## Windows — Git Bash con make

> Git Bash viene con Git for Windows pero **NO incluye `make` por defecto**.
> Hay dos formas de instalarlo:

### Opción 1: Chocolatey (recomendado)

```bash
# Instalar Chocolatey primero si no lo tienes (en PowerShell como Administrador):
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Luego instalar make:
choco install make
```

### Opción 2: Scoop

```bash
# Instalar Scoop si no lo tienes (en PowerShell):
irm get.scoop.sh | iex

# Luego:
scoop install make
```

### Una vez instalado make — flujo en Git Bash

```bash
# Ir al proyecto
cd /e/Projects/mining-dashboard

# Ver comandos disponibles
make help

# Crear entorno virtual e instalar dependencias
make setup

# Ejecutar la app
make run
```

> El `Makefile` detecta automáticamente si estás en Windows o Linux
> y usa la ruta correcta (`.venv/Scripts/` o `.venv/bin/`).

---

## Ubuntu / Linux

> `make` viene preinstalado. Solo necesitas Python y el módulo `venv`.

### Instalar dependencias del sistema (una sola vez)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv make -y
```

### Flujo completo

```bash
# Ir al proyecto
cd ~/Projects/mining-dashboard    # ajusta la ruta

# Ver comandos disponibles
make help

# Crear entorno virtual e instalar dependencias
make setup

# Ejecutar la app
make run
```

Abrir: **http://localhost:8050**

### Manual (sin make, Ubuntu)

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar  ← diferencia clave vs Windows
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app.py
```

---

## Comandos make (referencia)

```
make help      Muestra ayuda con todos los comandos
make setup     Crea .venv/ + instala todas las dependencias   ← empezar aquí
make run       Ejecuta la app en http://localhost:8050
make install   Solo instala/actualiza dependencias (venv existente)
make freeze    Actualiza requirements.txt con versiones actuales
make clean     Elimina el entorno virtual (.venv/)
make reset     Equivale a: make clean && make setup
```

---

## Diferencias clave Windows vs Ubuntu

| Aspecto | Windows | Ubuntu/Linux |
|---|---|---|
| Activar venv | `.venv\Scripts\activate` | `source .venv/bin/activate` |
| Python en venv | `.venv/Scripts/python` | `.venv/bin/python` |
| `make` disponible | NO por defecto (instalar) | SI por defecto |
| Script alternativo | `setup.bat` / `setup.ps1` | `make setup` directo |
| Comando Python | `python` | `python3` |

---

## Solución de problemas

| Problema | Solución |
|---|---|
| `python: command not found` (Ubuntu) | Usar `python3` en su lugar |
| `python no se reconoce` (Windows) | Reinstalar Python con "Add to PATH" marcado |
| `make: command not found` (Windows) | Instalar con `choco install make` o usar `setup.bat` |
| PowerShell bloquea scripts | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Puerto 8050 en uso | Cambiar `port=8050` en `app.py` |
| Error al instalar dependencias | `make reset` o borrar `.venv/` manualmente y repetir |

---

## Páginas del dashboard

| Ruta | Descripción | Gráficos |
|------|-------------|----------|
| `/` | **Resumen** | KPI cards, tonelaje mensual, finos Cu/Au, gauge DSA |
| `/produccion` | **Producción** | Tonelaje diario, recuperación, scatter ley vs ton, heatmap, box plot |
| `/equipos` | **Equipos** | Disponibilidad, utilización, heatmap semanal, tabla resumen |
| `/seguridad` | **Seguridad** | Días sin accidente, TRIR, heatmap incidentes, tipos |
| `/costos` | **Costos** | Donut categorías, stack mensual, costo/ton, waterfall |

---

## Estructura del proyecto

```
mining-dashboard/
├── app.py                  ← Entrada principal + routing
├── requirements.txt        ← Dependencias Python
├── Makefile                ← Comandos make (Windows Git Bash + Ubuntu)
├── setup.bat               ← Setup para CMD de Windows
├── run.bat                 ← Ejecutar app desde CMD
├── setup.ps1               ← Setup para PowerShell
├── run.ps1                 ← Ejecutar app desde PowerShell
├── assets/
│   └── style.css           ← Tema oscuro personalizado
├── data/
│   └── mining_data.py      ← Datos sintéticos de ejemplo
├── components/
│   └── navbar.py           ← Barra de navegación
└── pages/
    ├── overview.py         ← Página resumen
    ├── produccion.py       ← Página producción
    ├── equipos.py          ← Página equipos
    ├── seguridad.py        ← Página seguridad
    └── costos.py           ← Página costos
```
