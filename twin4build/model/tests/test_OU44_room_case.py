import os
import datetime
import pandas as pd
import unittest
from twin4build.model.model import Model
from twin4build.simulator.simulator import Simulator
import twin4build.utils.plot.plot as plot
from twin4build.utils.schedule import Schedule
from twin4build.utils.piecewise_linear_schedule import PiecewiseLinearSchedule
from twin4build.utils.uppath import uppath

def extend_model(self):
    '''
        The extend_model() function adds connections between components in a system model, 
        creates a schedule object, and adds it to the component dictionary.
        The test() function sets simulation parameters and runs a simulation of the system 
        model using the Simulator() class. It then generates several plots of the simulation results using functions from the plot module.
    '''
    occupancy_schedule = Schedule(
            weekDayRulesetDict = {
                "ruleset_default_value": 0,
                "ruleset_start_minute": [0,0,0,0,0,0,0],
                "ruleset_end_minute": [0,0,0,0,0,0,0],
                "ruleset_start_hour": [6,7,8,12,14,16,18],
                "ruleset_end_hour": [7,8,12,14,16,18,22],
                "ruleset_value": [3,5,20,25,27,7,3]}, #35
            add_noise = True,
            saveSimulationResult = True,
            id = "OE20-601b-2| Occupancy schedule")
    
    indoor_temperature_setpoint_schedule = Schedule(
            weekDayRulesetDict = {
                "ruleset_default_value": 20,
                "ruleset_start_minute": [0],
                "ruleset_end_minute": [0],
                "ruleset_start_hour": [7],
                "ruleset_end_hour": [17],
                "ruleset_value": [25]},
            weekendRulesetDict = {
                "ruleset_default_value": 20,
                "ruleset_start_minute": [0],
                "ruleset_end_minute": [0],
                "ruleset_start_hour": [7],
                "ruleset_end_hour": [17],
                "ruleset_value": [21]},
            mondayRulesetDict = {
                "ruleset_default_value": 20,
                "ruleset_start_minute": [0],
                "ruleset_end_minute": [0],
                "ruleset_start_hour": [7],
                "ruleset_end_hour": [17],
                "ruleset_value": [21]},
            saveSimulationResult = True,
            id = "OE20-601b-2| Temperature setpoint schedule")

    supply_water_temperature_setpoint_schedule = PiecewiseLinearSchedule(
            weekDayRulesetDict = {
                "ruleset_default_value": {"X": [-5, 5, 7],
                                          "Y": [58, 65, 60.5]},
                "ruleset_start_minute": [0],
                "ruleset_end_minute": [0],
                "ruleset_start_hour": [5],
                "ruleset_end_hour": [7],
                "ruleset_value": [{"X": [-7, 5, 9],
                                    "Y": [72, 55, 50]}]},
            saveSimulationResult = True,
            id = "Heating system| Supply water temperature schedule")

    self.add_component(occupancy_schedule)
    self.add_component(indoor_temperature_setpoint_schedule)
    self.add_component(supply_water_temperature_setpoint_schedule)
    initial_temperature = 21
    custom_initial_dict = {"OE20-601b-2": {"indoorTemperature": initial_temperature}}
    self.set_custom_initial_dict(custom_initial_dict)

def export_csv(simulator):
    model = simulator.model
    df_input = pd.DataFrame()
    df_output = pd.DataFrame()
    df_input.insert(0, "time", simulator.dateTimeSteps)
    df_output.insert(0, "time", simulator.dateTimeSteps)

    for component in model.component_dict.values():
        for property_, arr in component.savedInput.items():
            column_name = f"{component.id} ||| {property_}"
            df_input = df_input.join(pd.DataFrame({column_name: arr}))

        for property_, arr in component.savedOutput.items():
            column_name = f"{component.id} ||| {property_}"
            df_output = df_output.join(pd.DataFrame({column_name: arr}))

    df_measuring_devices = simulator.get_simulation_readings()

    df_input.set_index("time").to_csv("input.csv")
    df_output.set_index("time").to_csv("output.csv")
    df_measuring_devices.set_index("time").to_csv("measuring_devices.csv")


class TestOU44RoomCase(unittest.TestCase):
    @unittest.skipIf(False, 'Currently not used')
    def test_OU44_room_case(self):
        stepSize = 600 #Seconds
        # startPeriod = datetime.datetime(year=2022, month=10, day=23, hour=0, minute=0, second=0)
        # endPeriod = datetime.datetime(year=2022, month=11, day=6, hour=0, minute=0, second=0)
        startPeriod = datetime.datetime(year=2022, month=1, day=3, hour=0, minute=0, second=0) #piecewise 20.5-23
        endPeriod = datetime.datetime(year=2022, month=1, day=8, hour=0, minute=0, second=0) #piecewise 20.5-23
        # startPeriod = datetime.datetime(year=2022, month=1, day=1, hour=0, minute=0, second=0) #piecewise 20.5-23
        # endPeriod = datetime.datetime(year=2022, month=2, day=1, hour=0, minute=0, second=0) #piecewise 20.5-23
        # Model.extend_model = extend_model
        model = Model(id="model", saveSimulationResult=True)
        filename = os.path.join(uppath(os.path.abspath(__file__), 1), "test_data.csv")
        model.add_outdoor_environment(filename=filename)
        # filename = "configuration_template_1space_1v_1h_0c_test_new_layout_simple_naming.xlsx"
        filename = "configuration_template_OU44_room_case.xlsx"
        model.load_model(semantic_model_filename=filename, infer_connections=True, extend_model=extend_model)
        

        simulator = Simulator()
        simulator.simulate(model,
                            stepSize=stepSize,
                            startPeriod = startPeriod,
                            endPeriod = endPeriod)
        # export_csv(simulator)

        space_name = "OE20-601b-2"
        space_heater_name = "Space heater"
        temperature_controller_name = "Temperature controller"
        CO2_controller_name = "CO2 controller"
        damper_name = "Supply damper"

        # plot.plot_space_temperature(model, simulator, space_name)
        plot.plot_space_CO2(model, simulator, space_name)
        plot.plot_outdoor_environment(model, simulator)
        plot.plot_space_heater(model, simulator, space_heater_name)
        plot.plot_space_heater_energy(model, simulator, space_heater_name)
        plot.plot_temperature_controller(model, simulator, temperature_controller_name)
        plot.plot_CO2_controller_rulebased(model, simulator, CO2_controller_name)
        # plot.plot_supply_fan(model, simulator, supply_fan_name)
        # plot.plot_supply_fan_energy(model, simulator, supply_fan_name)
        # plot.plot_supply_fan_energy(model, simulator, "Exhaust fan")
        plot.plot_space_wDELTA(model, simulator, space_name)
        plot.plot_space_energy(model, simulator, space_name)
        plot.plot_damper(model, simulator, damper_name)
