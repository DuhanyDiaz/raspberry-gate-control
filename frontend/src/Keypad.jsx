import { useState } from 'react'
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
  const handleSubmit = () => {
    if (pin.length > 0) {
      alert(`Validando PIN en la nube: ${pin}`)
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