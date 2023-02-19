from notifypy import Notify
import pyaudio
import wave

from pathlib import Path

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
            if Path("./assets/poro.ico").exists():
                notification.icon = "./assets/poro.ico"
            elif Path("./src/assets/poro.ico").exists():
                notification.icon = "./src/assets/poro.ico"
            
            if soundOn:
                notification.audio = self.soundPath
            
            notification.send()
            
        elif soundOn:
            self.playSoundOnly()

    def makeNotificationOnStart(self, title, message):
        self._make_notification(self.notificationOnStart, self.soundOnStart, title, message)

    def makeNotificationOn2FA(self, title, message):
        self._make_notification(self.notificationOn2FA, self.soundOn2FA, title, message)
            
    def makeNotificationDrop(self, title, message):
        self._make_notification(self.notificationOnDrop, self.soundOnDrop, title, message)
    
    def makeNotificationOnFault(self, title, message):
        self._make_notification(self.notificationOnFault, self.soundOnFault, title, message)

    def playSoundOnly(self):
        chunk = 1024
        wf = wave.open(self.soundPath, "rb")
        p = pyaudio.PyAudio()

        stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

        data = wf.readframes(chunk)

        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()