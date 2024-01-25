import pygame
import random
import math
import numpy as np

global ground

# Society attributes
society_attr = {
  "Digitarian": {
    'energy': 100,
    'area': 0,
    'population': 16,
    'max_population': 999,
  },
  "Communo": {
    'energy': 9999,
    'area': 0,
    'population': 16,
    'max_population': 25,
  },
  "Evolutionist": {
    'energy': 100,
    'area': 0,
    'population': 16,
    'max_population': 999,
  },
  "Bio": {
    'energy': 100,
    'area': 0,
    'population': 16,
    'max_population': 999,
  },
}

pDigi = [0.25, 0.17, 0.2, 0.03, 0.2, 0.05, 0.1]
pBio = [0.25, 0.17, 0.2, 0.03, 0.2, 0.05, 0.1]
pCommuno = [0.35, 0.06, 0.18, 0.03, 0.05, 0.05, 0.28]
pEvo = [0.05, 0.22, 0.4, 0.03, 0.15, 0.1, 0.05]

# Initialize Pygame
pygame.init()

# Define constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
GRID_SIZE = 20
# grid_width, grid_height = 40, 40
block_size = 15
agent_size = 5
GRID_WIDTH, GRID_HEIGHT = int(WINDOW_WIDTH // GRID_SIZE), int(WINDOW_HEIGHT // GRID_SIZE)

FPS = 60


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAIN_CLR = (33, 33, 33)
FARM_CLR = (89, 69, 69)
CITY_CLR = (18, 75, 135)
LAB_CLR = (42, 87, 68)
NUCLEAR_CLR = (65, 42, 87)

DIGI_CLR = (148, 196, 247)
BIO_CLR = (237, 198, 55)
COMMUNO_CLR = (245, 47, 47)
EVO_CLR = (247, 148, 229)

class Grid():
  def __init__(self):
        self.ground = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)] 

  def update(self):
    pass

# Sprite group for agents

grid = Grid()
agents = pygame.sprite.Group()
ground = pygame.sprite.Group()

# Agent class
class Human(pygame.sprite.Sprite):
    def __init__(self, x, y, society, toxic_resistance, resident_idx):
        super().__init__()
        self.image = pygame.Surface((agent_size, agent_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 100
        self.happiness = 50
        self.mutations = 0
        self.toxic_resistance = toxic_resistance
        self.power = 100
        self.society = society
        self.cost = 1    
        self.positive_mutations = 0
        match self.society:
            case "Digitarian":
                self.image.fill(DIGI_CLR)
                self.resident_idx = resident_idx
                self.toxic_tiles = []
            case "Communo":
                self.image.fill(COMMUNO_CLR)
                self.cost = 0.5    
            case "Evolutionist":
                self.image.fill(EVO_CLR)
            case "Bio":
                self.image.fill(BIO_CLR)


    def get_ground(self):
        return grid.ground[int((self.rect.centery - block_size)/GRID_SIZE)][int((self.rect.centerx - block_size)/GRID_SIZE)]

    
    def is_enemy_on_tile(self, tile):
        for agent in tile.agents:
            if agent != self and agent.society != self.society:
                return agent
        return None


    def update(self, agents):
        if self.health <= 0:
            tile = self.get_ground()
            if random.random() > 0.5:
                tile.fertility += 1
            else:
                tile.toxicity += 1
            if self in self.get_ground().agents:
               self.get_ground().agents.remove(self)
            # agents.remove(self)
            society_attr[self.society]['population'] -= 1
            self.kill()
            return

        x = self.rect.x + random.randrange(-GRID_SIZE, GRID_SIZE+1, GRID_SIZE)
        y = self.rect.y + random.randrange(-GRID_SIZE, GRID_SIZE+1, GRID_SIZE)

        # tile = self.get_ground()
        p = [0.25, 0.12, 0.18, 0.1, 0.2, 0.05, 0.1]
        match self.society:
            case "Digitarian":
                p = pDigi
            case "Bio":
                p = pBio
            case "Communo":
                p = pCommuno
            case "Evolutionist":
                p = pEvo

        i = 2
        while i > 0:
            if self.health < 20 or self.happiness < 15 or society_attr[self.society]['energy']<10:
                match np.random.choice(2):
                    case 0:
                        self.rest()
                    case 1:
                        self.get_resource()

            else:
                match np.random.choice(range(7), p=p):
                    case 0:
                        # move
                        if x >= 10 and x <= WINDOW_WIDTH-2:
                            if self in self.get_ground().agents:
                                # TODO Digitarian
                                self.get_ground().agents.remove(self)
                                # tmp = self.rect.x
                                self.rect.x = x
                                self.get_ground().agents.append(self)
                                # if self.society == "Digitarian" and self.get_ground().toxicity >

                        if y >= 10 and y <= WINDOW_HEIGHT-10:
                            if self in self.get_ground().agents:
                                self.get_ground().agents.remove(self)
                                self.rect.y = y
                                self.get_ground().agents.append(self)
                    case 1:
                        self.get_resource()
                    case 2:
                        match self.society:
                            case "Digitarian":
                                self.detect_toxicity()
                            case "Communo":
                                self.share()
                            case "Evolutionist":
                                self.force_mutation()
                            case "Bio":
                                self.fertilize_tile()

                    case 3:
                        # self.conquer_tile()
                        self.reproduce()
                        society_attr[self.society]['energy'] -= self.cost
                    case 4:
                        self.rest()
                    case 5:
                        self.build_tile()
                    case 6:
                        self.conquer_tile()
            i -= 1
            
        self.battle_toxicity()
        
    def setTile(self, tile, type, color):
        tile.type = type
        tile.image.fill(color)
        tile.level = 0

    def build_tile(self):
        tile = self.get_ground()
        
        if self.is_enemy_on_tile(tile) == None:
            if tile.owner == self.society:
                tile.level_up()
            else:
                tile.owner = self.society
                match self.society:
                    case "Digitarian":
                        match np.random.choice(range(4), p=[0.50, 0.125, 0.125, 0.25]):
                            case 0:
                                self.setTile(tile, "City", CITY_CLR)
                            case 1:
                                self.setTile(tile, "Lab", LAB_CLR)
                            case 2:
                                self.setTile(tile, "Nuclear", NUCLEAR_CLR)
                            case 3:
                                self.setTile(tile, "Farm", FARM_CLR)
                    case "Communo":
                        match np.random.choice(range(3), p=[0.20, 0.7, 0.1]):
                            case 0:
                                self.setTile(tile, "City", CITY_CLR)
                            case 1:
                                self.setTile(tile, "Nuclear", NUCLEAR_CLR)
                            case 2:
                                self.setTile(tile, "Farm", FARM_CLR)
                    case "Evolutionist":
                        match np.random.choice(range(3), p=[0.1, 0.8, 0.1]):
                            case 0:
                                self.setTile(tile, "City", CITY_CLR)
                            case 1:
                                self.setTile(tile, "Lab", LAB_CLR)
                            case 2:
                                self.setTile(tile, "Farm", FARM_CLR)
                    case "Bio":
                        match np.random.choice(range(2), p=[0.20, 0.8]):
                            case 0:
                                self.setTile(tile, "City", CITY_CLR)
                            case 1:
                                self.setTile(tile, "Farm", FARM_CLR)
                tile.level_up()
        else:
            self.conquer_tile()


    def get_resource(self):
        self.happiness -= 1
        self.get_ground().generate_energy(self)
        society_attr[self.society]['energy'] -= self.cost


    def conquer_tile(self):
        tile = self.get_ground()
        enemy = self.is_enemy_on_tile(tile)
        if not enemy:
            tile.owner = self.society    
            return

        
        sboost, eboost = 0, 0
        if self.society == "Digitarian":
            if self.resident_idx < 25:
                sboost = 15    
        if enemy.society == "Digitarian":
            if enemy.resident_idx < 25:
                eboost = 15   

        enemy.health -= ((self.power+sboost) * 0.2 + self.positive_mutations )
        self.health -= ((enemy.power+eboost) * 0.2 + enemy.positive_mutations)
        enemy.happiness -= 2 
        self.happiness -= 2 

        if enemy.health <= 0:
            tile.owner = self.society

        society_attr[self.society]['energy'] -= self.cost


    def battle_toxicity(self):
        if self.mutations and random.randint(0,10) > self.toxic_resistance:
           self.health -= self.mutations * 3 
           self.happiness -= 1
    

    def rest(self):
        self.health += 10
        if self.health > 100:
            self.health = 100
        self.happiness += 10
        if self.happiness > 100:
            self.happiness = 100


    def reproduce(self):
        if self.society != "Communo" and society_attr[self.society]['population'] == society_attr[self.society]['max_population']:
            return 
        
        for i in range(-1,2,1):
            for j in range(-1,2,1):
                x = int((self.rect.centery - block_size)/GRID_SIZE + i)
                y = int((self.rect.centerx - block_size)/GRID_SIZE + j)
                if 0 <= x and x < GRID_WIDTH and y >= 0 and y < GRID_HEIGHT:
                    tile = grid.ground[x][y]
                    for agent in tile.agents:
                        if agent != self and agent.society == self.society and self.happiness > 50 and agent.happiness > 50:
                            a = Human(x*GRID_SIZE+block_size, y*GRID_SIZE+block_size, self.society, random.randint(0, 10), 0)
                            society_attr[self.society]['population'] += 1
                            grid.ground[y][x].agents.append(a)
                            # print(f'{grid.ground[y][x].rect.center} {a.rect.center}')
                            agents.add(a)
                            if a.society == "Communo" and society_attr[self.society]['population'] >= society_attr[self.society]['max_population']:
                                to_delete = agent
                                for ag in agents:
                                    if ag.power + ag.health < to_delete.power + to_delete.health:
                                        to_delete = ag
                                
                                if to_delete in to_delete.get_ground().agents:
                                    to_delete.get_ground().agents.remove(to_delete)
                                to_delete.kill()
                                society_attr[self.society]['population'] -= 1
                            return
                            # print(f'{self.rect.center} {agent.rect.center}')


    # Digitarian
    def detect_toxicity(self):
        for i in range(-1,2,1):
            for j in range(-1,2,1):
                tile = grid.ground[int((self.rect.centery - block_size)/GRID_SIZE + i)][int((self.rect.centerx - block_size)/GRID_SIZE + j)]
                if (tile.toxicity > 0):
                    self.toxic_tiles.append(tile)
        society_attr[self.society]['energy'] -= self.cost

    
    # Communo
    def share(self):
        agents = self.get_ground().agents
        if len(agents) < 1:
            return
        rnd = agents[random.randint(0, len(agents) -1)]
        health_share = (rnd.health + self.health)/2
        happiness_share = (rnd.happiness + self.happiness)/2
        power_share = (rnd.happiness + self.happiness)/2
        self.health = health_share
        rnd.health = health_share
        self.happiness = happiness_share
        rnd.happiness = happiness_share
        self.power = power_share
        rnd.power = power_share
        society_attr[self.society]['energy'] -= self.cost


    # Bio
    def fertilize_tile(self):
        self.get_ground().fertility += random.randint(2, 8)
        society_attr[self.society]['energy'] -= self.cost


    # Evolutionist
    def force_mutation(self):
        if self.get_ground().type == "Lab":
            if random.random() > 0.2:
                if self.positive_mutations < 5:
                    self.positive_mutations += 1
                    self.health += 10
                    self.happiness += 5
                    self.power += 10
                    self.toxic_resistance += 1
            else:
                self.mutations +=  1
        society_attr[self.society]['energy'] -= self.cost

# Ground class
class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y, fertility, toxicity, resources, max_citizens, regeneration ,type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((block_size, block_size))
        # self.image = pygame.Rect((10,10))
        self.image.fill(PLAIN_CLR)
        self.owner = ''
        self.rect = self.image.get_rect(center=(x, y))
        self.fertility = fertility
        self.toxicity = toxicity
        self.resources = resources
        self.level = 0
        self.max_citizens = max_citizens
        self.regeneration = regeneration
        self.allow_demutate = False
        self.agents = []


    def update(self):
        for agent in self.agents:
            if self.type == "Lab":
                self.decreaseMutation(agent)
            else:
                if self.type == "Farm":
                    self.give_happines(agent)
                    if self.level > 2:
                        agent.power += 10
                if (agent.mutations < 5 and random.randint(0, 10) < self.toxicity):
                    agent.mutations += 1


    def level_up (self):
        if(self.level == 3):
            return
        self.level = self.level + 1
        

    def decreaseMutation(self, agent):   
        if(agent.mutations > 0 and random.random() > 0.88):
            agent.mutations -= 1
        
    
    def generate_energy(self, agent):
        basic = random.randint(5,10)
        energyMultiplier = 1
        decreaseFertility = 1
        match self.type:
            case 'City':
                energyMultiplier += 1
            case 'Lab':
                energyMultiplier += 1
            case 'Nuclear':
                match self.level:
                    case 1:
                        energyMultiplier += 2
                    case 2:
                        energyMultiplier += 4
                    case 3:
                        energyMultiplier += 6
            case 'Farm':
                energyMultiplier += 1
                if(self.level == 3):
                    decreaseFertility = 0
        society_attr[agent.society]['energy'] += basic * energyMultiplier + self.resources//2
        self.resources //= 2
        if(random.random() > 0.85):
            self.fertility = self.fertility - decreaseFertility
            if self.fertility < 0:
                self.fertility = 0
        if random.random() < self.regeneration:
            self.resources += 10
        

    def give_happines(self, agent):
        if (self.level >= 2):
            #TODO neghbours
            agent.happiness += random.randint(5,10)
        
aside = pygame.Surface((300, WINDOW_HEIGHT))
aside.fill(BLACK)

# Setup Pygame window
window = pygame.display.set_mode((WINDOW_WIDTH + 300, WINDOW_HEIGHT))
pygame.display.set_caption("Agent Systems Simulation")
clock = pygame.time.Clock()

for i in range(0, GRID_WIDTH):
    for j in range(0, GRID_HEIGHT):
        fertility = random.randint(50,100)
        toxicity = random.randint(0,10)
        resources = random.randint(0,5)
        max_citizens = 1
        regeneration = random.random()
        type = 'plain'
        # g = Ground(i * WINDOW_WIDTH/GRID_WIDTH+block_size, j*WINDOW_HEIGHT/GRID_HEIGHT+block_size, fertility, toxicity, resources, max_citizens, regeneration, type)
        
        g = Ground(i*GRID_SIZE+block_size, j*GRID_SIZE+block_size, fertility, toxicity, resources, max_citizens, regeneration, type)

        # j=x i=y
        grid.ground[j][i] = g

        ground.add(g)


# Create agents
for i in range(16):
    x, y = random.randint(0, GRID_WIDTH//2-1), random.randint(0, GRID_HEIGHT//2-1)
    agent = Human(x*GRID_SIZE+block_size, y*GRID_SIZE+block_size, "Digitarian", random.randint(0, 10), 1)
    agents.add(agent)
    grid.ground[y][x].agents.append(agent)
    
    x, y = random.randint(GRID_WIDTH//2, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT//2)
    agent = Human(x*GRID_SIZE+block_size, y*GRID_SIZE+block_size, "Bio", random.randint(0, 10), 0)
    agents.add(agent)
    grid.ground[y][x].agents.append(agent)
    
    x, y = random.randint(0, GRID_WIDTH//2-1), random.randint(GRID_HEIGHT//2, GRID_HEIGHT-1)
    agent = Human(x*GRID_SIZE+block_size, y*GRID_SIZE+block_size, "Communo", random.randint(0, 10), 0)
    agents.add(agent)
    grid.ground[y][x].agents.append(agent)
        
    x, y = random.randint(GRID_WIDTH//2-1, GRID_WIDTH-1), random.randint(GRID_HEIGHT//2-1, GRID_HEIGHT-1)
    agent = Human(x*GRID_SIZE+block_size, y*GRID_SIZE+block_size, "Evolutionist", random.randint(0, 10), 0)
    agents.add(agent)
    grid.ground[y][x].agents.append(agent)

FONT = pygame.font.SysFont('Arial', 36)
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # if event.type == KEYDOWN:
        #     if event.key == K_RIGHT:
        # Update
        agents.update(agents)
        ground.update()

        text_surface = FONT.render("Digitarians", True, (255, 255, 255))
        aside.blit(text_surface, (40, 10))
        text_surface = FONT.render("Bio", True, (255, 255, 255))
        aside.blit(text_surface, (40, 60))
        text_surface = FONT.render("Communo", True, (255, 255, 255))
        aside.blit(text_surface, (40, 110))
        text_surface = FONT.render("Evolutionists", True, (255, 255, 255))
        aside.blit(text_surface, (40, 160))
        # Draw
        window.fill(BLACK)
        window.blit(aside, (WINDOW_WIDTH, 0))
        
        ground.draw(window)
        agents.draw(window)

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
