from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException

class FailFind2FAException(CapsuleFarmerEvolvedException):
    def __init__(self):
        super().__init__("Failed to find 2FA email.")