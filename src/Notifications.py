import warnings
from notifypy import Notify
import simpleaudio as sa

class NotificationManager:

    def __init__(self, config):
        """
        Initialize the NotificationManager class

        :param config: Config class object
        """
        self.notificationOnStart = config.get("notificationOnStart", False)
        self.notificationOn2FA = config.get("notificationOn2FA", False)
        self.notificationOnDrop = config.get("notificationOnDrop", False)
        self.notificationOnFault = config.get("notificationOnFault", False)
        
        self.soundPath = config.get("soundPath","./assets/defaultNotificationSound.wav")        
        self.soundOnStart = config.get("soundOnStart", False)
        self.soundOn2FA = config.get("soundOn2FA", False)
        self.soundOnDrop = config.get("soundOnDrop", False)
        self.soundOnFault = config.get("soundOnFault", False)
        
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