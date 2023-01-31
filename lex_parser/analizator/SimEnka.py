from cmath import inf
import copy
import os
import pprint
import sys

sys.path.insert(0,'..')

import lex_parser.analizator.constants as constants

class Enka:

    # initialization

    def __init__(self, input_lines, current_pos, testing=False):
        self.rules_dict = {}
        self.states = []
        self.characters = []
        self.acceptable_states = []
        self.start_state = ''

        self.current_states = []
        self.next_character = ''

        self.current_pos = current_pos
        self.furthest_pos = -inf
        self.testing = testing

        if self.testing:
            self.LINE_SEPARATOR = '\n'
            self.INLINE_SEPARATOR = ','
            self.STATE_TRANSITION_SEPARATOR = '->'
        else:
            self.LINE_SEPARATOR = constants.LINE_SEPARATOR
            self.INLINE_SEPARATOR = constants.INLINE_SEPARATOR
            self.STATE_TRANSITION_SEPARATOR = constants.STATE_TRANSITION_SEPARATOR

        self.__parse(input_lines)
        
        if not self.testing:
            self.__epsilon_step()


    # private methods

    def __clear_data(self):
        self.current_states = [self.start_state]
        self.next_character = ''
        self.furthest_pos = -inf
        self.current_pos = 0


    def __add_to_rules_dict(self, rule):
        state_and_input, output = rule.split(self.STATE_TRANSITION_SEPARATOR)
        state, input = state_and_input.split(self.INLINE_SEPARATOR)
        output_states = output.split(self.INLINE_SEPARATOR)
        if (state, input) in self.rules_dict:
            self.rules_dict[(state, input)].extend(output_states)
        else:
            self.rules_dict[(state, input)] = output_states
        return


    def __parse(self, input_lines):
        states, characters, acceptable_states, start_state = input_lines[:4]
        rules = input_lines[4:]
        rules = [rule for rule in rules if rule != '']

        self.states = states.split(self.INLINE_SEPARATOR)
        self.characters = characters.split(self.INLINE_SEPARATOR)
        self.acceptable_states = acceptable_states.split(self.INLINE_SEPARATOR)
        self.start_state = start_state

        for rule in rules:
            self.__add_to_rules_dict(rule)

        return


    def __get_eps_states(self, states_to_be_evaluated):
        eps_states = []
        for state in states_to_be_evaluated:
            eps_states += self.rules_dict.get((state, '$'), [None])
        return eps_states


    def __prune_eps_states(self, eps_states):
        pruned_states = []
        for state in eps_states:
            if state not in self.current_states and state is not None and state != '#':
                pruned_states.append(state)
        return list(set(pruned_states))


    def __compute_eps_states(self, states_to_be_evaluated):
        return self.__prune_eps_states(self.__get_eps_states(states_to_be_evaluated))


    def __epsilon_step(self):
        if self.current_states == ['#']:
            return

        states_to_be_evaluated = self.current_states
        while len(states_to_be_evaluated) > 0:
            computed_states = self.__compute_eps_states(states_to_be_evaluated)
            self.current_states += computed_states
            states_to_be_evaluated = computed_states
            if self.is_in_acceptable_state():
                self.furthest_pos = self.current_pos
        return


    def __get_transition_states(self, input):
        transition_states = []
        for state in self.current_states:
            transition_states += self.rules_dict.get((state, input), [None])
        return transition_states


    def __prune_transition_states(self, transition_states):
        pruned_states = []
        for state in transition_states:
            if state is not None and state != '#':
                pruned_states.append(state)
        return list(set(pruned_states))


    def __compute_transition_states(self, input):
        return self.__prune_transition_states(self.__get_transition_states(input))

    
    def __copy(self):
        return copy.deepcopy(self)

    def __sim_end_step(self):
        c = self.__copy()
        c.__epsilon_step()
        return c


    # public methods

    def restart_from_pos(self, pos):
        self.__clear_data()
        if not self.testing:
            self.__epsilon_step()
        self.current_pos = pos


    def feed_next_character(self, character):
        self.next_character = character
        if self.testing:
            self.__epsilon_step()

        transition_states = self.__compute_transition_states(self.next_character)
        
        if len(transition_states) == 0:
            self.current_states = ['#']
        else:
            self.current_states = transition_states
            self.__epsilon_step()

        self.current_pos += 1

        return


    def is_in_acceptable_state(self):
        return set(self.acceptable_states).intersection(set(self.current_states)) != set()


    def has_terminated(self):
        end_sim = self.__sim_end_step()
        return end_sim.current_states == ['#']


    def string_from_current_states(self):
        end_sim = self.__sim_end_step()
        return ','.join(sorted(end_sim.current_states))

    def get_current_pos(self):
        return self.current_pos

    def set_current_pos(self, current_pos):
        self.current_pos = current_pos

    def get_furthest_pos(self):
        return self.furthest_pos

    def set_furthest_pos(self, furthest_pos):
        self.furthest_pos = furthest_pos


    def __repr__(self):
        return pprint.pformat({k:v for (k, v) in vars(self).items()}, indent=2, width=200, compact=True)

def test_enka_tests():
    dir = '../enka_tests'
    subdirs = [os.path.abspath(os.path.join(dir, subdir)) for subdir in os.listdir(dir)]

    count = 0
    for subdir in subdirs:
        config = os.path.join(subdir, 'test.c')
        input = os.path.join(subdir, 'test.a')
        output = os.path.join(subdir, 'test.b')

        with open(config, 'r') as conf_file:
            input_lines = conf_file.read().splitlines()
        
        enka = Enka(input_lines, 0, testing=True)
        enka.restart_from_pos(0)
        print(enka)

        print(input)
        with open(input) as input_file:
            input_first_line = input_file.read().splitlines()[0]
        input_characters = input_first_line.split(',')

        with open(output) as output_file:
            output_first_line = output_file.read().splitlines()[0]
        output_states = output_first_line.split('|')
        
        # Ignore the first line, since this is the eps-transition from the start state
        output_states = output_states[1:]

        assert len(output_states) == len(input_characters)

        out_list = []
        for i in range(len(input_characters)):
            char = input_characters[i]
            enka.feed_next_character(char)
            out = enka.string_from_current_states()
            out_list.append(out)

        print('Test:', subdir)

        print('Expected:')
        pprint.pprint(output_states)
        
        print('Computed:')
        pprint.pprint(out_list)

        assert output_states == out_list

        count += 1
        print(f"Passed tests: {count}")


def test_simplePpj():
    fname = '../integration_tests/simplePpjLang/tablice/<S_pocetno>25.txt'
    with open(fname, 'r') as config:
        input_lines = config.read()

    enka = Enka(input_lines.split(constants.LINE_SEPARATOR), 0)
    enka.restart_from_pos(0)
    enka.feed_next_character("'")
    enka.feed_next_character("'")
    print(enka)
    return
 
if __name__ == '__main__':
    test_enka_tests()