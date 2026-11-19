import turtle
import math
import colorsys

screen = turtle.Screen()
screen.bgcolor("#050510")  # the void is aesthetically pleasing
screen.title("BLOOM.exe")
screen.setup(900, 900)

artist = turtle.Turtle()
artist.speed(0)
artist.hideturtle()
artist.penup()

turtle.colormode(255)

PARTICLES = 2500       # more particles 
GOLDEN_ANGLE = 137.5  
SPREAD = 5            
DOT_SIZE = 3        

# Color controls:
SATURATION = 0.9      # 0 = grayscale, 1 = violently colorful
BRIGHTNESS = 1.0        # 0 = darkness, 1 = screaming photons

for i in range(PARTICLES):

    angle = i * GOLDEN_ANGLE
    radius = SPREAD * math.sqrt(i)

    x = radius * math.cos(math.radians(angle))
    y = radius * math.sin(math.radians(angle))

    hue = 0.75 + (i / PARTICLES) * 0.15
    hue = hue % 1

    r, g, b = colorsys.hsv_to_rgb(
        hue,
        SATURATION,
        BRIGHTNESS
    )

    artist.goto(x, y)
    artist.dot(DOT_SIZE, (int(r * 255), int(g * 255), int(b * 255)))

screen.mainloop()
