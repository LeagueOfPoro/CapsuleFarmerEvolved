from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException

class InvalidCredentialsException(CapsuleFarmerEvolvedException):
    def __init__(self):
        super().__init__(f"Invalid account credentials.")