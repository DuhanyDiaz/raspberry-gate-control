// Configuración dinámica de la URL del Backend
// Si se define VITE_API_URL (ej. en Vercel/producción), tiene prioridad.
// De lo contrario, utiliza automáticamente la IP o dominio del navegador con el puerto 8000.
const hostname = typeof window !== 'undefined' && window.location.hostname ? window.location.hostname : '127.0.0.1';
export const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${hostname}:8000`;
