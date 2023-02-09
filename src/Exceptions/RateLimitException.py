from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException

class RateLimitException(CapsuleFarmerEvolvedException):
    def __init__(self, retryAfter: int):
        super().__init__(f"You have been rate limited. Please try again after {retryAfter} seconds.")
