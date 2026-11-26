import pygame
import random
import math
from array import array

# Audio init
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# cosmic notes
def create_note(frequency):
    sample_rate = 44100
    duration = 0.7
    samples = array("h")

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        envelope = math.exp(-4 * t)

        sound = (
            math.sin(2 * math.pi * frequency * t) * 0.65 +
            math.sin(2 * math.pi * frequency * 2 * t) * 0.20 +
            math.sin(2 * math.pi * frequency * 3 * t) * 0.10
        )

        value = int(sound * envelope * 7500)
        samples.append(max(-32768, min(32767, value)))

    return pygame.mixer.Sound(buffer=samples.tobytes())

notes = [
    create_note(523.25),  # C5
    create_note(659.25),  # E5
    create_note(783.99),  # G5
    create_note(587.33),  # D5
]

for note in notes:
    note.set_volume(0.65)

click_index = 0


WIDTH, HEIGHT = 1100, 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Return to Yourself")

clock = pygame.time.Clock()

BG = (3, 7, 20)

FONT = pygame.font.SysFont("segoeui", 92)
BODY_FONT = pygame.font.SysFont("segoeui", 27)

WANDER = 12
GATHER = 25
HOLD = 12
DISSOLVE = 15

CYCLE = WANDER + GATHER + HOLD + DISSOLVE


# Create text particle positions
def create_text_points(text, font, center, spacing=2):

    surface = font.render(text, True, (255, 255, 255))
    mask = pygame.mask.from_surface(surface)

    points = []

    ox = center[0] - surface.get_width() // 2
    oy = center[1] - surface.get_height() // 2

    for x in range(0, surface.get_width(), spacing):
        for y in range(0, surface.get_height(), spacing):

            if mask.get_at((x, y)):
                points.append((ox + x, oy + y))

    return points


targets = create_text_points(
    "RETURN TO YOURSELF",
    FONT,
    (WIDTH // 2, 275)
)


class Particle:

    def __init__(self, target):

        self.target = target

        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)

        self.vx = random.uniform(-0.7, 0.7)
        self.vy = random.uniform(-0.7, 0.7)

        self.phase = random.uniform(0, math.tau)
        self.size = random.uniform(1, 1.8)

        self.last_cycle = -1

    def update(self, elapsed, dt, mouse):

        tx, ty = self.target

        cycle_number = int(elapsed // CYCLE)
        local_time = elapsed % CYCLE

        if cycle_number != self.last_cycle:

            self.last_cycle = cycle_number

            self.vx = random.uniform(-0.8, 0.8)
            self.vy = random.uniform(-0.8, 0.8)

        if local_time < WANDER:

            # Free wandering
            self.vx += random.uniform(-0.025, 0.025)
            self.vy += random.uniform(-0.025, 0.025)

            self.vx *= 0.995
            self.vy *= 0.995

            self.x += self.vx
            self.y += self.vy

            if self.x < 0 or self.x > WIDTH:
                self.vx *= -1

            if self.y < 0 or self.y > HEIGHT:
                self.vy *= -1

        elif local_time < WANDER + GATHER:

            # Slowly form the message
            progress = (local_time - WANDER) / GATHER
            progress = progress * progress * (3 - 2 * progress)

            strength = 0.04 + progress * 0.24
            alpha = 1 - math.exp(-strength * dt)

            drift_x = math.sin(
                elapsed * 0.35 + self.phase
            ) * 0.35

            drift_y = math.cos(
                elapsed * 0.35 + self.phase
            ) * 0.35

            self.x += (tx + drift_x - self.x) * alpha
            self.y += (ty + drift_y - self.y) * alpha

        elif local_time < WANDER + GATHER + HOLD:

            # Hold the formed message
            alpha = 1 - math.exp(-1.5 * dt)

            drift_x = math.sin(
                elapsed * 0.4 + self.phase
            ) * 0.3

            drift_y = math.cos(
                elapsed * 0.4 + self.phase
            ) * 0.3

            self.x += (tx + drift_x - self.x) * alpha
            self.y += (ty + drift_y - self.y) * alpha

        else:

            # Dissolve into space
            self.vx += random.uniform(-0.025, 0.025)
            self.vy += random.uniform(-0.025, 0.025)

            self.vx *= 0.995
            self.vy *= 0.995

            self.x += self.vx
            self.y += self.vy

            if self.x < 0 or self.x > WIDTH:
                self.vx *= -1

            if self.y < 0 or self.y > HEIGHT:
                self.vy *= -1

        # Gentle mouse disturbance
        dx = self.x - mouse[0]
        dy = self.y - mouse[1]

        distance = math.hypot(dx, dy)

        if 0 < distance < 75:

            force = (75 - distance) / 75 * 0.5

            self.x += dx / distance * force
            self.y += dy / distance * force

    def draw(self, surface, elapsed):

        glow = (
            math.sin(elapsed * 0.7 + self.phase) + 1
        ) / 2

        color = (
            int(45 + glow * 45),
            int(105 + glow * 70),
            int(175 + glow * 75)
        )

        radius = max(1, int(self.size + glow * 0.5))

        pygame.draw.circle(
            surface,
            color,
            (int(self.x), int(self.y)),
            radius
        )


particles = [Particle(p) for p in targets]


# Background stars
stars = [
    (
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.uniform(0.5, 1.5)
    )
    for _ in range(160)
]


start = pygame.time.get_ticks()
running = True

while running:

    dt = clock.tick(60) / 1000
    elapsed = (pygame.time.get_ticks() - start) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Each click plays the next cosmic note
        if event.type == pygame.MOUSEBUTTONDOWN:

            notes[click_index].play()

            click_index = (click_index + 1) % len(notes)

    mouse = pygame.mouse.get_pos()
    local_time = elapsed % CYCLE

    screen.fill(BG)

    for x, y, size in stars:

        twinkle = (
            math.sin(elapsed * 0.5 + x) + 1
        ) / 2

        brightness = int(25 + twinkle * 25)

        pygame.draw.circle(
            screen,
            (
                brightness,
                brightness + 8,
                brightness + 20
            ),
            (x, y),
            max(1, int(size))
        )

    for particle in particles:

        particle.update(elapsed, dt, mouse)
        particle.draw(screen, elapsed)

    # text box
    message_start = WANDER + GATHER
    dissolve_start = WANDER + GATHER + HOLD

    if local_time > message_start:

        fade = min(
            (local_time - message_start) / 6,
            1
        )

        if local_time > dissolve_start:

            fade *= max(
                0,
                1 - (local_time - dissolve_start) / 4
            )

        fade = max(0, min(fade, 1))

        message = BODY_FONT.render(
            "You're still here; beneath all the noise...",
            True,
            (150, 185, 225)
        )

        message.set_alpha(int(255 * fade))

        rect = message.get_rect(
            center=(WIDTH // 2, 430)
        )

        screen.blit(message, rect)

    pygame.display.flip()

pygame.quit()
