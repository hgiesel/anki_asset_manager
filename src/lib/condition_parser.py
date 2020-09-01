from functools import reduce


def get_condition_parser(card, position):
    is_true = lambda v: isinstance(v, bool) and v == True
    is_false = lambda v: isinstance(v, bool) and v == False

    # [needscondection, newcondection]
    def parse_condition(cond) -> [bool, list]:
        if len(cond) == 0:
            # empty conditions
            return True, cond

        elif isinstance(cond, bool):
            return cond, cond

        ############################### COMBINATORS
        elif cond[0] == '&':
            parsed_conds = [parse_condition(i) for i in cond[1:]]
            truth_result = reduce(lambda x, y: x and y, [res[0] for res in parsed_conds])
            parsed_result = [res[1] for res in parsed_conds]

            if any([is_false(pr) for pr in parsed_result]):
                # and condition contains False
                result = False
            else:
                # filter out False
                result = list(filter(lambda v: not is_true(v), parsed_result))
                if len(result) > 1:
                    # reinsert "&"
                    result.insert(0, cond[0])
                else:
                    # flatten list, drop "&"
                    result = [item for sublist in result for item in sublist]

            return truth_result, result

        elif cond[0] == '|':
            parsed_conds = [parse_condition(i) for i in cond[1:]]
            truth_result =  reduce(lambda x, y: x or y, [res[0] for res in parsed_conds])
            parsed_result = [res[1] for res in parsed_conds]

            if any([is_true(pr) for pr in parsed_result]):
                # or condition contains True
                result = True
            else:
                # filter out True
                result = list(filter(lambda v: not is_false(v), parsed_result))
                if len(result) > 1:
                    result.insert(0, cond[0])
                else:
                    result = [item for sublist in result for item in sublist]

            return truth_result, result

        elif cond[0] == '!':
            parsed_cond = parse_condition(cond[1])

            if isinstance(parsed_cond[1], bool):
                return True, not parsed_cond[1]
            else:
                return True, [cond[0], parsed_cond[1]]

        ############################### PREDICATES
        elif cond[0] == 'card':
            if cond[1] == '=':
                val = card == cond[2]

            elif cond[1] == '!=':
                val = card != cond[2]

            elif cond[1] == 'includes':
                val = cond[2] in card

            elif cond[1] == 'startsWith':
                val = card.startswith(cond[2])

            elif cond[1] == 'endsWith':
                val = card.endswith(cond[2])

            return val, val

        elif cond[0] == 'pos':
            if cond[1] == '=':
                if (position == cond[2]):
                    return True, True

                else:
                    return False, False

            elif cond[1] == '!=':
                if (position != cond[2]):
                    return True, True

                else:
                    return False, False

        elif cond[0] == 'tag' or cond[0] == 'tagFull' or cond[0] == 'iter':
            return True, cond

    return parse_condition

def stringify_conds(conds) -> str:
    if len(conds) == 0:
        return 'true'

    elif isinstance(conds, bool) and conds:
        return 'true'

    elif isinstance(conds, bool) and not conds:
        return 'false'

    elif conds[0] == '&':
        stringified_conds = [stringify_conds(c) for c in conds[1:]]
        parsed_result = [res[1] for res in stringified_conds]
        if 'false' in parsed_result:
            return 'false'
        else:
            return ' && '.join([p for p in parsed_result if p != 'true'])

    elif conds[0] == '|':
        stringified_conds = [stringify_conds(c) for c in conds[1:]]
        parsed_result = [res[1] for res in stringified_conds]
        if 'true' in parsed_result:
            return 'true'
        else:
            return ' || '.join([p for p in parsed_result if p != 'false'])

    elif conds[0] == '!':
        stringed_cond = stringify_conds(conds[1])

        if stringed_cond == 'false':
            return 'true'
        elif stringed_cond == 'true':
            return 'false'
        else:
            return f'!({stringed_cond})'

    elif conds[0] == 'card':
        if conds[1] == '=':
            return f"'{{{{Card}}}}' === {conds[2]}"

        elif conds[1] == '!=':
            return f"'{{{{Card}}}}' === {conds[2]}"

        elif conds[1] == 'includes':
            return f"'{{{{Card}}}}'.includes('{conds[2]}')"

        elif conds[1] == 'startsWith':
            return f"'{{{{Card}}}}'.startsWith('{conds[2]}')"

        elif conds[1] == 'endsWith':
            return f"'{{{{Card}}}}'.endsWith('{conds[2]}')"

    elif conds[0] == 'tagString':
        if conds[1] == '=':
            return f"'{{{{Tags}}}}' === {conds[2]}"

        elif conds[1] == '!=':
            return f"'{{{{Tags}}}}' === {conds[2]}"

        elif conds[1] == 'includes':
            return f"'{{{{Tags}}}}'.includes('{conds[2]}')"

        elif conds[1] == 'startsWith':
            return f"'{{{{Tags}}}}'.startsWith('{conds[2]}')"

        elif conds[1] == 'endsWith':
            return f"'{{{{Tags}}}}'.endsWith('{conds[2]}')"

    elif conds[0] == 'tag':
        if conds[1] == '=':
            return f"'{{{{Tags}}}}'.split(' ').includes('{conds[2]}')"

        elif conds[1] == '!=':
            return f"'!{{{{Tags}}}}'.split(' ').includes('{conds[2]}')"

        elif conds[1] == 'includes':
            return f"'{{{{Tags}}}}'.split(' ').some(v => v.includes('{conds[2]}'))"

        elif conds[1] == 'startsWith':
            return f"'{{{{Tags}}}}'.split(' ').some(v => v.startsWith('{conds[2]}'))"

        elif conds[1] == 'endsWith':
            return f"'{{{{Tags}}}}'.split(' ').some(v => v.endsWith('{conds[2]}'))"
