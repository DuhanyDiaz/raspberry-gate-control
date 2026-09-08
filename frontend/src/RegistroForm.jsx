import { useState, useEffect } from 'react'
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
  const enviarFormulario = async (e) => {
    e.preventDefault() // Evita que la página se recargue

    // 1. Empaquetamos los datos exactamente como los pide schemas.py en Python
    const payload = {
      nombre: datos.nombres,
      carne: datos.carne,
      dpi: datos.dpi,
      correo: datos.correo,
      dias_permitidos: datos.dias,
      // Si el alumno escribe "14:00 - 16:00", lo cortamos por el guion para separar inicio y fin
      hora_inicio: datos.horarios.split("-")[0]?.trim() || "00:00",
      hora_fin: datos.horarios.split("-")[1]?.trim() || "23:59"
    }

    try {
      // 2. Usamos fetch para conectarnos a tu servidor de FastAPI
      const respuesta = await fetch("http://127.0.0.1:8000/api/solicitudes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })

      if (respuesta.ok) {
        alert('¡Éxito! Tu solicitud ha sido registrada en la base de datos.')
        onVolver() // Regresa al teclado numérico
      } else {
        alert('Ocurrió un error al registrar la solicitud.')
      }
    } catch (error) {
      alert('Error: No se pudo conectar con el servidor de Python.')
    }
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
