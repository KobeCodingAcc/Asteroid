import pygame
import random
import math
import asyncio


pygame.init()


# =========================================================
# GAME CONSTANTS
# =========================================================


WIDTH = 800
HEIGHT = 600
FPS = 60


NUM_ASTEROIDS = 5
ROTATION_SPEED = 3


THRUST = 0.15
DRAG = 0.99
MAX_SPEED = 7


MISSILE_SPEED = 8


# AI SETTINGS
AI_THRUST = 0.08
AI_DRAG = 0.99
AI_MAX_SPEED = 4
AI_DETECTION_RADIUS = 220
AI_FOV = 90
AI_ROTATION_SPEED = 2


# COLORS
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
GREEN = (80, 255, 150)
YELLOW = (255, 230, 80)
RED = (255, 80, 80)
BLUE = (80, 180, 255)
ORANGE = (255, 140, 50)
PURPLE = (200, 80, 255)


# =========================================================
# PYGAME SETUP
# =========================================================


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)




# =========================================================
# SPACESHIP CLASS
# =========================================================


class Spaceship:


   def __init__(self, x, y):
       self.position = pygame.Vector2(x, y)
       self.velocity = pygame.Vector2(0, 0)
       self.acceleration = pygame.Vector2(0, 0)


       self.angle = 90
       self.radius = 18
       self.is_thrusting = False


   def get_forward_vector(self):
       radians = math.radians(self.angle)


       return pygame.Vector2(
           math.cos(radians),
           -math.sin(radians)
       )


   def update(self):
       keys = pygame.key.get_pressed()


       # Rotation
       if keys[pygame.K_LEFT] or keys[pygame.K_a]:
           self.angle += ROTATION_SPEED


       if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
           self.angle -= ROTATION_SPEED


       forward = self.get_forward_vector()


       # Reset acceleration
       self.acceleration = pygame.Vector2(0, 0)
       self.is_thrusting = False


       # Thrust
       if keys[pygame.K_UP] or keys[pygame.K_w]:
           self.acceleration = forward * THRUST
           self.is_thrusting = True


       # Physics
       self.velocity += self.acceleration
       self.velocity *= DRAG


       if self.velocity.length() > MAX_SPEED:
           self.velocity.scale_to_length(MAX_SPEED)


       self.position += self.velocity
      
       # Screen wrapping
       if self.position.x > WIDTH:
           self.position.x = 0
       if self.position.x < 0:
           self.position.x = WIDTH
       if self.position.y > HEIGHT:
           self.position.y = 0
       if self.position.y < 0:
           self.position.y = HEIGHT


   def draw(self):
       forward = self.get_forward_vector()


       left = forward.rotate(140)
       right = forward.rotate(-140)


       front = self.position + forward * 22
       back_left = self.position + left * 17
       back_right = self.position + right * 17


       pygame.draw.polygon(
           screen,
           GREEN,
           [front, back_left, back_right],
           2
       )


       pygame.draw.circle(
           screen,
           GREEN,
           (int(self.position.x), int(self.position.y)),
           3
       )


       if self.is_thrusting:
           flame_position = self.position - forward * 20


           pygame.draw.circle(
               screen,
               ORANGE,
               (int(flame_position.x),
                int(flame_position.y)),
               5
           )


   def draw_forward_vector(self):
       end_point = (
           self.position
           + self.get_forward_vector() * 60
       )


       pygame.draw.line(
           screen, RED, self.position, end_point, 2
       )


   def draw_velocity_vector(self):
       if self.velocity.length() > 0.1:
           end_point = self.position + self.velocity * 10


           pygame.draw.line(
               screen, BLUE, self.position, end_point, 3
           )




# =========================================================
# AI ENEMY CLASS
# =========================================================


class AIEnemy:


   def __init__(self, x, y):
       self.position = pygame.Vector2(x, y)
       self.velocity = pygame.Vector2(0, 0)
       self.acceleration = pygame.Vector2(0, 0)


       self.angle = 0


       self.detection_radius = AI_DETECTION_RADIUS
       self.fov = AI_FOV


       self.chasing = False


   def get_forward_vector(self):
       radians = math.radians(self.angle)


       return pygame.Vector2(
           math.cos(radians),
           -math.sin(radians)
       )


   def can_see_player(self, player):
  
       distance = self.position.distance_to(
           player.position
       )


      
       if distance > self.detection_radius:
           return False


       forward = self.get_forward_vector()
       direction_to_player = (player.position - self.position).normalize()


       dot = forward.dot(direction_to_player)


       threshold = math.cos(
           math.radians(self.fov / 2)
       )


       return dot >= threshold


   def update(self, player):
       self.acceleration = pygame.Vector2(0, 0)


       distance = self.position.distance_to(
           player.position
       )


       if not self.chasing:
           if self.can_see_player(player):
               self.chasing = True


       if distance > self.detection_radius * 1.3:
           self.chasing = False


       if self.chasing:
           to_player = player.position - self.position


          
           target_angle = math.degrees(
               math.atan2(-to_player.y, to_player.x)
           )


           difference = (
               (target_angle - self.angle + 180) % 360
           ) - 180


      
           if difference > AI_ROTATION_SPEED:
               self.angle += AI_ROTATION_SPEED


           elif difference < -AI_ROTATION_SPEED:
               self.angle -= AI_ROTATION_SPEED


           else:
               self.angle = target_angle


         
           forward = self.get_forward_vector()
           self.acceleration = forward * AI_THRUST


   
       self.velocity += self.acceleration
       self.velocity *= AI_DRAG


       if self.velocity.length() > AI_MAX_SPEED:
           self.velocity.scale_to_length(AI_MAX_SPEED)


       self.position += self.velocity


       if self.position.x > WIDTH:
           self.position.x = 0
       if self.position.x < 0:
           self.position.x = WIDTH
       if self.position.y > HEIGHT:
           self.position.y = 0
       if self.position.y < 0:
           self.position.y = HEIGHT


   def draw(self):
       forward = self.get_forward_vector()


       front = self.position + forward * 20
       left = self.position + forward.rotate(140) * 15
       right = self.position + forward.rotate(-140) * 15


      
       pygame.draw.polygon(
           screen,
           PURPLE,
           [front, left, right],
           2
       )


       pygame.draw.circle(
           screen,
           YELLOW,
           (int(self.position.x), int(self.position.y)),
           self.detection_radius,
           1
       )


       for offset in (-self.fov / 2, self.fov / 2):
           boundary = forward.rotate(offset)


           endpoint = (
               self.position
               + boundary * self.detection_radius
           )


           pygame.draw.line(
               screen,
               YELLOW,
               self.position,
               endpoint,
               1
           )


      




# =========================================================
# ASTEROID CLASS
# =========================================================


class Asteroid:


   def __init__(self):
       self.radius = random.randint(18, 35)


       self.position = pygame.Vector2(
           random.randint(self.radius, WIDTH - self.radius),
           random.randint(self.radius, HEIGHT - self.radius)
       )


       angle = random.uniform(0, 2 * math.pi)
       speed = random.uniform(1.0, 2.5)


       self.velocity = pygame.Vector2(
           math.cos(angle),
           math.sin(angle)
       ) * speed


   def update(self):
       self.position += self.velocity


       if self.position.x > WIDTH + self.radius:
           self.position.x = -self.radius


       if self.position.x < -self.radius:
           self.position.x = WIDTH + self.radius


       if self.position.y > HEIGHT + self.radius:
           self.position.y = -self.radius


       if self.position.y < -self.radius:
           self.position.y = HEIGHT + self.radius


   def draw(self):
       pygame.draw.circle(
           screen,
           GRAY,
           (int(self.position.x), int(self.position.y)),
           self.radius,
           2
       )




# =========================================================
# MISSILE CLASS
# =========================================================


class Missile:


   def __init__(self, start_position, direction):
       self.position = pygame.Vector2(start_position)
       self.radius = 4
       self.velocity = direction * MISSILE_SPEED


   def update(self):
       self.position += self.velocity


   def draw(self):
       pygame.draw.circle(
           screen,
           YELLOW,
           (int(self.position.x), int(self.position.y)),
           self.radius
       )


   def is_off_screen(self):
       return (
           self.position.x < 0
           or self.position.x > WIDTH
           or self.position.y < 0
           or self.position.y > HEIGHT
       )




# =========================================================
# COLLISION DETECTION
# =========================================================


def missile_hits_asteroid(missile, asteroid):
   distance = missile.position.distance_to(
       asteroid.position
   )


   return distance < missile.radius + asteroid.radius




# =========================================================
# CREATE OBJECTS
# =========================================================


player = Spaceship(WIDTH / 2, HEIGHT / 2)


# AI starts at this position
enemy = AIEnemy(150, 150)


asteroids = [
 
]
for i in range(NUM_ASTEROIDS):
   asteroids.append(
       Asteroid()
   )


missiles = []
score = 0




# =========================================================
# MAIN GAME LOOP
# =========================================================
async def main():
    global missiles, score, asteroids, running
    running = True


    while running:


        clock.tick(FPS)


        # -----------------------------------------------------
        # 1. EVENTS
        # -----------------------------------------------------


        for event in pygame.event.get():


            if event.type == pygame.QUIT:
                running = False


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:


                    forward = player.get_forward_vector()


                    missile_start = (
                        player.position + forward * 24
                    )


                    missiles.append(
                        Missile(missile_start, forward)
                    )


        # -----------------------------------------------------
        # 2. UPDATE PLAYER AND AI
        # -----------------------------------------------------


        player.update()
        enemy.update(player)


        # -----------------------------------------------------
        # 3. UPDATE ASTEROIDS
        # -----------------------------------------------------


        for asteroid in asteroids:
            asteroid.update()


        # -----------------------------------------------------
        # 4. UPDATE MISSILES
        # -----------------------------------------------------


        for missile in missiles:
            missile.update()


        missiles = [
            missile for missile in missiles
            if not missile.is_off_screen()
        ]


        # -----------------------------------------------------
        # 5. MISSILE / ASTEROID COLLISIONS
        # -----------------------------------------------------


        for missile in missiles[:]:
            for asteroid in asteroids[:]:


                if missile_hits_asteroid(missile, asteroid):


                    missiles.remove(missile)
                    asteroids.remove(asteroid)


                    asteroids.append(Asteroid())
                    score += 1


                    break


        # -----------------------------------------------------
        # 6. DRAW
        # -----------------------------------------------------


        screen.fill(BLACK)


        # Draw AI
        enemy.draw()


        # Draw asteroids
        for asteroid in asteroids:
            asteroid.draw()


        # Draw missiles
        for missile in missiles:
            missile.draw()


        # Draw player vectors and ship
        player.draw_forward_vector()
        player.draw_velocity_vector()
        player.draw()


            # =====================================================
        # 8. DISPLAY INFORMATION
        # =====================================================


        forward = (
            player.get_forward_vector()
        )


        speed = (
            player.velocity.length()
        )




        # -----------------------------------------------------
        # Controls
        # -----------------------------------------------------


        controls_text = font.render(
            "LEFT/RIGHT: Rotate   UP: Thrust   SPACE: Fire",
            True,
            WHITE
        )


        screen.blit(
            controls_text,
            (20, 15)
        )




        # -----------------------------------------------------
        # Angle
        # -----------------------------------------------------


        angle_text = font.render(
            f"Angle: {player.angle % 360:.0f} degrees",
            True,
            WHITE
        )


        screen.blit(
            angle_text,
            (20, 45)
        )




        # -----------------------------------------------------
        # Forward Vector
        # -----------------------------------------------------


        forward_text = font.render(
            f"Forward: ({forward.x:.2f}, {forward.y:.2f})",
            True,
            RED
        )


        screen.blit(
            forward_text,
            (20, 75)
        )




        # -----------------------------------------------------
        # Velocity Vector
        # -----------------------------------------------------


        velocity_text = font.render(
            f"Velocity: ({player.velocity.x:.2f}, "
            f"{player.velocity.y:.2f})",
            True,
            BLUE
        )


        screen.blit(
            velocity_text,
            (20, 105)
        )




        # -----------------------------------------------------
        # Speed
        # -----------------------------------------------------


        speed_text = font.render(
            f"Speed: {speed:.2f}",
            True,
            WHITE
        )


        screen.blit(
            speed_text,
            (20, 135)
        )




        # -----------------------------------------------------
        # Acceleration
        # -----------------------------------------------------


        acceleration_text = font.render(
            f"Acceleration: "
            f"({player.acceleration.x:.2f}, "
            f"{player.acceleration.y:.2f})",
            True,
            WHITE
        )


        screen.blit(
            acceleration_text,
            (20, 165)
        )




        # -----------------------------------------------------
        # Score
        # -----------------------------------------------------


        score_text = font.render(
            f"Asteroids Hit: {score}",
            True,
            WHITE
        )


        screen.blit(
            score_text,
            (20, 195)
        )




        # -----------------------------------------------------
        # Vector Legend
        # -----------------------------------------------------


        legend_text = font.render(
            "RED = Facing Direction     BLUE = Velocity",
            True,
            WHITE
        )


        screen.blit(
            legend_text,
            (20, HEIGHT - 65)
        )




        # -----------------------------------------------------
        # Main Lesson Formula
        # -----------------------------------------------------


        formula_text = font.render(
            "Acceleration -> Velocity -> Position",
            True,
            GREEN
        )


        screen.blit(
            formula_text,
            (20, HEIGHT - 35)
        )

        pygame.display.flip()


        await asyncio.sleep(0)

    pygame.quit()
asyncio.run(main())
