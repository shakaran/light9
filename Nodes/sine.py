"""node that generates a sine wave"""


class SineGenerator(Node):
    def op(self, input, output, stateaccess):

        # input and output have names
        output.sin = stateaccess.magnitude * math.sin(stateaccess.phase+input.time)

        """
        # dict-style access for names with spaces
        output['sin'] = input['ti me']
        # underscore magic for accessing names with spaces-- the port object makes
        # this work
        output.sin=input.ti_me

        input.time = input.money
        """

    def getports(self):
        return OutputPort('sin'), InputPort('time'), InputPort('money')
