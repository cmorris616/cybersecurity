import abc

from output import Output


class ReconOperation:

    def __init__(self, name='', target_url=''):
        self.name = name
        self.target_url = target_url

    @abc.abstractmethod
    def execute(self, args, output: Output):
        pass

    @abc.abstractmethod
    def validate(self, args):
        pass
