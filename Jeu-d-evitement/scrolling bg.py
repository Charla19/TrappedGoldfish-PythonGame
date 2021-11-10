import pygame
pygame.init()

window=pygame.display.set_mode((961,650))
bg=pygame.image.load('assets/splash.png')
bg_x=0
bg_y=0

run= True
while run:
    bg_rel_y=bg_y % bg.get_rect().width

    window.blit(bg,(bg_rel_y,0))
    if bg_rel_y < 961:
        window.blit(bg,(bg_rel_y-bg.get_rect().width,0))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
    bg_y-=1
    pygame.display.update()
pygame.quit()
quit()