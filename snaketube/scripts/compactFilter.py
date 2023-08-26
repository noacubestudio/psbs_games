from psbs.extension import Extension
import re

class Decompact(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register_filter("relaxRules", self.compactToPatternScript)

    def _decompactLine(self, line):
        # return original line if it is already in [left] -> [right] format, or doesn't contain a rule to begin with
        if "->" in line or "[" not in line or "]" not in line:
            return line

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
            # always use the last keyword to determine whether or not to add to the left, right, or both sides
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

    def compactToPatternScript(self, input_string):
        # separate blocks into left and right side
        new_lines = [self._decompactLine(line) for line in input_string.rstrip().split('\n')]
        new_string = '\n'.join(new_lines)
        return new_string