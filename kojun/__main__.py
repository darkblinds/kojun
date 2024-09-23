import logging
from kojun.game_logic.Actor_Player import ActorPlayer

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("__main__.py").info("Project has run")
    ActorPlayer()
