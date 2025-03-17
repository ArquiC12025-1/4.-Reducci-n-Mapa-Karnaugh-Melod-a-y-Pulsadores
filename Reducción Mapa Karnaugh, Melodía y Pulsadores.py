from machine import Pin, I2C, PWM
import ssd1306
import neopixel
import time


i2c = I2C(0, scl=Pin(25), sda=Pin(33))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)


NUM_LEDS = 16
led_ring = neopixel.NeoPixel(Pin(15), NUM_LEDS)


botones = {
    "A": Pin(13, Pin.IN, Pin.PULL_UP),
    "B": Pin(12, Pin.IN, Pin.PULL_UP),
    "C": Pin(14, Pin.IN, Pin.PULL_UP),
    "D": Pin(27, Pin.IN, Pin.PULL_UP)
}

buzzer = PWM(Pin(32))

notes = {
    "C4": 261, "C#4": 277, "D4": 294, "D#4": 311, "E4": 330,
    "F4": 349, "F#4": 370, "G4": 392, "G#4": 415, "A4": 440,
    "A#4": 466, "B4": 494, "C5": 523, "C#5": 554, "D5": 587,
    "D#5": 622, "E5": 659, "F5": 698, "F#5": 740, "G5": 784,
    "G#5": 831, "A5": 880, "A#5": 932, "B5": 988
}

# Secuencia corregida de la melodía (Mario Game Over)
game_over_melody = [
    ("C5", 200), ("C#5", 200), ("D5", 200),(None,200),
    ("B4", 200), ("F5", 100), ("F5", 100), ("F5", 100),
    ("E5", 100), ("D5", 100), ("E5", 200), ("E5", 200),
    ("E5", 200), ("C5", 400)
]



button_sound = [
    (1000, 100), (800, 100), (600, 100)
]


def reproducir_melodia(melody):
    for note, duration in melody:
        if note is not None and note in notes:
            buzzer.freq(notes[note])  # Configura la frecuencia
            buzzer.duty(512)  # Activa el buzzer
        else:
            buzzer.duty(0)  # Silencio

        time.sleep_ms(duration)  # Duración de la nota o el silencio
        buzzer.duty(0)  # Apaga el buzzer entre notas
        time.sleep_ms(50)  # Pequeña pausa entre notas


def evaluar_expresiones():
    """Evalúa las fórmulas lógicas y verifica si todas se cumplen."""
    a, b, c, d = [not botones[k].value() for k in "ABCD"]
    
    formulas = [
        ((not d and not c and b and a) or (not d and c and not b and a) or 
         (not d and c and b and a) or (d and not c and b and a) or 
         (d and c and not b and not a) or (d and c and not b and a) or 
         (d and c and b and not a) or (d and c and b and a)),
        
        ((c and not d and a and not b) or (c and d) or (a and b)),

        ((a and c) or (c and d) or (a and b))
    ]
    
    return all(formulas), formulas

def actualizar_leds(formulas):
    """Enciende los LEDs según qué fórmula se cumpla."""
    led_ring.fill((0, 0, 0))  
    
    colores = [(128, 0, 128), (255, 255, 0), (255, 105, 180)]
    
    for i, formula in enumerate(formulas):
        if formula:
            for j in range(3):
                led_ring[i * 3 + j] = colores[i]
    
    if all(formulas):
        for i in range(9, NUM_LEDS):
            led_ring[i] = (255, 255, 255)  

    led_ring.write()

def mostrar_oled(formulas):
    """Muestra en la OLED el estado de las fórmulas."""
    oled.fill(0)
    oled.text("Expresion Logica", 10, 0)

    botones_presionados = "Btns: " + " ".join(k for k, v in botones.items() if not v.value())
    oled.text(botones_presionados if botones_presionados != "Btns: " else "Btns: Ninguno", 10, 10)

    estado = "NINGUNA"
    if all(formulas):
        estado = "TODAS CUMPLIDAS"
    else:
        colores = ["F1: Morado", "F2: Amarillo", "F3: Rosado"]
        estado = " ".join([colores[i] for i in range(3) if formulas[i]])

    oled.text(estado, 10, 20)
    oled.show()


estado_botones = {k: botones[k].value() for k in botones}

while True:
    todas_cumplidas, formulas = evaluar_expresiones()
    actualizar_leds(formulas)
    mostrar_oled(formulas)

   
    if todas_cumplidas:
        reproducir_melodia(game_over_melody)

  
    for k, pin in botones.items():
        if not pin.value() and estado_botones[k]:  
            reproducir_melodia(button_sound)
    
    estado_botones = {k: botones[k].value() for k in botones}

    time.sleep(0.1)