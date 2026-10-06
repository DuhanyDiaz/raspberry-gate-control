import { useState, useEffect } from 'react'
import Swal from 'sweetalert2'
import ReactSlider from 'react-slider'
import DatePicker from 'react-datepicker'
import "react-datepicker/dist/react-datepicker.css"
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import './RegistroForm.css'
import { API_BASE_URL } from './apiConfig'

export default function RegistroForm({ onVolver }) {
  // Estado para guardar todo lo que el usuario escribe
  const [datos, setDatos] = useState({
    nombres: '',
    carne: '',
    dpi: '',
    correo: '',
    rol: 'Estudiante',
    usuario: '',
    password: ''
  })

  // Estado para el slider de doble pulgar (de 14:00 a 16:00 por defecto)
  const [horario, setHorario] = useState([14, 16])

  // Estado para el rango de fechas
  const [dateRange, setDateRange] = useState([null, null])
  const [startDate, endDate] = dateRange

  // --- NUEVO ESTADO PARA EL WIZARD ---
  const [pasoActual, setPasoActual] = useState(1) 

  const format12h = (hour) => {
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const h = hour % 12 || 12;
    return `${h.toString().padStart(2, '0')}:00 ${ampm}`;
  };

  const format24h = (hour) => {
    return `${hour.toString().padStart(2, '0')}:00`;
  };

  const manejarCambio = (e) => {
    setDatos({
      ...datos,
      [e.target.name]: e.target.value
    })
  }

  // --- VALIDACIÓN POR PASOS ---
  const avanzarPaso = () => {
    if (pasoActual === 1) {
      const regexLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
      if (!datos.nombres || !regexLetras.test(datos.nombres)) {
        return Swal.fire({ icon: 'warning', text: 'El nombre solo puede contener letras y espacios.' });
      }
      const regexDPI = /^\d{13}$/;
      if (!datos.dpi || !regexDPI.test(datos.dpi)) {
        return Swal.fire({ icon: 'warning', text: 'El DPI debe tener exactamente 13 números.' });
      }
      const regexCarne = /^\d{9}$/;
      if (!datos.carne || !regexCarne.test(datos.carne)) {
        return Swal.fire({ icon: 'warning', text: 'El carné debe tener exactamente 9 números.' });
      }
    } else if (pasoActual === 2) {
      const regexCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!datos.correo || !regexCorreo.test(datos.correo)) {
        return Swal.fire({ icon: 'warning', text: 'Por favor, ingresa un correo válido.' });
      }
      const regexUsuario = /^[a-zA-Z0-9]+$/;
      if (!datos.usuario || !regexUsuario.test(datos.usuario)) {
        return Swal.fire({ icon: 'warning', text: 'El usuario solo puede contener letras y números.' });
      }
      if (!datos.password || datos.password.length < 4) {
        return Swal.fire({ icon: 'warning', text: 'La contraseña debe tener al menos 4 caracteres.' });
      }
    }
    // Si pasa las validaciones, va al siguiente paso
    setPasoActual(pasoActual + 1);
  };

  const retrocederPaso = () => {
    setPasoActual(pasoActual - 1);
  };

  const enviarFormulario = async (e) => {
    e.preventDefault() 

    if (!startDate) {
      return Swal.fire({ icon: 'warning', text: 'Por favor, selecciona un rango de fechas.' });
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
      rol: datos.rol,
      usuario: datos.usuario,
      password: datos.password,
      dias_permitidos: diasTexto,
      hora_inicio: format24h(horario[0]),
      hora_fin: format24h(horario[1]),
      fecha_expiracion: endDate ? format(endDate, 'yyyy-MM-dd') : format(startDate, 'yyyy-MM-dd')
    }

    try {
      // 2. Usamos fetch para conectarnos a tu servidor de FastAPI
      const respuesta = await fetch(`${API_BASE_URL}/api/solicitudes`, {
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
      
      {/* Indicador de progreso del Wizard */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '20px' }}>
        <div style={{ width: '32px', height: '6px', borderRadius: '3px', background: pasoActual >= 1 ? '#ffffff' : 'rgba(255,255,255,0.3)', boxShadow: pasoActual >= 1 ? '0 0 6px rgba(255,255,255,0.5)' : 'none', transition: 'all 0.3s ease' }}></div>
        <div style={{ width: '32px', height: '6px', borderRadius: '3px', background: pasoActual >= 2 ? '#ffffff' : 'rgba(255,255,255,0.3)', boxShadow: pasoActual >= 2 ? '0 0 6px rgba(255,255,255,0.5)' : 'none', transition: 'all 0.3s ease' }}></div>
        <div style={{ width: '32px', height: '6px', borderRadius: '3px', background: pasoActual >= 3 ? '#ffffff' : 'rgba(255,255,255,0.3)', boxShadow: pasoActual >= 3 ? '0 0 6px rgba(255,255,255,0.5)' : 'none', transition: 'all 0.3s ease' }}></div>
      </div>

      <form onSubmit={enviarFormulario}>

        {/* PASO 1: Identidad */}
        {pasoActual === 1 && (
          <div style={{ animation: 'fadeIn 0.3s' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '15px', color: '#ffffff', fontWeight: '600', letterSpacing: '0.5px' }}>Paso 1: Identidad</h3>
            <div className="input-group">
              <label className="chips-label">Rol Institucional</label>
              <div className="input-group">
                <select 
                  name="rol" 
                  className="rol-select"
                  value={datos.rol} 
                  onChange={manejarCambio}
                >
                  <option value="Estudiante">Estudiante</option>
                  <option value="Auxiliar">Auxiliar</option>
                  <option value="Profesor">Profesor</option>
                  <option value="Dirección">Dirección</option>
                </select>
              </div>
            </div>

            <div className="input-group">
              <input type="text" name="nombres" placeholder="Nombres y Apellidos Completos" value={datos.nombres} onChange={manejarCambio} />
            </div>

            <div className="row-group">
              <div className="input-group">
                <input type="number" name="dpi" placeholder="DPI (13 dígitos)" value={datos.dpi} onChange={manejarCambio} />
              </div>
              <div className="input-group">
                <input type="number" name="carne" placeholder="Carné (9 dígitos)" value={datos.carne} onChange={manejarCambio} />
              </div>
            </div>
          </div>
        )}

        {/* PASO 2: Credenciales */}
        {pasoActual === 2 && (
          <div style={{ animation: 'fadeIn 0.3s' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '15px', color: '#ffffff', fontWeight: '600', letterSpacing: '0.5px' }}>Paso 2: Cuenta de Sistema</h3>
            
            <div className="input-group">
              <input type="email" name="correo" placeholder="Correo Electrónico" value={datos.correo} onChange={manejarCambio} />
            </div>

            <div className="row-group">
              <div className="input-group">
                <input
                  type="text"
                  name="usuario"
                  placeholder="Usuario (Letras y Números)"
                  value={datos.usuario}
                  onChange={manejarCambio}
                />
              </div>
              <div className="input-group">
                <input
                  type="password"
                  name="password"
                  placeholder="Contraseña"
                  value={datos.password}
                  onChange={manejarCambio}
                />
              </div>
            </div>
          </div>
        )}

        {/* PASO 3: Fechas y Horarios */}
        {pasoActual === 3 && (
          <div style={{ animation: 'fadeIn 0.3s' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '15px', color: '#ffffff', fontWeight: '600', letterSpacing: '0.5px' }}>Paso 3: Permisos de Acceso</h3>
            
            <div className="input-group custom-datepicker-container">
              <label className="chips-label">Días de acceso (Selecciona un rango)</label>
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
                  { name: "preventOverflow", options: { boundary: "window" } },
                ]}
              />
            </div>

            <div className="input-group">
              <label className="chips-label">Horario de acceso</label>
              <div className="slider-container">
                <div className="slider-labels-top">
                  <span>08:00 AM</span>
                  <span>07:00 PM</span>
                </div>

                <ReactSlider
                  className="horizontal-slider"
                  thumbClassName="slider-thumb"
                  trackClassName="slider-track"
                  min={8}
                  max={19}
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
            </div>
          </div>
        )}

        <div className="form-buttons">
          {pasoActual === 1 ? (
            <button type="button" onClick={onVolver} className="btn-cancel">Cancelar</button>
          ) : (
            <button type="button" onClick={retrocederPaso} className="btn-cancel">Atrás</button>
          )}

          {pasoActual < 3 ? (
            <button type="button" onClick={avanzarPaso} className="btn-submit">Siguiente</button>
          ) : (
            <button type="submit" className="btn-submit">Enviar Solicitud</button>
          )}
        </div>

      </form>
    </div>
  )
}
