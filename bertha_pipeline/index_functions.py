import pandas as pd
# A function that checks the index
def index_of_function(functions, filename, function_name, start_line, end_line, start_column, end_column):
    for i in range(len(functions)):
        if functions[i][0] == filename and functions[i][1] == function_name and functions[i][2] == start_line and functions[i][3] == end_line and functions[i][4] == start_column and functions[i][5] == end_column:
            return i
    return -1
def index_functions(package):
    # The dynamic functions path:
    dyn_nodes_path = "/mansion/MH000070/bertha_pipeline/data/nodes/" + package + "_dyn_functions.csv"
    # The static functions path:
    static_nodes_path = "/mansion/MH000070/bertha_pipeline/data/nodes/" + package + "_static_functions.csv"
    # Edges file names
    static_edges_file_name = "/mansion/MH000070/bertha_pipeline/data/edges/" + package + "_static_edges.csv"
    dyn_edges_file_name = "/mansion/MH000070/bertha_pipeline/data/edges/" + package + "_dyn_edges.csv"
    # Graph files names
    indexed_nodes_file_name = "/mansion/MH000070/bertha_pipeline/model_data/nodes/" + package + "_indexed_nodes.csv"
    indexed_edges_file_name = "/mansion/MH000070/bertha_pipeline/model_data/edges/" + package + "_indexed_edges.csv"
    # Open the dynamic functions file
    dyn_functions_df = pd.read_csv(dyn_nodes_path, delimiter = " ", header = 0)
    if len(list(dyn_functions_df)) != 0:
        # Open the static functions file
        static_functions_df = pd.read_csv(static_nodes_path, delimiter = " ", header = 0)
        # Create a file for the graph
        indexed_nodes_file = open(indexed_nodes_file_name, "w")
        indexed_nodes_file.writelines(["index filename function_name start_line end_line start_column end_column returns is_async number_of_parameters parameter_names literals jelly label\n"])
        indexed_edges_file = open(indexed_edges_file_name, "w")
        indexed_edges_file.writelines(["index1 index2 src_indegree src_outdegree dst_indegree dst_outdegree occurences jelly label\n"])
        # Add them all to one list
        functions = []
        static_functions = [(function.filename, function.function_name, function.start_line, function.end_line, function.start_column, function.end_column) for function in static_functions_df.itertuples()]
        dyn_functions = [(function.filename, function.function_name, function.start_line, function.end_line, function.start_column, function.end_column) for function in dyn_functions_df.itertuples()]
        for function in static_functions_df.itertuples():
            temp = (function.filename, function.function_name, function.start_line, function.end_line, function.start_column, function.end_column)
            if temp in dyn_functions:
                functions.append((function.filename.replace("\\", "/"), function.function_name, function.start_line, function.end_line, function.start_column, function.end_column, function.returns, function.is_async, function.number_of_parameters, function.parameter_names, function.literals, "1", "1"))
            else:
                functions.append((function.filename.replace("\\", "/"), function.function_name, function.start_line, function.end_line, function.start_column, function.end_column, function.returns, function.is_async, function.number_of_parameters, function.parameter_names, function.literals, "1", "0"))
        for function in dyn_functions_df.itertuples():
            temp = (function.filename, function.function_name, function.start_line, function.end_line, function.start_column, function.end_column)
            if temp in static_functions:
                pass
            else:
                functions.append((function.filename, function.function_name, function.start_line, function.end_line, function.start_column, function.end_column, function.returns, function.is_async, function.number_of_parameters, function.parameter_names, function.literals, "0", "1"))
        # Remove duplicates
        functions = list(set(functions))
        functions = [list(function) for function in functions]
        # Fill the nodes file
        for i in range(len(functions)):
            indexed_nodes_file.writelines([str(i) + " " + str(functions[i][0]) + " " + str(functions[i][1]) + " " + str(functions[i][2]) + " " + str(functions[i][3]) + " " + str(functions[i][4]) + " " + str(functions[i][5]) + " " + str(functions[i][6]) + " " + str(functions[i][7]) + " " + str(functions[i][8]) + " " + str(functions[i][9]) + " " + str(functions[i][10]) + " " + str(functions[i][11]) + " " + str(functions[i][12]) + "\n"])
        # Open the edges files
        static_edges_df = pd.read_csv(static_edges_file_name, delimiter = " ", header = 0)
        dyn_edges_df = pd.read_csv(dyn_edges_file_name, delimiter = " ", header = 0)
        static_edges = [(edge.filename1, edge.function_name1, edge.start_line1, edge.end_line1, edge.start_column1, edge.end_column1, edge.filename2, edge.function_name2, edge.start_line2, edge.end_line2, edge.start_column2, edge.end_column2) for edge in static_edges_df.itertuples()]
        dyn_edges = [(edge.filename1, edge.function_name1, edge.start_line1, edge.end_line1, edge.start_column1, edge.end_column1, edge.filename2, edge.function_name2, edge.start_line2, edge.end_line2, edge.start_column2, edge.end_column2) for edge in dyn_edges_df.itertuples()]
        # Collecting all the edges
        all_edges = []
        for edge in static_edges_df.itertuples():
            temp = (edge.filename1.replace("\\", "/"), edge.function_name1, edge.start_line1, edge.end_line1, edge.start_column1, edge.end_column1, edge.filename2.replace("\\", "/"), edge.function_name2, edge.start_line2, edge.end_line2, edge.start_column2, edge.end_column2)
            if temp in dyn_edges:
                index1 = index_of_function(functions, temp[0].replace("\\", "/"), temp[1], temp[2], temp[3], temp[4], temp[5])
                index2 = index_of_function(functions, temp[6].replace("\\", "/"), temp[7], temp[8], temp[9], temp[10], temp[11])
                all_edges.append((index1, index2, edge.src_indegree, edge.src_outdegree, edge.dst_indegree, edge.dst_outdegree, edge.occurences,  1, 1))
            else:
                index1 = index_of_function(functions, temp[0].replace("\\", "/"), temp[1], temp[2], temp[3], temp[4], temp[5])
                index2 = index_of_function(functions, temp[6].replace("\\", "/"), temp[7], temp[8], temp[9], temp[10], temp[11])
                all_edges.append((index1, index2, edge.src_indegree, edge.src_outdegree, edge.dst_indegree, edge.dst_outdegree, edge.occurences, 1, 0))
        for edge in dyn_edges_df.itertuples():
            temp = (edge.filename1.replace("\\", "/"), edge.function_name1, edge.start_line1, edge.end_line1, edge.start_column1, edge.end_column1, edge.filename2.replace("\\", "/"), edge.function_name2, edge.start_line2, edge.end_line2, edge.start_column2, edge.end_column2)
            if temp not in static_edges:
                index1 = index_of_function(functions, temp[0], temp[1], temp[2], temp[3], temp[4], temp[5])
                index2 = index_of_function(functions, temp[6], temp[7], temp[8], temp[9], temp[10], temp[11])
                all_edges.append((index1, index2, edge.src_indegree, edge.src_outdegree, edge.dst_indegree, edge.dst_outdegree, edge.occurences, 0, 1))
        for edge in all_edges:
            indexed_edges_file.writelines([str(edge[0]) + " " + str(edge[1]) + " " + str(edge[2]) + " " + str(edge[3]) + " " + str(edge[4]) + " " + str(edge[5]) + " " + str(edge[6]) + " " + str(edge[7]) + " " + str(edge[8]) + "\n"])
        indexed_edges_file.close()
        indexed_nodes_file.close()