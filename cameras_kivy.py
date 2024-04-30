from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.label import Label

import subprocess

import cv2

def get_camera_names():
    code = "ffmpeg -list_devices true -f dshow -i dummy"
    a = subprocess.Popen(code, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    str_a = a.stdout.read()

    split_sign = "\""
    media_result = []

    sum = 0
    while (str_a.find(split_sign) != -1) and sum < 100:
        sum += 1
        start_index = str_a.find(split_sign)
        end_index = str_a[start_index+1:].find(split_sign)
        end_index = start_index+end_index
        item_str = str_a[start_index+1:end_index+1]
        if item_str[0:1] != '\n' and item_str[0:1] != '@' and item_str != '':
            media_result.append(item_str)
        str_a = str_a[end_index+2:len(str_a)-1]
    return media_result

class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        self.paused = False
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        if not self.paused:  # Only capture frame and update texture if not paused
            ret, frame = self.capture.read()
            if ret:
                # convert it to texture
                buf1 = cv2.flip(frame, 0)
                buf = buf1.tostring()
                image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                # display image from the texture
                self.texture = image_texture

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(Label(text='Welcome!\n This is the OpenSource Software for multistreaming of video captures. To start, press the button below.\n'))
        self.start_button = Button(text='Start Application')
        self.start_button.bind(on_press=self.go_to_camera)
        self.layout.add_widget(self.start_button)
        self.add_widget(self.layout)

    def go_to_camera(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'camera'
        
class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical')
        self.camera_layout = GridLayout(cols=2)

        self.home_button = Button(text='Home', size_hint=(1, 0.5))
        self.home_button.bind(on_press=self.go_home)
        self.layout.add_widget(self.home_button)
        self.layout.add_widget(self.camera_layout)
        self.start_button = Button(text='Start Camera')
        self.start_button.bind(on_press=self.start_camera)
        self.layout.add_widget(self.start_button)

        # Add radio buttons for camera selection
        self.radio_layout = BoxLayout(orientation='horizontal')
        self.radio1 = CheckBox(group='camera', active=True)
        self.radio1.bind(active=self.on_radio_active)
        self.radio2 = CheckBox(group='camera')
        self.radio2.bind(active=self.on_radio_active)
        self.radio_all = CheckBox(group='camera')  
        self.radio_all.bind(active=self.on_radio_active)
        self.radio_layout.add_widget(Label(text='Camera 1'))
        self.radio_layout.add_widget(self.radio1)
        self.radio_layout.add_widget(Label(text='Camera 2'))
        self.radio_layout.add_widget(self.radio2)
        self.radio_layout.add_widget(Label(text='All'))
        self.radio_layout.add_widget(self.radio_all)
        self.layout.add_widget(self.radio_layout)

        self.button = Button(text='Pause')
        self.button.bind(on_press=self.on_pause_press)
        self.layout.add_widget(self.button)

        self.add_widget(self.layout)
        self.is_capturing = False 

    def on_radio_active(self, instance, value):
        if value:  # Only respond when a radio button is selected, not deselected
            self.stop_camera()
            # self.start_camera(instance)

    def stop_camera(self):
        if self.is_capturing:
            self.camera_layout.clear_widgets()
            if hasattr(self, 'capture'):
                self.capture.release()
            if hasattr(self, 'capture1'):
                self.capture1.release()
            if hasattr(self, 'capture2'):
                self.capture2.release()
            self.is_capturing = False

    def start_camera(self, instance):
        if not self.is_capturing:  
            if self.radio1.active:
                self.capture = cv2.VideoCapture(0)
                self.my_camera = KivyCamera(capture=self.capture, fps=30)
                self.camera_layout.add_widget(self.my_camera)
            elif self.radio2.active:
                self.capture = cv2.VideoCapture(1)
                self.my_camera = KivyCamera(capture=self.capture, fps=30)
                self.camera_layout.add_widget(self.my_camera)
            elif self.radio_all.active:  # Start captures for both cameras
                self.capture1 = cv2.VideoCapture(0)
                self.my_camera1 = KivyCamera(capture=self.capture1, fps=30)
                self.camera_layout.add_widget(self.my_camera1)
                self.capture2 = cv2.VideoCapture(1)
                self.my_camera2 = KivyCamera(capture=self.capture2, fps=30)
                self.camera_layout.add_widget(self.my_camera2)
            else:
                return
            
            self.is_capturing = True  

    def go_home(self, instance):
        #self.capture.release()
        self.manager.transition.direction = 'right'  # Set the direction of the transition
        self.manager.current = 'start'
    
    def on_pause_press(self, instance):
        # Pause or resume the capture depending on the current state
        if self.my_camera.paused:
            self.my_camera.paused = False
            self.button.text = 'Pause'
        else:
            self.my_camera.paused = True
            self.button.text = 'Resume'


class CamApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(CameraScreen(name='camera'))
        return sm

    def on_stop(self):
        # close the camera properly
        self.capture.release()

if __name__ == '__main__':
    CamApp().run()