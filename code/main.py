import sys
import pygame
import cv2
import threading

from game_data import level_0
from level import Level
from ui import UI
from settings import *

from tracking.cam import Camera
from tracking.hand_tracker import HandTracker
from tracking.face_tracker import FaceTracker

from event_handler import EventHandler, EventTypes

# M4 Final programming project Max Liebe and Ysbrand Burgstede
# A mashup of pacman and mario. The goal is to collect all the coins without being hit by a ghost!
# Control with WASD or 'SPACE'ASD, fullscreen mode accessible by f11


class Game:

    def __init__(self):
        self.is_running = True
        self.event_handler = EventHandler(self)

        if use_tracking:
            self.tracker_thread = TrackerThread(1, self, self.event_handler)
            self.tracker_thread.start()
        else:
            self.cam = None
            self.hand_tracker = None
        pygame.init()

        # make the screen and save the dimensions of your screen for fullscreen mode and resizing
        self.game_screen_ratio = game_screen_width / game_screen_height
        self.infoObject = pygame.display.Info()
        self.window_width = game_screen_width * window_scale + tracker_width
        self.window_height = game_screen_height * window_scale
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        self.game_screen = pygame.Surface((game_screen_width, game_screen_height))
        self.fullscreen = False

        self.resized_width = self.screen.get_height() * self.game_screen_ratio
        self.resized_height = self.screen.get_height()
        self.resized_x_offset = tracker_width + (self.resized_width / game_screen_width)
        self.resized_y_offset = 0

        # initialize the game and all its necessary components
        self.clock = pygame.time.Clock()

        self.level = Level(level_0, self.game_screen)
        self.player = self.level.player
        self.ghosts = self.level.ghosts

        self.ui = UI()
        intro = pygame.mixer.Sound('../sfx/intro.wav')
        intro.play()

    def loop(self):
        # make sure we run at the right framerate
        dt = min(self.clock.tick(target_fps) * 0.1, max_delta_time)

        # handle events
        for event in pygame.event.get():
            event_type = self.get_event_type(event)
            self.event_handler.emit(event_type)

        # update the level
        self.level.run(dt)

        # resize the game screen and put it onto the screen and update it
        resized_screen = pygame.transform.scale(self.game_screen, (self.resized_width, self.resized_height))
        self.screen.blit(resized_screen, (self.resized_x_offset, self.resized_y_offset))

        # draw the ui
        self.ui.draw(self.level, self.screen, self.resized_x_offset)

        # draw the tracking result in the black area on the left
        if use_tracking and self.tracker_thread.tracking_result is not None:
            tracking_result_rgb = cv2.cvtColor(self.tracker_thread.tracking_result, cv2.COLOR_RGB2BGR)
            result_pygame_image = convert_opencv_image_to_pygame(tracking_result_rgb)
            scaled_width = self.resized_x_offset
            scaled_height = scaled_width / self.tracker_thread.cam.get_aspect_ratio()
            scaled_image = pygame.transform.scale(result_pygame_image, (scaled_width, scaled_height))
            flipped_image = pygame.transform.flip(scaled_image, True, False)
            self.screen.blit(flipped_image, (0, 0))
        pygame.display.update()

    @staticmethod
    def get_event_type(event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return EventTypes.QUIT
        elif event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_a: return EventTypes.LEFT_DOWN
                case pygame.K_d: return EventTypes.RIGHT_DOWN
                case pygame.K_SPACE: return EventTypes.JUMP_DOWN
                case pygame.K_w: return EventTypes.JUMP_DOWN
                case pygame.K_LSHIFT: return EventTypes.RUN_DOWN
                case pygame.K_e: return EventTypes.DEBUG_RESET
                case pygame.K_F11: return EventTypes.FULLSCREEN
        elif event.type == pygame.KEYUP:
            match event.key:
                case pygame.K_a: return EventTypes.LEFT_UP
                case pygame.K_d: return EventTypes.RIGHT_UP
                case pygame.K_SPACE: return EventTypes.JUMP_UP
                case pygame.K_LSHIFT: return EventTypes.RUN_UP
        elif event.type == pygame.VIDEORESIZE:
            return EventTypes.RESIZE
        return EventTypes.NONE

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        else:
            self.screen = pygame.display.set_mode((self.infoObject.current_w, self.infoObject.current_h), pygame.FULLSCREEN)
        self.fullscreen = not self.fullscreen

    def fix_screen_after_resize(self):
        # calculate the offsets our game screen needs inside the real screen (seen as black bars)
        if self.screen.get_width() < self.window_width or self.screen.get_height() < self.window_height:
            self.resized_width = self.window_height * self.game_screen_ratio
            self.resized_height = self.window_height
            self.resized_y_offset = 0
            self.resized_x_offset = tracker_width + (self.resized_width / game_screen_width)
            self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        else:
            self.resized_width = self.screen.get_height() * (game_screen_width / game_screen_height)
            self.resized_height = self.screen.get_height()
            resized_y_offset = 0
            if self.screen.get_width() - tracker_width < self.resized_width:
                self.screen = pygame.display.set_mode((self.resized_width + tracker_width, self.resized_height), pygame.RESIZABLE)
            if self.screen.get_width() > self.resized_width + (tracker_width * 2):
                self.resized_x_offset = (self.screen.get_width() - self.resized_width) / 2
            else:
                self.resized_x_offset = tracker_width + (self.resized_width / game_screen_width)


class TrackerThread(threading.Thread):
    def __init__(self, thread_id, game_instance, event_handler):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.cam = Camera(webcam_id)
        self.event_handler = event_handler
        self.hand_tracker = HandTracker(event_handler)
        self.face_tracker = FaceTracker(event_handler)
        self.game_instance = game_instance
        self.tracking_result = None

    def run(self):
        while self.game_instance.is_running:
            frame = self.cam.read_frame()
            hand_tracked_frame = self.hand_tracker.track_frame(frame, True)
            self.tracking_result = self.face_tracker.track_frame(hand_tracked_frame, True)


def convert_opencv_image_to_pygame(image):
    return pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")


# initialize the game
game = Game()

# run the game loop
while game.is_running:
    game.loop()

# quit the game
game.tracker_thread.join()
pygame.quit()
sys.exit()
