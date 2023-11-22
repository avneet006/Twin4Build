

import os
import sys
import datetime
from dateutil.tz import tzutc

###Only for testing before distributing package
if __name__ == '__main__':
    uppath = lambda _path,n: os.sep.join(_path.split(os.sep)[:-n])
    file_path = uppath(os.path.abspath(__file__), 3)
    sys.path.append(file_path)

from twin4build.model.model import Model
from twin4build.simulator.simulator import Simulator
from twin4build.saref4bldg.physical_object.building_object.building_device.distribution_device.distribution_flow_device.flow_controller.damper.damper_system import DamperSystem
from twin4build.saref4bldg.building_space.building_space_system_co2 import BuildingSpaceSystem
from twin4build.saref.measurement.measurement import Measurement
from twin4build.utils.schedule import Schedule
import twin4build.utils.plot.plot as plot


def extend_model(self):
    ##############################################################
    ################## First, define components ##################
    ##############################################################
    position_schedule = Schedule(
            weekDayRulesetDict = {
                "ruleset_default_value": 0,
                "ruleset_start_minute": [0,0,0,0,0,0,0],
                "ruleset_end_minute": [0,0,0,0,0,0,0],
                "ruleset_start_hour": [6,7,8,12,14,16,18],
                "ruleset_end_hour": [7,8,12,14,16,18,22],
                "ruleset_value": [0,0.1,1,0,0,0.5,0.7]}, #35
            add_noise=False,
            saveSimulationResult = self.saveSimulationResult,
            id="Position schedule")

    # Define damper component
    damper = DamperSystem(
        nominalAirFlowRate = Measurement(hasValue=1.6),
        a=5,
        saveSimulationResult = self.saveSimulationResult,
        id="Damper")

    #################################################################
    ################## Add connections to the model #################
    #################################################################
    self.add_connection(position_schedule, damper, "scheduleValue", "damperPosition")

    # Cycles are not allowed (with the exeption of controllers - see the controller example). If the follwing line is commented in, 
    # a cycle is introduced and the model will generate an error when "model.get_execution_order()" is run". 
    # You can see the generated graph with the cycle in the "system_graph.png" file.
    # self.add_connection(damper, damper, "airFlowRate", "damperPosition") #<------------------- comment in to create a cycle

def test():
    '''
        The code defines and simulates a model of a position schedule and a damper component, 
        and adds connections between them. The model is simulated for a specified time period 
        and the results can be plotted. The code also generates graphs of the components and connections, 
        and the execution order of the model.
    '''
    stepSize = 600 #Seconds
    startPeriod = datetime.datetime(year=2021, month=1, day=10, hour=0, minute=0, second=0) #piecewise 20.5-23
    endPeriod = datetime.datetime(year=2021, month=1, day=12, hour=0, minute=0, second=0) #piecewise 20.5-23
    model = Model(id="example_model", saveSimulationResult=True)
    model.load_model(infer_connections=False, extend_model=extend_model)
    
    # Create a simulator instance
    simulator = Simulator()

    # Simulate the model
    simulator.simulate(model,
                        stepSize=stepSize,
                        startPeriod = startPeriod,
                        endPeriod = endPeriod)
    
    plot.plot_damper(model, simulator, "Damper", show=True)

if __name__ == '__main__':
    test()

