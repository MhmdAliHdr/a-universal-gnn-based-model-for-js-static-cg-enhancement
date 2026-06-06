# This script is used to calculate the number of nodes, and different kinds of edges in the packages used in the study
# This information is relevant to determine the number of epochs to use to train the model + to formally present the study
def metrics_per_package(package_name):
    ast_edges_file = open("./combined_features_asts/" + package_name + "_edges.csv")
    ast_n_edges_file = open("./combined_features_asts/" + package_name + "_negative_edges.csv")
    function_edges_file = open("./combined_features_asts/" + package_name + "_function_edges.csv")
    function_n_edges_file = open("./combined_features_asts/" + package_name + "_negative_function_edges.csv")
    nodes_file = open("./combined_features_asts/" + package_name + "_node.csv")
    node_lines = nodes_file.readlines()
    num_calls = len([1 for line in node_lines if (("CallExpression" in line) or ("NewExpression" in line))])
    num_fns = len([1 for line in node_lines if (("FunctionExpression" in line) or ("FunctionDeclaration" in line) or ("ArrowFunctionExpression" in line))])
    num_nodes = len(node_lines) - 1
    num_ast_edges = len(ast_edges_file.readlines()) - 1
    num_n_ast_edges = len(ast_n_edges_file.readlines()) - 1
    num_function_edges = len(function_edges_file.readlines()) - 1
    num_n_function_edges = len(function_n_edges_file.readlines()) - 1
    nodes_file.close()
    ast_edges_file.close()
    ast_n_edges_file.close()
    function_edges_file.close()
    function_n_edges_file.close()
    return (num_nodes, num_calls, num_fns, num_ast_edges, num_n_ast_edges, num_function_edges, num_n_function_edges)
def all_metrics():
    # Make a list to store all the values for the different packages
    all_values = []
    file = open("./used_packages.txt", "r")
    new_file = open("./packages_metrics.txt", "w")
    packages = [p.replace("\n", "") for p in file.readlines()]
    file.close()
    new_file.writelines(["package,nodes,call_nodes,function_nodes,ast_edges,negative_ast_edges,function_edges,negative_function_edges" + "\n"])
    # Loop over all the packages and grab the values of each
    for package in packages:
        # Write the values to the file
        value = metrics_per_package(package)
        new_file.writelines([str(package) + "," + str(value[0]) + "," + str(value[1]) + "," + str(value[2]) 
                             + "," + str(value[3]) + "," + str(value[4]) + "," + str(value[5]) + "," + str(value[6]) + "\n"])
        all_values.append(value)
    # Sum up the values for the last row
    sums = [0, 0, 0, 0, 0, 0, 0]
    for val in all_values:
        sums[0] = sums[0] + val[0]
        sums[1] = sums[1] + val[1]
        sums[2] = sums[2] + val[2]
        sums[3] = sums[3] + val[3]
        sums[4] = sums[4] + val[4]
        sums[5] = sums[5] + val[5]
        sums[6] = sums[6] + val[6]
    # Write the last row containing the totals
    new_file.writelines(["total," + str(sums[0]) + "," + str(sums[1]) + "," + str(sums[2]) + "," 
                         + str(sums[3]) + "," + str(sums[4]) + "," + str(sums[5]) + "," + str(sums[6]) + "\n"])
    new_file.close()
all_metrics()
