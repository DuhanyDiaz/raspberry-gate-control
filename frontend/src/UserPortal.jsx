import { useState } from 'react'
import Swal from 'sweetalert2'
import './UserPortal.css'

export default function UserPortal({ onVolver }) {
  const [usuario, setUsuario] = useState('')
  const [password, setPassword] = useState('')
  const [userData, setUserData] = useState(null) // Si está null, muestra el login. Si tiene datos, muestra el dashboard.

  const manejarLogin = async (e) => {
    e.preventDefault()
    try {
      const respuesta = await fetch("http://127.0.0.1:8000/api/usuario/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario, password })
      })

      if (respuesta.ok) {
        const datos = await respuesta.json()
        setUserData(datos)
      } else {
        const errorData = await respuesta.json()
        Swal.fire({
          icon: 'error',
          title: 'Error de Autenticación',
          text: errorData.detail || 'Usuario o contraseña incorrectos',
          confirmButtonColor: '#ff6b6b'
        })
      }
    } catch (error) {
      Swal.fire('Error', 'No se pudo conectar con el servidor', 'error')
    }
  }

  const manejarCerrarSesion = () => {
    setUserData(null)
    setUsuario('')
    setPassword('')
  }

  // 1. PANTALLA DE INICIO DE SESIÓN PARA EL USUARIO
  if (!userData) {
    return (
      <div className="user-container">
        <h2>Mi Acceso (Usuarios)</h2>
        <p style={{ textAlign: 'center', marginBottom: '20px', color: 'rgba(255,255,255,0.8)' }}>
          Ingresa para ver el estado de tu solicitud y tu Llave de Acceso (PIN).
        </p>
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

          <div className="form-buttons" style={{ display: 'flex', gap: '10px' }}>
            <button type="button" onClick={onVolver} className="btn-cancel">Volver al Inicio</button>
            <button type="submit" className="btn-submit" style={{ flex: 1, padding: '12px', background: 'var(--verde-fiusac)', border: 'none', borderRadius: '8px', color: 'white', cursor: 'pointer', fontWeight: 'bold' }}>Ingresar</button>
          </div>
        </form>
      </div>
    )
  }

  // 2. PANTALLA DEL DASHBOARD DEL USUARIO (SI YA INICIÓ SESIÓN)
  return (
    <div className="user-dashboard">
      <div className="user-header">
        <div>
          <h2>Panel de Usuario</h2>
          <p style={{ color: 'rgba(0,0,0,0.6)', margin: '5px 0 0 0', fontSize: '16px' }}>
            ¡Hola, {userData.nombre}!
          </p>
        </div>
        <button
          onClick={manejarCerrarSesion}
          style={{ background: '#ff4d4f', border: 'none', color: '#ffffff', padding: '8px 12px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', boxShadow: '0 4px 6px rgba(255, 77, 79, 0.2)' }}
        >
          Cerrar Sesión
        </button>
      </div>

      {/* ESTADO DE LA SOLICITUD */}
      {userData.estado === 'APROBADA' && (
        <div className="status-card status-aprobada">
          ¡Felicidades! Tu solicitud ha sido aprobada.
        </div>
      )}
      {userData.estado === 'PENDIENTE' && (
        <div className="status-card status-pendiente">
          Tu solicitud está en proceso de revisión por la administración.
        </div>
      )}
      {userData.estado === 'DENEGADA' && (
        <div className="status-card status-denegada">
          Lo sentimos, tu solicitud ha sido denegada.
        </div>
      )}

      {/* MOSTRAR PIN SI ESTÁ APROBADA */}
      {userData.estado === 'APROBADA' && userData.pin_acceso && (
        <div className="pin-display">
          <h3 style={{ margin: '0 0 10px 0', color: '#1a1a1a', fontWeight: '600' }}>Tu Llave de Acceso (PIN)</h3>
          <div className="pin-number">{userData.pin_acceso}</div>
          <p style={{ fontSize: '13px', color: 'rgba(0,0,0,0.6)', marginTop: '15px' }}>
            Ingresa este código en el teclado principal para abrir la puerta. NO compartas tu PIN con nadie.
          </p>
        </div>
      )}

      {/* INFORMACIÓN DEL USUARIO */}
      <div className="user-info">
        <h3 style={{ margin: '0 0 15px 0', borderBottom: '1px solid rgba(0,0,0,0.1)', paddingBottom: '10px' }}>Detalles de Acceso</h3>
        <p><strong>Rol:</strong> {userData.rol}</p>
        <p><strong>Usuario:</strong> {userData.usuario}</p>
        <p><strong>Carné:</strong> {userData.carne}</p>
        <p><strong>Días Permitidos:</strong> {userData.dias_permitidos}</p>
        <p><strong>Horario:</strong> {userData.hora_inicio} a {userData.hora_fin}</p>
      </div>

    </div>
  )
}
