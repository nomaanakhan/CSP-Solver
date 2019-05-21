import re
import operator
import copy
import sys

allowed_operators = {
    ">": operator.gt,
    "<": operator.lt,
    "=": operator.eq,
    "!": operator.ne}

def main():
    global counter
    counter = 0
    variableList = {}
    with open(sys.argv[1], errors='ignore') as input_file:
        for i, line in enumerate(input_file):
            line = re.sub(r'\n', '', line)
            line = re.sub(r'[ \t]+$', '', line)
            variable = Variable()
            variable.label = line[0]
            tempDom = []
            for l in line[3:].split(' '):
                tempDom.append(int(l))
            variable.domain = tempDom
            variable.assignment = None
            variableList[variable.label] = variable

    constraints = []
    with open(sys.argv[2], errors='ignore') as input_file:
        for i, line in enumerate(input_file):
            line = re.sub(r'\n', '', line)
            line = re.sub(r'[ \t]+$', '', line)
            constraints.append((line[0], line[2], line[4]))

    # change this to a function based on arg3 later
    
    if sys.argv[3] == "none":
        #print(type(sys.argv[3]))
        forward_checking = False
    else:
        forward_checking = True

    vas = recursive_backtracking({}, variableList, constraints, forward_checking)
    if vas is not False:
        c = 0
        counter += 1
        print(counter, ". ", end="", sep="")
        for v in vas.keys():
            if c is len(vas.keys()) - 1:
                print(v, "=", vas[v], " solution", sep="")
            else:
                print(v, "=", vas[v], ", ", end="", sep="")
            c += 1


class Variable():
    label = None
    domain = None
    assignment = None

counter = 0

def recursive_backtracking(assigned, variableList, constraints, forward_checking):
    global counter
    if all(variable.assignment != None for variable in variableList.values()):
        return assigned

    var = select_unassigned_variable(variableList, constraints)

    orderedDomain = sorted_domain(variableList, constraints, var)
    
    for vals in orderedDomain:
        for val in vals:
            # if val is consistent with assignment accn to constraints
            val = int(val)
            flag = True
            for cons in constraints:
                if cons[0] is variableList[var].label:
                    if variableList[cons[2]].assignment is None:
                        continue
                    else:
                        flag = allowed_operators[cons[1]](val, int(variableList[cons[2]].assignment))
                        
                elif cons[2] is variableList[var].label:
                    if variableList[cons[0]].assignment is None:
                        continue
                    else:
                        flag = allowed_operators[cons[1]](int(variableList[cons[0]].assignment), val)
                        
                if flag is False:
                    c = 0
                    counter += 1
                    print(counter, ". ", end="", sep="")
                    for v in assigned.keys():
                        if c is len(assigned.keys()) - 1:
                            print(v, "=", assigned[v], ", ", end="", sep="")
                            print(variableList[var].label, "=", val, " failure", sep="")
                        else:
                            print(v, "=", assigned[v], ", ", end="", sep="")
                        c += 1
                    if counter >= 30:
                        SystemExit
                    break

            if flag is True:
                variableList[var].assignment = val
                assigned[var] = val
                resultVariableList = None
                #forward checking stuff here
                if forward_checking is True:
                    #restrict domains based on assignent
                    resultVariableList = forward_checking_function(copy.deepcopy(variableList), constraints, var)
                    #bit to make sure no domains are empty, if one is then return false
                    for variable in resultVariableList.values():
                        if len(variable.domain) is 0:
                            c = 0
                            counter += 1
                            print(counter, ". ", end="", sep="")
                            for v in assigned.keys():
                                if c is len(assigned.keys()) - 1:
                                    #print(v, "=", assigned[v], ", ", end="", sep="")
                                    print(variableList[var].label, "=", val, " failure", sep="")
                                else:
                                    print(v, "=", assigned[v], ", ", end="", sep="")
                                c += 1
                            if counter >= 30:
                                SystemExit
                            continue
                else:
                    resultVariableList = variableList

                result = recursive_backtracking(assigned, resultVariableList, constraints, forward_checking)
                if result is not False:
                    return result
                variableList[var].assignment = None
                assigned.pop(var)
    
    return False


def forward_checking_function(variableList, constraints, var):
    assignedValue = variableList[var].assignment
    # remove values from other variable domains that mess up constraints
    for cons in constraints:
        if cons[0] is variableList[var].label:
            # if other variable in constraint is not assigned then restrict domain
            if variableList[cons[2]].assignment is None:
                removalList = []
                for value in variableList[cons[2]].domain:
                    if allowed_operators[cons[1]](assignedValue, value) is False:
                        removalList.append(value)
                
                for r in removalList:
                    variableList[cons[2]].domain.remove(r)
   
        elif cons[2] is variableList[var].label:
            # if other variable in constraint is not assigned then restrict domain
            if variableList[cons[0]].assignment is None:
                removalList = []
                for value in variableList[cons[0]].domain:
                    if allowed_operators[cons[1]](value, assignedValue) is False:
                        removalList.append(value)
                for r in removalList:
                    variableList[cons[0]].domain.remove(r)
                        
    return variableList


def select_unassigned_variable(variables, constraints):
    var = None
    varList = []
    for v in variables.keys():
        # if variable has no assignment
        if variables[v].assignment == None:
            # if no variable currently being checked just take the first one
            if var == None:
                var = v
                varList.append(v)
            # check for most constrained
            elif len(variables[var].domain) > len(variables[v].domain):
                var = v
                varList = [v]
            # otherwise if equaly constrained then most constraining tie breaker
            elif len(variables[var].domain) == len(variables[v].domain):
                varcount = 0
                variablecount = 0
                # compare current best value contraint interactions if its on left side of the constraint
                varcount += sum(
                    1 for i in constraints if i[0] == variables[var].label and variables[i[2]].assignment == None)
                # compare current best value constraint interactions if its on the right side of the constraint
                varcount += sum(
                    1 for i in constraints if variables[i[0]].assignment == None and i[2] == variables[var].label)
                # compare current iteration constraint interactions if its on the left side of the constraint
                variablecount += sum(
                    1 for i in constraints if i[0] == variables[v].label and variables[i[2]].assignment == None)
                # compare current iteration constraint interactions if its on the right side of the constraint
                variablecount += sum(
                    1 for i in constraints if variables[i[0]].assignment == None and i[2] == variables[v].label)
                # if the new variable has a higher constraint interaction count then make it new current best
                if varcount < variablecount:
                    var = v
                    varList = [v]
                elif varcount == variablecount:
                    varList.append(v)
    
    return var


def sorted_domain(variableList, constraints, var):
    # create an array that holds the constraining values for each variable, lets us LCV later
    constrainingValues = {}
    for val in variableList[var].domain:
        val = int(val)
        tempValue = 0
        for cons in constraints:
            
            if cons[0] is variableList[var].label and variableList[cons[2]].assignment is None:
                for compValue in variableList[cons[2]].domain:
                    if not allowed_operators[cons[1]](val, int(compValue)):
                        tempValue += 1
            elif variableList[cons[0]].assignment is None and cons[2] == variableList[var].label:
                for compValue in variableList[cons[0]].domain:
                    if not allowed_operators[cons[1]](int(compValue), val):
                        tempValue += 1
        
        if tempValue in constrainingValues:
            constrainingValues[tempValue].append(int(val))
        else:
            constrainingValues[tempValue] = [int(val)]

    orderedDomain = []
    for s in sorted(constrainingValues.keys()):
        orderedDomain.append(constrainingValues[s])

    return orderedDomain


if __name__ == "__main__":
    main()

