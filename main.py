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


def main():
    st.title("Argumentation Framework")
    st.text("This is a simple implementation of an Argumentation Framework using Python.")
    st.text("The rules are read from a file called rules.txt")

    rules = parse_rules("rules1.txt")
    for rule in rules:
        rule.print()


main()
