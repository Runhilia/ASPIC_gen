from Literal import Literal
from Rule import Rule
from Argument import Argument

import matplotlib.pyplot as plt
import networkx as nx
import re
import streamlit as st

def parse_rules(file):
    rules = []
    pattern = r"\[(\w+)\]?(.*)\s*([-=]>)\s*(.*)\s?(\d+)?"
    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            priority = -1
            is_defeasible = False
            premises_string = []
            conclusion_string = ""
            conclusion_literal = None
            rule_name = ""
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                rule_name = groups[0] if groups[0] else None
                premises_string = groups[1].split(",") if groups[1] else None
                is_defeasible = False if groups[2] == "->" else True
                conclusion_string = groups[3].strip() if groups[3] else None
                priority = int(groups[4]) if groups[4] else -1

            premises_literal = None
            if premises_string:
                premises_literal = []
                for premise in premises_string:
                    premise = premise.strip()  # Supprimer les espaces supplémentaires
                    if premise:
                        negate = False
                        if premise[0] == "!":
                            negate = True
                            premise = premise[1:]
                        premises_literal.append(Literal(premise, negate))
            else :
                premises_literal = None

            if conclusion_string[0] == "!":
                conclusion_literal = Literal(conclusion_string[1:], True)
            else:
                conclusion_literal = Literal(conclusion_string, False)

            rules.append(Rule(premises_literal, conclusion_literal, is_defeasible, priority, Literal(rule_name, False)))
    return rules

        
       
#Création d'une fonction qui fait la contraposée des règles strictes
def contraposition(rule):
    new_rules = []
    # If the rule is not defeasible and has premises
    if not rule.get_is_defeasible() and len(rule.get_premises()) > 0:
        # Visit each premise
        for i, _ in enumerate(rule.get_premises()):
            new_premises = list(rule.get_premises())
            new_premises.pop(i)
            new_premises.append(Literal(rule.get_conclusion().get_value(), not rule.get_conclusion().get_is_negative()))
            f = rule.get_reference().get_value() + "c" + str(i + 1)
            new_rule = Rule(new_premises, Literal(rule.get_premises()[i].get_value(), not rule.get_premises()[i].get_is_negative()), False, rule.get_weight(), Literal(f, False))
            new_rules.append(new_rule)
            
    return new_rules 
     


#Affichage des règles et de leur(s) contraposée(s) d'un tableau de règles
def print_rules(rules):
    #on cast en list pour être sur de ce qu'on manipule
    total_rules = list(rules)
    
    for rule in rules:
        new_rules = contraposition(rule)
        for new_rule in new_rules:
            total_rules.append(new_rule)
            
    for rule in total_rules:
        rule.print()
    print()
    
     
        
#Fonction qui permer de créer les arguments à partir d'une liste de règles passé en paramètre
def create_arguments(total_rules):
    arguments = []
    rules = list(total_rules) # list of Rule to be processed
    remaining_rules = list(rules) # list of Rule to be processed
    new_argument_created = True
    
    while (len(remaining_rules) > 0 and new_argument_created):
        new_argument_created = False      
        for i, rule in enumerate(remaining_rules):
            # If the rule has no premises, create a new argument
            if len(rule.get_premises()) == 0:
                name = "A" + str(len(arguments) + 1)
                argument = Argument(rule, [], name)
                arguments.append(argument)
                rules.remove(rule)
                new_argument_created = True
                
        for i, rule in enumerate(remaining_rules):
            # If the rule has premises
                sub_arguments = []
                # Find the sub-arguments which can be used to create a new argument
                for premise in rule.get_premises():
                    for argument in arguments:
                        if argument.get_top_rule().get_conclusion() == premise:
                            sub_arguments.append(argument)
                
                nb_premises = len(rule.get_premises())
                # If the rule has one premise
                if(nb_premises == 1):
                    found = False
                    # Create a new argument if the sub-argument is not found in a argument for the current rule
                    for sub_argument in sub_arguments:
                        for argument in arguments:
                            if argument.get_top_rule() == rule:
                                for sub in argument.get_sub_arguments():
                                    if sub_argument == sub:
                                        found = True
                                        break

                        if not found:
                            name = "A" + str(len(arguments) + 1)
                            argument = Argument(rule,[sub_argument], name)
                            arguments.append(argument)
                            new_argument_created = True
                        found = False
                            
                # If the rule has two premises
                elif(nb_premises == 2):
                    found = False
                    # Create a new argument if the 2 sub-arguments are not found in a same argument for the current rule
                    for i in range(0, len(sub_arguments)):
                        for j in range(0, len(sub_arguments)):
                            if(sub_arguments[i].get_top_rule().get_conclusion() != sub_arguments[j].get_top_rule().get_conclusion()):
                                for argument in arguments:
                                    if argument.get_top_rule() == rule:
                                        for sub in argument.get_sub_arguments():
                                            for sub2 in argument.get_sub_arguments():
                                                if sub != sub2:
                                                    if (sub_arguments[i] == sub and sub_arguments[j] == sub2) or (sub_arguments[i] == sub2 and sub_arguments[j] == sub):
                                                        found = True
                                                        break
                                                        
                                if not found :
                                    name = "A" + str(len(arguments) + 1)
                                    argument = Argument(rule, [sub_arguments[i], sub_arguments[j]], name)
                                    arguments.append(argument)
                                    new_argument_created = True
                                found = False
                        
        remaining_rules = list(rules)
        
    return arguments


def affichageArgument(argumentsList):
    
    for argument in argumentsList:
        argument.print()
    
    defeasible_rules = argument.get_defeasible_rules()
    print("Defeasible rules of " + argument.get_name() + ":", end=" ")
    for i, rule in enumerate(defeasible_rules):
        print(rule.get_reference().get_value(), end="")
        if i < len(defeasible_rules) - 1:
            print(",", end="")  
    print()   
    
    last_defeasible_rules = argument.get_last_defeasible_rules()
    print("Last defeasible rules of " + argument.get_name() + ":" , end=" ")
    for i, rule in enumerate(last_defeasible_rules):
        print(rule.get_reference().get_value(), end="")
        if i < len(last_defeasible_rules) - 1:
            print(",", end="")
    print()
        
    sub_arguments = argument.get_sub_arguments()
    print("Sub-arguments of " + argument.get_name() + ":" , end=" ")
    for sub_argument in sub_arguments:
        print(sub_argument.get_name(), end="")
        if sub_argument != sub_arguments[-1]:
            print(",", end="")

    print("\n")


#Fonction qui permet de générer et afficher les undercuts par rapport a la liste d'arguments passés en paramètre
def generate_undercuts(arguments):
    attackers = []
    undercuts = []
    
    for argument in arguments:
        conclusion = argument.get_top_rule().get_conclusion()
        # Check if the conclusion is the negation of a rule
        if "r" in conclusion.get_value() and conclusion.get_is_negative():
            attackers.append(argument)

    for attacker in attackers:
        for argument in arguments:
            # Check if the attacker's conclusion is the argument's top rule's 
            if argument.get_top_rule().get_reference().get_value() == attacker.get_top_rule().get_conclusion().get_value():
                undercuts.append([attacker.get_name(), argument.get_name()])
            else :
                # Find if a sub-argument be part of the attacked arguments
                for sub_argument in argument.get_sub_arguments():
                    for i, _ in enumerate(undercuts):
                        # Chek if the sub-argument is already in the undercuts list
                        if undercuts[i][0] == attacker.get_name() and undercuts[i][1] == sub_argument.get_name():
                            undercuts.append([attacker.get_name(), argument.get_name()])
                            break
          
    # Print the undercuts
    for i, _ in enumerate(undercuts):
        print("(" + undercuts[i][0] + "," + undercuts[i][1] + ")" , end=" ")
        
    print("\n")
        
    return undercuts


#Fonction qui permet de générer et d'afficher les rebuts par rapport a la liste d'argument passsé en paramètre 
def generate_rebuts(arguments):
    rebuts = []
    
    for argument in arguments:
        for argument2 in arguments:
            #Check if the argument's conclusion is the negation of the argument2's conclusion
            if (argument.get_top_rule().get_conclusion().get_value() == argument2.get_top_rule().get_conclusion().get_value() and 
            argument.get_top_rule().get_conclusion().get_is_negative() != argument2.get_top_rule().get_conclusion().get_is_negative()):
                rebuts.append([argument.get_name(), argument2.get_name()])
            else :
                # Find if a sub-argument of argument2 be part of the attacked arguments
                for sub_argument in argument2.get_sub_arguments():
                    for i, _ in enumerate(rebuts):
                        # Check if the sub-argument is already attacked by the argument 
                        if rebuts[i][0] == argument.get_name() and rebuts[i][1] == sub_argument.get_name():
                            # Check duplicates
                            if [argument.get_name(), argument2.get_name()] not in rebuts:
                                rebuts.append([argument.get_name(), argument2.get_name()])
                                break
                        
    # Print the rebuts
    attacker = 1
    print("Number of rebuts: " + str(len(rebuts)))
    for i, _ in enumerate(rebuts):
        number = rebuts[i][0][1:]
        if int(number) > attacker:
            attacker = int(number)
            print()
        print("(" + rebuts[i][0] + "," + rebuts[i][1] + ")" , end=" ")
    print("\n")
        
    return rebuts


#Représentation des préférences entre les règles d'une liste de règles passée en paramètre
def  representPreferencesRules(total_rules):
    preferred_rules = {}
    for rule in total_rules:
        if rule.get_weight() == -1:
            preferred_rules[rule.get_reference().get_value()] = 1
        elif rule.get_weight() == 0:
            preferred_rules[rule.get_reference().get_value()] = 3
        elif rule.get_weight() == 1:
            preferred_rules[rule.get_reference().get_value()] = 2 
    
    for rule in preferred_rules:
        print(rule + ":", preferred_rules[rule])


#Création d'une fonction qui permet de comparer les arguments entre eux et d'afficher cette comparaison 
def compareArguments(arguments,preferred_rules,principle,link_principle):
    preferred_arguments = {}
    priorityArgument = 0
           
    for argument in arguments:
        # Place the arguments without defeasible rule in the preferred arguments 
        if argument.get_defeasible_rules() == []:
            preferred_arguments[argument.get_name()] = 1
        
        # Place the arguments with defeasible rules in the preferred arguments
        else:
            match link_principle:
                # In the case of the Weakest Link principle, we get the defeasible rules of the argument
                case "Weakest Link":
                    defeasible_rules = argument.get_defeasible_rules()
                    match principle:
                        # In the case of the Elitist principle, the argument take the priority of the best rule
                        case "Elitist":
                            priorityArgument = 99999    
                            for rule in defeasible_rules:
                                priorityRule = preferred_rules[rule.get_reference().get_value()]
                                if priorityRule < priorityArgument:
                                    priorityArgument = priorityRule
                        # In the case of the Democratic principle, the argument take the priority of the worst rule
                        case "Democratic":
                            priorityArgument = 0
                            for rule in defeasible_rules:
                                priorityRule = preferred_rules[rule.get_reference().get_value()]
                                if priorityRule > priorityArgument:
                                    priorityArgument = priorityRule
                    
                # In the case of the Last Link principle, we get the last defeasible rules of the argument
                case "Last Link":
                    last_defeasible_rules = argument.get_last_defeasible_rules()
                    match preferred_arguments:
                        # In the case of the Elitist principle, the argument take the priority of the best rule
                        case "Elitist":
                            priorityArgument = 99999
                            for rule in last_defeasible_rules:
                                priorityRule = preferred_rules[rule.get_reference().get_value()]
                                if priorityRule < priorityArgument:
                                    priorityArgument = priorityRule
                        # In the case of the Democratic principle, the argument take the priority of the worst rule
                        case "Democratic":
                            priorityArgument = 0
                            for rule in last_defeasible_rules:
                                priorityRule = preferred_rules[rule.get_reference().get_value()]
                                if priorityRule > priorityArgument:
                                    priorityArgument = priorityRule
                                    
            preferred_arguments[argument.get_name()] = priorityArgument
        
    # Print in order of priority
    max_priority = 0
    for argument in preferred_arguments:
        if preferred_arguments[argument] > max_priority:
            max_priority = preferred_arguments[argument]
            
    for i in range(1,max_priority + 1):
        for argument in preferred_arguments:
            if preferred_arguments[argument] == i:
                print(argument, end=" ")
        if i < max_priority:
            print("<", end=" ")
    print("\n")
        
    return preferred_arguments


#Fonction permettant de générer et d'afficher les défaites
def generate_defeats(arguments, rebuts, preferred_arguments):
    defeats = []
    for rebut in rebuts:
        # Check if the attacker is in the preferred arguments
        if preferred_arguments[rebut[0]] <= preferred_arguments[rebut[1]]:
            defeats.append(rebut)
        else:
            # Check if the attacker argument has aleady a defeat in a sub-argument of the attacked argument
            for argument in arguments:
                if argument.get_name() == rebut[1]:
                    for sub_argument in argument.get_sub_arguments():
                        for defeat in defeats:
                            if defeat[0] == rebut[0] and defeat[1] == sub_argument.get_name():
                                defeats.append(rebut)
                                break
                    
    # Print the defeats
    attacker = 1
    print("Number of defeats: " + str(len(defeats)))
    for i, _ in enumerate(defeats):
        number = defeats[i][0][1:]
        if int(number) > attacker:
            attacker = int(number)
            print()
        print("(" + defeats[i][0] + "," + defeats[i][1] + ")" , end=" ")
    print("\n")
    
    return defeats



def main():
    st.title("Argumentation Framework")
    st.text("This is a simple implementation of an Argumentation Framework using Python.")
    st.text("The rules are read from a file called rules.txt")

    rules = parse_rules("rules1.txt")
    for rule in rules:
        rule.print()

        

main()
