import { useState, useEffect } from 'react'
import Swal from 'sweetalert2'
import ReactSlider from 'react-slider'
import DatePicker from 'react-datepicker'
import "react-datepicker/dist/react-datepicker.css"
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
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

  // Estado para el rango de fechas
  const [dateRange, setDateRange] = useState([null, null])
  const [startDate, endDate] = dateRange

  // Funciones para formatear horas
  const format12h = (hour) => {
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const h = hour % 12 || 12;
    return `${h.toString().padStart(2, '0')}:00 ${ampm}`;
  };

  const format24h = (hour) => {
    return `${hour.toString().padStart(2, '0')}:00`;
  };

  // Función genérica para guardar lo que se escribe en el estado
  const manejarCambio = (e) => {
    setDatos({
      ...datos,
      [e.target.name]: e.target.value
    })
  }

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

    if (!startDate) {
      Swal.fire({
        icon: 'error',
        title: 'Faltan fechas',
        text: 'Por favor, selecciona un rango de fechas de acceso.',
        confirmButtonColor: '#ff6b6b'
      });
      return;
    }

    let diasTexto = '';
    if (startDate && endDate) {
      diasTexto = `${format(startDate, 'dd MMM yyyy', { locale: es })} - ${format(endDate, 'dd MMM yyyy', { locale: es })}`;
    } else if (startDate) {
      diasTexto = format(startDate, 'dd MMM yyyy', { locale: es });
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

        <div className="input-group custom-datepicker-container">
          <label className="chips-label">Días de acceso (Selecciona un rango de fechas)</label>
          <DatePicker
            selectsRange={true}
            startDate={startDate}
            endDate={endDate}
            onChange={(update) => setDateRange(update)}
            monthsShown={2}
            locale={es}
            dateFormat="dd MMM yyyy"
            placeholderText="Selecciona fechas..."
            className="date-picker-input"
            isClearable={true}
            popperPlacement="bottom-start"
            popperModifiers={[
              {
                name: "preventOverflow",
                options: {
                  boundary: "window",
                },
              },
            ]}
          />
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
