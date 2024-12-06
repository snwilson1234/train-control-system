class TrainTM():

    id = 0
    authority_diff = 0
    authority_dest = 0
    distance_m = 0
    block_i = 0
    direction = 1

    def __init__(self, auth_dest : int, auth_diff : int, id : int, block : int):
        super().__init__()
        self.authority_dest = auth_dest
        self.authority_diff = auth_diff
        self.id = id
        self.block_i = block
        self.distance_m = 0
        direction = 1