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

        include_words_left = True
        include_words_right = True
        current_prefix = ""

        for word in line.split(" "):

            # check if this word should appear on the left or right, determined by the last keyword
            if word in ["[", "|", "]", "is"]:
                include_words_left = True
                include_words_right = True
            elif word in ["no", "was"]:
                include_words_left = True
                include_words_right = False
            elif word in ["add", "del"]:
                include_words_left = False
                include_words_right = True
            # else, keep as last keyword

            # keywords are either normally included, as a prefix in front of each one, or never
            if word in ["no", "del"]:
                current_prefix = "no"
                word = ""
            elif word in ["add", "is", "was"]:
                current_prefix = ""
                word = ""
            elif word in ["[", "|", "]"]:
                current_prefix = ""
            elif current_prefix != "": # normal keyword after a prefix
                word = current_prefix + " " + word
            
            # add the word to the sides
            if include_words_left:
                lhs.append(word)
            if include_words_right:
                rhs.append(word)

        result = " ".join(lhs) + " -> " + " ".join(rhs)
        return re.sub(r'\s+', ' ', result) # clean multi spaces

    def compactToPatternScript(self, input_string):
        # separate blocks into left and right side
        new_lines = [self._decompactLine(line) for line in input_string.rstrip().split('\n')]
        new_string = '\n'.join(new_lines)
        return new_string