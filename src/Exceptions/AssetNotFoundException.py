from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException

class AssetNotFoundException(CapsuleFarmerEvolvedException):
    def __init__(self, filePath):
        super().__init__(f"Cannot find asset at {filePath}")
