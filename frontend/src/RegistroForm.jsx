import { useState } from 'react'
import Swal from 'sweetalert2'
import './RegistroForm.css'

export default function RegistroForm({ onVolver }) {
  // Estado para guardar todo lo que el usuario escribe
  const [datos, setDatos] = useState({
    nombres: '',
    correo: '',
    dpi: '',
    carne: '',
    dias: '',
    horarios: ''
  })

  // Función genérica para actualizar el estado cada vez que se escribe en un campo
  const manejarCambio = (e) => {
    setDatos({
      ...datos,
      [e.target.name]: e.target.value
    })
  }

  // Función cuando le dan "Enviar Solicitud"
  const enviarFormulario = (e) => {
    e.preventDefault() // Evita que la página se recargue
    Swal.fire({
      icon: 'success',
      title: '¡Enviado!',
      text: 'Tu solicitud ha sido enviada al administrador. Recibirás un correo cuando sea aprobada.',
      confirmButtonColor: '#2a7a43'
    })
    // Aquí en la Fase 2, conectaremos esto con FastAPI y la base de datos real.
    onVolver() // Regresa a la pantalla del teclado
  }

  return (
    <div className="form-container">
      <h2>Solicitar Acceso</h2>
      <form onSubmit={enviarFormulario}>
        
        <div className="input-group">
          <input type="text" name="nombres" placeholder="Nombres y Apellidos Completos" required onChange={manejarCambio} />
        </div>
        
        <div className="input-group">
          <input type="email" name="correo" placeholder="Correo Electrónico" required onChange={manejarCambio} />
        </div>
        
        <div className="row-group">
          <div className="input-group">
            <input type="number" name="dpi" placeholder="DPI" required onChange={manejarCambio} />
          </div>
          <div className="input-group">
            <input type="number" name="carne" placeholder="Carné Estudiantil" required onChange={manejarCambio} />
          </div>
        </div>
        
        <div className="input-group">
          <input type="text" name="dias" placeholder="Días de acceso (Ej: Lunes, Miércoles)" required onChange={manejarCambio} />
        </div>
        
        <div className="input-group">
          <input type="text" name="horarios" placeholder="Horario (Ej: 14:00 - 16:00)" required onChange={manejarCambio} />
        </div>

        <div className="form-buttons">
          <button type="button" onClick={onVolver} className="btn-cancel">Cancelar</button>
          <button type="submit" className="btn-submit">Enviar Solicitud</button>
        </div>

      </form>
    </div>
  )
}
