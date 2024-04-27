class Rule:
    def __init__(self, premises, conclusion, is_defeasible, weight, reference):
        self.premises = premises # set of Literal
        self.conclusion = conclusion # Literal
        self.is_defeasible = is_defeasible # boolean
        self.weight = weight # int
        self.reference = reference # Literal
        
    def to_string(self):
        str = ""
        str += self.reference.to_string()
        str += " : "
        if len(self.premises) > 0:
            for i, premise in enumerate(self.premises):
                str += premise.to_string()
                if i < len(self.premises) - 1:
                    str += ", "
        str += " => " if self.is_defeasible else " -> "
        str += self.conclusion.to_string()
        if self.weight != 99:
            str += f" {self.weight}"
        return str

    def print(self):
        print(self.to_string())

    def get_is_defeasible(self):
        return self.is_defeasible

    def get_premises(self):
        return self.premises

    def get_conclusion(self):
        return self.conclusion
    
    def get_weight(self):
        return self.weight

    def get_reference(self):
        return self.reference
