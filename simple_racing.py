"""
🏎️ Basit Yarış AI Simülasyonu
GitHub: https://github.com/[KULLANICI_ADINIZ]/racing-ai-simulator
"""
import pygame
import math
import random

# PyGame başlatma
pygame.init()

# Ekran ayarları
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🏎️ AI Racing Simulator")
clock = pygame.time.Clock()

# Renkler
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
GRAY = (80, 80, 80)
YELLOW = (255, 255, 0)

class Car:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.width = 35
        self.height = 55
        self.speed = 0
        self.max_speed = 6
        self.acceleration = 0.15
        self.braking = 0.25
        self.steering = 4
        self.angle = 0
        self.color = RED
        self.sensor_distances = [0, 0, 0]  # sol, ön, sağ
        
    def draw(self, surface):
        # Araba gövdesi
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, self.color, (0, 0, self.width, self.height), border_radius=8)
        
        # Ön cam
        pygame.draw.rect(car_surface, (150, 200, 255), (5, 8, self.width-10, 12), border_radius=3)
        
        # Tekerlekler
        pygame.draw.rect(car_surface, (20, 20, 20), (2, 5, 6, 10), border_radius=2)
        pygame.draw.rect(car_surface, (20, 20, 20), (self.width-8, 5, 6, 10), border_radius=2)
        pygame.draw.rect(car_surface, (20, 20, 20), (2, self.height-15, 6, 10), border_radius=2)
        pygame.draw.rect(car_surface, (20, 20, 20), (self.width-8, self.height-15, 6, 10), border_radius=2)
        
        # Döndür ve çiz
        rotated = pygame.transform.rotate(car_surface, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect.topleft)
        
        # Sensörleri çiz
        self.draw_sensors(surface)
    
    def draw_sensors(self, surface):
        angles = [-45, 0, 45]  # sol, ön, sağ
        sensor_colors = [GREEN, YELLOW, GREEN]
        
        for i, angle in enumerate(angles):
            total_angle = self.angle + angle
            rad = math.radians(total_angle)
            
            sensor_x = self.x + math.sin(rad) * 100
            sensor_y = self.y - math.cos(rad) * 100
            
            # Sensör çizgisi
            pygame.draw.line(surface, sensor_colors[i], (self.x, self.y), (sensor_x, sensor_y), 2)
            
            # Mesafe hesapla
            distance = self.calculate_distance(sensor_x, sensor_y)
            self.sensor_distances[i] = distance
            
            # Mesafe noktası
            end_x = self.x + math.sin(rad) * 100 * distance
            end_y = self.y - math.cos(rad) * 100 * distance
            pygame.draw.circle(surface, RED, (int(end_x), int(end_y)), 5)
    
    def calculate_distance(self, x, y):
        # Ekran sınırlarına olan mesafeyi hesapla
        distances = [
            x,                    # sol duvar
            WIDTH - x,            # sağ duvar  
            y,                    # üst duvar
            HEIGHT - y            # alt duvar
        ]
        min_distance = min(distances)
        return min(min_distance / 100, 1.0)
    
    def update(self, action):
        # Fizik güncelleme
        if action == "ACCELERATE":
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif action == "BRAKE":
            self.speed = max(self.speed - self.braking, -self.max_speed/2)
        elif action == "LEFT":
            self.angle += self.steering
        elif action == "RIGHT":
            self.angle -= self.steering
        elif action == "NONE":
            # Yavaşça dur
            if abs(self.speed) > 0.1:
                self.speed *= 0.95
            else:
                self.speed = 0
        
        # Pozisyon güncelleme
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
        
        # Ekran sınırları
        self.x = max(self.width//2, min(WIDTH - self.width//2, self.x))
        self.y = max(self.height//2, min(HEIGHT - self.height//2, self.y))

class SimpleAI:
    def __init__(self):
        self.safe_distance = 0.4
        
    def decide_action(self, sensor_data, car_speed):
        left_dist, front_dist, right_dist = sensor_data
        
        print(f"🤖 AI Sensörler: Sol={left_dist:.2f}, Ön={front_dist:.2f}, Sağ={right_dist:.2f}")
        
        # Karar ağacı
        if front_dist < self.safe_distance:
            # Önde engel var
            if left_dist > right_dist:
                return "LEFT"
            else:
                return "RIGHT"
        elif front_dist < self.safe_distance * 1.5:
            # Yaklaşan engel
            if car_speed > 3:
                return "BRAKE"
            else:
                return "NONE"
        elif min(left_dist, right_dist) < self.safe_distance * 0.7:
            # Yanlarda çok yakın
            if left_dist < right_dist:
                return "RIGHT"
            else:
                return "LEFT"
        elif car_speed < 4:
            # Hızlanma zamanı
            return "ACCELERATE"
        else:
            # Güvenli sürüş
            return "NONE"

def draw_track(surface):
    # Pist
    pygame.draw.rect(surface, GRAY, (100, 80, 600, 440), border_radius=20)
    pygame.draw.rect(surface, BLACK, (120, 100, 560, 400), border_radius=15)
    
    # Start/Finish çizgisi
    for i in range(0, 400, 40):
        color = WHITE if (i // 40) % 2 == 0 else BLACK
        pygame.draw.rect(surface, color, (490, 100 + i, 20, 20))

def draw_ui(surface, car, ai_action, frame_count):
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # AI bilgileri
    info_lines = [
        f"AI Aksiyon: {ai_action}",
        f"Hız: {abs(car.speed):.1f}",
        f"Açı: {car.angle}°",
        f"Sensörler: L:{car.sensor_distances[0]:.2f} F:{car.sensor_distances[1]:.2f} R:{car.sensor_distances[2]:.2f}",
        f"Kare: {frame_count}",
        "",
        "Kontroller:",
        "ESC: Çıkış, R: Reset",
        "SPACE: AI Aç/Kapa"
    ]
    
    for i, line in enumerate(info_lines):
        color = WHITE if i < 5 else YELLOW
        text = small_font.render(line, True, color)
        surface.blit(text, (10, 10 + i * 25))
    
    # GitHub bilgisi
    github_text = small_font.render("GitHub: racing-ai-simulator", True, BLUE)
    surface.blit(github_text, (10, HEIGHT - 30))

def main():
    car = Car()
    ai = SimpleAI()
    ai_enabled = True
    running = True
    frame_count = 0
    
    print("🚗 Yarış AI Simülasyonu Başlatıldı!")
    print("📍 GitHub Repository'si Hazır!")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    car = Car()  # Reset
                elif event.key == pygame.K_SPACE:
                    ai_enabled = not ai_enabled
                    print(f"🤖 AI {'AÇIK' if ai_enabled else 'KAPALI'}")
        
        # AI kararı
        if ai_enabled:
            action = ai.decide_action(car.sensor_distances, car.speed)
        else:
            action = "NONE"
        
        # Araba güncelleme
        car.update(action)
        
        # Çizim
        screen.fill(BLACK)
        draw_track(screen)
        car.draw(screen)
        draw_ui(screen, car, action, frame_count)
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
        
        if frame_count % 60 == 0:
            print(f"⏱️ Simülasyon çalışıyor... AI: {'AKTİF' if ai_enabled else 'PASİF'}")
    
    pygame.quit()
    print("🎯 Simülasyon sonlandı! GitHub projeniz hazır!")

if __name__ == "__main__":
    main()
