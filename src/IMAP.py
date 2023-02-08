#Credit for a large portion of this code goes to https://github.com/thomaswieland, I really didn't see a reason to redo what was already well made. However all the code within the dosync function is all original (along with some other minor changes)

import imaplib2, time, email #built using https://github.com/jazzband/imaplib2/
from threading import *
import re
 
class IMAP(object):
    def __init__(self, conn):
        self.thread = Thread(target=self.idle)
        self.M = conn
        self.code = ""
        self.event = Event()
 
    def start(self):
        self.thread.start()
 
    def stop(self):
        self.event.set()
 
    def join(self):
        self.thread.join()
 
    def idle(self):
        while True:
            try:
                if self.event.isSet():
                    return
                self.needsync = False
                def callback(args):
                    if not self.event.isSet():
                        self.needsync = True
                        self.event.set()
                self.M.idle(callback=callback)
                self.event.wait()
                if self.needsync:
                    self.event.clear()
                    self.dosync()
            except:
                self.event.set()
 
    def dosync(self):
        try:
            status, info = self.M.uid('search', None, 'ALL')
            if status == "OK":
                status, info = self.M.uid('fetch', info[0].split()[-1], '(RFC822)')
                if status == "OK":
                    object = email.message_from_bytes(info[0][1])
                    if object['From'].find('noreply@mail.accounts.riotgames.com') > -1:
                        self.code = re.findall(r'\d{6}', object["Subject"])[0]
                        self.event.set()
        except:
            self.event.set()