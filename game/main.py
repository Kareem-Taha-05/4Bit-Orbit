import pygame, sys
from level import LevelManager
import state
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Aether Phoenix')
        self.clock = pygame.time.Clock()

        self.current_manager = None
        self.current_state = None
        self.event_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.event_timer, 1000)

    def run(self):
        while True:
            for event in pygame.event.get():
                if self.current_manager:
                    self.current_manager.handle_events(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.current_state != state.GAME_STATE:
                self.current_manager = self.create_manager(state.GAME_STATE)
                self.current_state = state.GAME_STATE
            if state.GAME_STATE == state.GameState.EXIT:
                sys.exit(0)
            if state.GAME_STATE == state.GameState.RESTART:
                self.current_manager = self.create_manager(state.GameState.PLAY)
                state.GAME_STATE = state.GameState.PLAY
                state.LEVEL_STATE = state.LevelState.MAP_1
                state.PLAY_STATE = state.PlayState.PLAY
                self.current_state = state.GAME_STATE
            else:
                if self.current_manager:
                    self.screen.fill('#0e0f2c')
                    self.current_manager.update()
            pygame.display.update()
            self.clock.tick(60)

    def create_manager(self, game_state):
        if game_state == state.GameState.PLAY:
            return LevelManager()

if __name__ == '__main__':
     game = Game()
     game.run()

