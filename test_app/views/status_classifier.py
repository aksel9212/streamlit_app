
class States:
    N_A, IN_DIALOG, IN_WORK, SOLVED = range(4)    # static member
    names = ["N_A", "IN_DIALOG", "IN_WORK", "SOLVED" ]

    @staticmethod
    def getStatusName(self, state):
        if state >= self.N_A and state <= self.SOLVED:
            return self.names[state]
        
class StatusClassification:
    """
    0: INITIALZED
    1: IN_DIALOG        # KI or Expert waits for new input from Client
    2: IN_WORK          # Client waits for feedback from KI or Expert
    3: SOLVED           # Problem solved
    """
    def __init__(self):
        self.oldstate = States.N_A
        self.state = States.N_A

    # status: raw LLM repsonse: "Status : n"
    @staticmethod
    def __parse_status(status):
        try:
            status = status.lower()
            val = status.replace("status", "")
            val = val.replace(":", "").strip()
            ival = int(val)
            return ival
        except Exception as e:
            print("ERROR: ", e)
            return 0

    def set_status(self, new_state_raw):
        new_state = self.__parse_status(new_state_raw)
        if new_state == States.N_A:
            print("ERROR")
            return 
        
        if new_state == self.oldstate:
            print("No State changed: ", new_state)
            return
        
        if new_state == States.IN_DIALOG:
            print("State set to IN_DIALOG")
        elif new_state == States.IN_WORK:
            print("State set to IN_WORK")
        elif new_state == States.SOLVED:
            print("State set to SOLVED")
        else:
            print("ERROR, wrong state:", new_state)
            
        return new_state
