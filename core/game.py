"""Legacy Shining Soul runtime adapted to a modular project layout.

This module preserves original game mechanics while loading settings and assets
through modern project structure helpers.
"""

from pygame import *
from random import *

from config import GAME_SETTINGS, asset_path
from core.camera import Camera
from core.input import read_input
from core.mechanics import (
    ai_move,
    choose_direction,
    direct_get_attacked,
    direction_to_index,
    enemy_sprite_size,
    fallback_directions,
    generate_enemies,
    is_all_clear,
    move_self,
    sprite_mode_index,
)
from core.rendering import (
    character_blit as render_character_blit,
    draw_blade_block as render_draw_blade_block,
    draw_enemy as render_draw_enemy,
    draw_hp_bar as render_draw_hp_bar,
    draw_knife as render_draw_knife,
    draw_round_label as render_draw_round_label,
    draw_self as render_draw_self,
)
from core.screens import (
    apply_levelup_option,
    gameover_hover_option,
    help_hover_option,
    levelup_hover_option,
    menu_hover_option,
    skill_hover_option,
    story_hover_option,
)
from entities.models import SkillTree
from utils import geometry as geom
from utils.loaders import load_resource_bundle

#---------------functions----------------------------#
def nuke():#for testing
    if keys[K_i]:
        while mapenemyx!=[]:
            AIgetkilled(0)                
def note(a):#returns if the number put in is -,0,or+ by returning -1,0,1
    return geom.note(a)
def dist(x1,y1,x2,y2):#return the distance between two points
    return geom.dist(x1,y1,x2,y2)
def remove(rlist,unit):#remove the an element of a list
    return geom.remove(rlist,unit)
def midpointrect(x,y,l,h):#create a rect that the midpoint is x,y
    return geom.midpointrect(x,y,l,h)
def treeblockrect(x,y):#put in the topleft corner of a tree and return a tree's blocking rect
    return geom.treeblockrect(x,y)
def collideanyrect(rec,reclist):#return if the rect collide with any of the rect in the list or not
    return geom.collideanyrect(rec,reclist)
#direction: a cooridinate [x,y] that represents the direction that AI will go. for example, [-1,-1] means going left and up
def getdirect(ex,ey,sx,sy):     #return all the possible direction that will go
    return fallback_directions(ex,ey,sx,sy)
def choosedirect(d,sx,sy,ex,ey,exlist,eylist,blockrect,enemysize,ve):#check which direction in the 2dlist from getdirect() works and return it
    return choose_direction(d,sx,sy,ex,ey,exlist,eylist,blockrect,enemysize,ve)
def AImove(sx,sy,ex,ey,ve,direct):                              #moves AI by using the direction got from
    return ai_move(sx,sy,ex,ey,ve,direct)
def moveself(mapselfx,mapselfy,exlist,eylist,esize,blockrect):#move the character with keyboard
    global selfsize,selfdirectionx,selfdirectiony,vself,keys
    mapselfx,mapselfy,selfdirectionx,selfdirectiony = move_self(
        mapselfx,
        mapselfy,
        exlist,
        eylist,
        esize,
        blockrect,
        selfsize,
        vself,
        bool(keys[K_UP]),
        bool(keys[K_DOWN]),
        bool(keys[K_RIGHT]),
        bool(keys[K_LEFT]),
    )
    return mapselfx,mapselfy
def backtorange(mpselfx,mpselfy,selfsize,mapsize):#anything that is out of the map will be pull back to the map
    return geom.backtorange(mpselfx,mpselfy,selfsize,mapsize)
def screenoutputdata(mpselfx,mpselfy,mpenemyx,mpenemyy,mptreex,mptreey,mpblock,mapsize,knife):          #change everything from the coordinate on the map to 
    global camera,selfsize,enemysize
    return camera.project(
        mpselfx,
        mpselfy,
        mpenemyx,
        mpenemyy,
        mptreex,
        mptreey,
        mapsize,
        knife,
        selfsize,
        enemysize,
        treeblockrect,
    )
def directgetatked(sx,sy,sz,ex,ey,ez):#returns a direction that the AI is atk later
    return direct_get_attacked(sx,sy,sz,ex,ey,ez)
def directinstr(status):#trun a direction in coordinate form into a var which relates to a certain position in sprite pics list
    return direction_to_index(status)
def checkallclear():#check if all enemies are dead
    return is_all_clear(mapenemyx)
def characterblit(ima,pt,lock,sz):#blit character/enemy sprite with a corner(tl,tr,dl,dr,mid) locked
    render_character_blit(screen, ima, pt, lock, sz)
def mode(status,cha):#return the mode of character/enemy in a string and them turn it into a number by using the sprmode list
    return sprite_mode_index(status,cha,selfsprmode,enesprmode)
def enesprsize(status):#the size of the enemy sprite changes when the direction is not the same so this function use direction to adjust the size of the enemy
    return enemy_sprite_size(status)
def enemygenerater():#generate enemies in random position for each round
    global mapselfx,mapselfy,mapblockrect,gamelevel
    return generate_enemies(
        mapselfx,
        mapselfy,
        mapblockrect,
        gamelevel,
        mapsize,
        enemysize,
        selfsize,
    )
def drawself():#draw the character
    render_draw_self(
        screen,
        selfpic,
        frameselfstatus,
        selfstatus,
        selfsprmode,
        lock,
        scrselfx,
        scrselfy,
        selfframedelay,
    )
def drawenemy():#draw all the enemies and it works the same way as drawself()
    render_draw_enemy(
        screen,
        enemypic,
        frameenemystatus,
        enemystatus,
        enesprmode,
        enemylock,
        screnemyx,
        screnemyy,
        enemyframedelay,
    )
def drawknife():#draw all the knifes in the air
    render_draw_knife(screen,selfknife,selfpic,kniferange)
def drawhpbar():#draw the health bar on the screen
    render_draw_hp_bar(screen,hpbarpic,hpfont,selfstatus,selfhp)
def drawround():#draw the round number on the screen
    render_draw_round_label(screen,hpfont,gamelevel)
def drawbladeblock():#whenever "blade block" works, it will tell the player by showing him/her the word "block" on the top of the character
    global showblock
    render_draw_blade_block(screen,bladeblockpic,showblock,scrselfx,scrselfy)
def AIgetkilled(i):#if an AI get killed, remove all the data about it
    del mapenemyx[i],mapenemyy[i],screnemyx[i],screnemyy[i],enemystatus[i],frameenemystatus[i]
    enemydeadsound.play()
def selfmodechanging():#change the type of motion of the character based on the keyboard action
    """Update player mode state based on current input and cooldowns."""
    global selfstatus,scrmode,frameselfstatus
    if selfstatus[2]<=0:
        selfstatus[4]="dead"
        selfstatus[2]=0
        frameselfstatus[3]=0#avoid crushing
    if selfstatus[3]==0 and selfstatus[4]!="dead":
        if keys[K_a] and not okeys[K_a]:#switch weapon
            selfstatus[5]+=1
            selfstatus[5]=selfstatus[5] % 2
        if keys[K_z] and not okeys[K_z]:#atk
            selfstatus[4]="atk"
            if selfstatus[5]==0:              #the character should not atk "continueously" and it should be controled by attack speed
                selfstatus[3]+=selfbladeatkcd
            elif selfstatus[5]==1:
                selfstatus[3]+=selfdartatkcd
        elif (keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT]):#this is mainly for sprites bliting
            selfstatus[4]="move"
        if (not keys[K_a] and not keys[K_z] and not (keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT])) or (selfstatus[4]=="atk" and selfstatus[3]==0):
            selfstatus[4]=""                    #doing nothing                                                                  #makes a break between two atks 
    if selfstatus[3]>0:#stun recover
        selfstatus[3]-=1
    if selfstatus[4]=="dead":
        scrmode="gameover"
        mixer.music.stop()
def enemymodechanging():#change the type of motion of the enemy based on the AI functions
    """Update enemy finite-state machine for move, pre-attack, attack, and death."""
    global enemystatus
    for i in range(len(enemystatus)):
        if enemystatus[i][3]==0 and enemystatus[i][4]!="dead":
            if directgetatked(mapselfx,mapselfy,selfsize,mapenemyx[i],mapenemyy[i],enemysize)==False and enemystatus[i][4]!="preatk":
                enemystatus[i][4]="move"
            if  directgetatked(mapselfx,mapselfy,selfsize,mapenemyx[i],mapenemyy[i],enemysize)!=False and oenemystatus[i][4]!="preatk" and enemystatus[i][3]==0:
                enemystatus[i][4]="preatk"          #give player time to escape
                enemystatus[i][3]+=enemypreatkstun  #
                enemystatus[i][0],enemystatus[i][1]=directgetatked(mapselfx,mapselfy,selfsize,mapenemyx[i],mapenemyy[i],enemysize)[0],directgetatked(mapselfx,mapselfy,selfsize,mapenemyx[i],mapenemyy[i],enemysize)[1]
            if enemystatus[i][4]=="preatk" and enemystatus[i][3]==0:#deal damage
                enemystatus[i][4]="atk"
        if enemystatus[i][2]<=0:
            enemystatus[i][4]="dead"
        if enemystatus[i][3]>0:
            enemystatus[i][3]-=1
        if enemystatus[i][4]=="dead":
            AIgetkilled(i)
            break
def selfrege():#selfregeneration
    global regecounter,selfstatus
    regecounter+=1
    if regecounter>59 and selfstatus[2]<selfhp:
        selfstatus[2]+=1
        regecounter=0
def enemymove():#use choosedirect,getdirect,AImove to move enemy
    global mapenemyx,mapenemyy,enemydirect,enemystatus
    for i in range(len(mapenemyx)):
        if enemystatus[i][4]=="move":
            enemydirect[i]=choosedirect(getdirect(mapenemyx[i],mapenemyy[i],mapselfx,mapselfy),mapselfx,mapselfy,mapenemyx[i],mapenemyy[i],mapenemyx,mapenemyy,mapblockrect,enemysize,venemy)
            enemystatus[i][0],enemystatus[i][1]=enemydirect[i][0],enemydirect[i][1]
            mapenemyx[i],mapenemyy[i]=AImove(mapselfx,mapselfy,mapenemyx[i],mapenemyy[i],venemy,enemydirect[i])
def selfmove():#use moveself() to move the character
    global selfstatus,mapselfx,mapselfy
    if selfstatus[4]=="move":
        mapselfx,mapselfy=moveself(mapselfx,mapselfy,mapenemyx,mapenemyy,enemysize,mapblockrect)
        if (selfdirectionx,selfdirectiony)!=(0,0):
            selfstatus[0],selfstatus[1]=selfdirectionx,selfdirectiony
def getframedata():#get the information from status in order to draw the character/enemy
    global frameselfstatus,frameenemystatus
    if (selfstatus[0],selfstatus[1])!=(0,0):
        frameselfstatus[0],frameselfstatus[1]=selfstatus[0],selfstatus[1]
    for i in range(len(mapenemyx)):
        if (enemystatus[i][0],enemystatus[i][1])!=(0,0):
            frameenemystatus[i][0],frameenemystatus[i][1]=enemystatus[i][0],enemystatus[i][1]
def block():#returns T/F that if block is active or not based on the level of bladeblock
    prob=skill_tree.blade_block*5
    tem=randint(1,100)
    if tem<=prob:
        return True
    return False
def AIatk():#if mode of enemy is deal damage, deal damage to the same direction of preatk
    """Resolve enemy attacks against player including block chance feedback."""
    global selfstatus,enemystatus,showblock
    for i in range(len(enemystatus)):
        if oenemystatus[i][4]=="preatk" and enemystatus[i][4]=="atk" and selfstatus[4]!="dead":
            enemyatkrect=midpointrect(mapenemyx[i]+enemystatus[i][0]*enemysize,mapenemyy[i]+enemystatus[i][1]*enemysize,enemyatkrange,enemyatkrange)
            tem=block()
            if midpointrect(mapselfx,mapselfy,selfsize,selfsize).colliderect(enemyatkrect)==True and selfstatus[4]!="dead":
                if (selfstatus[5]==0 and tem==False) or selfstatus[5]==1:#if blade block not active or chara is using dart
                    getdamagesound.play()
                    selfstatus[4]="damage"######
                    selfstatus[2]-=enemyatk
                    if selfstatus[2]<0:
                        selfstatus[2]=0
                    selfstatus[3]=enemyatkstun########
            enemystatus[i][3]+=enemyatkcd
            if tem==True and selfstatus[5]==0:
                showblock.append(20)
                blocksound.play()
def dartmodeatk():#check if the dart hit or not in dart mode
    """Spawn, move and resolve dart projectile collisions."""
    global selfstatus,selfknife,enemystatus,frameenemystatus
    if selfstatus[5]==1 and selfstatus[4]=="atk" and selfstatus[3]==selfdartatkcd-1:#create dart
        selfknife.append([selfstatus[0],selfstatus[1],mapselfx,mapselfy,0,0,0,0])
        knifesound.play()
    for n in selfknife:#move dart
        if n[0]!=0 and n[1]!=0: 
            n[2],n[3]=n[2]+n[0]*vknife/(2**0.5),n[3]+n[1]*vknife/(2**0.5)
        else:
            n[2],n[3]=n[2]+n[0]*vknife,n[3]+n[1]*vknife
        n[7]=midpointrect(n[2],n[3],knifesize,knifesize)
    for n in selfknife:#deals damage
        for i in range(len(mapenemyx)):
            if n[7].colliderect(midpointrect(mapenemyx[i],mapenemyy[i],enemysize,enemysize)):
                hitsound.play()
                enemystatus[i][3]=selfdartatkstun
                enemystatus[i][2]-=selfdartatk
                enemystatus[i][4]="damage"
                frameenemystatus[i][3]=0
                del selfknife[selfknife.index(n)]
                break
def blademodeatk():#checks if deals damage to enemy on blade mode
    """Resolve melee blade damage and life-steal when attack hitbox collides."""
    global selfstatus, enemystatus, frameenemystatus,mapselfatkrect
    if selfstatus[4]=="atk" and selfstatus[5]==0:
        mapselfatkrect=midpointrect(mapselfx+selfstatus[0]*selfsize,mapselfy+selfstatus[1]*selfsize,selfatkrange,selfatkrange)
        if selfstatus[3]==10:
            bladesound.play()
    if mapselfatkrect!=0:
        for i in range(len(mapenemyx)):
            if selfstatus[5]==0 and mapselfatkrect.colliderect(midpointrect(mapenemyx[i],mapenemyy[i],enemysize,enemysize))==True and oselfstatus[4]!="atk" and selfstatus[4]=="atk":
                hitsound.play()
                enemystatus[i][3]=selfbladeatkstun
                enemystatus[i][2]-=selfbladeatk
                enemystatus[i][4]="damage"
                selfstatus[2]+=skill_tree.blade_lifesteal*4
                if selfstatus[2]>selfhp:
                    selfstatus[2]=selfhp
                frameenemystatus[i][3]=0
def allbacktorange():#use backtorange to both enemy and character
    global mapselfx,mapselfy,mpenenyx,mpenemyy
    mapselfx,mapselfy=backtorange(mapselfx,mapselfy,selfsize,mapsize)
    for i in range(len(mapenemyx)):
        mapenemyx[i],mapenemyy[i]=backtorange(mapenemyx[i],mapenemyy[i],enemysize,mapsize)
def framereset():#reset the framepic position everytime the mode changes so it wont crush
    global frameselfstatus,frameenemystatus
    for i in range(len(enemystatus)):
        if enemystatus[i][4]!=oenemystatus[i][4]:
            frameenemystatus[i][3]=0
    if selfstatus[4]!=oselfstatus[4]:
        frameselfstatus[3]=0
def levelupreset():#update the datas of the character after levelup the skills
    """Recompute derived combat values from the current skill tree."""
    global mapx,mapy,mapselfx,mapselfy,mapselfox,mapselfoy,mapselfatkrect,scrselfx,scrselfy,selfknife,maptreex,maptreey,scrtreex,scrtreey,mapblockrect,scrblockrect
    global mapenemyx,mapenemyy,mapenemyox,mapenemyoy,screnemyx,screnemyy,vself,venemy,vknife,selfsize,enemysize,selfhp,enemyhp,selfstatus,enemystatus,oenemystatus
    global selfatkrange,enemyatkrange,selfbladeatkcd,selfdartatkcd,selfbladeatkstun,selfdartatkstun,enemypreatkstun,enemyatkcd,enemyatkstun,knifesize,kniferange,selfdirectionx,selfdirectiony
    global enemyatk,selfbladeatk,selfdartatk,mapsize,selflevel,gamelevel,enemydirect,frameselfstatus,selfframedelay,frameenemystatus,enemyframedelay
    global skill_tree
    vself=4+skill_tree.move_speedup*2
    selfhp=100+skill_tree.max_hp*30

    selfdartatkcd=int(27/1.0/(skill_tree.dart_attack_speedup*0.6+1))


    selfbladeatkstun=30+skill_tree.blade_stun*15
    selfdartatkstun=15+skill_tree.dart_stun*8
    kniferange=10+skill_tree.dart_rangeup*3
    selfbladeatk=40+skill_tree.blade_powerup*6
    selfdartatk=20+skill_tree.dart_powerup*5
def allreset():#reset everything when you restart the game
    """Reset full runtime state to start a new run from main menu."""
    global mapx,mapy,mapselfx,mapselfy,mapselfox,mapselfoy,mapselfatkrect,scrselfx,scrselfy,selfknife,maptreex,maptreey,scrtreex,scrtreey,mapblockrect,scrblockrect
    global mapenemyx,mapenemyy,mapenemyox,mapenemyoy,screnemyx,screnemyy,vself,venemy,vknife,selfsize,enemysize,selfhp,enemyhp,selfstatus,enemystatus,oenemystatus
    global selfatkrange,enemyatkrange,selfbladeatkcd,selfdartatkcd,selfbladeatkstun,selfdartatkstun,enemypreatkstun,enemyatkcd,enemyatkstun,knifesize,kniferange,selfdirectionx,selfdirectiony
    global enemyatk,selfbladeatk,selfdartatk,mapsize,selflevel,gamelevel,enemydirect,frameselfstatus,selfframedelay,frameenemystatus,enemyframedelay
    global skill_tree
    mapx,mapy=0,0
    mapselfx,mapselfy=400,300
    mapselfox,mapselfoy=0,0
    mapselfatkrect=0
    scrselfx,scrselfy=0,0
    selfknife=[]
    maptreex,maptreey=[],[]
    scrtreex,scrtreey=[],[]
    mapblockrect=[]
    scrblockrect=[]
    mapenemyx,mapenemyy=[],[]
    mapenemyox,mapenemyoy=[],[]
    screnemyx,screnemyy=[],[]
    for i in range(len(blockpos)):
        if i%2==0:
            maptreex.append(int(blockpos[i]))
            mapblockrect.append(treeblockrect(int(blockpos[i]),int(blockpos[i+1])))
        else:
            maptreey.append(int(blockpos[i]))
    vself=4
    venemy=2
    vknife=20
    selfsize=50
    enemysize=60
    selfhp=100
    enemyhp=100
    selfatkrange=80
    enemyatkrange=75
    selfbladeatkcd=20
    selfdartatkcd=27
    selfbladeatkstun=15#stun the enemy
    selfdartatkstun=15
    enemypreatkstun=25#stun enemy itself
    enemyatkcd=14
    enemyatkstun=15
    knifesize=30
    kniferange=10
    selfdirectionx,selfdirectiony=0,0
    enemyatk=10
    selfbladeatk=40
    selfdartatk=20
    gamelevel=1
    mapsize=(4000,3000)
    mapenemyx,mapenemyy=enemygenerater()
    selfstatus=[1,0,selfhp,0,"",0]#0 dx,1 dy,2 hp,3 stuntime,4 mode,5.blade(0)or dart(1) !!!!and mode can be "atk" "move" "dead"
    enemystatus,oenemystatus=[0]*len(mapenemyx),[0]*len(mapenemyx)
    for i in range(len(mapenemyx)):
        enemystatus[i]=[1,0,enemyhp,0,""]#0 dx,1 dy,2 hp,3 stuntime,4 mode !!!!and mode can be "preatk"(allow player to escape) "atk" "move" "dead"
    scrtreex,scrtreey=[0]*len(maptreex),[0]*len(maptreex)
    mapenemyox,mapenemyoy,screnemyx,screnemyy,enemydirect=[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx)
    scrblockrect=scrtreex
    frameselfstatus=[0,0,0,0]#dx,dy,frstun,frame
    selfframedelay=5
    frameenemystatus=[0]*len(mapenemyx)
    for i in range(len(mapenemyx)):
        frameenemystatus[i]=[0,0,0,0]#dx,dy,frstun,frame
    skill_tree=SkillTree()
    mixer.music.load(asset_path("sound", "background.wav"))
    mixer.music.play(-1)
def roundreset():#reset the enemys and their status at the beginning of each round
    """Advance to next round and regenerate enemies with scaled difficulty."""
    global mapx,mapy,mapselfx,mapselfy,mapselfox,mapselfoy,mapselfatkrect,scrselfx,scrselfy,selfknife,maptreex,maptreey,scrtreex,scrtreey,mapblockrect,scrblockrect
    global mapenemyx,mapenemyy,mapenemyox,mapenemyoy,screnemyx,screnemyy,vself,venemy,vknife,selfsize,enemysize,selfhp,enemyhp,selfstatus,enemystatus,oenemystatus
    global selfatkrange,enemyatkrange,selfbladeatkcd,selfdartatkcd,selfbladeatkstun,selfdartatkstun,enemypreatkstun,enemyatkcd,enemyatkstun,knifesize,kniferange,selfdirectionx,selfdirectiony
    global enemyatk,selfbladeatk,selfdartatk,mapsize,selflevel,gamelevel,enemydirect,frameselfstatus,selfframedelay,frameenemystatus,enemyframedelay,endingpic,scrmode
    global scrmode,skill_tree
    endingpic=screen.subsurface(Rect(0,0,resolution[0],resolution[1])).copy()
    venemy=2+0.08*gamelevel
    if venemy>5:
        venemy=5
    enemyhp=100+8*gamelevel
    enemyatkcd=14
    enemyatk=10+0.5*gamelevel
    gamelevel+=1
    mapenemyx,mapenemyy=enemygenerater()
    enemystatus,oenemystatus=[0]*len(mapenemyx),[0]*len(mapenemyx)
    for i in range(len(mapenemyx)):
        enemystatus[i]=[1,0,enemyhp,0,""]#0 dx,1 dy,2 hp,3 stuntime,4 mode !!!!and mode can be "preatk"(allow player to escape) "atk" "move" "dead"
        oenemystatus[i]=[1,0,enemyhp,0,""]
    mapenemyox,mapenemyoy,screnemyx,screnemyy,enemydirect=[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx)
    frameenemystatus=[0]*len(mapenemyx)
    for i in range(len(mapenemyx)):
        frameenemystatus[i]=[0,0,0,0]#dx,dy,frstun,frame
    scrmode="levelup"
    if gamelevel%5==0 and ogamelevel!=gamelevel:#every 5 level you get a credit
        skill_tree.move_speedup_credit+=1
    levelupsound.play()
def levelup():#the levelup screen of the game
    """Handle level-up UI interactions and apply selected skill upgrades."""
    global scrmode,skill_tree
    mx,my=mouse.get_pos()
    mb=mouse.get_pressed()
    n=levelup_hover_option(mx,my,skill_tree)
    if mb[0]==1 and omb[0]!=1:
        if apply_levelup_option(n,skill_tree):
            yessound.play()
    levelupreset()
    if mb[0]==1 and omb[0]!=1 and n!=0:
        scrmode="mainloop"
    screen.blit(endingpic,(0,0))
    screen.blit(leveluppic[n],(0,0))
    display.flip()
def menu():#the main menu of the game
    """Render and handle main menu interactions."""
    global scrmode
    mx,my=mouse.get_pos()
    mb=mouse.get_pressed()
    n=menu_hover_option(mx,my)
    if mb[0]==1 and omb[0]!=1:
        if n==1:
            scrmode="mainloop"
            allreset()
        elif n==2:
            scrmode="help"
        elif n==3:
            scrmode="story"
    screen.blit(menupic[n],(0,0))
    display.flip()

def gameover():#the game over screen of the game
    """Render and handle game-over screen interactions."""
    global scrmode
    mx,my=mouse.get_pos()
    mb=mouse.get_pressed()
    n=gameover_hover_option(mx,my)
    if n==0 and mb[0]==1 and omb[0]!=1:
        scrmode="menu"
    screen.blit(gameoverpic[n],(0,0))
    display.flip()
def helpscr():#the help screen of the game
    """Render and handle help screen navigation."""
    global scrmode
    mx,my=mouse.get_pos()
    mb=mouse.get_pressed()
    n=help_hover_option(mx,my)
    if mb[0]==1 and omb[0]!=1:
        if n==2:
            scrmode="menu"
        elif n==0:
            scrmode="skillscr"
    screen.blit(helppic[n],(0,0))
    display.flip()
def story():#the story screen
    """Render and handle story screen navigation."""
    global scrmode
    mx,my=mouse.get_pos()
    mb=mouse.get_pressed()
    n=story_hover_option(mx,my)
    if n==1 and mb[0]==1 and omb[0]!=1:
        scrmode="menu"
    screen.blit(storypic[n],(0,0))
    display.flip()
def skillscr():#the skill explanation screen
    """Render and handle skill explanation screen navigation."""
    global scrmode
    mx,my=mouse.get_pos()
    mb=mouse.get_pressed()
    n=skill_hover_option(mx,my)
    if n==1 and mb[0]==1 and omb[0]!=1:
        scrmode="help"
    screen.blit(skillpic[n],(0,0))
    display.flip()
def mainloop():#the main program of the game
    """Execute one frame of gameplay state update and rendering."""
    global mapselfatkrect,keys,mapselfx,mapselfy,mapx,mapy,scrselfx,scrselfy,screnemyx,screnemyy,scrtreex,scrtreey,scrblockrect,selfknife
    global mapselfox,mapselfoy,mapenemyox,mapenemyoy,okeys,selfdirectionx,selfdirectiony,oselfstatus,oenemystatus
    mapselfox,mapselfoy=mapselfx,mapselfy
    mapenemyox,mapenemyoy=mapenemyx[:],mapenemyy[:]
    okeys=tuple(keys)
    ogamelevel=gamelevel
    selfdirectionx,selfdirectiony=0,0
    oselfstatus=selfstatus[:]
    for i in range(len(enemystatus)):
        oenemystatus[i]=enemystatus[i][:] 
    mapselfatkrect=0
    keys = key.get_pressed()
    #####map analyzing#####
    nuke()
    if checkallclear()==True:
        roundreset()
    selfmodechanging()
    enemymodechanging()
    selfrege()
    enemymove()
    selfmove()
    AIatk()
    dartmodeatk()
    blademodeatk()
    allbacktorange()
    framereset()
    #------------------start drawing everything------------#
    getframedata()
    mapselfx,mapselfy,mapx,mapy,scrselfx,scrselfy,screnemyx,screnemyy,scrtreex,scrtreey,scrblockrect,selfknife=screenoutputdata(mapselfx,mapselfy,mapenemyx,mapenemyy,maptreex,maptreey,mapblockrect,mapsize,selfknife)
    screen.fill((0,0,0))
    screen.blit(gamemap,(mapx,mapy))
    for i in range(len(scrtreex)):
        screen.blit(treepic,(scrtreex[i],scrtreey[i]+200))
    drawself()
    drawknife()
    drawenemy()
    for i in range(len(scrtreex)):
        screen.blit(ballpic,(scrtreex[i],scrtreey[i]))
    drawhpbar()
    drawround()
    drawbladeblock()
    myClock.tick(tick)
    display.flip()

    
#-------------------initiating------------------------#
myClock = time.Clock()
running=True
font.init()
init()
hpfont = font.SysFont(GAME_SETTINGS.ui_font, 35)
resolution=GAME_SETTINGS.resolution
camera = Camera(resolution)
screen =display.set_mode(resolution)
blockpos=open(asset_path("blockpos.txt")).read().strip().split()#all the positions of the tree
keys = key.get_pressed()
mb=mouse.get_pressed()
omb=mouse.get_pressed()
#-------------------end of initiating-----------------#
#--------------------loading resources-----------------------#
resource_bundle = load_resource_bundle()

getdamagesound = resource_bundle.sounds.get_damage
hitsound = resource_bundle.sounds.hit
knifesound = resource_bundle.sounds.knife
levelupsound = resource_bundle.sounds.levelup
bladesound = resource_bundle.sounds.blade
yessound = resource_bundle.sounds.yes
blocksound = resource_bundle.sounds.block
enemydeadsound = resource_bundle.sounds.enemy_dead

gamemap = resource_bundle.ui.game_map
treepic = resource_bundle.ui.tree
ballpic = resource_bundle.ui.ball
hpbarpic = resource_bundle.ui.hp_bar
bladeblockpic = resource_bundle.ui.blade_block
menupic = resource_bundle.ui.menu
helppic = resource_bundle.ui.help
storypic = resource_bundle.ui.story
leveluppic = resource_bundle.ui.levelup
gameoverpic = resource_bundle.ui.gameover
skillpic = resource_bundle.ui.skill

up,upright,right,downright,down,downleft,left,upleft=0,1,2,3,4,5,6,7
selfsprmode = resource_bundle.characters.self_modes
enesprmode = resource_bundle.characters.enemy_modes
selfpic = resource_bundle.characters.self_sprites
lock = resource_bundle.characters.self_locks
enemypic = resource_bundle.characters.enemy_sprites
enemylock = resource_bundle.characters.enemy_locks
#-------------------end of loading image---------------#
#------------------position defining------------------#
#naming rule:frame+object+type of coordinate
mapx,mapy=0,0
#character
mapselfx,mapselfy=400,300
mapselfox,mapselfoy=0,0
mapselfatkrect=0
scrselfx,scrselfy=0,0
selfknife=[]#element:[0,0,0,0,0,0,0,0]dx,dy,mapx,mapy,scrx,scry,time,atkrect
#tree
maptreex,maptreey=[],[]
scrtreex,scrtreey=[],[]
#block
mapblockrect=[]
scrblockrect=[]
#enemy
mapenemyx,mapenemyy=[],[]
mapenemyox,mapenemyoy=[],[]
screnemyx,screnemyy=[],[]
#------------------end of pos defining----------------#
#------------------load vars---------------------#
for i in range(len(blockpos)):
    if i%2==0:
        maptreex.append(int(blockpos[i]))
        mapblockrect.append(treeblockrect(int(blockpos[i]),int(blockpos[i+1])))
    else:
        maptreey.append(int(blockpos[i]))
#----------------end of load var-----------------#
#----------------defining game data--------------------#
vself=5
venemy=2
vknife=20
selfsize=50
enemysize=60
selfhp=50
enemyhp=100
selfatkrange=75
enemyatkrange=75
selfbladeatkcd=25
selfdartatkcd=25
selfatkstun=20#stun the enemy
enemypreatkstun=25#stun enemy itself before atk
enemyatkcd=14
enemyatkstun=20
knifesize=30
kniferange=15
selfdirectionx,selfdirectiony=0,0
enemyatk=10
selfbladeatk=20
selfdartatk=10
selflevel=0
tick=GAME_SETTINGS.fps
regecounter=0
gamelevel=1
ogamelevel=1
mapsize=(4000,3000)
mapenemyx,mapenemyy=enemygenerater()
selfstatus=[1,0,selfhp,0,"",0]#0 dx,1 dy,2 hp,3 stuntime,4 mode,5.blade(0)or dart(1) !!!!and mode can be "atk" "move" "dead"
enemystatus,oenemystatus=[0]*len(mapenemyx),[0]*len(mapenemyx)
for i in range(len(mapenemyx)):
    enemystatus[i]=[1,0,enemyhp,0,""]#0 dx,1 dy,2 hp,3 stuntime,4 mode !!!!and mode can be "preatk"(allow player to escape) "atk" "move" "dead"
scrtreex,scrtreey=[0]*len(maptreex),[0]*len(maptreex)
mapenemyox,mapenemyoy,screnemyx,screnemyy,enemydirect=[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx),[0]*len(mapenemyx)
scrblockrect=scrtreex
endingpic=0
showblock=[]# the list of block fonts
####skills####
skill_tree=SkillTree()
#-----------------end of defining game data------------#
#-----------------frame data---------------------------#
scrmode="menu"#can be "menu", "level up", "mainloop", "gameover","skillscr","help","story"
frameselfstatus=[0,0,0,0]#dx,dy,frstun,frame
selfframedelay=5
frameenemystatus=[0]*len(mapenemyx)
for i in range(len(mapenemyx)):
    frameenemystatus[i]=[0,0,0,0]#dx,dy,frstun,frame
enemyframedelay=7
########################################################
#####################   MAIN   #########################
def run_game() -> None:
    """Run the legacy game loop using the modularized project layout."""
    global running, omb, mb, keys

    while running:
        for evnt in event.get():
            if evnt.type == QUIT:
                running = False

        frame_input = read_input(tuple(bool(button) for button in mb))
        omb = frame_input.previous_mouse_buttons
        mb = frame_input.mouse_buttons
        keys = frame_input.keys

        if scrmode=="menu":
            menu()
        if scrmode=="mainloop":
            mainloop()
        if scrmode=="gameover":
            gameover()
        if scrmode=="help":
            helpscr()
        if scrmode=="story":
            story()
        if scrmode=="levelup":
            levelup()
        if scrmode=="skillscr":
            skillscr()
    quit()


if __name__ == "__main__":
    run_game()
#I tried to organize/generalize my code as much as possible, but after making the basic structure, I just cannot hold the structure
#while adding new things, so it comes out pretty messy as what i have now.
#all the images, musics, and sound effects are from SEGA's GBA game "Shining Soul II"
