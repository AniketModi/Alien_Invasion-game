import sys
import pygame
from bullets import Bullet
from alien import Alien
import pygame.sprite 
from time import sleep
from button import Button

def check_keydown_events(event,ai_settings,screen,ship,bullets,stats,aliens):
    #Respond to keypresses
    if event.key == pygame.K_RIGHT:
        ship.moving_right=True
    elif event.key == pygame.K_LEFT:
        ship.moving_left=True
    elif event.key==pygame.K_SPACE:
        fire_bullet(ai_settings,screen,ship,bullets)
    elif event.key==pygame.K_q:
        sys.exit()
    elif event.key==pygame.K_p:
        stats.start=True
        check_play_button(ai_settings,screen,stats,ship,aliens,bullets,False)
        
def get_number_rows(ai_settings,ship_height,alien_height):
    #Determine the number of rows of aliens that fit on the screen.
    available_space_y=(ai_settings.screen_height - (3*alien_height)-ship_height)
    number_rows=int(available_space_y/(2*alien_height))
    return number_rows

def check_keyup_events(event,ship):
    #Respond to keypresses
     if event.key == pygame.K_RIGHT:
        ship.moving_right=False
     elif event.key == pygame.K_LEFT:
        ship.moving_left=False

def number_aliens_x(ai_settings,screen):
     #Create an alien and find the number of aliens in a raw
    #Spacing between each alien is equal to one alien width
    alien=Alien(ai_settings,screen)
    alien_width=alien.rect.width
    available_space_x=ai_settings.screen_width-2*alien_width
    number_x=int(available_space_x/(2*alien_width))
    return number_x
    
def check_events(ai_settings,screen,ship,aliens,bullets,play_button,stats,sb):
    #Respond to keypresses and mouse events.
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            sys.exit()
        elif event.type==pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets,stats,aliens)               
        elif event.type==pygame.KEYUP:
            check_keyup_events(event,ship)
        elif event.type==pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y=pygame.mouse.get_pos()
            button_clicked=play_button.rect.collidepoint(mouse_x,mouse_y)
            check_play_button(ai_settings,screen,stats,ship,aliens,bullets,button_clicked,sb)


def check_play_button(ai_settings,screen,stats,ship,aliens,bullets,button_clicked,sb):
    #Start a new game when player clicks play.
    if (stats.start and not stats.game_active) or (button_clicked and not stats.game_active):
        stats.reset_stats()
        stats.game_active=True

        sb.prep_score()
        sb.prep_highscore()
        sb.prep_level()
        
        ai_settings.initialize_dynamic_settings()
        #Empty the list of aliens and bulllets.
        aliens.empty()
        bullets.empty()

        #Create a new fleet and center the ship.
        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()

        #Hide the mouse cursor
        pygame.mouse.set_visible(False)
        
def create_fleet(ai_settings,screen,ship,aliens):
    #Create a full fleet of aliens
    #Create the first row of aliens.
    alien=Alien(ai_settings,screen)
    for row_number in range(get_number_rows(ai_settings,ship.rect.height,alien.rect.height)):
        for alien_number in range(number_aliens_x(ai_settings,screen)):
            #Create an alien and place in it group.
            alien=Alien(ai_settings,screen)
            alien_width=alien.rect.width
            alien.x=alien_width+(2*alien_width)*alien_number
            alien.rect.x=alien.x
            alien.rect.y=alien.rect.height + 2*alien.rect.height*row_number
            aliens.add(alien)
        
def update_bullets(ai_settings,screen,ship,aliens,bullets,sb,stats):
    #Update position of bullets and get rid of old bullets
    #Update Bullet position
     #Get rid of bullets that have disappeared.
    bullets.update()     
    for bullet in bullets.copy():
            if bullet.rect.bottom<=0:
                    bullets.remove(bullet)
   # print(len(bullets))
    check_bullet_collision(ai_settings,screen,ship,aliens,bullets,sb,stats)
   
def check_bullet_collision(ai_settings,screen,ship,aliens,bullets,sb,stats):

   #Check for any bullets that have hit aliens.
   #If so,get rid of the bullet and the alien.
    collisions=pygame.sprite.groupcollide(bullets,aliens,True,True)

    if collisions:
        for aliens in collisions.values():
            
            stats.score+=ai_settings.alien_points
            sb.prep_score()
            check_high_scores(stats,sb)
        
    if len(aliens)==0:
        #Destroy existing bullets and create new fleet
        bullets.empty()
        ai_settings.increase_speed()

        stats.level+=1
        sb.prep_level()
        
        create_fleet(ai_settings,screen,ship,aliens)

def ship_hit(ai_settings,stats,screen,ship,aliens,bullets):
    #Respond to ship being hit by alien.
    #Decrement ships_left
    if stats.ships_left>0:
        stats.ships_left-=1

    #Empty the list of aliens and bullets.
        aliens.empty()
        bullets.empty()

    #Create a new fleet and center the ship.
        create_fleet(ai_settings,screen,ship,aliens)

    #Pause
        sleep(0.5)
    else:
        stats.game_active=False
        pygame.mouse.set_visible(True)
        stats.start=False
    
def update_aliens(ai_settings,stats,screen,ship,aliens,bullets):
    #Update the position of all aliens in the fleet.
    check_fleet_edges(ai_settings,aliens)
    aliens.update()

    #Look for alien-ship collisions.
    if pygame.sprite.spritecollideany(ship,aliens):
        ship_hit(ai_settings,stats,screen,ship,aliens,bullets)
    check_aliens_bottom(ai_settings,stats,screen,ship,aliens,bullets)

def check_aliens_bottom(ai_settings,stats,screen,ship,aliens,bullets):
    #Check if any aliens have reached the bottom of the screen.
    screen_rect=screen.get_rect()
    for alien in aliens.sprites():
        #print (alien.rect.y)
        #print (alien.rect.bottom)
        if alien.rect.bottom>=screen_rect.bottom:
            #Treat this the same as if the ship got hit.
            ship_hit(ai_settings,stats,screen,ship,aliens,bullets)
            #print (alien.rect.bottom)
            #return True
        #else:
        #   return False
            
        
def fire_bullet(ai_settings,screen,ship,bullets):
    #Fire a bullet if limit not reached yet.
    #Create a new bullet and add it to the bullets group
    if len(bullets)<ai_settings.bullet_allowed:
        new_bullet=Bullet(ai_settings,screen,ship)
        bullets.add(new_bullet)

def check_fleet_edges(ai_settings,aliens):
    #Respond appropriately if any aliens have reached an edge.
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break

def change_fleet_direction(ai_settings,aliens):
    #Drop the entire fleet and change the fleet direction.
    for alien in aliens.sprites():
        alien.rect.y+=ai_settings.fleet_drop_speed
    ai_settings.fleet_direction*=-1
    
def update_screen(ai_settings,screen,ship,aliens,bullets,play_button,stats,sb):
    #update images on the screen and flip the screen.
    screen.fill(ai_settings.bg_color)
    ship.blitme()
   # alien.blitme()
    aliens.draw(screen)
    sb.show_score()
    #aliens.draw(screen)
    #Redraw all bullets behind ship and aliens.
    for bullet in bullets.sprites():
        bullet.draw_bullets()

   # sb.show_score()
    if not stats.game_active:
        play_button.draw_button()
    #Make the most recently drawn visible.
    pygame.display.flip()


def check_high_scores(stats,sb):

    if stats.score>stats.high_score:
        stats.high_score=stats.score
        sb.prep_highscore()
