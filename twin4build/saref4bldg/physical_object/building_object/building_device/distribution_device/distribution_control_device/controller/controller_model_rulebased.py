from .controller import Controller
class ControllerModelRulebased(Controller):
    def __init__(self, 
                **kwargs):
        super().__init__(**kwargs)

    def update_output(self):
        if self.input["actualValue"]>900:
            self.output["inputSignal"] = 1
        
        if self.input["actualValue"]>866:
            self.output["inputSignal"] = 0.9

        if self.input["actualValue"]>833:
            self.output["inputSignal"] = 0.8

        if self.input["actualValue"]>800:
            self.output["inputSignal"] = 0.7

        if self.input["actualValue"]>766:
            self.output["inputSignal"] = 0.6

        if self.input["actualValue"]>733:
            self.output["inputSignal"] = 0.5

        if self.input["actualValue"]>700:
            self.output["inputSignal"] = 0.4

        elif self.input["actualValue"]>666:
            self.output["inputSignal"] = 0.3

        elif self.input["actualValue"]>633:
            self.output["inputSignal"] = 0.2

        elif self.input["actualValue"]>600:
            self.output["inputSignal"] = 0.1
        else:
            self.output["inputSignal"] = 0
