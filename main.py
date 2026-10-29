import pygame
import sys
import os
import math # Importar math para usar a função sqrt (ou magnitude/normalize do Vector2)

# fix para diretorio de trabalho
BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)

# --- CONFIGURAÇÕES GLOBAIS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32

# Mapa De Dados (1 = Parede, P = Posição Inicial do Player)
level_map = [
    '11111111111111111111111111111111',
    '1P000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '10000000000000000000000000000001',
    '11111111111111111111111111111111',
]

# classe Tile(Parede)
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        # Imagem da Parede
        self.image = pygame.image.load('grafics/backgroud/Sala_1.jpeg').convert() # ATENÇÃO: Verifique se o caminho do arquivo está correto!

        # posição do mundo
        self.rect = self.image.get_rect(topleft=pos)

# --- CLASSE JOGADOR (Player) ---
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        # Inicializa o Sprite
        super().__init__()

        # 1. Carregamento dos sprites. CORRIGIDO: O caminho 'grafic' estava errado
        self.sprites = {
            'south': pygame.image.load('grafics/Player/rotations/south.png').convert_alpha(),
            'north': pygame.image.load('grafics/Player/rotations/north.png').convert_alpha(),
            'east': pygame.image.load('grafics/Player/rotations/east.png').convert_alpha(),
            'west': pygame.image.load('grafics/Player/rotations/west.png').convert_alpha(),
            'north-east': pygame.image.load('grafics/Player/rotations/north-east.png').convert_alpha(),
            'north-west': pygame.image.load('grafics/Player/rotations/north-west.png').convert_alpha(),
            'south-east': pygame.image.load('grafics/Player/rotations/south-east.png').convert_alpha(),
            'south-west': pygame.image.load('grafics/Player/rotations/south-west.png').convert_alpha(),
        }

        # 2 status Inicial
        self.status = 'south'
        self.image = self.sprites[self.status]
        self.rect = self.image.get_rect(topleft=pos)

        # 3 Movimento
        self.direction = pygame.math.Vector2()
        self.speed = 5

    def input(self):
        # CORRIGIDO: get.pressed() para get_pressed()
        keys = pygame.key.get_pressed()

        # Input vertical
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'north'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'south'
        else:
            self.direction.y = 0

        # Input horizontal
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            # Prioriza a direção horizontal ao mudar o status, se não houver diagonal
            if self.direction.y == 0:
                self.status = 'east'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            if self.direction.y == 0:
                self.status = 'west'
        else:
            self.direction.x = 0
            
        # Lógica de Diagonais (opcional, mas bom para 8 direções)
        if self.direction.x == 1 and self.direction.y == -1: self.status = 'north-east'
        elif self.direction.x == -1 and self.direction.y == -1: self.status = 'north-west'
        elif self.direction.x == 1 and self.direction.y == 1: self.status = 'south-east'
        elif self.direction.x == -1 and self.direction.y == 1: self.status = 'south-west'
        
        # Atualiza a imagem do sprite com base no status (para testar as rotações)
        self.image = self.sprites.get(self.status, self.sprites['south']) # Usa 'south' como default se o status não for encontrado

    def move(self, speed):
        # Normaliza o vetor de direção para que a movimentação em diagonal não seja mais rápida
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * speed
        self.rect.y += self.direction.y * speed

    def update(self):
        # NOVO MÉTODO: Chama o input para saber a direção e move para atualizar a posição
        self.input()
        self.move(self.speed)
        
# Camera do jogo
class CameraGroup(pygame.sprite.Group):
    # ... (Nenhuma alteração significativa aqui)
    def __init__(self, player):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2
        self.player = player # O player que a camera deve seguir

    def center_target_camera(self):
        # calcula o quanto a camera precisa "andar" para centralizar no player
        self.offset.x = self.player.rect.centerx - self.half_w
        self.offset.y = self.player.rect.centery - self.half_h

    def custom_drawn(self, background_color):

        self.center_target_camera()
        self.display_surface.fill(background_color)

        # desenha todos os sprites (tiles e player) com o offset da camera
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

# --- CLASSE PRINCIPAL DO JOGO (Jogo) ---
class Jogo:
    def __init__(self, screen):
        self.screen = screen

        # Grupo de colisões
        self.obstacle_sprites = pygame.sprite.Group()

        # Criação do mapa (chama função do tiles)
        self.setup_level(level_map)

        # 2 Criação do Player na posição P do mapa
        self.player = Player(self.player_start_pos)

        # Grupo da camera (grupo que sera desenhado na tela)
        # CORRIGIDO: Recomendo usar 'visible_sprites' minúsculo
        self.visible_sprites = CameraGroup(self.player) 
        self.visible_sprites.add(self.player)

        # adiciona os tiles criados ao grupo da camera
        # CORRIGIDO: Nome da variável de 'obstacle_sprite' para 'obstacle_sprites'
        for tile in self.obstacle_sprites:
            self.visible_sprites.add(tile) 
        
        self.running = True

    def setup_level(self, layout):
        """Lê o mapa de dados e cria os Tiles."""
        for row_index, rouw in enumerate(layout):
            for col_index, col in enumerate(rouw):

                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if col == '1':
                    # cria uma parede usando a classe tile
                    # CORRIGIDO: 'Self' para 'self'
                    Tile((x, y), [self.obstacle_sprites]) 

                if col == 'P':
                    self.player_start_pos = (x, y) # Salva posição do player

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # 2 Atualização
            # CORRIGIDO: 'sel' para 'self'
            self.player.update() 

            # 3 Desenho agora usando a camera
            self.visible_sprites.custom_drawn('black')

            # 4. Atualização de tela e fps
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

# --- INICIALIZAÇÃO DO PROGRAMA ---
if __name__ == '__main__':
    # Inicializa todos os módulos necessários do Pygame
    pygame.init() 
    
    # Cria a janela principal do jogo
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Meu RPG 2D - Fase 1: Movimento")
    
    # Cria e roda a instância do Jogo
    game = Jogo(screen)
    game.run()