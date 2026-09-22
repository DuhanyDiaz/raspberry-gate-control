import { useState, useEffect } from 'react'
import Swal from 'sweetalert2'
import ReactSlider from 'react-slider'
import './RegistroForm.css'

export default function RegistroForm({ onVolver }) {
  // Estado para guardar todo lo que el usuario escribe
  const [datos, setDatos] = useState({
    nombres: '',
    carne: '',
    dpi: '',
    correo: ''
  })

  // Estado para el slider de doble pulgar (de 14:00 a 16:00 por defecto)
  const [horario, setHorario] = useState([14, 16])

  // Funciones para formatear horas
  const format12h = (hour) => {
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const h = hour % 12 || 12;
    return `${h.toString().padStart(2, '0')}:00 ${ampm}`;
  };

  const format24h = (hour) => {
    return `${hour.toString().padStart(2, '0')}:00`;
  };

  const DIAS_SEMANA = [
    { id: 1, nombre: 'Lunes', corto: 'Lun' },
    { id: 2, nombre: 'Martes', corto: 'Mar' },
    { id: 3, nombre: 'Miércoles', corto: 'Mié' },
    { id: 4, nombre: 'Jueves', corto: 'Jue' },
    { id: 5, nombre: 'Viernes', corto: 'Vie' },
    { id: 6, nombre: 'Sábado', corto: 'Sáb' }
  ];
  const [diasSeleccionados, setDiasSeleccionados] = useState([])

  // Función genérica para guardar lo que se escribe en el estado
  const manejarCambio = (e) => {
    setDatos({
      ...datos,
      [e.target.name]: e.target.value
    })
  }

  const toggleDia = (diaId) => {
    setDiasSeleccionados(prev => {
      if (prev.includes(diaId)) {
        return prev.filter(id => id !== diaId);
      } else {
        return [...prev, diaId].sort();
      }
    });
  };

  const diasTexto = diasSeleccionados.map(id => DIAS_SEMANA.find(d => d.id === id).nombre).join(', ');

  // Función cuando le dan "Enviar Solicitud"
  const enviarFormulario = async (e) => {
    e.preventDefault() // Evita que la página se recargue

    // --- VALIDACIÓN DE SEGURIDAD ---
    const regexLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
    if (!regexLetras.test(datos.nombres)) {
      Swal.fire({
        icon: 'error',
        title: 'Nombre Inválido',
        text: 'El nombre solo puede contener letras y espacios. No se permiten números ni símbolos.',
        confirmButtonColor: '#ff6b6b'
      });
      return; // Detiene la ejecución
    }

    const regexCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!regexCorreo.test(datos.correo)) {
      Swal.fire({
        icon: 'error',
        title: 'Correo Inválido',
        text: 'Por favor, ingresa un correo electrónico real (ejemplo: alumno@gmail.com).',
        confirmButtonColor: '#ff6b6b'
      });
      return;
    }

    const regexCarne = /^\d{9}$/;
    if (!regexCarne.test(datos.carne)) {
      Swal.fire({
        icon: 'error',
        title: 'Carné Inválido',
        text: 'El carné debe contener exactamente 9 números sin guiones.',
        confirmButtonColor: '#ff6b6b'
      });
      return;
    }

    const regexDPI = /^\d{13}$/;
    if (!regexDPI.test(datos.dpi)) {
      Swal.fire({
        icon: 'error',
        title: 'DPI Inválido',
        text: 'El DPI debe contener exactamente 13 números sin espacios ni guiones.',
        confirmButtonColor: '#ff6b6b'
      });
      return;
    }

    if (diasSeleccionados.length === 0) {
      Swal.fire({
        icon: 'error',
        title: 'Faltan días',
        text: 'Por favor, selecciona al menos un día de acceso usando las etiquetas.',
        confirmButtonColor: '#ff6b6b'
      });
      return;
    }

    // 1. Empaquetamos los datos exactamente como los pide schemas.py en Python
    const payload = {
      nombre: datos.nombres,
      carne: datos.carne,
      dpi: datos.dpi,
      correo: datos.correo,
      dias_permitidos: diasTexto,
      hora_inicio: format24h(horario[0]),
      hora_fin: format24h(horario[1])
    }

    try {
      // 2. Usamos fetch para conectarnos a tu servidor de FastAPI
      const respuesta = await fetch("http://127.0.0.1:8000/api/solicitudes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })

      if (respuesta.ok) {
        Swal.fire({
          icon: 'success',
          title: '¡Enviado!',
          text: 'Tu solicitud ha sido enviada al administrador. Recibirás un correo cuando sea aprobada.',
          confirmButtonColor: '#2a7a43'
        })
        onVolver() // Regresa al teclado numérico
      } else {
        const errorData = await respuesta.json()
        Swal.fire('Error', errorData.detail || 'Ocurrió un error al registrar la solicitud.', 'error')
      }
    } catch (error) {
      Swal.fire('Error', 'No se pudo conectar con el servidor de Python.', 'error')
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
          <label className="chips-label">Días de acceso solicitados</label>
          <div className="chips-container">
            {DIAS_SEMANA.map(dia => (
              <button
                type="button"
                key={dia.id}
                className={`chip ${diasSeleccionados.includes(dia.id) ? 'selected' : ''}`}
                onClick={() => toggleDia(dia.id)}
              >
                {diasSeleccionados.includes(dia.id) && <span className="check-icon">✓</span>}
                {dia.corto}
              </button>
            ))}
          </div>
          {diasSeleccionados.length > 0 && (
            <div className="dias-seleccionados-texto">
              Seleccionados: {diasTexto}
            </div>
          )}
        </div>

        <div className="input-group">
          <label className="chips-label">Horario de acceso</label>
          <div className="slider-container">
            <div className="slider-labels-top">
              <span>06:00 AM</span>
              <span>08:00 PM</span>
            </div>

            <ReactSlider
              className="horizontal-slider"
              thumbClassName="slider-thumb"
              trackClassName="slider-track"
              min={6}
              max={20}
              value={horario}
              onChange={(val) => setHorario(val)}
              minDistance={1}
              renderThumb={(props, state) => (
                <div {...props}>
                  <div className="thumb-label">{format12h(state.valueNow)}</div>
                </div>
              )}
            />
          </div>

          <div className="rango-seleccionado-caja">
            <span></span> Rango seleccionado: {format12h(horario[0])} - {format12h(horario[1])}
          </div>
        </div>

        <div className="form-buttons">
          <button type="button" onClick={onVolver} className="btn-cancel">Cancelar</button>
          <button type="submit" className="btn-submit">Enviar Solicitud</button>
        </div>

      </form>
    </div>
  )
}
