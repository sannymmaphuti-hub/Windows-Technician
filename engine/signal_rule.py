class SignalRule:

    def matches(self, observation):
        raise NotImplementedError

    def create_signal(self, observation):
        raise NotImplementedError
