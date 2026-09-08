import { useState } from 'react'
import Swal from 'sweetalert2'
import './Keypad.css'

export default function Keypad() {
  const [pin, setPin] = useState('')

  // Función que se ejecuta al presionar un número
  const handleKeyPress = (num) => {
    // Asumimos un PIN de 4 a 6 dígitos. Lo limitamos a 4 para este ejemplo.
    if (pin.length < 4) {
      setPin(prev => prev + num)
    }
  }

  // Borrar un número a la vez (Retroceso)
  const handleBackspace = () => {
    setPin(prev => prev.slice(0, -1))
  }

  // Enviar el PIN
  const handleSubmit = async () => {
    if (pin.length > 0) {
      Swal.fire({
        title: 'Validando...',
        text: 'Conectando con el servidor',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading()
        }
      })

      try {
        const respuesta = await fetch("http://127.0.0.1:8000/api/accesos/validar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pin: pin })
        })

        if (respuesta.ok) {
          const datos = await respuesta.json()
          Swal.fire({
            icon: 'success',
            title: '¡Acceso Concedido!',
            text: `Bienvenido(a), ${datos.nombre}`,
            confirmButtonColor: '#2a7a43'
          })
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Acceso Denegado',
            text: 'PIN incorrecto o inactivo.',
            confirmButtonColor: '#ff6b6b'
          })
        }
      } catch (error) {
        Swal.fire('Error', 'No se pudo conectar con el servidor', 'error')
      }

      setPin('') // Limpiamos después de enviar
    }
  }

  return (
    <div className="keypad-container">
      {/* Pantalla del PIN */}
      <div className="pin-display">
        {/* Mostramos 4 puntitos, y los rellenamos según escriba el usuario */}
        {pin.padEnd(4, '•').split('').map((char, index) => (
          <span key={index} className={char !== '•' ? 'filled' : ''}>
            {char !== '•' ? '*' : '•'}
            {/* Usamos '*' en lugar de 'char' para ocultar la contraseña real */}
          </span>
        ))}
      </div>

      {/* Botones del teclado */}
      <div className="keypad-grid">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
          <button
            key={num}
            onClick={() => handleKeyPress(num.toString())}
            className="key-btn"
          >
            {num}
          </button>
        ))}

        {/* Fila Inferior */}
        <button onClick={handleBackspace} className="key-btn action-btn clear-btn">◀︎</button>
        <button onClick={() => handleKeyPress('0')} className="key-btn">0</button>
        <button onClick={handleSubmit} className="key-btn action-btn submit-btn">✔</button>
      </div>
    </div>
  )
}