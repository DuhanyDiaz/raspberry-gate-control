import './App.css'
import logoFiusac from './assets/EMI-FIUSAC.png'


function App() {
  return (
    <div className="app-container">
      {/* Barra de navegación superior (Estilo USAC/FIUSAC) */}
      <nav className="navbar">
        <div className="navbar-logo">
          {/* Aquí usamos la imagen que importamos arriba */}
          <img src={logoFiusac} alt="Logo FIUSAC EMI" className="logo-imagen" />
        </div>

        <div className="navbar-links">
          <a href="#">Inicio</a>
          <a href="#">Administración</a>
        </div>
      </nav>

      {/* Contenido principal con el fondo verde */}
      <main className="main-content">
        <div className="keypad-section">
          <h1>INGRESO AL SALÓN</h1>
          <p>Por favor, ingrese su código asignado para abrir la puerta.</p>

          {/* Aquí irá el teclado más adelante */}
          <div className="placeholder-teclado">
            [ Aquí irá el teclado numérico ]
          </div>

        </div>
      </main>
    </div>
  )
}

export default App
