import { useState, useEffect } from 'react'
import './App.css'
import logoFiusac from './assets/EMI-FIUSAC.png'

// En React, las imágenes locales se deben "importar" como si fueran código
import imgT3 from './assets/T3.png'
import imgPlaza from './assets/PLAZA.png'
import imgEstudiante from './assets/ESTUDIANTE.png'
import imgUsac from './assets/USAC.png'
import Keypad from './Keypad'
import RegistroForm from './RegistroForm'
import AdminPanel from './AdminPanel'

const imagenesFondo = [
  imgT3,
  imgPlaza,
  imgEstudiante,
  imgUsac
]

function App() {
  const [fondoActual, setFondoActual] = useState(0)
  const [vistaActiva, setVistaActiva] = useState('teclado') // Puede ser 'teclado' o 'registro'
  const [adminLoggedIn, setAdminLoggedIn] = useState(false) // Control global de la sesión del admin

  const irAInicio = () => {
    if (vistaActiva === 'admin' && adminLoggedIn) {
      alert("Por seguridad, debes cerrar sesión antes de salir del panel de administración.");
      return;
    }
    setVistaActiva('teclado');
  }

  // Efecto para rotar la imagen cada 10 segundos
  useEffect(() => {
    const intervalo = setInterval(() => {
      setFondoActual((prev) => (prev + 1) % imagenesFondo.length)
    }, 15000)
    return () => clearInterval(intervalo)
  }, [])

  return (
    <div className="app-container">

      {/* Carrusel de fondos animados (Se manejan en CSS) */}
      <div className="background-slider">
        {imagenesFondo.map((img, index) => (
          <div
            key={index}
            className={`bg-image ${index === fondoActual ? 'active' : ''}`}
            style={{ backgroundImage: `url('${img}')` }}
          ></div>
        ))}
        {/* Degradado verde sobre las imágenes */}
        <div className="bg-overlay"></div>
      </div>

      {/* Barra de navegación superior (Estilo USAC/FIUSAC) */}
      <nav className="navbar">
        <div className="navbar-logo">
          {/* Aquí usamos la imagen que importamos arriba */}
          <img src={logoFiusac} alt="Logo FIUSAC EMI" className="logo-imagen" />
        </div>

        <div className="navbar-links">
          <a href="#" onClick={(e) => { 
            e.preventDefault(); 
            if (vistaActiva === 'admin' && adminLoggedIn) {
              alert("Por seguridad, debes cerrar sesión antes de salir del panel de administración.");
              return;
            }
            setVistaActiva('teclado');
          }}>Inicio</a>
          <a href="#" onClick={(e) => { 
            e.preventDefault(); 
            if (vistaActiva === 'admin' && adminLoggedIn) {
              alert("Por seguridad, debes cerrar sesión antes de salir del panel de administración.");
              return;
            }
            setVistaActiva('admin');
          }}>Administración</a>
        </div>
      </nav>

      {/* Contenido principal */}
      <main className="main-content">
        {vistaActiva === 'teclado' ? (
          <div className="keypad-section">
            <h1>INGRESO AL SALÓN</h1>
            <p>Por favor, ingrese su código asignado para abrir la puerta.</p>

            <Keypad />
            
            {/* Enlace para ir al formulario */}
            <button 
              onClick={() => setVistaActiva('registro')}
              style={{
                marginTop: '30px', 
                background: 'transparent', 
                color: 'white', 
                border: 'none', 
                textDecoration: 'underline', 
                cursor: 'pointer', 
                fontSize: '16px'
              }}
            >
              ¿No tienes código? Solicita acceso aquí
            </button>
          </div>
        ) : vistaActiva === 'registro' ? (
          <RegistroForm onVolver={() => setVistaActiva('teclado')} />
        ) : (
          <AdminPanel 
            onVolver={() => setVistaActiva('teclado')} 
            sesionIniciada={adminLoggedIn}
            setSesionIniciada={setAdminLoggedIn}
          />
        )}
      </main>
    </div>
  )
}

export default App
