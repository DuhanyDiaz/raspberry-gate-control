import { useState } from 'react'
import Swal from 'sweetalert2'
import jsPDF from 'jspdf'
import 'jspdf-autotable'
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
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Usuario o contraseña incorrectos',
        confirmButtonColor: '#2a7a43'
      })
    }
  }

  const manejarCambioPassword = () => {
    Swal.fire({
      title: 'Cambiar Contraseña',
      html: `
        <input type="password" id="current-password" class="swal2-input" placeholder="Contraseña actual" style="margin-bottom: 10px;">
        <input type="password" id="new-password" class="swal2-input" placeholder="Nueva contraseña" style="margin-bottom: 10px;">
        <input type="password" id="confirm-password" class="swal2-input" placeholder="Confirmar nueva contraseña">
      `,
      confirmButtonText: 'Guardar',
      confirmButtonColor: '#2a7a43',
      showCancelButton: true,
      cancelButtonText: 'Cancelar',
      preConfirm: () => {
        const current = Swal.getPopup().querySelector('#current-password').value
        const newPass = Swal.getPopup().querySelector('#new-password').value
        const confirmPass = Swal.getPopup().querySelector('#confirm-password').value
        
        if (!current || !newPass || !confirmPass) {
          Swal.showValidationMessage('Por favor completa todos los campos')
          return false
        }
        
        if (newPass !== confirmPass) {
          Swal.showValidationMessage('Las contraseñas nuevas no coinciden')
          return false
        }
        
        return { current, newPass }
      }
    }).then((result) => {
      if (result.isConfirmed) {
        Swal.fire({
          icon: 'success',
          title: 'Contraseña Actualizada',
          text: 'Tu contraseña ha sido cambiada exitosamente.',
          confirmButtonColor: '#2a7a43'
        })
      }
    })
  }

  const generarPDF = () => {
    const doc = new jsPDF()
    doc.text("Historial de Accesos - EMI FIUSAC", 14, 15)
    
    const tableColumn = ["Usuario / Persona", "Acción Realizada", "Fecha y Hora"]
    const tableRows = []
    
    historial.forEach(reg => {
      const rowData = [
        reg.nombres,
        reg.accion,
        reg.fecha
      ]
      tableRows.push(rowData)
    })
    
    doc.autoTable({
      head: [tableColumn],
      body: tableRows,
      startY: 20,
      styles: { fontSize: 10 },
      headStyles: { fillColor: [42, 122, 67] } // Verde FIUSAC
    })
    
    doc.save(`Historial_Accesos_${new Date().toISOString().split('T')[0]}.pdf`)
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
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="settings-btn" onClick={manejarCambioPassword} title="Cambiar Contraseña">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </button>
          <button className="Btn" onClick={() => setSesionIniciada(false)}>
            <div className="sign">
              <svg viewBox="0 0 512 512">
                <path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z"></path>
              </svg>
            </div>
            <div className="text">Cerrar Sesión</div>
          </button>
        </div>
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
                    <button className="pushable approve" onClick={() => Swal.fire({
                      icon: 'success',
                      title: 'Aprobado',
                      text: 'Código generado para ' + sol.nombres,
                      confirmButtonColor: '#2a7a43'
                    })}>
                      <span className="shadow"></span>
                      <span className="edge"></span>
                      <span className="front">Aprobar</span>
                    </button>
                    <button className="pushable deny" onClick={() => Swal.fire({
                      icon: 'info',
                      title: 'Denegado',
                      text: 'Se ha denegado la solicitud de ' + sol.nombres,
                      confirmButtonColor: '#ff6b6b'
                    })}>
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Historial de Accesos Recientes</h3>
            <button className="btn-download-csv" onClick={generarPDF} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              Descargar PDF
            </button>
          </div>
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
