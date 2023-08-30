import os 
import sys
import time
import sched
import json
import requests
from datetime import datetime


###Only for testing before distributing package
if __name__ == '__main__':
    # Define a function to move up in the directory hierarchy
    uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
    # Calculate the file path using the uppath function
    file_path = uppath(os.path.abspath(__file__), 5)
    # Append the calculated file path to the system path
    sys.path.append(file_path)

from twin4build.api.codes.ml_layer.input_data import input_data
from twin4build.api.codes.database.db_data_handler import db_connector
from twin4build.config.Config import ConfigReader
from twin4build.logger.Logging import Logging

from twin4build.api.codes.ml_layer.simulator_api import SimulatorAPI


import pandas as pd

# Initialize the logger
logger = Logging.get_logger('ai_logfile')

def transform_dict(original_dict):
    time_str = original_dict['time'][0]
    datetime_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
    formatted_time = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

    transformed_dict = {
        'simulation_time': formatted_time,
        'outdoorenvironment_outdoortemperature': original_dict['Outdoorenvironment_outdoorTemperature'][0],
        'outdoorenvironment_globalirradiation': original_dict['Outdoorenvironment_globalIrradiation'][0],
        'indoortemperature': original_dict['temperaturesensor_indoorTemperature'][0],
        'indoorco2concentration': original_dict['CO2sensor_indoorCo2Concentration'][0],
        'supplydamper_airflowrate': original_dict['Supplydamper_airFlowRate'][0],
        'supplydamper_damperposition': original_dict['Supplydamper_damperPosition'][0],
        'exhaustdamper_airflowrate': original_dict['Supplydamper_airFlowRate'][0],  # Assuming this is correct
        'exhaustdamper_damperposition': original_dict['Exhaustdamper_damperPosition'][0],
        'spaceheater_outletwatertemperature': original_dict['Spaceheater_outletWaterTemperature'][0],
        'spaceheater_power': original_dict['Spaceheater_Power'][0],
        'spaceheater_energy': original_dict['Spaceheater_Energy'][0],
        'valve_waterflowrate': original_dict['Valve_waterFlowRate'][0],
        'valve_valveposition': original_dict['Valve_valvePosition'][0],
        'temperaturecontroller_inputsignal': original_dict['Temperaturecontroller_inputSignal'][0],
        'co2controller_inputsignal': original_dict['CO2controller_inputSignal'][0],
        'temperaturesensor_indoortemperature': original_dict['temperaturesensor_indoorTemperature'][0],
        'valvepositionsensor_valveposition': original_dict['Valvepositionsensor_valvePosition'][0],
        'damperpositionsensor_damperposition': original_dict['Damperpositionsensor_damperPosition'][0],
        'co2sensor_indoorco2concentration': original_dict['CO2sensor_indoorCo2Concentration'][0],
        'heatingmeter_energy': original_dict['Heatingmeter_Energy'][0],
        'occupancyschedule_schedulevalue': original_dict['Occupancyschedule_scheduleValue'][0],
        'temperaturesetpointschedule_schedulevalue': original_dict['Temperaturesetpointschedule_scheduleValue'][0],
        'supplywatertemperatureschedule_supplywatertemperaturesetpoint': original_dict['Supplywatertemperatureschedule_supplyWaterTemperatureSetpoint'][0],
        'ventilationsystem_supplyairtemperatureschedule_schedulevaluet': original_dict['Supplyairtemperatureschedule_scheduleValue'][0],
    }

    return transformed_dict


class request_class:
     
    def __init__(self):
        # Initialize the configuration, database connection, process input data, and disconnect
        try:
                self.get_configuration()
                #self.db_connect()
        except Exception as e:
                logger.error("An error occurred during data conversion: %s", str(e))

    def get_configuration(self):
            # Read configuration using ConfigReader
            try:
                self.conf = ConfigReader()
                config_path = os.path.join(os.path.abspath(
                uppath(os.path.abspath(__file__), 4)), "config", "conf.ini")
                self.config = self.conf.read_config_section(config_path)
                logger.info("[DBConnector: Configuration has been read from file]")
            except Exception as e:
                logger.error("Error reading configuration: %s", str(e))


    def request_to_simulator_api(self):

        #url of web service will be placed here
        url = self.config["simulation_api_cred"]["url"]

        # get data from multiple sources code wiil be called here
        logger.info("Getting input data from input_data class")
        data_obj = input_data()
        _data = data_obj.input_data_for_simulation()

        simulator_obj = SimulatorAPI()
        results=simulator_obj.run_simulation(_data)

        #we will send a request to API and srote its response here

        try :
            response = requests.post(url,json=_data)

            model_output_data = response.json()

            #response_data = data_obj.output_data(response.data,inputs)

            # Check if the request was successful (HTTP status code 200)
            if response.status_code == 200:
                output_data = transform_dict(model_output_data)

                output_data['input_start_datetime'] = _data['metadata']['start_time']
                output_data['input_end_datetime'] = _data['metadata']['end_time']
                output_data['spacename'] = _data['metadata']['roomname']

                db = db_connector()
                
                db.connect()
                db.add_data(table_name="ml_simulation_results",inputs=output_data)
                db.disconnect()

                logger.info("data from the reponse is added to the database in ml_simulation_results table")
            else:
                print(response)
                logger.error("get a reponse from api other than 200 response is")
        except Exception as e :
            logger.error("An Exception occured while requesting to simulation API:",e)


if __name__ == '__main__':
    
    # function to be called
    reuest_obj = request_class()

    reuest_obj.request_to_simulator_api()
    
    
    """# Initialize the scheduler
    scheduler = sched.scheduler(time.time, time.sleep)

    # function to be called
    reuest_obj = request_class()
    
    # Schedule the first function call
    scheduler.enter(0, 1, reuest_obj.request_to_simulator_api(), ())
    #logger.info("Function called at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("Function called at:", time.strftime("%Y-%m-%d %H:%M:%S"))

    # Schedule subsequent function calls at 2-hour intervals
    interval = 60  # 2 hours in seconds

    count = 0
    while True:
        scheduler.run()
        time.sleep(interval)
        if count >= 3:
            break
        count  = count+1"""

    # This loop will keep the scheduler running indefinitely, calling the function every 2 hours.

    """Keep in mind that if you want to stop the scheduler at some point, 
    you'll need to add a condition to exit the loop. This is a basic example, 
    and in a real-world application, you might want to handle exceptions, manage the scheduler's state, 
    and possibly use a more robust scheduling library depending on your requirements."""
    





