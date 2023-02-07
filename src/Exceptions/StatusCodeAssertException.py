from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException

class StatusCodeAssertException(CapsuleFarmerEvolvedException):
    def __init__(self, expected, received, url):
        self.expected = expected
        self.received = received
        self.url = url
        super().__init__(f"Received unexpected status code. Wanted {self.expected} but got {self.received} in {self.url}")
