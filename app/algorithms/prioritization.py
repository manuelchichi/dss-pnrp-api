import numpy as np
from app.db.connection import get_db_client

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

    for criterion in normalized_criteria:
        # Comparison matrix
        comparison_matrix = construct_comparison_matrix(criterion, issues)
        # Ponderate according to dimension
        comparison_matrix = ponderate(comparison_matrix, normalized_criteria[criterion])

        # Global comparison matrix (T-norm min)
        if len(global_comparison_matrix) == 0:
            global_comparison_matrix = comparison_matrix
        else:
            global_comparison_matrix = np.minimum(global_comparison_matrix, comparison_matrix)

    # Strict relation
    strict_relation = global_comparison_matrix - global_comparison_matrix.T
    strict_relation[strict_relation < 0] = 0

    # Non dominance vector
    while len(indexes) > 0:
       non_dominance_vector = 1 - np.amax(strict_relation, 0)
       non_dominated = np.where(non_dominance_vector == max(non_dominance_vector))
       # get non dominated requirements
       order.append(list(indexes[non_dominated]))
       # remove non_dominated from matrix and indexes
       indexes = np.delete(indexes, non_dominated)
       strict_relation = np.delete(np.delete(strict_relation, non_dominated, 0), non_dominated, 1)

    # Building solution with the obtained order
    new_execution = {
        "prioritization_process_id": execution_dict["prioritization_process_id"],
        "pp_execution_id": execution_dict["pp_execution_id"],
        "solution": build_solution(order, issues)
    }
    # Update execution with the obtained solution
    client = await get_db_client()
    await client["api"]["executions"].update_one({"pp_execution_id": new_execution["pp_execution_id"]}, {"$set": new_execution})
