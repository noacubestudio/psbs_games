import re

from psbs.extension import Extension


class Filters(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register_filter("relaxRules", self.compactToPatternScript)
        self.register_filter("organizeLevels", self.organizeLevels)

    def _cloneMutateLine(self, line):
        if "[" not in line or "]" not in line or "/" not in line:
            return [line]
        
        # temporarily remove comments so they dont get processed
        comment = ""
        if "(" in line:
            index = line.index("(")
            comment = line[index:]
            line = line[:index].strip()

        # take a line and make copies of it that each use different parameters in a a/b/c notation of objects
        # find out how many mutations to include
        variants_count = 1
        for word in line.split(" "):
            variants_count = max(word.count("/") + 1, variants_count)

        # clone the line and choose the next mutation each time
        lines = []
        for i in range(variants_count):
            mutatedLine = line.split(" ")

            # choose the right mutations for this copy of the line
            for j, word in enumerate(mutatedLine):
                variants = word.split("/")
                variants = [var if var != '.' else '' for var in variants] # dots mean empty
                mutatedLine[j] = variants[i % len(variants)]

            # add comment to the first copy
            if i == 0:
                mutatedLine += " " + comment

            lines.append(" ".join(mutatedLine))
        
        return lines

    def _decompactLine(self, line):
        # return original line if it is already in [left] -> [right] format, or doesn't contain a rule to begin with
        if "->" in line or "[" not in line or "]" not in line:
            return line

        lhs = []
        rhs = []

        include_words_left = True
        include_words_right = True
        current_prefix = ""
        pattern_closed = False
        patterns_started = False

        for word in line.split(" "):

            # everything after end of block is at the end of a line and thus only on the RHS.
            # likewise, everything before a block start is only on the LHS.
            if word == "[":
                pattern_closed = False
                patterns_started = True

            # check if this word should appear on the left or right, determined by the last keyword
            if not patterns_started:
                include_words_left = True
                include_words_right = False
            elif pattern_closed:
                include_words_left = False
                include_words_right = True
            elif word in ["[", "|", "]", "is"]:
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

            # since spaces between "stationary player" and such would be a problem with recognizing where each object starts...
            # allow some new syntax. also some replacements for convenience using characters otherwise not allowed in object names.
            word = word.replace('.', ' ').replace('-', '_')
            
            # add the word to the sides
            if include_words_left:
                lhs.append(word)
            if include_words_right:
                rhs.append(word)
            
            if word == "]":
                pattern_closed = True

        result = " ".join(lhs) + " -> " + " ".join(rhs)
        return re.sub(r'\s+', ' ', result) # clean multi spaces
    
    def _mutateLinesArray(self, lines):
        # mutate lines with / to create variants
        result = []
        for line in lines:
            mutated_lines = self._cloneMutateLine(line)
            result.extend(mutated_lines)
        return result

    def compactToPatternScript(self, input_string):

        linesArray = input_string.rstrip().split('\n')

        # split lines with "/" into mutated copies
        linesArray = self._mutateLinesArray(linesArray)
        # clean up extra spaces
        linesArray = [re.sub(r'\s+', ' ', line) for line in linesArray]

        # separate compact blocks into left and right side
        linesArray = [self._decompactLine(line) for line in linesArray]

        return '\n'.join(linesArray)
    
    def organizeLevels(self, levels_string):
        skip_sections = 2 # title and first section don't need a character
        max_section_index = 8 + skip_sections

        output = ""
        current_section = ""
        index_in_section = 0
        section_index = 0
        line_of_level = 0
        for line in levels_string.splitlines():
            # get words following 'section ' 
            if line.strip().startswith("section"):
                current_section = line.split("section")[1].strip()
                index_in_section = 0
                section_index += 1
                continue
            # get words following 'level '
            if line.strip().startswith("level"):
                level_name = line.split("level")[1].strip()
                # if empty, increment index and use that
                if level_name == "":
                    index_in_section += 1
                    level_name = str(index_in_section)
                output += f"section {current_section}{level_name}\n"
                output += f"level   {current_section}{level_name}\n"
                line_of_level = 0
                continue
            if line.strip().startswith("#"):
                line_of_level += 1
                if line_of_level == 1 and section_index > skip_sections and section_index <= max_section_index:
                    # replace leading # with section index for color theming.
                    line = line.replace("#", str(section_index - skip_sections), 1)
                elif line_of_level == 11:
                    # replace final leading # with frame character.
                    # first level of each section gets a different frame.
                    line = line.replace("#", "£" if index_in_section > 0 else "₤", 1) 
            output += line + "\n"
        return output.strip()
