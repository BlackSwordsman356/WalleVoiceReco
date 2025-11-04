import speech_recognition as sr
import pyttsx3
import serial
import time

engine = pyttsx3.init()

# Reemplazar 'COM6' con el puerto que corresponda
try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)
    print("Conexión con Arduino establecida.")
except serial.SerialException:
    print("Error: No se pudo conectar al Arduino. Verifica el puerto COM y la conexión.")
    arduino = None

# Diccionario de comandos → números
COMANDOS = {
    "wally saluda": 1,
    "wally adelante": 2,
    "wally reversa": 3,
    "wally ojos": 4,
    "wally detener": 5
    #"derecha": 6
    #"izquierda": 7
    #"cabeza": 8
}

def listen_command():
    """Escucha por micrófono y devuelve texto."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Reconociendo...")
        query = r.recognize_google(audio, language="es-ES").lower()
        print(f"Comando detectado: {query}")
        return query
    except sr.UnknownValueError:
        print("No pude entender lo que dijiste.")
        return ""
    except sr.RequestError as e:
        print(f"Error en el servicio de Google: {e}")
        return ""

def send_command_to_arduino(command_key):
    """Enviar número correspondiente al Arduino."""
    if arduino and arduino.is_open:
        num = COMANDOS[command_key]
        arduino.write(f"{num}\n".encode())  # envía número + salto de línea
        print(f"Comando '{command_key}' (número {num}) enviado al Arduino.")
        engine.say(f"Ejecutando {command_key}")
        engine.runAndWait()
    else:
        print("El Arduino no está conectado.")
        engine.say("El Arduino no está conectado.")
        engine.runAndWait()

def main():
    if not arduino:
        return

    while True:
        command = listen_command()

        # Buscar si es uno de los comandos definidos
        for palabra in COMANDOS:
            if palabra in command:
                send_command_to_arduino(palabra)
                break

        # Comando para salir y cerrar
        if "salir" in command or "adiós" in command:
            engine.say("Hasta luego.")
            engine.runAndWait()
            if arduino and arduino.is_open:
                arduino.close()
                print("Puerto serie cerrado.")
            break  # salir del bucle → termina el programa

if __name__ == "__main__":
    main()
