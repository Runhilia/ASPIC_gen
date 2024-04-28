from Literal import Literal
from Rule import Rule
from Argument import Argument

import matplotlib.pyplot as plt
import networkx as nx
import re
import streamlit as st


# Creation of a function that reads the rules from a file and returns a list of rules :
def parse_rules(file):
    rules = []
    pattern = r"\[(\w+)\]?(.*)\s*([-=]>)\s*(\W?\w+)\s?(\d+)?"
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

                priority = int(groups[4]) if groups[4] else 99
            premises_literal = None
            if premises_string:
                premises_literal = []
                for premise in premises_string:
                    premise = premise.strip()
                    if premise:
                        negate = False
                        if premise[0] == "!":
                            negate = True
                            premise = premise[1:]
                        premises_literal.append(Literal(premise, negate))
            else :
                premises_literal = None

            if conclusion_string and conclusion_string[0] == "!":
                conclusion_literal = Literal(conclusion_string[1:], True)
            else:
                conclusion_literal = Literal(conclusion_string, False)

            rules.append(Rule(premises_literal, conclusion_literal, is_defeasible, priority, Literal(rule_name, False)))
    return rules


# Creation of a function that performs the contrapositive of the strict rules :
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
            new_rule = Rule(new_premises, Literal(rule.get_premises()[i].get_value(),
                                                  not rule.get_premises()[i].get_is_negative()),
                            False, rule.get_weight(), Literal(f, False))
            # Check if the new rule is not already in the list
            rule_exists = False
            for r in rules:
                if r.get_conclusion().get_value() == new_rule.get_conclusion().get_value() and r.get_premises() == new_rule.get_premises():
                    rule_exists = True
                    break
            if not rule_exists:
                new_rules.append(new_rule)
            
    return new_rules


# Function for creating arguments from rules :
def create_arguments(total_rules):
    arguments = []
    rules = list(total_rules)  # list of Rule to be processed
    remaining_rules = list(rules)  # list of Rule to be processed
    new_argument_created = True

    # While there are rules to be processed and a new argument has been created in the last iteration
    while len(remaining_rules) > 0 and new_argument_created:
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
            if len(rule.get_premises()) > 0:
                sub_arguments = []
                # Find the sub-arguments which can be used to create a new argument
                for premise in rule.get_premises():
                    for argument in arguments:
                        if argument.get_top_rule().get_conclusion() == premise:
                            sub_arguments.append(argument)

                nb_premises = len(rule.get_premises())
                # If the rule has one premise
                if nb_premises == 1:
                    found = False
                    # Create a new argument if the sub-argument is not found in a argument for the current rule
                    for sub_argument in sub_arguments:
                        for argument in arguments:
                            if argument.get_top_rule() == rule:
                                # Check if the sub-argument is already in an sub-argument for the current rule
                                for sub in argument.get_sub_arguments():
                                    if sub_argument == sub:
                                        found = True
                                        break

                        if not found:
                            name = "A" + str(len(arguments) + 1)
                            argument = Argument(rule, [sub_argument], name)
                            arguments.append(argument)
                            new_argument_created = True
                        found = False

                # If the rule has two premises
                elif nb_premises == 2:
                    found = False
                    # Create a new argument if the 2 sub-arguments are not found in a same argument for the current rule
                    for i in range(0, len(sub_arguments)):
                        for j in range(0, len(sub_arguments)):
                            if (sub_arguments[i].get_top_rule().get_conclusion() != sub_arguments[
                                    j].get_top_rule().get_conclusion()):
                                for argument in arguments:
                                    if argument.get_top_rule() == rule:
                                        # Check if the 2 sub-arguments are already sub-arguments
                                        # in an argument for the current rule
                                        for sub in argument.get_sub_arguments():
                                            for sub2 in argument.get_sub_arguments():
                                                if sub != sub2:
                                                    if (sub_arguments[i] == sub and sub_arguments[j] == sub2) or (
                                                            sub_arguments[i] == sub2 and sub_arguments[j] == sub):
                                                        found = True
                                                        break

                                if not found:
                                    name = "A" + str(len(arguments) + 1)
                                    argument = Argument(rule, [sub_arguments[i], sub_arguments[j]], name)
                                    arguments.append(argument)
                                    new_argument_created = True
                                found = False

        remaining_rules = list(rules)

    return arguments


# Display arguments with a list of their undoable rules,
# a list of their last undoable rules and a list of their sub-arguments:
def display_arguments(arguments_list):
    ret = ""
    for argument in arguments_list:
        argument.to_string()

        defeasible_rules = argument.get_defeasible_rules()
        ret += "Defeasible rules of " + argument.get_name() + ": "
        for i, rule in enumerate(defeasible_rules):
            ret += rule.get_reference().get_value()
            if i < len(defeasible_rules) - 1:
                ret += ","
        ret += "\n"

        last_defeasible_rules = argument.get_last_defeasible_rules()
        ret += "Last defeasible rules of " + argument.get_name() + ":"
        for i, rule in enumerate(last_defeasible_rules):
            ret += rule.get_reference().get_value()
            if i < len(last_defeasible_rules) - 1:
                ret += ","
        ret += "\n"

        sub_arguments = argument.get_sub_arguments()
        ret += "Sub-arguments of " + argument.get_name() + ":"
        for sub_argument in sub_arguments:
            ret += sub_argument.get_name()
            if sub_argument != sub_arguments[-1]:
                ret += ","
        ret += "\n \n"
    return ret


# Function used to generate undercuts in relation to arguments :
def generate_undercuts(arguments):
    attackers = []
    undercuts = []

    # Get the attackers
    for argument in arguments:
        conclusion = argument.get_top_rule().get_conclusion()
        # Check if the conclusion is the negation of a rule
        if "r" in conclusion.get_value() and conclusion.get_is_negative():
            attackers.append(argument)

    # Find the undercuts
    for attacker in attackers:
        for argument in arguments:
            # Check if the attacker's conclusion is the argument's top rule's
            if argument.get_top_rule().get_reference().get_value() == attacker.get_top_rule().get_conclusion().get_value():
                undercuts.append([attacker.get_name(), argument.get_name()])
            else:
                # Find if a sub-argument be part of the attacked arguments
                for sub_argument in argument.get_sub_arguments():
                    for i, _ in enumerate(undercuts):
                        # Chek if the sub-argument is already in the undercuts list
                        if undercuts[i][0] == attacker.get_name() and undercuts[i][1] == sub_argument.get_name():
                            undercuts.append([attacker.get_name(), argument.get_name()])
                            break

    # Print the undercuts
    st.text("Number of undercuts: " + str(len(undercuts)))
    ret = ""
    for i, _ in enumerate(undercuts):
        ret += "(" + undercuts[i][0] + "," + undercuts[i][1] + ")" + " "
    ret += "\n"
    st.code(ret, language="python")
    return undercuts


# Function used to generate rebuttals in relation to the arguments :
def generate_rebuts(arguments):
    rebuts = []
    ret = ""

    for argument in arguments:
        for argument2 in arguments:
            # Check if the argument's conclusion is the negation of the argument2's conclusion
            if (argument.get_top_rule().get_conclusion().get_value() == argument2.get_top_rule().get_conclusion().get_value() and
                    argument.get_top_rule().get_conclusion().get_is_negative() != argument2.get_top_rule().get_conclusion().get_is_negative()):
                rebuts.append([argument.get_name(), argument2.get_name()])
            else:
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
    st.text("Number of rebuts: " + str(len(rebuts)))
    for i, _ in enumerate(rebuts):
        number = rebuts[i][0][1:]
        if int(number) > attacker:
            attacker = int(number)
            ret += "\n"
        ret += "(" + rebuts[i][0] + "," + rebuts[i][1] + ")" + " "
    ret += "\n"

    st.code(ret, language="python")
    return rebuts


# Representation of preferences between rules :
def represent_preferences_rules(total_rules):
    preferred_rules = {}
    for rule in total_rules:
        preferred_rules[rule.get_reference().get_value()] = rule.get_weight()

    return preferred_rules


# Create a function to compare arguments. To do this, we use a function to obtain the strongest rule
# for an argument and a function to obtain the weakest rule for an argument:
def best_rule(rules, preferred_rules):
    best_priority = 0
    for rule in rules:
        priority_rule = preferred_rules[rule.get_reference().get_value()]
        if priority_rule > best_priority:
            best_priority = priority_rule
    return best_priority


# Function to get the weakest rule for an argument :
def worst_rule(rules, preferred_rules):
    worst_priority = 99999
    for rule in rules:
        priority_rule = preferred_rules[rule.get_reference().get_value()]
        if priority_rule < worst_priority:
            worst_priority = priority_rule
    return worst_priority


# Function to compare arguments according to the principle and the link principle chosen :
def compare_arguments(arguments, preferred_rules, principle, link_principle):
    preferred_arguments = {}
    priority_argument = 0

    for argument in arguments:
        # Place the arguments without defeasible rule in the preferred arguments
        if argument.get_defeasible_rules() == []:
            preferred_arguments[argument.get_name()] = 99

        # Place the arguments with defeasible rules in the preferred arguments
        else:
            match link_principle:
                # In the case of the Weakest Link principle, we get the defeasible rules of the argument
                case "Weakest Link":
                    defeasible_rules = argument.get_defeasible_rules()
                    match principle:
                        # In the case of the Elitist principle, the argument take the priority of the best rule
                        case "Elitist":
                            priority_argument = best_rule(defeasible_rules, preferred_rules)
                        # In the case of the Democratic principle, the argument take the priority of the worst rule
                        case "Democratic":
                            priority_argument = worst_rule(defeasible_rules, preferred_rules)

                # In the case of the Last Link principle, we get the last defeasible rules of the argument
                case "Last Link":
                    last_defeasible_rules = argument.get_last_defeasible_rules()
                    match principle:
                        # In the case of the Elitist principle, the argument take the priority of the best rule
                        case "Elitist":
                            priority_argument = best_rule(last_defeasible_rules, preferred_rules)
                        # In the case of the Democratic principle, the argument take the priority of the worst rule
                        case "Democratic":
                            priority_argument = worst_rule(last_defeasible_rules, preferred_rules)

            preferred_arguments[argument.get_name()] = priority_argument
            
    # Print in order of priority
    ret = ""
    for i in range(99, -1, -1):
        has_print = False
        for argument in preferred_arguments:
            if preferred_arguments[argument] == i:
                ret += argument + " "
                has_print = True
        if i > 0 and has_print:
            ret += "> "
    ret += "\n"
    st.text("Preferred arguments: ")
    st.text(ret)
    return preferred_arguments


# Function for generating defeats :
def generate_defeats(arguments, rebuts, preferred_arguments, preferred_rules, principle, link_principle):
    defeats = []
    match principle:
        case "Elitist":
            for rebut in rebuts:
                # Check if the attacker is in the preferred arguments
                if preferred_arguments[rebut[0]] >= preferred_arguments[rebut[1]]:
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

        case "Democratic":
            for rebut in rebuts:
                for argument in arguments:
                    if argument.get_name() == rebut[1]:
                        match link_principle:
                            case "Weakest Link":
                                # Check if the attacker has a better priority than
                                # the attacked argument and all his sub-arguments
                                if preferred_arguments[rebut[0]] >= best_rule(argument.get_defeasible_rules(),
                                                                              preferred_rules):
                                    defeats.append(rebut)
                                    break
                                # Check if the attacker argument has already a defeat
                                # in a sub-argument of the attacked argument
                                else:
                                    for sub_argument in argument.get_sub_arguments():
                                        for defeat in defeats:
                                            if defeat[0] == rebut[0] and defeat[1] == sub_argument.get_name():
                                                defeats.append(rebut)
                                                break
                            case "Last Link":
                                # Check if the attacker has a better priority than
                                # the attacked argument and all his sub-arguments
                                if preferred_arguments[rebut[0]] >= best_rule(argument.get_last_defeasible_rules(),
                                                                              preferred_rules):
                                    defeats.append(rebut)
                                    break
                                # Check if the attacker argument has aleady a defeat
                                # in a sub-argument of the attacked argument
                                else:
                                    for sub_argument in argument.get_sub_arguments():
                                        for defeat in defeats:
                                            if defeat[0] == rebut[0] and defeat[1] == sub_argument.get_name():
                                                defeats.append(rebut)
                                                break

    # Print the defeats
    attacker = 1
    st.text("Number of defeats: " + str(len(defeats)))
    ret = ""
    for i, _ in enumerate(defeats):
        number = defeats[i][0][1:]
        if int(number) > attacker:
            attacker = int(number)
            ret += "\n"
        ret += "(" + defeats[i][0] + "," + defeats[i][1] + ")" + " "
    ret += "\n"
    st.code(ret, language="python")
    return defeats


# Function which gives the number of defeats received by the arguments :
def degree_of_defeat(arguments, defeats):
    deg_of_defeat = {}
    for argument in arguments:
        number_defeats = 0
        for i, _ in enumerate(defeats):
            if defeats[i][1] == argument.get_name():
                number_defeats += 1
        deg_of_defeat[argument.get_name()] = number_defeats

    return deg_of_defeat


# Function used to calculate the burden number for each argument :
def get_burden_number(arguments, defeats, steps):
    burden_number = {}
    # We calculate the burden number for each argument for the number of steps
    for i in range(0, steps):
        for argument in arguments:
            # If it is the first step, the burden number is 1
            if i == 0:
                burden_number[argument.get_name()] = [1]
            # Else the burden number is 1 + 1/burden_number of the defeated arguments
            else:
                bur = 1
                for defeat in defeats:
                    if defeat[1] == argument.get_name():
                        for arg in arguments:
                            if arg.get_name() == defeat[0]:
                                bur += 1 / (burden_number[arg.get_name()][i - 1])
                                bur = round(bur, 4)
                burden_number[argument.get_name()].append(bur)

    st.text("Burden number: ")
    ret = ""
    # Print the burden number of each argument
    for burden in burden_number:
        ret += burden + ": "
        for i in range(0, steps):
            ret += str(burden_number[burden][i]) + " "
        ret += "\n"

    st.code(ret, language="python")
    return burden_number


# Function that classifies arguments using burden-based semantics:
def rank_arguments(arguments, burden_number):
    rank = {}
    # Get the last value of the burden number of each argument
    for argument in arguments:
        rank[argument.get_name()] = burden_number[argument.get_name()][9]

    # Sort the arguments by the burden number
    rank = dict(sorted(rank.items(), key=lambda item: item[1]))

    st.text("Rank of arguments: ")
    ret = ""
    # Print the rank of the arguments
    for r in rank:
        if r == list(rank.keys())[0]:
            ret += r
        else:
            # Check if the burden number is the same that the previous argument
            if rank[r] == rank[list(rank.keys())[list(rank.keys()).index(r) - 1]]:
                ret += ", " + r
            else:
                ret += " > " + r

    st.text(ret)
    return rank


def main():
    st.title("Argumentation Framework")
    st.subheader("This is a simple implementation of an Argumentation Framework using Python.")

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        rules = parse_rules(uploaded_file.name)

        st.subheader("Rules")
        st.text("The rules are : ")
        code = ""
        for rule in rules:
            code += rule.to_string() + "\n"
        st.code(code, language="python")

        st.text("The rules and their counterparts are as follows ")
        code = ""
        total_rules = list(rules)
        for rule in rules:
            new_rules = contraposition(rule)
            for new_rule in new_rules:
                total_rules.append(new_rule)

        for rule in total_rules:
            code += rule.to_string() + "\n"
        st.code(code, language="python")

        st.subheader("Arguments ")
        code = ""
        arguments = create_arguments(total_rules)
        for argument in arguments:
            code += argument.to_string() + "\n"
        st.code(code, language="python")

        st.text(display_arguments(arguments))

        generate_undercuts(arguments)

        rebuts = generate_rebuts(arguments)
        st.subheader("Defeats")
        preferred_rules = represent_preferences_rules(total_rules)

        strat1 = st.radio("Choose a principle", ("Elitist", "Democratic"), index=None)
        strat2 = st.radio("Choose a link principle", ("Weakest Link", "Last Link"), index=None)
        if strat1 and strat2:
            preferred_arguments = compare_arguments(arguments, preferred_rules, strat1, strat2)
            defeats = generate_defeats(arguments, rebuts, preferred_arguments, preferred_rules, strat1, strat2)

            # Generation of a graph with arguments as vertices and defeats as edges :
            st.subheader("Argumentation graph")
            g = nx.DiGraph()

            # Add the nodes (arguments)
            argument_names = []
            for argument in arguments:
                argument_names.append(argument.get_name())
            g.add_nodes_from(argument_names)

            # Add the edges (attacks)
            g.add_edges_from(defeats)

            plt.figure(figsize=(8, 6))
            pos = nx.shell_layout(g)
            nx.draw(g, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=12, arrowsize=20,
                    linewidths=1, edge_color='gray', arrows=True)

            plt.title("Argumentation graph")
            st.pyplot(plt)

            # Drawing of the histogram representing the number of defeats received by the arguments :
            d_of_defeat = degree_of_defeat(arguments, defeats)

            arg_per_defeat = {}
            for argument in d_of_defeat:
                if d_of_defeat[argument] in arg_per_defeat:
                    arg_per_defeat[d_of_defeat[argument]] += 1
                else:
                    arg_per_defeat[d_of_defeat[argument]] = 1

            plt.clf()
            # Separation of data into lists for x-axis and y-axis
            x = list(arg_per_defeat.keys())
            y = list(arg_per_defeat.values())

            # Creating and displaying the histogram
            plt.bar(x, y, color='skyblue')
            plt.title('Number of arguments per defeat-in-degree')
            plt.xlabel('Histogram')
            plt.ylabel('Frequency')
            st.pyplot(plt)

            st.subheader("Rank of arguments")
            burden_number = get_burden_number(arguments, defeats, 10)

            rank_arguments(arguments, burden_number)


main()
