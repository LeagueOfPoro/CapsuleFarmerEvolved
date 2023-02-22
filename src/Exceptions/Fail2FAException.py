from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException

class Fail2FAException(CapsuleFarmerEvolvedException):
    def __init__(self):
        super().__init__("Unable to login with 2FA.")