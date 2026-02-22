# ============================================================
#  MineVision Dashboard – Makefile cross-platform
#  Funciona en: Ubuntu/Linux, Git Bash (Windows con make)
#  NO requiere activar el venv: llama al python del venv directamente
# ============================================================

# ── Detección de SO ──────────────────────────────────────────
ifeq ($(OS),Windows_NT)
    PYTHON  := .venv/Scripts/python
    PIP     := .venv/Scripts/pip
    VENV_OK := .venv/Scripts/activate
    RM      := rm -rf
else
    PYTHON  := .venv/bin/python
    PIP     := .venv/bin/pip
    VENV_OK := .venv/bin/activate
    RM      := rm -rf
endif

VENV := .venv
APP  := app.py
PORT := 8050

.DEFAULT_GOAL := help

# ── Ayuda ────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  MineVision Dashboard"
	@echo "  ─────────────────────────────────────────────"
	@echo "  make setup     Crea venv + instala dependencias"
	@echo "  make run       Ejecuta la app (localhost:$(PORT))"
	@echo "  make install   Solo actualiza dependencias"
	@echo "  make freeze    Guarda versiones en requirements.txt"
	@echo "  make clean     Elimina el entorno virtual"
	@echo "  make reset     clean + setup"
	@echo ""

# ── Crear venv ───────────────────────────────────────────────
$(VENV_OK):
	@echo "→ Creando entorno virtual..."
	python3 -m venv $(VENV) 2>/dev/null || python -m venv $(VENV)
	@echo "  OK  Entorno virtual creado en $(VENV)/"

# ── Setup completo ───────────────────────────────────────────
.PHONY: setup
setup: $(VENV_OK)
	@echo "→ Instalando dependencias..."
	$(PYTHON) -m pip install --upgrade pip --quiet
	$(PYTHON) -m pip install -r requirements.txt
	@echo ""
	@echo "  Listo. Ejecuta:  make run"
	@echo ""

# ── Instalar / actualizar dependencias ───────────────────────
.PHONY: install
install: $(VENV_OK)
	$(PYTHON) -m pip install --upgrade pip --quiet
	$(PYTHON) -m pip install -r requirements.txt

# ── Ejecutar app ──────────────────────────────────────────────
.PHONY: run
run: $(VENV_OK)
	@echo "→ http://localhost:$(PORT)"
	$(PYTHON) $(APP)

# ── Freeze ───────────────────────────────────────────────────
.PHONY: freeze
freeze:
	$(PIP) freeze > requirements.txt
	@echo "  OK  requirements.txt actualizado."

# ── Limpiar ───────────────────────────────────────────────────
.PHONY: clean
clean:
	$(RM) $(VENV)
	@echo "  OK  .venv/ eliminado."

# ── Reset ─────────────────────────────────────────────────────
.PHONY: reset
reset: clean setup
