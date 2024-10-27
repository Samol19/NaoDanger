import customtkinter
import subprocess
import os
import time
from PIL import Image, ImageTk, ImageSequence  # Para manejar el GIF

procesos = []

# Función para ejecutar los archivos python
def ejecutar_scripts():
    ruta_actual = os.getcwd()  # Obtiene el directorio actual donde se está ejecutando el script
    script1 = os.path.join(ruta_actual, 'pose_detection.py')
    script2 = os.path.join(ruta_actual, 'response_detection.py')
    script3 = os.path.join(ruta_actual, 'NaoDanger_detection.py')
    
    ip = ip_entry.get()
    port = port_entry.get()

    subprocess.Popen(['py', '-3', script2], creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(3)
    subprocess.Popen(['py', '-3', script1], creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(9)
    subprocess.Popen(['py', '-2', script3, ip, port])

# Función para animar el GIF
def actualizar_gif(ind):
    # Actualizar el frame del GIF
    frame = frames[ind]
    image_label.configure(image=frame)
    delay = gif.info['duration']  # Obtener la duración de cada frame en ms
    root.after(delay, actualizar_gif, (ind + 1) % len(frames))  # Cambiar según la duración del frame

# Configuración de CustomTkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Ventana principal
root = customtkinter.CTk()
root.geometry("700x400")
root.title("NAO Danger")
root.grid_columnconfigure((0, 1, 2), weight=1)

# Título principal
titulo = customtkinter.CTkLabel(root, text="Nao DANGER - Conectar a NAO", font=("Cascadia Code SemiBold", 24))
titulo.grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

# Entrada de IP
ip_label = customtkinter.CTkLabel(root, text="IP:", font=("Cascadia Code SemiBold", 16))
ip_label.grid(row=1, column=0, pady=10, padx=10, sticky="e")
ip_entry = customtkinter.CTkEntry(root, width=200)
ip_entry.grid(row=1, column=1, pady=10, padx=10, sticky="w")

# Entrada de Puerto
port_label = customtkinter.CTkLabel(root, text="Port:", font=("Cascadia Code SemiBold", 16))
port_label.grid(row=2, column=0, pady=10, padx=10, sticky="e")
port_entry = customtkinter.CTkEntry(root, width=200)
port_entry.grid(row=2, column=1, pady=10, padx=10, sticky="w")

# Cargar el GIF animado
gif_path = os.path.join(os.getcwd(), "secure.gif")
gif = Image.open(gif_path)

# Obtener las dimensiones originales del GIF
original_width, original_height = gif.size
new_size = (original_width // 2, original_height // 2)  # Tamaño reducido a la mitad

# Crear una lista con todos los frames del GIF, redimensionados y asegurando que estén en RGBA para preservar la transparencia
frames = [ImageTk.PhotoImage(img.convert('RGBA').resize(new_size, Image.LANCZOS)) for img in ImageSequence.Iterator(gif)]

# Mostrar la animación
image_label = customtkinter.CTkLabel(root, text="")  # Asegurarse de que el texto está vacío
image_label.grid(row=1, column=2, rowspan=2, padx=50, pady=10, sticky="w")

# Iniciar la animación del GIF
root.after(0, actualizar_gif, 0)

# Botón para enviar los datos
submit_button = customtkinter.CTkButton(root, text="Conectar", command=ejecutar_scripts, width=120)
submit_button.grid(row=3, column=0, columnspan=2, pady=20)

# Loop principal de la interfazc
root.mainloop()
