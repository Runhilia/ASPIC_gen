class Argument:
    def __init__(self, top_rule, sub_arguments, name):
        self.top_rule = top_rule # Rule
        self.sub_arguments = sub_arguments # list of Argument
        self.name = name # string

    def print(self):
        print(f"{self.name} :", end=" ")

        if len(self.sub_arguments) > 0:
            for i, sub_argument in enumerate(self.sub_arguments):
                print(sub_argument.name, end="")
                if i < len(self.sub_arguments) - 1:
                    print(",", end="")
        print(" => " if self.top_rule.get_is_defeasible() else " -> ", end="")
        self.top_rule.get_conclusion().print()
        print()
    
    def __iter__(self):
        return iter(self.sub_arguments)
        
    def __next__(self):
        return next(self.sub_arguments)

    def get_top_rule(self):
        return self.top_rule

    def get_sub_arguments(self):
        return self.sub_arguments

    def get_name(self):
        return self.name
    
    def get_defeasible_rules(self):
        defeasible_rules = []
        # Check if the top rule is defeasible, if so, add it to the list
        if self.top_rule.get_is_defeasible():
            defeasible_rules.append(self.top_rule)
        
        # Add defeasible rules from sub-arguments
        for argument in self.sub_arguments:
            for defeasible_rule in argument.get_defeasible_rules():
                # Check duplicates
                if defeasible_rule not in defeasible_rules:
                    defeasible_rules.append(defeasible_rule)  
        return defeasible_rules
    
    def get_last_defeasible_rules(self):
        last_defeasible_rules = []
        # Check if the top rule is defeasible, if so, add it to the list
        if self.top_rule.get_is_defeasible():
            last_defeasible_rules.append(self.top_rule)
        else:
            # Else, add the last defeasible rules from the sub-arguments
            for argument in self.sub_arguments:
                for last_defeasible_rule in argument.get_last_defeasible_rules():
                    # Check duplicates
                    if last_defeasible_rule not in last_defeasible_rules:
                        last_defeasible_rules.append(last_defeasible_rule)
                
        return last_defeasible_rules