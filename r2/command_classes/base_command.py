class BaseCommand:
    def __init__(self, io, coder):
        self.io = io
        self.coder = coder

    def run(self, args):
        raise NotImplementedError("The run method must be implemented in the derived class.")
