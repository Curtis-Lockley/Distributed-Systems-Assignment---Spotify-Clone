import controlNODE
import helperFunctions

ROLE = "CONTROL"
myControlNode = controlNODE.controlNode(helperFunctions.get_myIP(),helperFunctions.get_random_port(),ROLE)
myControlNode.start()
