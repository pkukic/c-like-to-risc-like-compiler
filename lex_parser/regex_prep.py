import sys

class RegexPrep:
    
    def __init__(self, target: str):
        self.target = target
        self.prev_regex = {}
        return
    

    def change_references_to_regex(self, regex_with_references: str) -> str:
        out_regex = regex_with_references
        for name, reg in self.prev_regex.items():
            out_regex = out_regex.replace(name, "(" + reg + ")")
        return out_regex
    

    def start(self) -> str:
        beginning_state = ""
        with open(self.target, 'w') as wf:
            lines = sys.stdin.readlines()
            for line in lines:
                if len(line.rstrip()) != 1 and line.startswith("{"):
                    # for regex definitions
                    index = line.find(" ")
                    name, reg = line[:index + 1], (line[index + 1:]).rstrip() # remove the \n from the end (or \r\n)
                    processed = self.change_references_to_regex(reg)
                    self.prev_regex.update({name[:-1]: processed})
                elif line.startswith("%X"):
                    parsed = line.split(" ")
                    beginning_state = (parsed[1]).rstrip()
                    continue
                elif line.startswith("%L"):
                    continue
                elif line.startswith("<"):
                    # for actions
                    index = line.find(">")
                    new_line = line[0:index + 1]
                    processed = self.change_references_to_regex((line[index + 1:]).rstrip())
                    new_line = new_line + processed
                    if not new_line.endswith("\n"):
                        new_line = new_line + "\n"
                    wf.write(new_line)
                else:
                    new_line = line
                    wf.write(new_line)
        return beginning_state
                    
