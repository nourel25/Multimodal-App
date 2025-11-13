import os

class BaseController:
    def __init__(self):
        # Get project root directory (two levels up)
        self.base_dir = os.path.dirname(os.path.dirname(__file__))

        # Define audios directory
        self.audios_dir = os.path.join(self.base_dir, "assets", "audios")
        os.makedirs(self.audios_dir, exist_ok=True)