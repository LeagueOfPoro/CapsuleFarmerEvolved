from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException

class InvalidIMAPCredentialsException(CapsuleFarmerEvolvedException):
    def __init__(self):
        super().__init__("Invalid IMAP credentials.")