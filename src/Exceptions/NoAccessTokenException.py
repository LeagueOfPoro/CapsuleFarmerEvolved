from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException

class NoAccessTokenException(CapsuleFarmerEvolvedException):
    def __init__(self):
        super().__init__(f"There's no authentication access_token in cookies.")