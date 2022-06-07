import pygame
from pygame import mixer
import os


"""
Wichtig:
Spieler 1 Steuerung: A = Links;  D = Rechts;     W = Sprung;     R = Attacke 1;  T = Attacke 2
Spieler 2 Steuerung: Pfeiltaste Links = Links;   Pfeiltaste Rechts = Rechts;     Pfeiltaste Hoch = Sprung;   K = Attacke 1;  L = Attacke 2




Wenn man so will könnte das die Klasse Settings sein ich habe mich dagegen entschieden weil ich Ursprünglich mehrere Datein machen wollte und ich das dann leichter fand ohne eine Klasse zu machen.

Zu erst werden pygame und pygames mixer initializiert.
Als Nächstes werden die Standart Features für das Spiel erstellt.
wie z.b.: die Fenstergröße, der Fenster Titel, FPS, Dateipfad, Imagepfad, Audiopfad. 
"""
mixer.init()
pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 640
file_path = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(file_path, "images")
sound_path = os.path.join(file_path, "audio") 

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pyfighter")

clock = pygame.time.Clock()
fps = 60

"""
Hier werden einige Farb Variablen definiert die später benötigt werden. Die Farben verwende ich später für die Lebensanzeige, Score und Countdown.
Darunter werden game variablen definiert die ich fuer den Countdown Verwende und Score verwended werden.
Außerdem ein Couldown für einen Automatischen Neustart wenn einer spieler besiegt wurde.
Hier wird auch eine Lock variabel definiert die Solange False ist bis einer der Spieler tot ist.
"""

YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]          #Der erste Wert ist für den ersten Spieler der zweite für den zweiten Spieler. 
round_over = False
ROUND_OVER_COOLDOWN = 3000

"""
Hier fange ich an mit ein paar Variabeln die für das einladen der sprites benötigt werden. Da ich diese nicht einzeln per hand ausgeschnitten habe.
Die Sprite Sheets sind so aufgebaut, dass jede Animation seine eigene Reihe hat. z.B.: ist die Erste Reihe fuer die Idle Animation, die zweite fuer die Lauf Animation usw. 
Die Kästchen für die Einzelnen Frames sind immer gleich groß!

Die size ist wichtig damit das Programm spaeter weiß wie groß die einzelnen Sprite kaestchen im Sprite Sheet sind.
Scale ist wichtig um die Bilder richtig zu skalieren damit sie nicht zu klein sind.
Das Offset habe ich mit hilfe von ausprobieren gefunden da ich nicht genau wusste woran es gelegen hat, dass die Sprites verschoben waren.
Da es ein konstanter Fehler war konnte ich wenn auch nicht ganz sauber ihn damit beheben.

Die Zwei Listen die ich hier angelegt habe geben an wie viele frames die einzelnen Animationen lang sind.
Die Animationen vom Warrior haben z.b.: eine Idle Animations länge von 10 Frames, die Lauf Animation 8 Frames usw.
Da der Warrior und der Wizard nicht die selbe anzahl an Frames für jede Animation haben musste ich für jeden eine einzelne Liste erstellen
Die Listen werden später in der Fighter Klasse mit zwei verschachtelten for schleifen benutzt, um an die einzelnen Bitmaps aus dem Sprite sheet zu bekommen.
"""
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

warrior_animation_steps = [10, 8, 1, 7, 7, 3, 7]
wizard_animation_steps = [8, 8, 1, 8, 8, 3, 7]

"""
Hier habe ich die Hintergrundmusik eingeladen und die Lautstaerke eingestellt. 
Die Musik wird hier auch gestartet. Sie fängt leise an und nach 5 Sekunden ist sie bei der Maximalen Lautstärke.
Nachdem die Musik angefangen hat hört sie nicht mehr auf und spielt solange weiter bis das Spiel beendet.
"""
pygame.mixer.music.load(os.path.join(f"{sound_path}/music.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)

"""
Hier werden die benötigten Bilder eingeladen.
Am anfang lade ich das Bild für den Hintergrund ein und das Bild für den Sieg von einen Spieler über den Anderen.
Darüberhinaus werden auch die Sprite Sheets für den Magier und den Krieger geladen.
"""
background_image = pygame.image.load(f"{image_path}/background/background.png").convert_alpha()
victory_image = pygame.image.load(f"{image_path}/icons/victory.png").convert_alpha()

warrior_sheet = pygame.image.load(f"{image_path}/warrior/warrior.png").convert_alpha()
wizard_sheet = pygame.image.load(f"{image_path}/wizard/wizard.png").convert_alpha()

"""
Hier lege ich zwei Variabeln fest die den selben Font verwenden werden. Die eine Variabel verwende ich später für den Countdown und den anderen für den Score.
Ich habe zwei verschiedene Variabeln verwenden weil der Countdown und der Score verschiedene Größen haben sollen. 
"""
count_font = pygame.font.Font(f"{file_path}/fonts/turok.ttf", 100)
score_font = pygame.font.Font(f"{file_path}/fonts/turok.ttf", 30)


"""
Hier Fängt die Klasse Fighter an.

Zuerst wird der constructor erstellt das ist unsere __init__ Methode. Dort gebe ich der Klasse Fighter einige Attribute.
player ist wichtig um zu bestimmen um welchen Spieler es sich handelt. Darüberhinaus braucht man das Attribut player um herauszu finden wer der Gegner / Target ist. 
x und y beinhalten die Koordinaten für die Spieler. Die Spieler sind Rechtecke die für die Kollisions prüfung später wichtig werden
flip benutze ich damit sich die Spieler automatisch immer angucken.
data beinhaltet die groeße/Size, die Skalierung/Scale und das Offset. Diese Variabeln habe ich oberhalb der Fighter Klasse definiert.
In dem Attribut Sprite Sheet werden die einzelnen Sprite Sheets für den Warrior und den Wizard gespeichert.
In dem Attribut Animation Steps werden die zuvor erstellten Listen gespeichert 
"""
class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0 #0: idle Animation #1:Renn Animation #2:Sprung Animation #3: Erste Angriffs Animation #4: Zweite Angriffs Animation #5: Treffer Animation #6: Sterbe Animation #Die variabel wird später für das updaten der Animationen verwendet
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.velocity_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.hit = False
        self.health = 100
        self.alive = True
    
        """
        Hier werden die Bitmaps aus dem Sprite Sheet genommen und in die Liste 'animation_list' gespeichert

        Ich beginne mit der for schleife 'for x in range(animation)' dort loopt die schleife durch eine ganze animation.
        Die Schleife erstellt mehrere temporäre Bilder aus dem gesammten Sprite Sheet dafür werden die x und y Koordinaten gebraucht.
        Darüberhinaus muss man wissen wie Hoch und Breit die einzelnen Bilder sind. Das habe ich bereits in ein paar Variabeln weiter oben im programm code gespeichert.
        In der Zeile: sprite_sheet.subsurface 
        sieht die Klammer folgendermaßen aus: (x koordinate, y koordinate, breite, höhe).
        beim ersten bild ist x = 0 und y = 0 weil beide schleifen noch nicht durch gelaufen sind. so kann ich das nutzen um die Koordinaten zu bestimmen.
        Nachdem dieses kleinen Viereck mit hilfe der Koordinaten gefunden wurde werden sie in einer temporären Leeren Liste gespeichert. Nachdem das erledigt ist werden die Bilder auf die richtige Größe skaliert.
        Die richtig skalierten Bilder werden in die Leere Liste 'animation_list' gespeichert.  
        """
    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list


    """
    Hier werden die einzelnen Eingaben ausgewertet. Darüberhinaus sind wird dafür gesorgt das man nicht aus dem Bild laufen kann und einiges mehr.

    Zu erst erstelle ich ein paar Variabeln die ich in dieser Funktion benötigt werden.
    speed ist für den die geschwindigkeit der Spieler verantwortlich
    gravity ist für die Schwerkraft verantwortlich diese gibt an wie schnell der Spieler wieder runter fällt
    Ich habe es so gemacht das alles nur temporaer ist indem ich ueberpruefe of die Taste gedrückt gehalten wird
    """
    def move(self, window_width, window_height, surface, target, round_over):
        speed = 10
        gravity = 2
        delta_x = 0
        delta_y = 0
        self.running = False
        self.attack_type = 0

        key = pygame.key.get_pressed()
        
        """
        In der If schleife wird zu erst überprüft ob der Spieler gerade einen Angriff ausführt da sich die spieler sich währenddessen nicht bewegen sollen.
        Außerdem wird überprüft ob der Spieler am Leben ist.
        Zusätzlich wird überprüft ob die Runde vorbei ist da der Gewinner sich auch nicht mehr bewegen soll.
        nach dem if statement kommte eine weitere Überprüng um welchen Spieler es sich handelt.
        """
        if self.attacking == False and self.alive == True and round_over == False:
            if self.player == 1:
                """
                Während der Spieler 1 Läuft wird das self.running auf True gesetzt.
                Das wird gemacht um die Animation für das laufen aufzurufen.
                Während die 'a' Taste gedrückt wird, wird delta_x auf -10 gesetzt. sodas der Spieler sich nach links bewegt.
                Bei der 'd' Taste wird delta_x auf 10 gesetzt. sodas der Spieler sich nach rechts bewegt.
                Bei der 'w' Taste wird die velocity_y auf -30 gesetzt. sodas der Spieler sich nach oben bewegt. Die Schwerkraft sorgt dafür das der Spieler wieder auf den Boden zurück kommt.
                während der Spieler in der luft ist, wird Jump auf True gesetzt.
                Bei der überprüfung ob die 'w' Taste gedrückt wird gleichzeitig überprueft ob der Spieler auf dem Boden ist. sonst könnte man doppel sprünge machen
                """
                if key[pygame.K_a]:
                    delta_x = -speed
                    self.running = True
                if key[pygame.K_d]:
                    delta_x = speed
                    self.running = True
        
                if key[pygame.K_w] and self.jump == False:
                    self.velocity_y = -30
                    self.jump = True

                """
                Hier habe ich die Angriffe gemacht. Es wird überprüft um welchen Angriff es sich handelt.
                wenn die 'r' Taste gedrückt wird, wird der attack_type auf 1 gesetzt.
                Bei der 't' Taste wird die attack_type auf 2 gesetzt.
                """
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2



            """
            Hier begint die Steuerung des zweiten Spielers. Diese ist nahezu identisch zur Steuerung des ersten Spielers.
            Nur das der Spieler 2 die Pfeiltasten benutzt.
            """
            if self.player == 2:
                if key[pygame.K_LEFT]:
                    delta_x = -speed
                    self.running = True
                if key[pygame.K_RIGHT]:
                    delta_x = speed
                    self.running = True
                if key[pygame.K_UP] and self.jump == False:
                    self.velocity_y = -30
                    self.jump = True
        
                if key[pygame.K_k] or key[pygame.K_l]:
                    self.attack(target)
                    if key[pygame.K_k]:
                        self.attack_type = 1
                    if key[pygame.K_l]:
                        self.attack_type = 2
        
        #Hier wird geregelt, dass die velocity stehtig größer wird wenn sie unter 0 ist.
        self.velocity_y += gravity
        delta_y += self.velocity_y

        """
        Hier sorge ich dafür, dass die Spieler nicht über den Rand hinaus laufen können.
        das Regel ich mit ein paar einfachen if statements.
        ich überprüfe ob die linke seite des Rechtecks + die delta_x kleiner ist als 0.
        wenn das der fall ist wird wird die delta_x auf 0 - die linke seite des Rechtecks gesetzt.
        ich mache das so damit der Spieler an den Äußersten punkt gehen kann.
        Mit der Rechten Seite ist es genau umgekehrt.
        ich habe noch eine überprüfung nach unten. dort habe ich es so gemacht das der spieler nicht nach ganz unten kann.
        Stattdessen habe ich einen bestimmten wert gesetzt der nicht unterschritten werden darf. solange der Spieler damit Kontakt hat ist hump auch auf False gesetzt. 
        """
        if self.rect.left + delta_x < 0:
            delta_x = 0 - self.rect.left
        if self.rect.right + delta_x > window_width:
            delta_x = window_width - self.rect.right
        if self.rect.bottom + delta_y > window_height - 110:
            self.jump = False
            self.velocity_y = 0
            delta_y = window_height - 110 - self.rect.bottom
        
        """
        Hier kümmer ich mich darum, dass die Spieler sich immer angucken.
        das mache ich indem ich überprüfe ob das center des Targets eine höhere x-Koordinate hat als das center des spielers.
        wenn das der Fall ist, ist flip = False. Das heißt das die Bitmaps nicht geflipt werden sollen.
        Wenn das nicht der Fall ist, ist flip = True. Das heißt das die Bitmaps geflipt werden sollen.
        """
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True
        
        #Ich habe einen Angriffs Cooldown gemacht da man nur gedrückt halten musste und der andere spieler ist gestorben
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        #Hier wird die Position aktuell gehalten
        self.rect.x += delta_x
        self.rect.y += delta_y


    """
    In der Update Funktion werden die Animationen gemacht.
    zu erst habe ich ein if statement gemacht das überprüft kleiner oder gleich 0 ist wenn das der fall ist wird alive auf False gesetzt.
    das hat zur folge das der Andere gewinnt und das round_over auf True gesetzt wird.
    wenn das passiert wird ein punkt an den anderen vergeben und der Round_over_couldown wird runtergezählt bis es 0 beträgt.
    wenn das passiert startet der Countdown neu und es begint eine neue Runde. Die spieler starten wieder in aktion 0.
    außerdem wird update_action auf 6 gesetzt. so dass die Sterbe animationen ausgeführt wird.
    bei einem Gegnerischen Treffer wird update_action auf 5 gestzt. das hat zur folge das man leben verliert und das die hit animation abgespielt wird.
    bei den nächsten zwei wird überprüft ob Attacking True ist wenn das der fall ist wird geguckt welche Atacke es war 1 oder 2. Jenachdem welche es ist wird die passende animation abgespielt.
    die nächst überprüfung ist ob Jump True ist also ob der Spieler in der Luft ist wenn das der Fall ist wird die Sprung animation abgespielt.
    wenn das davorige nicht passte wird überprüft ob Running True ist. wenn das der Fall ist wird die Lauf animation abgespielt.
    wenn alles andere nicht der Fall ist wird die Idle animation abgespielt.
    """
    def update(self):

        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6) #6: Tod
        elif self.hit == True:
            self.update_action(5) #5: hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3) #3: Attacke1
            elif self.attack_type == 2:
                self.update_action(4) #4: Attacke2
        elif self.jump == True:
            self.update_action(2)#2: Sprung
        elif self.running == True:
            self.update_action(1) #1: Rennen
        else:
            self.update_action(0) #0: idle

        animation_cooldown = 75
        #hier wird das Bild geupdatet damit immer die richtige Animation angezeigt wird.
        self.image = self.animation_list[self.action][self.frame_index]

        """
        Hier wird dafür gesorgt das die Animationen die richtige geschwindigkeit haben in der sie abgespielt werden.
        sobald genug zeit vergangen ist wird der fram_index eins höher gesetzt. Dann wird das nächste Bild angezeigt.
        """
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        """
        Hier wird überprüft ob die animation zu ende ist.
        wenn das der fall ist wird geguckt ob der Spieler noch am leben ist wenn das nicht der fall ist bleibt es bei dem letzten Bild stehen indem fall ist es das letzte Bild der Sterbe Animation.
        wenn das nicht zutrifft wird der frame_index auf 0 gesetzt. Damit kann dann die nächste Animation abgespielt werden. Darüberhinaus wird überprüft ob eine Attacke verwendet wurde. 
        wenn ja dann wird der attack_cooldown auf 25 gesetzt damit man in der Zeit nicht angreifen kann. Danach wird geguckt ob man selber schaden bekommen hat wenn man auch in einer Attack war wird diese abgebrochen und der der Attack_cooldown wird auch auf 25 gesetzt. 
        """
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:    
                self.frame_index = 0
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 25

                #check if damage was taken
                if self.action == 5:
                    self.hit = False
                    #if the player was in the middle of an attack, then the attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 25

        """
        hier beginnt die attack funktion in dieser wird die kollision überprüft zwischen dem angriff und dem Gegner.
        zu erst schaut das programm ob der attack_cooldown 0 ist.
        wenn ja wird attacking auf True gesetzt. darauf wird dann ein Rechteck erstellt. Es ist unsichtbar und fängt in der mitte des eigenen spielers an und ist doppelt so breit wie der spieler.
        es wird auch flip überprüft damit die Attacke in die richtige richtung geht. Danach  fängt ein if statement an.
        Es überprüft ob eine kollision zwischen dem Angriffs Rechteck und dem Gegner vorliegt.
        wenn das der fall ist wird die hit animation des gegners abgespielt und er verliert 10 von seinen 100 Leben.
        """
    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

        """
        in dieser Funktion wird geschaut ob die nächste Animation eine andere ist, als die aktuelle.
        wenn das der fall ist wird der fram_index auf 0 gesetzt wenn das nicht passiert kann es zu abstürzen kommen.
        da nicht alle Animationen die gleiche länge haben.
        """
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))

#diese Funktion ist für das Zeichen von Text
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    window.blit(img, (x, y))

#Diese funktion ist für das Zeichen vom Hintergrund zuständig
def draw_background():
    scaled_background = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    window.blit(scaled_background, (0,0))

"""
In dieser Funktion habe ich die Lebensanzeige erstellt
ich habe zuerst eine Variabel aufgestellt da ich die Lebensanzeige 400 Pixel breit machen wollte und ich nur 100 Leben maximal habe.
in dieser habe ich das Leben durch 100 gerechnet und diese variabel zur erstellung des rechtecks verwendet. So ist die Lebensanzeige in abhängigkeit vom leben des Spielers.
"""

def draw_healt_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(window, BLACK, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(window, RED, (x, y, 400, 30))
    pygame.draw.rect(window, YELLOW, (x, y, 400 * ratio, 30))

#Hier habe ich zwei objekte der Klasse Fighter erstellt.
fighter_1 = Fighter(1, 250, 350, False, WARRIOR_DATA, warrior_sheet, warrior_animation_steps)
fighter_2 = Fighter(2, 950, 350, True, WIZARD_DATA, wizard_sheet, wizard_animation_steps)


"""
Hier beginnt die hauptprogrammschleife.
in dieser rufe ich verschiedene funktionen auf wie z.b.: draw_background, draw_healt_bar, fighter_1.draw, fighter_2.draw, draw_text 
"""
run = True
while run:
    clock.tick(fps)
    #zeiche Hintergrund
    draw_background()

    #Zeigt die Lebensanzeige und den Score der verschiedenen Spieler an.
    draw_healt_bar(fighter_1.health, 20, 20)
    draw_healt_bar(fighter_2.health, 860, 20)
    draw_text("Player 1: " + str(score[0]), score_font, RED, 20, 50)
    draw_text("Player 2: " + str(score[1]), score_font, RED, 860, 50)

    """
    Hier update ich den countdown am anfang des spiels und bei jedem Runden beginn. 
    Solange der countdown nicht auf 0 ist wird die move funktion nicht aufgerufen.
    wenn die move funktion nicht aufgerufen wird können sich die spieler nicht bewegen.
    wenn der countdown größer als 0 ist wird der countdown als Text angezeigt.
    Darunter wir dann der countdown geupdatet.
    """
    if intro_count <= 0:
        fighter_1.move(WINDOW_WIDTH, WINDOW_HEIGHT, window, fighter_2, round_over)
        fighter_2.move(WINDOW_WIDTH, WINDOW_HEIGHT, window, fighter_1, round_over)
    else:
        draw_text(str(intro_count), count_font, RED, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3)
        if (pygame.time.get_ticks() - last_count_update) > 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()
            

    #hier werden die beiden fighter objekte geupdatet.
    fighter_1.update()
    fighter_2.update()

    #hier werden die beiden fighter objekte gezeichnet.
    fighter_1.draw(window)
    fighter_2.draw(window)

    """
    Hier wird überprüft ob ein Spieler gewonnen hat.
    es wird überprüft ob round_over False ist.
    wenn das der Fall ist wird geschaut ob Spieler 1 kein leben mehr hat.
    wenn das der fall ist wird in der score list der zweite wert um 1 erhöht.
    round_over wird auf True gesetzt und der last_count_update nimmt die zeit und startet den countdown. 
    Für die nächste Runde. 
    Wenn der Spieler 1 am leben ist wird geschaut ob Spieler 2 auch noch am leben ist.
    wenn nicht wird in der score list der erste wert um 1 erhöht. und auch dann starter den countdown.
    Für die nächste Runde.
    """
    if round_over == False:
        if fighter_1.alive == False:
            score[1] += 1
            round_over = True
            last_round_update = pygame.time.get_ticks()
        elif fighter_2.alive == False:
            score[0] += 1
            round_over = True
            last_round_update = pygame.time.get_ticks()
    else:
        """
        wenn round_over True wird das Bild victory angezeigt.
        Nachdem der cooldown abgelaufen ist wird round_over auf False gesetzt.
        Die beiden Fighter objekte werden resetet. 
        Dann beginnt die nächste Runde.
        """
        window.blit(victory_image, (500, 200))
        if pygame.time.get_ticks() - last_round_update > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3
            fighter_1 = Fighter(1, 250, 350, False, WARRIOR_DATA, warrior_sheet, warrior_animation_steps)
            fighter_2 = Fighter(2, 950, 350, True, WIZARD_DATA, wizard_sheet, wizard_animation_steps)

    #hier wird überprüft ob das Spiel beendet werden soll.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
#        elif event.type == pygame.KEYDOWN:
#            if event.key == pygame.K_ESCAPE:
#                run = False

    #Hier wird das Fenster aktualisiert.
    pygame.display.update()

#Hier wird das Fenster geschlossen.
pygame.quit()