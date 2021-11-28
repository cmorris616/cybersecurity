import abc


class ReconOperation:

    def __init__(self, name='', target_url=''):
        self.name = name
        self.target_url = target_url

    @abc.abstractmethod
    def execute(self, args):
        pass

    @abc.abstractmethod
    def validate(self, args):
        pass
