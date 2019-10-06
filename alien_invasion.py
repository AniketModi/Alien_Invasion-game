import sys

import pygame
from settings import Settings
from ship import Ship
import game_functions as gf
from pygame.sprite import Group
from alien import Alien
from scoreboard import Scoreboard
from game_stats import GameStats
from button import Button

def run_game():
    #initialize pygame, settings and screen object.
    pygame.init()
   # screen=pygame.display.set_mode((1200,800))
    
    ai_settings=Settings()
    screen=pygame.display.set_mode((ai_settings.screen_width,ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    #Create an instance to store game statistics.
    stats=GameStats(ai_settings)
    sb=Scoreboard(ai_settings,screen,stats)
    #Make a ship
    ship=Ship(ai_settings,screen)

    #Make a play button
    play_button=Button(ai_settings,screen,"Play")
    #Make a alien
    alien=Alien(ai_settings,screen)
    #Make a group to store bullets in.
    bullets=Group()
    aliens=Group()

    #set the background color
   # bg_color=(0,255,0) #(230,230,230)-> light gray
                        #(0,255,0)->green-----------------|-->RGB color 
                        #(255,0,0)->red, (0,0,255)->blue  |
    #Create the fleet of aliens.
    gf.create_fleet(ai_settings,screen,ship,aliens)
    #Start the main loop for the game
    
    while True:
            gf.check_events(ai_settings,screen,ship,aliens,bullets,play_button,stats,sb)

            if stats.game_active:
                
                ship.update()
                gf.update_bullets(ai_settings,screen,ship,aliens,bullets,sb,stats)
                gf.update_aliens(ai_settings,stats,screen,ship,aliens,bullets)
                
            gf.update_screen(ai_settings,screen,ship,aliens,bullets,play_button,stats,sb)

run_game()
