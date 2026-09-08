import { useState } from 'react'
import './AdminPanel.css'

export default function AdminPanel({ onVolver, sesionIniciada, setSesionIniciada }) {
  const [usuario, setUsuario] = useState('')
  const [password, setPassword] = useState('')
  const [pestañaActiva, setPestañaActiva] = useState('solicitudes') // 'solicitudes' o 'historial'

  const manejarLogin = (e) => {
    e.preventDefault()
    // Credenciales simuladas por ahora (Fase 1). En Fase 2 verificaremos con la base de datos real.
    if (usuario === 'admin' && password === 'admin123') {
      setSesionIniciada(true)
    } else {
      alert('Usuario o contraseña incorrectos')
    }
  }

  // 1. PANTALLA DE INICIO DE SESIÓN
  if (!sesionIniciada) {
    return (
      <div className="admin-container">
        <h2>Acceso Administrativo</h2>
        <form onSubmit={manejarLogin}>
          <div className="input-group" style={{ marginBottom: '15px' }}>
            <input
              type="text"
              placeholder="Usuario"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
              required
              style={{ width: '100%', padding: '12px 15px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.4)', background: 'rgba(0,0,0,0.2)', color: 'white', boxSizing: 'border-box' }}
            />
          </div>
          <div className="input-group" style={{ marginBottom: '25px' }}>
            <input
              type="password"
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%', padding: '12px 15px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.4)', background: 'rgba(0,0,0,0.2)', color: 'white', boxSizing: 'border-box' }}
            />
          </div>
          <div className="form-buttons" style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <button type="submit" className="btn-login-skew">Iniciar Sesión</button>
          </div>
        </form>
      </div>
    )
  }

  // Datos simulados de estudiantes que llenaron el formulario
  const solicitudes = [
    { id: 1, nombres: 'Juan Pérez', carne: '202100123', dpi: '1234567890101', dias: 'Lunes, Jueves', horarios: '10:00 - 12:00' },
    { id: 2, nombres: 'María Gómez', carne: '202011222', dpi: '9876543210101', dias: 'Viernes', horarios: '14:00 - 16:00' },
    { id: 3, nombres: 'Carlos López', carne: '202345091', dpi: '4561237890101', dias: 'Martes', horarios: '08:00 - 10:00' }
  ]

  // Datos simulados del historial de quién entró y a qué hora
  const historial = [
    { id: 101, nombres: 'Admin', accion: 'Apertura Manual', fecha: '14/11/2023 08:30:00' },
    { id: 102, nombres: 'Carlos López', accion: 'Ingreso con PIN', fecha: '14/11/2023 09:15:22' },
    { id: 103, nombres: 'Desconocido', accion: 'Intento Fallido (PIN Incorrecto)', fecha: '14/11/2023 10:05:10' }
  ]

  // 2. PANTALLA DEL DASHBOARD DEL ADMINISTRADOR
  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h2>Panel de Control de Accesos</h2>
        <button className="Btn" onClick={() => setSesionIniciada(false)}>
          <div className="sign">
            <svg viewBox="0 0 512 512">
              <path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z"></path>
            </svg>
          </div>
          <div className="text">Cerrar Sesión</div>
        </button>
      </div>

      {/* PESTAÑAS DE NAVEGACIÓN */}
      <div className="admin-tabs">
        <button
          className={`pushable ${pestañaActiva === 'solicitudes' ? 'approve' : ''}`}
          onClick={() => setPestañaActiva('solicitudes')}
        >
          <span className="shadow"></span>
          <span className="edge"></span>
          <span className="front">Solicitudes Pendientes</span>
        </button>
        <button
          className={`pushable ${pestañaActiva === 'historial' ? 'approve' : ''}`}
          onClick={() => setPestañaActiva('historial')}
        >
          <span className="shadow"></span>
          <span className="edge"></span>
          <span className="front">Historial de Accesos</span>
        </button>
      </div>

      {pestañaActiva === 'solicitudes' && (
        <div className="table-container">
          <h3>Solicitudes Pendientes</h3>
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Carné</th>
                <th>DPI</th>
                <th>Días</th>
                <th>Horario</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {solicitudes.map(sol => (
                <tr key={sol.id}>
                  <td>{sol.nombres}</td>
                  <td>{sol.carne}</td>
                  <td>{sol.dpi}</td>
                  <td>{sol.dias}</td>
                  <td>{sol.horarios}</td>
                  <td>
                    <button className="pushable approve" onClick={() => alert('Código generado para ' + sol.nombres)}>
                      <span className="shadow"></span>
                      <span className="edge"></span>
                      <span className="front">Aprobar</span>
                    </button>
                    <button className="pushable deny">
                      <span className="shadow"></span>
                      <span className="edge"></span>
                      <span className="front">Denegar</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {pestañaActiva === 'historial' && (
        <div className="table-container">
          <h3>Historial de Accesos Recientes</h3>
          <table>
            <thead>
              <tr>
                <th>Usuario / Persona</th>
                <th>Acción Realizada</th>
                <th>Fecha y Hora</th>
              </tr>
            </thead>
            <tbody>
              {historial.map(reg => (
                <tr key={reg.id}>
                  <td>{reg.nombres}</td>
                  <td>
                    <span style={{
                      color: reg.accion.includes('Fallido') ? '#ff6b6b' : '#51cf66',
                      fontWeight: 'bold'
                    }}>
                      {reg.accion}
                    </span>
                  </td>
                  <td>{reg.fecha}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
