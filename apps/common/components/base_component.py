class BaseComponent():
    '''
    This is a basic interface for defining components. The only requirement is
    to implement the name method that uniquely identifies a component. It
    should also define other methods that implement the component functionality.
    '''

    @classmethod
    def name(cls):
        raise NotImplementedError()
