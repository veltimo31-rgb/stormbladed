import pygame
import random
import sys

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
FPS = 60

# Colors
GRASS = (86, 125, 70)
TREE_LEAVES = (45, 87, 44)
TREE_TRUNK = (101, 67, 33)
PLAYER = (200, 70, 70)
MERCHANT = (70, 130, 200)
UI_TEXT = (255, 255, 255)
PLATINUM_COLOR = (229, 228, 226)
SHOP_BG = (40, 40, 40)

class Lumberjack:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.speed = 4
        self.wood_inventory = 0
        self.platinum = 0
        self.facing = 'down'
        
        # Axe Stats
        self.axe_level = 1
        self.axe_damage = 1

    def move(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
            self.facing = 'up'
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
            self.facing = 'down'
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
            self.facing = 'left'
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            self.facing = 'right'

        self.rect.x = max(0, min(WIDTH - TILE_SIZE, self.rect.x + dx))
        self.rect.y = max(0, min(HEIGHT - TILE_SIZE, self.rect.y + dy))

    def get_reach_rect(self):
        reach = 20
        if self.facing == 'up':
            return pygame.Rect(self.rect.x, self.rect.y - reach, TILE_SIZE, reach)
        elif self.facing == 'down':
            return pygame.Rect(self.rect.x, self.rect.bottom, TILE_SIZE, reach)
        elif self.facing == 'left':
            return pygame.Rect(self.rect.x - reach, self.rect.y, reach, TILE_SIZE)
        elif self.facing == 'right':
            return pygame.Rect(self.rect.right, self.rect.y, reach, TILE_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER, self.rect)

class Tree:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.health = 3 

    def draw(self, surface):
        trunk_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 20, 20, 20)
        pygame.draw.rect(surface, TREE_TRUNK, trunk_rect)
        leaves_rect = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE - 10)
        pygame.draw.rect(surface, TREE_LEAVES, leaves_rect)

class Merchant:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, MERCHANT, self.rect)
        pygame.draw.circle(surface, PLATINUM_COLOR, self.rect.center, 8)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stormblade - Regrowing Forest")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    shop_font = pygame.font.SysFont(None, 48)

    player = Lumberjack(WIDTH // 2, HEIGHT // 2)
    merchant = Merchant(WIDTH - 100, 100)
    
    trees = []
    respawn_queue = [] # Stores: [x, y, time_chopped_down]
    RESPAWN_TIME_MS = 20000 # 20 seconds
    
    for _ in range(40):
        tx = random.randint(0, (WIDTH - TILE_SIZE) // TILE_SIZE) * TILE_SIZE
        ty = random.randint(0, (HEIGHT - TILE_SIZE) // TILE_SIZE) * TILE_SIZE
        tree_rect = pygame.Rect(tx, ty, TILE_SIZE, TILE_SIZE)
        if not tree_rect.colliderect(merchant.rect):
            trees.append(Tree(tx, ty))

    in_shop = False
    running = True

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if in_shop:
                    if event.key == pygame.K_1: 
                        if player.wood_inventory > 0:
                            player.platinum += player.wood_inventory * 5
                            player.wood_inventory = 0
                    elif event.key == pygame.K_2: 
                        upgrade_cost = player.axe_level * 50
                        if player.platinum >= upgrade_cost:
                            player.platinum -= upgrade_cost
                            player.axe_level += 1
                            player.axe_damage += 1
                    elif event.key in (pygame.K_e, pygame.K_ESCAPE): 
                        in_shop = False
                else:
                    reach_area = player.get_reach_rect()
                    
                    if event.key == pygame.K_SPACE:
                        for tree in trees[:]:
                            if reach_area.colliderect(tree.rect):
                                tree.health -= player.axe_damage
                                if tree.health <= 0:
                                    # Add to respawn queue before removing
                                    respawn_queue.append([tree.rect.x, tree.rect.y, current_time])
                                    trees.remove(tree)
                                    player.wood_inventory += random.randint(2, 5)
                    
                    if event.key == pygame.K_e:
                        if reach_area.colliderect(merchant.rect):
                            in_shop = True

        # Logic Update
        if not in_shop:
            keys = pygame.key.get_pressed()
            player.move(keys)

            # Check respawn queue
            for respawn_data in respawn_queue[:]:
                tx, ty, chopped_time = respawn_data
                if current_time - chopped_time >= RESPAWN_TIME_MS:
                    trees.append(Tree(tx, ty))
                    respawn_queue.remove(respawn_data)

        # Rendering
        screen.fill(GRASS)

        for tree in trees:
            tree.draw(screen)

        merchant.draw(screen)
        player.draw(screen)

        # Draw Base UI
        wood_text = font.render(f"Wood: {player.wood_inventory}", True, UI_TEXT)
        platinum_text = font.render(f"Platinum: {player.platinum}", True, PLATINUM_COLOR)
        axe_text = font.render(f"Axe Lvl: {player.axe_level} (Dmg: {player.axe_damage})", True, UI_TEXT)
        
        screen.blit(wood_text, (10, 10))
        screen.blit(platinum_text, (10, 40))
        screen.blit(axe_text, (10, 70))

        # Draw Shop Overlay
        if in_shop:
            shop_rect = pygame.Rect(150, 150, 500, 300)
            pygame.draw.rect(screen, SHOP_BG, shop_rect)
            pygame.draw.rect(screen, PLATINUM_COLOR, shop_rect, 3)
            
            title = shop_font.render("Merchant Shop", True, PLATINUM_COLOR)
            sell_opt = font.render("[1] Sell all Wood (5 Platinum each)", True, UI_TEXT)
            upgrade_cost = player.axe_level * 50
            upgrade_opt = font.render(f"[2] Upgrade Axe ({upgrade_cost} Platinum)", True, UI_TEXT)
            exit_opt = font.render("[E] Exit Shop", True, UI_TEXT)
            
            screen.blit(title, (shop_rect.x + 130, shop_rect.y + 30))
            screen.blit(sell_opt, (shop_rect.x + 50, shop_rect.y + 100))
            screen.blit(upgrade_opt, (shop_rect.x + 50, shop_rect.y + 150))
            screen.blit(exit_opt, (shop_rect.x + 50, shop_rect.y + 220))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
