from train.train_model.inc.train_model_enum import Controller_Mode

class Train_Controller:
    
    MAX_ENGINE_POWER = 120000
    
    def __init__(self) -> None:
        # self.v_cmd_mps = 0
        self.error_mps = 0
        self.prev_error_mps = 0
        self.kp = 0
        self.ki = 0
        #TODO: append unit to power command
        self.power_command = 0 #output of the PI controller
        self.i_term = 0 #u_k (out of the I controller)
        self.prev_i_term = 0 #u_k-1
        self.commanded_speed = 0.0
        self.auto_manual_mode = Controller_Mode.AUTO

    def set_gains(self, kp :float, ki :float) -> None:
        self.kp = kp
        self.ki = ki

    def set_commanded_speed(self, val : float) -> None:
        self.commanded_speed = val

    def get_commanded_speed(self) -> float:
        return self.commanded_speed
    
    def set_mode(self, mode : Controller_Mode):
        self.auto_manual_mode = mode

    def run(self, actual_velocity_mps : float, set_velocity_mps : float, delta_t_sec : float) -> float:
        self.error_mps = set_velocity_mps - actual_velocity_mps

        if self.power_command < Train_Controller.MAX_ENGINE_POWER:
            self.i_term = self.prev_i_term + (delta_t_sec / 2) * (self.error_mps+ self.prev_error_mps)
        else:
            self.i_term = self.prev_i_term
            # print("[TRAIN]: unsafe power")

        self.power_command = self.kp*self.error_mps + self.ki*self.i_term

        if(self.power_command > Train_Controller.MAX_ENGINE_POWER):
           self.power_command = Train_Controller.MAX_ENGINE_POWER 

        #store previous values
        self.prev_i_term = self.i_term
        self.prev_error_mps = self.error_mps

        return self.power_command