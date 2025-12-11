import numpy as np

def construct_comparison_matrix(criterion, issues):
    # function to make pairwise comparisons from utility function - 100 is maximum utility
    comparison_mu = lambda x, y: 1. if x >= y else 1. + (x - y) / 100

    # Comparison matrix
    comparison_matrix = np.array(
        [[comparison_mu(criteria_i["value"], criteria_j["value"])
            for issue_j in issues
                for criteria_j in issue_j["eval"]
                    if criteria_j["criteria_id"] == criterion]
                        for issue_i in issues
                            for criteria_i in issue_i["eval"]
                                if criteria_i["criteria_id"] == criterion])

    return comparison_matrix


def ponderate(matrix, weight):
    # return np.maximum(matrix, 1 - weight)
    return matrix ** weight


def build_solution(order, issues):
    initial_position = 1
    actual_position = initial_position
    solution = []
    for position_list in order:
        solution.extend(
            [{"issue_id": issues[position]["issue_id"], "position": actual_position} for position in position_list])
        actual_position += len(position_list)
    return solution


# Data processing background task
async def solve_execution(execution_dict):
    criterias = execution_dict["criterias"]
    issues = execution_dict["issues"]
    
    criterias_values = [c["value"] for c in criterias if "value" in c]
    # check criteria maps to numeric
    # check every issue has all required evaluations and are numeric

    # normalize criteria weights
    max_weight = max(criterias_values)
    normalized_criteria = {c["criteria_id"]: (c["value"] / max_weight) for c in criterias}

    indexes = np.array([i for i, _ in enumerate(issues)])
    global_comparison_matrix = []
    order = []

