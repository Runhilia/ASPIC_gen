class Rule:
    def __init__(self, premises, conclusion, is_defeasible, weight, reference):
        self.premises = premises # set of Literal
        self.conclusion = conclusion # Literal
        self.is_defeasible = is_defeasible # boolean
        self.weight = weight # int
        self.reference = reference # Literal

    def print(self):
        self.reference.print()
        print(" :", end="")
        if len(self.premises) > 0:
            print(" ", end="")
            for i, premise in enumerate(self.premises):
                premise.print()
                if i < len(self.premises) - 1:
                    print(",", end="")
        print(" => " if self.is_defeasible else " -> ", end="")
        self.conclusion.print()
        if self.weight != -1:
            print(" " + str(self.weight))
        else :
            print()

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
