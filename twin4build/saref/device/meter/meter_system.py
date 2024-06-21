from twin4build.saref.device.meter.meter import Meter
from twin4build.utils.time_series_input import TimeSeriesInputSystem
from twin4build.utils.pass_input_to_output import PassInputToOutput
from twin4build.utils.signature_pattern.signature_pattern import SignaturePattern, Node, Exact, IgnoreIntermediateNodes
import twin4build.base as base
import numpy as np
import copy

def get_signature_pattern():
    node0 = Node(cls=(base.Meter), id="<n<SUB>1</SUB>(Meter)>")
    sp = SignaturePattern(ownedBy="SensorSystem", priority=-1)
    sp.add_modeled_node(node0)
    return sp


def get_power_signature_pattern():
    node0 = Node(cls=(base.Meter,))
    node1 = Node(cls=(base.Power))
    node2 = Node(cls=(base.Fan))
    sp = SignaturePattern(ownedBy="SensorSystem")
    sp.add_edge(Exact(object=node0, subject=node1, predicate="observes"))
    sp.add_edge(Exact(object=node1, subject=node2, predicate="isPropertyOf"))
    sp.add_input("measuredValue", node2, "Power")
    sp.add_modeled_node(node0)
    return sp


class MeterSystem(Meter):
    sp = [get_signature_pattern(), get_power_signature_pattern()]
    def __init__(self,
                 filename=None,
                #  addUncertainty=False,
                **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.datecolumn = 0
        self.valuecolumn = 1
        # self.addUncertainty = addUncertainty
        self._config = {"parameters": {},
                        "readings": {"filename": self.filename,
                                     "datecolumn": self.datecolumn,
                                     "valuecolumn": self.valuecolumn}
                        }
                        

    @property
    def config(self):
        return self._config

    def set_is_physical_system(self):
        assert (len(self.connectsAt)==0 and self.filename is None)==False, f"Sensor object \"{self.id}\" has no inputs and the argument \"filename\" in the constructor was not provided."
        if len(self.connectsAt)==0:
            self.isPhysicalSystem = True
        else:
            self.isPhysicalSystem = False

    def set_do_step_instance(self):
        if self.isPhysicalSystem:
            self.do_step_instance = self.physicalSystem
        else:
            self.do_step_instance = PassInputToOutput(id="pass input to output")

    def cache(self,
            startTime=None,
            endTime=None,
            stepSize=None):
        pass
        
    def initialize(self,
                    startTime=None,
                    endTime=None,
                    stepSize=None,
                    model=None):
        if self.filename is not None:
            self.physicalSystem = TimeSeriesInputSystem(id=f"time series input - {self.id}", filename=self.filename)
        else:
            self.physicalSystem = None
        self.set_is_physical_system()
        self.set_do_step_instance()
        self.do_step_instance.input = self.input
        self.do_step_instance.output = self.output
        self.do_step_instance.initialize(startTime,
                                        endTime,
                                        stepSize)

        # self.inputUncertainty = copy.deepcopy(self.input)
        # percentile = 2
        # self.standardDeviation = self.observes.MEASURING_UNCERTAINTY/percentile
        # property_ = self.observes
        # if property_.MEASURING_TYPE=="P":
        #     key = list(self.inputUncertainty.keys())[0]
        #     self.inputUncertainty[key] = property_.MEASURING_UNCERTAINTY/100
        # else:
        #     key = list(self.inputUncertainty.keys())[0]
        #     self.inputUncertainty[key] = property_.MEASURING_UNCERTAINTY

    def do_step(self, secondTime=None, dateTime=None, stepSize=None):
        self.do_step_instance.input = self.input
        self.do_step_instance.do_step(secondTime=secondTime, dateTime=dateTime, stepSize=stepSize)
        # if self.addUncertainty:
        #     for key in self.do_step_instance.output:
        #         self.output[key] = self.do_step_instance.output[key] + np.random.normal(0, self.standardDeviation)
        # else:
        self.output = self.do_step_instance.output

    def get_subset_gradient(self, x_key, y_keys=None, as_dict=False):
        if as_dict==False:
            return np.array([1])
        else:
            return {key: 1 for key in y_keys}
        
    def get_physical_readings(self,
                            startTime=None,
                            endTime=None,
                            stepSize=None):
        assert self.physicalSystem is not None, "Cannot return physical readings as the argument \"filename\" was not provided when the object was initialized."
        self.physicalSystem.initialize(startTime,
                                        endTime,
                                        stepSize)
        return self.physicalSystem.physicalSystemReadings