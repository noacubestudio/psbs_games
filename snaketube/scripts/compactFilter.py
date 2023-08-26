from psbs.extension import Extension
import re

class Example(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register_filter("compactToPatternScript", self.compactToPatternScript)

    def _decompactLine(self, line):
        lhs = []
        rhs = []

        modes_dict = {
            "no": "LEFT",
            "add": "RIGHT",
            "was": "LEFT", 
            "del": "RIGHT",
            "is": "BOTH", 
            "[": "BOTH",
            "|": "BOTH",
            "]": "BOTH"
        }

        currentMode = "BOTH"
        for word in line.split(" "):
            currentMode = modes_dict.get(word, currentMode)

            if word == "add" or word == "is" or word == "was":
                continue
            elif currentMode == "LEFT":
                lhs.append(word)
            elif currentMode == "RIGHT":
                if word == "del":
                    rhs.append("no")
                else:
                    rhs.append(word)
            else:
                lhs.append(word)
                rhs.append(word)

        result = " ".join(lhs) + " -> " + " ".join(rhs)
        return re.sub(r'\s+', ' ', result) # clean multi spaces
    
    def _customNamingSchemeToPatternScript(self, input_string):
        return input_string.replace(".", "_")

    def compactToPatternScript(self, input_string):
        # remove dots with underscores or :, depending on text
        input_string = self._customNamingSchemeToPatternScript(input_string)
        # separate blocks into left and right side
        new_lines = [self._decompactLine(line) for line in input_string.rstrip().split('\n')]
        new_string = '\n'.join(new_lines)
        return new_string