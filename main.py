import pygame
import random
import config
import asyncio

# --- CONFIGURACIÓN ---
ANCHO, ALTO = config.ANCHO, config.ALTO
FPS = config.FPS

class FantasmaIA:
    def __init__(self, imagen, pos_inicial, id_fantasma):
        self.image = imagen
        self.rect = self.image.get_rect(top=pos_inicial[0], left=pos_inicial[1])
        self.direccion_actual = [0, 0]
        self.id = id_fantasma
        self.personalidad = random.uniform(0.7, 1.3) 

    def mover(self, target_rect, bloques, vel):
        direcciones = [[vel, 0], [-vel, 0], [0, vel], [0, -vel]]
        def evaluar_ruta(d):
            tx = self.rect.x + d[0]
            ty = self.rect.y + d[1]
            dist = (tx - target_rect.x)**2 + (ty - target_rect.y)**2
            return dist * (self.personalidad if (self.id % 2 == 0) else 1.0)

        direcciones.sort(key=evaluar_ruta)

        movido = False
        for d in direcciones:
            if d[0] == -self.direccion_actual[0] and d[1] == -self.direccion_actual[1]:
                if random.random() > 0.1: continue 

            proxima_pos = self.rect.move(d[0], d[1])
            if not any(proxima_pos.colliderect(b) for b in bloques):
                self.rect.x += d[0]
                self.rect.y += d[1]
                self.direccion_actual = d
                movido = True
                break

        if not movido:
            random.shuffle(direcciones)
            for d in direcciones:
                if not any(self.rect.move(d[0], d[1]).colliderect(b) for b in bloques):
                    self.rect.x += d[0]
                    self.rect.y += d[1]
                    self.direccion_actual = d
                    break

def cargar_recursos():
    try:
        r = {
            "pac_cero": config.load_image("pac_cero.png"),
            "pac_dir": {
                "up": config.load_image("pac_up.png"), "down": config.load_image("pac_down.png"),
                "left": config.load_image("pac_left.png"), "right": config.load_image("pac_right.png")
            },
            "fantasmas_imgs": [
                config.load_image("enemigo.png"), 
                config.load_image("fant001.png"), 
                config.load_image("enemi14.png")
            ],
            "win_imgs": {"lose": config.load_image("pac_triste.png"), "win": config.load_image("pac_win.png")},
            "botones": {
                "play": config.load_image("playbttn.png"), 
                "pause": config.load_image("pausebttn.png"), 
                "restart": config.load_image("restartbttn.png"),
                "zone1": config.load_image("number-1.png"),
                "zone2": config.load_image("number-2.png"),
                "zone3": config.load_image("number-3.png")
            },
            "sonidos": {
                "choque": config.load_sound("choque.wav"), 
                "comiendo": config.load_sound("comiendo.wav"),
                "inicio": config.load_sound("inicio.wav"), 
                "lose": config.load_sound("loseSound.wav")
            }
        }
        
        # Generar "flechas" proceduralmente con Surfaces ya que no hay imagenes
        btn_size = 90
        up_btn = pygame.Surface((btn_size, btn_size)); up_btn.fill((200, 200, 200))
        down_btn = pygame.Surface((btn_size, btn_size)); down_btn.fill((200, 200, 200))
        left_btn = pygame.Surface((btn_size, btn_size)); left_btn.fill((200, 200, 200))
        right_btn = pygame.Surface((btn_size, btn_size)); right_btn.fill((200, 200, 200))

        font_arrows = pygame.font.SysFont("Arial", 60, True)
        up_btn.blit(font_arrows.render("^", True, (0,0,0)), (25, 5))
        down_btn.blit(font_arrows.render("v", True, (0,0,0)), (30, 0))
        left_btn.blit(font_arrows.render("<", True, (0,0,0)), (25, 0))
        right_btn.blit(font_arrows.render(">", True, (0,0,0)), (25, 0))

        r["dpad"] = {
            "up": up_btn, "down": down_btn, 
            "left": left_btn, "right": right_btn
        }
        
        return r
    except: return None

def cargar_mapa(archivo):
    bloques, bonus = [], []
    x, y, w, h = 40, 10, 20, 20
    try:
        with open(config.LEVEL_DIR / archivo, "r") as zona:
            data = zona.read()
            for char in data:
                if char == "0": bloques.append(pygame.Rect(x, y, w, h))
                if char == "1":
                    if random.randint(1, 10) > 8: bonus.append(pygame.Rect(x, y, 10, 10))
                if char == "]": y += 30; x = 10
                x += 30
    except: pass
    return bloques, bonus

async def main():
    if getattr(pygame, 'init', None):
        pygame.init()
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    vent = pygame.display.set_mode([ANCHO, ALTO])
    res = cargar_recursos()
    if not res: return

    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Arial", 20, True, True)
    
    jugando, ganado, perdido = False, False, False
    puntos_echos, cambio, veces_perdidas = 0, 0, 0
    vx, vy, inicio_ticks, tiempo_restante = 0, 0, 0, 60

    current_level_idx = 0
    bloques, bonus = cargar_mapa(config.LEVELS[current_level_idx])
    pac_man_rect = res["pac_cero"].get_rect(top=210, left=540)
    pac_orientacion = res["pac_cero"]
    
    pos_comun = (150, 540)
    fantasmas = [FantasmaIA(res["fantasmas_imgs"][i], pos_comun, i) for i in range(3)]
    
    btn_play = res["botones"]["play"].get_rect(top=50, left=5)
    btn_pause = res["botones"]["pause"].get_rect(top=143, left=5)
    btn_restart = res["botones"]["restart"].get_rect(top=236, left=5)
    
    zone1_rect = res["botones"]["zone1"].get_rect(top=500, left=200)
    zone2_rect = res["botones"]["zone2"].get_rect(top=500, left=350)
    zone3_rect = res["botones"]["zone3"].get_rect(top=500, left=500)

    # D-Pad UI Positioning
    dpad_size = 90
    dpad_y = 500
    dpad_x = 750
    btn_up = res["dpad"]["up"].get_rect(top=dpad_y, left=dpad_x + dpad_size + 10)
    btn_down = res["dpad"]["down"].get_rect(top=dpad_y + dpad_size + 10, left=dpad_x + dpad_size + 10)
    btn_left = res["dpad"]["left"].get_rect(top=dpad_y + dpad_size + 10, left=dpad_x)
    btn_right = res["dpad"]["right"].get_rect(top=dpad_y + dpad_size + 10, left=dpad_x + (dpad_size * 2) + 20)

    if res["sonidos"]["inicio"]: res["sonidos"]["inicio"].play()

    def reset_state(nuevo_nivel_idx=None):
        nonlocal jugando, ganado, perdido, puntos_echos, cambio, veces_perdidas
        nonlocal vx, vy, inicio_ticks, tiempo_restante, pac_man_rect, pac_orientacion, fantasmas, bloques, bonus, current_level_idx
        
        if nuevo_nivel_idx is not None:
            current_level_idx = nuevo_nivel_idx
            
        bloques, bonus = cargar_mapa(config.LEVELS[current_level_idx])
        pac_man_rect = res["pac_cero"].get_rect(top=210, left=540)
        pac_orientacion = res["pac_cero"]
        fantasmas = [FantasmaIA(res["fantasmas_imgs"][i], pos_comun, i) for i in range(3)]
        
        jugando, ganado, perdido = False, False, False
        puntos_echos, cambio, veces_perdidas = 0, 0, 0
        vx, vy, inicio_ticks, tiempo_restante = 0, 0, 0, 60
        if res["sonidos"]["inicio"]: res["sonidos"]["inicio"].play()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
            if event.type == pygame.MOUSEBUTTONDOWN:
                m = pygame.mouse.get_pos()
                if btn_play.collidepoint(m) and not jugando and not ganado and not perdido:
                    jugando, inicio_ticks = True, pygame.time.get_ticks()
                    if res["sonidos"]["inicio"]: res["sonidos"]["inicio"].stop()
                if btn_pause.collidepoint(m) and not ganado and not perdido: jugando = False
                
                if btn_restart.collidepoint(m): 
                    # If game was won, advance level organically
                    next_idx = (current_level_idx + 1) % len(config.LEVELS) if ganado else current_level_idx
                    reset_state(next_idx)

                # Zone selection clicks
                if zone1_rect.collidepoint(m): reset_state(0)
                if zone2_rect.collidepoint(m): reset_state(1)
                if zone3_rect.collidepoint(m): reset_state(2)

                # D-Pad clicks
                if jugando and not (ganado or perdido):
                    if btn_up.collidepoint(m): vy = -5; vx = 0; pac_orientacion = res["pac_dir"]["up"]
                    if btn_down.collidepoint(m): vy = 5; vx = 0; pac_orientacion = res["pac_dir"]["down"]
                    if btn_left.collidepoint(m): vx = -5; vy = 0; pac_orientacion = res["pac_dir"]["left"]
                    if btn_right.collidepoint(m): vx = 5; vy = 0; pac_orientacion = res["pac_dir"]["right"]
            
            if event.type == pygame.MOUSEBUTTONUP:
                # Stop movement when touch is released to emulate exact KEYUP behavior
                m = pygame.mouse.get_pos()
                if btn_up.collidepoint(m) or btn_down.collidepoint(m): vy = 0
                if btn_left.collidepoint(m) or btn_right.collidepoint(m): vx = 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    reset_state((current_level_idx + 1) % len(config.LEVELS))

            if jugando and not (ganado or perdido):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: vy = -5; vx = 0; pac_orientacion = res["pac_dir"]["up"]
                    if event.key == pygame.K_DOWN: vy = 5; vx = 0; pac_orientacion = res["pac_dir"]["down"]
                    if event.key == pygame.K_LEFT: vx = -5; vy = 0; pac_orientacion = res["pac_dir"]["left"]
                    if event.key == pygame.K_RIGHT: vx = 5; vy = 0; pac_orientacion = res["pac_dir"]["right"]
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_UP, pygame.K_DOWN): vy = 0
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT): vx = 0

        if jugando and not (ganado or perdido):
            ticks = (pygame.time.get_ticks() - inicio_ticks) // 1000
            tiempo_restante = max(0, 60 - ticks)
            if tiempo_restante <= 0: perdido = True

            # Movimiento Pacman
            px, py = pac_man_rect.x, pac_man_rect.y
            pac_man_rect.x += vx
            if any(pac_man_rect.colliderect(b) for b in bloques): pac_man_rect.x = px
            pac_man_rect.y += vy
            if any(pac_man_rect.colliderect(b) for b in bloques): pac_man_rect.y = py

            # Colisiones Puntos
            for p in bonus[:]:
                if pac_man_rect.colliderect(p):
                    if res["sonidos"]["comiendo"]: res["sonidos"]["comiendo"].play()
                    bonus.remove(p)
                    puntos_echos += 1
            if len(bonus) == 0 and puntos_echos > 0: ganado = True

            # --- ACTUALIZACIÓN DE FANTASMAS ---
            tiempos_salida = [59, 57, 55] 
            for i, f in enumerate(fantasmas):
                if tiempo_restante < tiempos_salida[i]:
                    f.mover(pac_man_rect, bloques, 2)
                    if pac_man_rect.colliderect(f.rect): perdido = True

            cambio += 2
            pac_img = res["pac_cero"] if (cambio % 40 < 20) else pac_orientacion
        else:
            pac_img = res["pac_cero"]

        # --- DIBUJO ---
        vent.fill((125, 125, 125))
        vent.blit(res["botones"]["play"], btn_play)
        vent.blit(res["botones"]["pause"], btn_pause)
        vent.blit(res["botones"]["restart"], btn_restart)
        
        vent.blit(res["botones"]["zone1"], zone1_rect)
        vent.blit(res["botones"]["zone2"], zone2_rect)
        vent.blit(res["botones"]["zone3"], zone3_rect)
        
        vent.blit(res["dpad"]["up"], btn_up)
        vent.blit(res["dpad"]["down"], btn_down)
        vent.blit(res["dpad"]["left"], btn_left)
        vent.blit(res["dpad"]["right"], btn_right)
        
        for b in bloques: pygame.draw.rect(vent, (0, 0, 0), b)
        for p in bonus: pygame.draw.rect(vent, (50, 140, 240), p)

        vent.blit(pac_img, pac_man_rect)

        for i, f in enumerate(fantasmas):
            if tiempo_restante < [59, 57, 55][i]:
                vent.blit(f.image, f.rect)

        txt = fuente.render(f"Tiempo: {tiempo_restante}", True, (255, 255, 255))
        pts_txt = fuente.render(f"Puntos: {puntos_echos}", True, (255, 255, 255))
        
        vent.blit(txt, (10, 10))
        vent.blit(pts_txt, (140, 10))

        if perdido:
            vent.blit(res["win_imgs"]["lose"], pac_man_rect)
            if veces_perdidas == 0: 
                if res["sonidos"]["lose"]: res["sonidos"]["lose"].play()
                veces_perdidas = 1
        if ganado: vent.blit(res["win_imgs"]["win"], pac_man_rect)

        pygame.display.update()
        await asyncio.sleep(0) # Required for Pygbag to yield to browser
        reloj.tick(FPS)

if __name__ == "__main__":
    asyncio.run(main())