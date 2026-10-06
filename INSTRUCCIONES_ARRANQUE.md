#  Guía de Arranque Rápido: Control de Accesos EMI

Este documento contiene las instrucciones paso a paso para levantar ambos servidores (Backend y Frontend) en tu computadora de desarrollo. 

El proyecto consta de dos partes separadas que deben correr al mismo tiempo en dos terminales distintas.

---

## 1️ Levantar el Servidor Python (Backend)

El backend expone la API y se conecta con la base de datos SQLite. Debes ejecutarlo dentro de su entorno virtual.

**Pasos en la Terminal 1:**
1. Abre tu terminal y navega a la carpeta del backend:
   ```bash
   cd /Users/alexander/Desktop/raspberry-gate-control/backend
   ```
2. Activa el entorno virtual de Python:
   ```bash
   source .venv/bin/activate
   ```
3. Inicia el servidor con `uvicorn`:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
*(El servidor quedará corriendo en `http://127.0.0.1:8000`)*

---

## 2️ Levantar el Servidor React (Frontend)

El frontend maneja la interfaz gráfica y se conecta al backend localmente.

**Pasos en la Terminal 2:**
1. Abre **otra** ventana/pestaña en tu terminal y navega a la carpeta del frontend:
   ```bash
   cd /Users/alexander/Desktop/raspberry-gate-control/frontend
   ```
2. Inicia el servidor de desarrollo de Vite:
   ```bash
   npm run dev
   ```
*(La aplicación web estará disponible en `http://localhost:5173`)*

---

##  Cómo detener los servidores
Cuando termines de trabajar, simplemente ve a cada terminal y presiona la combinación de teclas:
`Control + C`
