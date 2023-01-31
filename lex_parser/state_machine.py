class Transition:
    '''
    Used for storing transitions
    '''
    def __init__(self, start: int, end: int, char: int):
        self.start = start
        self.end = end
        self.char = char
        return



class StateMachine:

    def __init__(self):
        self.number_of_states = 0
        self.start_state = -1
        self.end_state = -1
        self.transitions = []
        self.symbols = set()
        return
    

    def new_epsilon_transition(self, left_state: int, right_state: int):
        self.symbols.add("$")
        self.transitions.append(Transition(left_state, right_state, "$"))
        return
    

    def new_transition(self, left_state: int, right_state: int, char: str):
        self.symbols.add(char)
        self.transitions.append(Transition(left_state, right_state, char))
        return


    def is_operator(expression: str, i: int) -> bool:
        # check if even number of '\' is in front of the target char
        counter = 0
        while (i - 1 >= 0 and expression[i-1] == "\\"):
            counter += 1
            i -= 1
        return counter % 2 == 0
    

    def find_right_prnths_index(expression: str) -> int:
        counter = 0
        for s, i in zip(expression, range(0, len(expression))):
            if s == '(' and StateMachine.is_operator(expression, i):
                counter += 1
            elif s == ')' and counter == 1 and StateMachine.is_operator(expression, i):
                return i
            elif s == ')' and StateMachine.is_operator(expression, i):
                counter -= 1
        return -1
    

    def new_state(self) -> int:
        self.number_of_states += 1
        return self.number_of_states - 1
    

    def translate(self, expression: str):
        choices = []
        num_of_prnths = 0
        start = 0
        choice_found = False
        i = 0
        while (i < len(expression)):
            if expression[i] == '(' and StateMachine.is_operator(expression, i):
                num_of_prnths += 1
            elif expression[i] == ')' and StateMachine.is_operator(expression, i):
                num_of_prnths -= 1
            elif num_of_prnths == 0 and expression[i] == '|' and StateMachine.is_operator(expression, i):
                # group into a separate expression
                choices.append(expression[start: i])
                start = i + 1
                choice_found = True
            i += 1
        
        if choice_found:
            # group the rest of the expression
            choices.append(expression[start: len(expression)])
        
        left_state = self.new_state()
        right_state = self.new_state()

        if choice_found:
            for choice in choices:
                # recursivly add epsilon transition to all groups
                left_state_temp, right_state_temp = self.translate(choice)
                self.new_epsilon_transition(left_state, left_state_temp)
                self.new_epsilon_transition(right_state_temp, right_state)
        else:
            prefixed = False
            previous_state = left_state
            i = 0
            while (i < len(expression)):
                a, b = -1, -1
                if prefixed:
                    # case 1
                    prefixed = False
                    char = ''
                    if expression[i] == 't':
                        char = '\t'
                    elif expression[i] == 'n':
                        char = '\n'
                    elif expression[i] == '_':
                        char = ' '
                    elif expression[i] == '$':
                        char = '\$'
                    else:
                        char = expression[i]
                    
                    a = self.new_state()
                    b = self.new_state()
                    self.new_transition(a, b, char)
                else:
                    # case 2
                    if expression[i] == '\\':
                        prefixed = True
                        i += 1
                        continue
                    
                    if expression[i] != '(':
                        # case 2a
                        a = self.new_state()
                        b = self.new_state()
                        if expression[i] == '$':
                            self.new_epsilon_transition(a, b)
                        else:
                            self.new_transition(a, b, expression[i])
                    else:
                        # case 2b
                        j = StateMachine.find_right_prnths_index(expression[i:])
                        left_state_temp, right_state_temp = self.translate(expression[i+1:j+i])
                        a = left_state_temp
                        b = right_state_temp
                        i = j + i
                # check for Kleen operator
                if i+1 < len(expression) and expression[i+1] == '*':
                    x = a
                    y = b
                    a = self.new_state()
                    b = self.new_state()
                    self.new_epsilon_transition(a, x)
                    self.new_epsilon_transition(y, b)
                    self.new_epsilon_transition(a, b)
                    self.new_epsilon_transition(y, x)
                    i += 1
                
                # connect with the rest of the state machine
                self.new_epsilon_transition(previous_state, a)
                previous_state = b
                i += 1
            self.new_epsilon_transition(previous_state, right_state)
        
        return left_state, right_state
