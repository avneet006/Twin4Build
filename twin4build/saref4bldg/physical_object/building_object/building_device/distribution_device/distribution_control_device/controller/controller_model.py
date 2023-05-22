from .controller import Controller
import torch
from scipy.optimize import least_squares
import numpy as np

import sys
import os

uppath = lambda _path,n: os.sep.join(_path.split(os.sep)[:-n])
file_path = uppath(os.path.abspath(__file__), 9)
sys.path.append(file_path)

from twin4build.logger.Logging import Logging

logger = Logging.get_logger("ai_logfile")

class ControllerModel(Controller):
    def __init__(self,
                     # isTemperatureController=None,
                     # isCo2Controller=None,
                     K_p=None,
                     K_i=None,
                     K_d=None,
                     **kwargs):
         
        logger.info("[Controller Model] : Entered in Initialise Function")

        Controller.__init__(self, **kwargs)
        self.K_p = K_p
        self.K_i = K_i
        self.K_d = K_d

        self.input = {"actualValue": None,
                          "setpointValue": None}
        self.output = {"inputSignal": None}

    def initialize(self,
                       startPeriod=None,
                       endPeriod=None,
                       stepSize=None):
        self.acc_err = 0
        self.prev_err = 0

    def do_step(self, secondTime=None, dateTime=None, stepSize=None):
        err = self.input["setpointValue"]-self.input["actualValue"]
        p = err*self.K_p
        i = self.acc_err*self.K_i
        d = (err-self.prev_err)*self.K_d
        signal_value = p + i + d
        if signal_value > 1:
            signal_value = 1
            self.acc_err = 1/self.K_i
            self.prev_err = 0
        elif signal_value < 0:
            signal_value = 0
            self.acc_err = 0
            self.prev_err = 0
        else:
            self.acc_err += err
            self.prev_err = err
            self.output["inputSignal"] = signal_value

    def do_period(self, input):
        self.clear_report()
        self.acc_err = 0
        self.prev_err = 0
        for index, row in input.iterrows():
            for key in input:
                self.input[key] = row[key]
            self.do_step()
            self.update_report()
        output_predicted = np.array(self.savedOutput["inputSignal"])
        return output_predicted

    def obj_fun(self, x, input, output):
        '''
             method sets the gains based on the input parameter x and then calls the do_period() method to calculate 
             the predicted output values. 
             It then returns the residual of the predicted output values compared to the actual output values
        '''
        self.K_p = x[0]
        self.K_i = x[1]
        self.K_d = x[2]
        output_predicted = self.do_period(input)
        res = output_predicted-output  # residual of predicted vs measured
        logger.info(f"MAE: {np.mean(np.abs(res))}")
        logger.info(f"RMSE: {np.mean(res**2)**(0.5)}")
       
        return res
        
    def calibrate(self, input=None, output=None):
        '''
               find the optimal values for the gains that minimize the residual calculated by the obj_fun() method. 
                It then sets the optimal values as the instance attributes and returns them.
        '''
        x0 = np.array([self.K_p, self.K_i, self.K_d])
        lw = [0, 0.01, 0]
        up = [1, 1, 1]
        bounds = (lw, up)
        sol = least_squares(self.obj_fun, x0=x0,
                                bounds=bounds, args=(input, output))
        self.K_p, self.K_i, self.K_d = sol.x
        logger.info(self.K_p, self.K_i, self.K_d)

        logger.info("[Controller Model] : Exited from Calibrate Function")

            # print(sol)
        return (self.K_p, self.K_i, self.K_d)
