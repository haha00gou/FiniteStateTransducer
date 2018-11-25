import re
from graphviz import Digraph

class FST:
     def __init__(self, file_name):
         self.states = {0}
         self.final_states = set()  
         self.delta = {}
         self.file_to_fst(file_name)

     def add_transition(self, from_state, inputsymbol, outputsymbol):
             next_from_state = 0
             if ((from_state, inputsymbol) not in self.delta.keys()):
                 next_from_state = self.new_state()
                 self.delta[(from_state, inputsymbol)] = {(next_from_state, outputsymbol)}
             elif ((from_state, inputsymbol) in self.delta.keys() and outputsymbol not in [pair[1] for pair in self.delta[(from_state, inputsymbol)]]):
                 next_from_state = self.new_state()
                 self.delta[(from_state, inputsymbol)].add((next_from_state, outputsymbol))
             return next_from_state


     def new_state(self):
         new = max(self.states) + 1
         self.states.add(new)
         return new


     def make_final(self, state):
         self.final_states.add(state)

     def file_to_fst(self, file_name):
         file = open(file_name, encoding='utf-8-sig')
         for line in file:
            field = re.sub(r'[(:.)(\[)(\])]|(\w*=)', '', line.strip()).split()
            output = list(field[1]) + field[2:]
            input = list(field[0]) + ['eps'] * (len(output) - len(field[0]))
            self.make_path(output, input)


     def make_path(self, output, input):
         from_state = 0
         for i in range(len(output)):
             if (from_state, input[i]) in self.delta.keys() and output[i] in [pair[1] for pair in self.delta[(from_state, input[i])]]:
                 from_state = [paar[0] for paar in self.delta[(from_state, input[i])] if paar[1] == output[i]].pop()
             else:
                 from_state = self.add_transition(from_state, input[i], output[i])
             if i == len(output) - 1:
                 self.make_final(from_state)
                 return


     def draw(self):
         fst = Digraph('Finite State Transducer')
         fst.attr(rankdir='LR', size='8,5')
         for key in sorted(self.delta.keys(), key=lambda paar: paar[0]):
             for pair in self.delta[key]:
                shape = 'circle'
                if pair[0] in self.final_states:
                    shape='doublecircle'
                fst.attr('node', shape=shape)
                fst.edge(str(key[0]), str(pair[0]), label=key[1] + ':' + pair[1])
         # saving a visualization in a .gv file
         fst.render(r'fst.gv', view=True)


     def rec_lookup(self, state, visited, symbol, symbol_list, outputs, final_result):
         visited.append(state)
         if state in self.final_states:
             a_copy = outputs.copy()
             final_result.append(a_copy)
         else:
             if (state, symbol) not in self.delta.keys():
                 return
             for i in range(len(self.delta[(state, symbol)])):
                 pair = list(self.delta[(state, symbol)])[i]
                 if pair[0] not in visited:
                     outputs.append(pair[1])
                     self.rec_lookup(pair[0], visited, symbol_list[len(outputs)], symbol_list, outputs, final_result)
         if outputs:
             outputs.pop()
         visited.remove(state)

     def lookup(self, word):
         word_list = list(word) + ['eps'] * 20
         visited = []
         outputs = []
         final_result = []
         self.rec_lookup(0, visited, word_list[0], word_list, outputs, final_result)
         return final_result

#test
f = FST(r'werfen.txt')
f.draw()
verbs = ['geworfen', 'warfen', 'warfst', 'warft', 'warf', 'werfend', 'werfen', 'werfest',
         'werfet', 'werfe', 'werft', 'wirfst', 'wirf', 'würfen', 'würfest',
         'würfet', 'würfe', 'würfst']
for verb in verbs:
    print(verb)
    for i in f.lookup(verb):
        print(i)
    print()
