import sys
import pygame
import cv2
import threading

from game_data import level_0
from level import Level
from settings import *

from tracking.cam import Camera
from tracking.hand_tracker import HandTracker

# M4 Final programming project Max Liebe and Ysbrand Burgstede
# A mashup of pacman and mario. The goal is to collect all the coins without being hit by a ghost!
# Control with WASD or 'SPACE'ASD, fullscreen mode accessible by f11

if use_tracking:
    cam = Camera(webcam_id)
    hand_tracker = HandTracker()
else:
    cam = None
    hand_tracker = None
pygame.init()

# make the screen and save the dimensions of your screen for fullscreen mode and resizing
game_screen_ratio = game_screen_width / game_screen_height
infoObject = pygame.display.Info()
window_width = game_screen_width * window_scale + tracker_width
window_height = game_screen_height * window_scale
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
fullscreen = False
game_screen = pygame.Surface((game_screen_width, game_screen_height))

resized_width = screen.get_height() * game_screen_ratio
resized_height = screen.get_height()
resized_x_offset = tracker_width + (resized_width / game_screen_width)
resized_y_offset = 0

# initialize the game and all its necessary components
clock = pygame.time.Clock()

level = Level(level_0, game_screen)
player = level.player
ghosts = level.ghosts
intro = pygame.mixer.Sound('../sfx/intro.wav')
intro.play()

is_running = True


class CamThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.tracking_result = None

    def run(self):
        while is_running:
            frame = cam.read_frame()
            self.tracking_result = hand_tracker.track_frame(frame, True)


if use_tracking:
    cam_thread = CamThread(1)
    cam_thread.start()

def fix_screen_after_resize():
    global screen, resized_width, resized_height, resized_y_offset, resized_x_offset

    # calculate the offsets our game screen needs inside the real screen (seen as black bars)
    if screen.get_width() < window_width or screen.get_height() < window_height:
        resized_width = window_height * game_screen_ratio
        resized_height = window_height
        resized_y_offset = 0
        resized_x_offset = tracker_width + (resized_width / game_screen_width)
        screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    else:
        resized_width = screen.get_height() * (game_screen_width / game_screen_height)
        resized_height = screen.get_height()
        resized_y_offset = 0
        if screen.get_width() - tracker_width < resized_width:
            screen = pygame.display.set_mode((resized_width + tracker_width, resized_height), pygame.RESIZABLE)
        if screen.get_width() > resized_width + (tracker_width * 2):
            resized_x_offset = (screen.get_width() - resized_width) / 2
        else:
            resized_x_offset = tracker_width + (resized_width / game_screen_width)


def convert_opencv_image_to_pygame(image):
    return pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")


# our game loop
while is_running:
    dt = min(clock.tick(target_fps) * 0.1, max_delta_time)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            is_running = False
        elif event.type == pygame.KEYDOWN:
            match event.key:
                # player movement
                case pygame.K_a:
                    player.left = True
                    player.flipped = True
                case pygame.K_d:
                    player.right = True
                    player.flipped = False
                case pygame.K_SPACE:
                    player.jump()
                case pygame.K_w:
                    player.jump()
                case pygame.K_LSHIFT:
                    player.speed_multiplier = player.RUNNING_SPEED
                case pygame.K_e:
                    player.position.x = tile_size * horizontal_tile_number / 2
                    player.position.y = tile_size * vertical_tile_number / 2 - tile_size
                # fullscreen
                case pygame.K_F11:
                    if fullscreen:
                        screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
                        fullscreen = False
                    else:
                        fullscreen = True
                        screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)

                    fix_screen_after_resize()

        elif event.type == pygame.KEYUP:
            # more player movement
            match event.key:
                case pygame.K_a:
                    player.left = False
                case pygame.K_d:
                    player.right = False
                case pygame.K_SPACE:
                    if player.jumping:
                        player.velocity.y *= 0.5
                case pygame.K_LSHIFT:
                    player.speed_multiplier = player.DEFAULT_SPEED

        elif event.type == pygame.VIDEORESIZE:
            fix_screen_after_resize()

    # update the level
    level.run(dt)
    # resize the game screen and put it onto the screen and update it
    resized_screen = pygame.transform.scale(game_screen, (resized_width, resized_height))
    screen.blit(resized_screen, (resized_x_offset, resized_y_offset))

    # draw the tracking result in the black area on the left
    if use_tracking and cam_thread.tracking_result is not None:
        tracking_result_rgb = cv2.cvtColor(cam_thread.tracking_result, cv2.COLOR_RGB2BGR)
        result_pygame_image = convert_opencv_image_to_pygame(tracking_result_rgb)
        scaled_width = resized_x_offset
        scaled_height = scaled_width / cam.get_aspect_ratio()
        scaled_image = pygame.transform.scale(result_pygame_image, (scaled_width, scaled_height))
        screen.blit(scaled_image, (0, 0))
    pygame.display.update()

cam_thread.join()
pygame.quit()
sys.exit()
