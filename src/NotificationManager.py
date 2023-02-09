import warnings
from notifypy import Notify
import simpleaudio as sa
from Config import Config

class NotificationManager:

    def __init__(self, config: Config):
        """
        Initialize the NotificationManager class

        :param config: Config class object
        """
        self.notificationOnStart = config.getNotificationOnStart()
        self.notificationOn2FA = config.getNotificationOn2FA()
        self.notificationOnDrop = config.getNotificationOnDrop()
        self.notificationOnFault = config.getNotificationOnFault()
        
        self.soundPath = config.getSoundPath()      
        self.soundOnStart = config.getSoundOnStart()
        self.soundOn2FA = config.getSoundOn2FA()
        self.soundOnDrop = config.getSoundOnDrop()
        self.soundOnFault = config.getSoundOnFault()
        
    def _make_notification(self, notificationOn, soundOn, title:str ="Capsule Farmer Evolved", message:str ="New message"):
        if notificationOn:
            notification = Notify()
            notification.title = title
            notification.message = message
            notification.icon = "./assets/poro.ico"
            
            if soundOn:
                notification.audio = self.soundPath
            
            notification.send()
            
        elif soundOn:
            wave_obj = sa.WaveObject.from_wave_file(self.soundPath)
            play_obj = wave_obj.play()

    def makeNotificationOnStart(self, title, message):
        self._make_notification(self.notificationOnStart, self.soundOnStart, title, message)

    def makeNotificationOn2FA(self, title, message):
        self._make_notification(self.notificationOn2FA, self.soundOn2FA, title, message)
            
    def makeNotificationDrop(self, title, message):
        self._make_notification(self.notificationOnDrop, self.soundOnDrop, title, message)
    
    def makeNotificationOnFault(self, title, message):
        self._make_notification(self.notificationOnFault, self.soundOnFault, title, message)