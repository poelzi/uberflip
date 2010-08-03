#!/usr/bin/python
# -*- coding: utf-8 -*-
import ci_init as ci
import ci_alarm

#####################################################################
# Modulo GFX 0.1.2 FLIP ALARM CLOCK PLANKTON
# Draw everythin happen on the screen
# Ciro Ippolito
# 20.00 02/21/2009
#####################################################################
# ************************************* BACKGROUNDS ******************************************************


def bg_clock():
    ci.cl_screen.blit(ci.cl_bground, (0, 0))  # Draw the CLOCK background


def bg_alarm():
    ci.al_screen.blit(ci.al_bground, (0, 0))  # Draw the ALARM background


def bg_about():
    try:
        ci.al_screen.blit(ci.us_bground, (0, 0))  # Draw the ABOUT background with the user background
    except:
        ci.pygame.draw.rect(ci.cl_screen, (ci.mr, ci.mg, ci.mb), (0, 0,
                            800, 480))
        pass
    ci.al_screen.blit(ci.ab_bground, (0, 0))  # Draw the ABOUT background with the backup background (root)
    ci.cl_screen.blit(ci.mood_bas, (0, 440))  # bottom light


def bg_windo():
    try:
        ci.al_screen.blit(ci.us_bground, (0, 0))  # Draw the WINDO background with the user background
    except:
        ci.pygame.draw.rect(ci.cl_screen, (ci.mr, ci.mg, ci.mb), (0, 0,
                            800, 480))
        pass
    ci.wi_screen.blit(ci.wi_bground, (0, 0))  # Draw the ALARM background


def bg_night():
    ci.wi_screen.blit(ci.ni_bground, (0, 0))  # Draw the ALARM background


# ************************************* MODES ******************************************************


def drawclock():
    ci.cl_screen.blit(ci.cl_numeri[int(ci.orario[11])],
                      ci.cl_coords['ore_decine'])  # ORE    (11ma lettera)
    ci.cl_screen.blit(ci.cl_numeri[int(ci.orario[12])],
                      ci.cl_coords['ore_unita'])
    ci.cl_screen.blit(ci.cl_numeri[int(ci.orario[14])],
                      ci.cl_coords['minuti_decine'])  # MINUTI (14ma lettera)
    ci.cl_screen.blit(ci.cl_numeri[int(ci.orario[15])],
                      ci.cl_coords['minuti_unita'])
    if ci.sw_help == 1:
        ci.cl_screen.blit(ci.gr_help[0], (210, 120))


def drawalarm():
    ci.al_screen.blit(ci.al_numeri[int(ci.al_edi[0])],
                      ci.al_coords['ore_decine'])  # ORE    (11ma lettera)
    ci.al_screen.blit(ci.al_numeri[int(ci.al_edi[1])],
                      ci.al_coords['ore_unita'])
    ci.al_screen.blit(ci.al_numeri[int(ci.al_edi[2])],
                      ci.al_coords['minuti_decine'])  # MINUTI (14ma lettera)
    ci.al_screen.blit(ci.al_numeri[int(ci.al_edi[3])],
                      ci.al_coords['minuti_unita'])
    if ci.sw_help == 1:
        ci.cl_screen.blit(ci.gr_help[1], (50, 5))


def drawwindo():  # ci.fcmode= 2
    if ci.sw_help == 1:
        ci.cl_screen.blit(ci.gr_help[3], (100, 20))
    ci.pygame.display.flip()


def drawnight():
    ci.ni_screen.blit(ci.ni_numeri[int(ci.orario[11])],
                      ci.ni_coords['ore_decine'])  # ORE    (11ma lettera)
    ci.ni_screen.blit(ci.ni_numeri[int(ci.orario[12])],
                      ci.ni_coords['ore_unita'])
    ci.ni_screen.blit(ci.ni_numeri[int(ci.orario[14])],
                      ci.ni_coords['minuti_decine'])  # MINUTI (14ma lettera)
    ci.ni_screen.blit(ci.ni_numeri[int(ci.orario[15])],
                      ci.ni_coords['minuti_unita'])
    if ci.sw_help == 1:
        ci.cl_screen.blit(ci.gr_help[0], (210, 120))


# ************************************* PARTS ******************************************************


def drawsveglia():
    (x0, y0, x1, y1) = ci.sv_coords
    if ci.fcmode == 0:  # ********************CLOCK SCREEN
        str_ala = '%d%d:%d%d' % (ci.sveglia[0], ci.sveglia[1],
                                 ci.sveglia[2], ci.sveglia[3])
    elif ci.fcmode == 1:

                                      # ********************ALARM SET SCREEN

        str_ala = ci.alarms[ci.bt_aledit]
        (
            posx,
            posy,
            x,
            y,
            posoff,
            poson,
            ) = ci.al_switch_coords
        drawswitch(
            ci.sw_config[0],
            posx,
            posy,
            x,
            y,
            posoff,
            poson,
            )
        (
            posx,
            posy,
            x,
            y,
            posoff,
            poson,
            ) = ci.mt_switch_coords
        drawswitch(
            ci.sw_config[1],
            posx,
            posy,
            x,
            y,
            posoff,
            poson,
            )
    elif ci.fcmode == 3:

                                      # ****************** WINDO MODE

        str_ala = '%d%d:%d%d' % (ci.sveglia[0], ci.sveglia[1],
                                 ci.sveglia[2], ci.sveglia[3])
        (
            posx,
            posy,
            x,
            y,
            posoff,
            poson,
            ) = ci.al_switch_coords
        drawswitch(
            ci.sw_config[0],
            posx - 80,
            posy - 59,
            x,
            y,
            posoff - 80,
            poson - 80,
            )
        (
            posx,
            posy,
            x,
            y,
            posoff,
            poson,
            ) = ci.mt_switch_coords
        drawswitch(
            ci.sw_config[1],
            posx - 80,
            posy - 59,
            x,
            y,
            posoff - 80,
            poson - 80,
            )
        y0 = y0 - 60
    elif ci.fcmode == 4:

                                      # ****************** NIGHT MODE

        str_ala = '%d%d:%d%d' % (ci.sveglia[0], ci.sveglia[1],
                                 ci.sveglia[2], ci.sveglia[3])
    elif ci.fcmode == 5:

                                      # ****************** ALARM PLAYING

        str_ala = '%d%d:%d%d' % (ci.sveglia[0], ci.sveglia[1],
                                 ci.sveglia[2], ci.sveglia[3])
    if ci.sw_config[0] == 1:  # Alarm ON
        msg = ci.font.render(str_ala, True, (ci.mr, ci.mg, ci.mb))  # alarm string (armed)
        ci.cl_screen.blit(msg, (x0, y0))
        msg = ci.font1.render('ALARM', True, (ci.mr, ci.mg, ci.mb))
        ci.cl_screen.blit(msg, (x0 + 27, y0 - 11))
        msg = ci.font1.render('ENGAGED', True, (ci.mr, ci.mg, ci.mb))
        ci.cl_screen.blit(msg, (x0 + 17, y0 + 43))
    elif ci.sw_config[0] == 0:

                                           # Alarm OFF

        msg = ci.font.render(str_ala, True, (110, 110, 110))  # alarm string (disarmed)
        ci.cl_screen.blit(msg, (x0, y0))
    elif ci.sw_config[0] == 2:

                                         # Alarm Playing

        msg = ci.font.render(str_ala, True, (ci.mr, ci.mg, ci.mb))
        ci.cl_screen.blit(msg, (x0, y0))
        msg = ci.font1.render('ALARM', True, (ci.mr, ci.mg, ci.mb))
        ci.cl_screen.blit(msg, (x0 + 27, y0 - 11))
        msg = ci.font1.render('ENGAGED', True, (ci.mr, ci.mg, ci.mb))
        ci.cl_screen.blit(msg, (x0 + 17, y0 + 43))


#  drawcountdown()


def drawmood():
    if ci.fcmode == 0:
        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 20))  # top light
        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 380))  # bottom light
    elif ci.fcmode == 1:
        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 20))  # top light
        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 70))  # bottom light
    elif ci.fcmode == 2:
        pass
    elif ci.fcmode == 3:

    # ci.cl_screen.blit(ci.mood_bas,(0,440))            ....#bottom light
                                                                      # WINDO MODE

        ci.cl_screen.blit(ci.mood_col[ci.moodc], (0, 0))  # top light
    elif ci.fcmode == 5:

                                                                      # Alarm is playing

        ci.pygame.draw.rect(ci.cl_screen, (255, 255, 255), (0, 380,
                            800, 100))
        ci.cl_screen.blit(ci.mood_col[2], (0, 380))  # bottom light
    if ci.tablet:
        ci_alarm.led()
    ci.pygame.display.flip()


def drawluxgraph(x, y):
    mins = 0
    pos = 0
    while 1:
        mins = mins + 1
        pos = pos + 1
        if pos > 300:
            pos = 0
        try:
            ci.pygame.draw.line(ci.cl_screen, (ci.r, ci.g, ci.b), (x
                                + mins - 1, y - ci.luxlog[mins - 1]),
                                (x + mins, y - ci.luxlog[mins]), 1)
        except:

      # moltiplica l'asse X se vuoi una scala differente

            return


def drawcountdown():
    (x0, y0, x1, y1) = ci.sv_coords
    if ci.fcmode == 3:
        y1 = y1 - 60
    stringaremain = str(ci.remaing[0]) + str(ci.remaing[1]) + ':' \
        + str(ci.remaing[2]) + str(ci.remaing[3])
    msg = ci.font1.render(stringaremain, True, (120, 120, 120))
    msg = ci.pygame.transform.rotate(msg, 90)
    ci.cl_screen.blit(msg, (x1, y1))
    if ci.fcmode == 1:
        drawallsched()


def drawallsched():
    x = 0
    daystr = ci.alarms[0]
    if ci.bt_aledit == 7:
        ci.pygame.draw.rect(ci.cl_screen, (40, 40, 40), (645, 475, 32,
                            5))
    for d in range(0, 7):
        daystr = ci.alarms[d]
        msg = ci.font1.render(daystr, True, (40, 40, 40))
        msg = ci.pygame.transform.rotate(msg, 90)
        if ci.al_set == d:
            ci.pygame.draw.rect(ci.cl_screen, (125, 180, 60), (321 + x,
                                391, 29, 57))
        ci.cl_screen.blit(msg, (322 + x, 393))
        if ci.bt_aledit == d:
            ci.pygame.draw.rect(ci.cl_screen, (40, 40, 40), (320 + x,
                                475, 32, 5))
            msg = ci.font1.render(str(d + 1), True, (30, 30, 30))
            ci.cl_screen.blit(msg, (240, 330))
        x = x + 50


def changecaption():
    ci.pygame.display.set_caption(ci.orario[11:16] + ' - '
                                  + ci.orario[0:10] + 'th '
                                  + ci.orario[20:24])


def drawdate():
    (x0, y0, x1, y1) = ci.date_coords
    if ci.fcmode == 3:
        y0 = y0 - 55
        y1 = y1 - 55
    dayn = ci.orario[0:3]
    dday = ci.orario[8:10]
    mont = ci.orario[4:7]
    year = ci.orario[20:25]
    msg = ci.font1.render('%s - %s' % (mont, year), True, (55, 55, 55))
    ci.cl_screen.blit(msg, (x0, y0))

  # [DEBUG]msg=ci.font.render(("Thu - 20 th"),True,(20,20,20))

    msg = ci.font.render('%s - %s th' % (dayn, dday), True, (55, 55,
                         55))
    ci.cl_screen.blit(msg, (x1, y1))  # mont year


def gfx_refresh():
    ci.pygame.display.flip()


def drawswitch(
    switch,
    posx,
    posy,
    x,
    y,
    posoff,
    poson,
    ):
    if switch == 0:  # Switch OFF
        ci.al_screen.set_clip(posx, posy, x, y)
        ci.al_screen.blit(ci.onoff_switch[1], (posoff, posy + 1))
        ci.al_screen.blit(ci.onoff_switch[0], (posx, posy))
        ci.al_screen.set_clip(0, 0, 800, 480)
    elif switch == 1:

                              # Switch ON

        ci.al_screen.set_clip(posx, posy, x, y)
        ci.al_screen.blit(ci.onoff_switch[1], (poson, posy + 1))
        ci.al_screen.blit(ci.onoff_switch[0], (posx, posy))
        ci.al_screen.set_clip(0, 0, 800, 480)


# [DEBUG] pygame.draw.rect(Surface, (255, 255, 255), (0, 0, height, height))
