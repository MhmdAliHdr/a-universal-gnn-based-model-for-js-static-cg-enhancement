import pandas as pd
import json
import re
# A function to count the number of occurences of a node as a source node
def indegree(node, edges):
    deg = 0
    for e in edges:
        if e[1] == node:
            deg += 1
    return deg
# A function to count the number of occurences of a node as the destination node
def outdegree(node, edges):
    deg = 0
    for e in edges:
        if e[0] == node:
            deg += 1
    return deg
def make_dyn_edges(package):
    # Read the functions
    functions_df = pd.read_csv("/mansion/MH000070/bertha_pipeline/data/nodes/" + package + "_dyn_functions.csv", delimiter=" ", header=0, index_col=0)
    # The target static call graph
    package_path = package + "_dyn_cg.json.out"
    # Opening the call graph
    file = open("/mansion/MH000070/bertha_pipeline/raw_callgraphs/" + package_path, "r")
    # Reading the json
    json_file = json.load(file)
    # Extracting the files having the functions
    files = json_file["files"]
    # Collecting indices of the dependency files
    out_of_module_files_indices = [i for i in range(len(files)) if (re.findall("node_modules", files[i]) != [])]
    # Extracting the functions
    functions = functions_df.index.values
    # Reading the edges
    edges_1 = list(json_file["fun2fun"])
    edges = [edge for edge in edges_1 if (int(edge[0]) in functions and int(edge[1]) in functions)]
    # FILTER THE EDGES CORRECTLY
    # Make a csv file for the edges
    edges_csv = open("/mansion/MH000070/bertha_pipeline/data/edges/" + package + "_dyn_edges.csv", "w")
    edges_csv.writelines(["index1 filename1 function_name1 start_line1 end_line1 start_column1 end_column1 returns1 is_async1 number_of_parameters1 parameter_names1 literals1 index2 filename2 function_name2 start_line2 end_line2 start_column2 end_column2 returns2 is_async2 number_of_parameters2 parameter_names2 literals2 src_indegree src_outdegree dst_indegree dst_outdegree occurences\n"])
    # Collect structural features for the edges
    for edge in edges:
        # The indegree of the source node
        source_indegree = indegree(edge[0], edges)
        # The outdegree of the source node
        source_outdegree = outdegree(edge[0], edges)
        # The indegree of the receiver node
        receiver_indegree = indegree(edge[1], edges)
        # The outdegree of the receiver node
        receiver_outdegree = outdegree(edge[1], edges)
        # Number of times the edge is repeated
        repeated = edges.count(edge)
        edges_csv.writelines([str(edge[0]) + " " + functions_df["filename"][edge[0]] + " " + functions_df["function_name"][edge[0]] + " " + str(functions_df["start_line"][edge[0]]) + " " + str(functions_df["end_line"][edge[0]]) + " " + str(functions_df["start_column"][edge[0]]) + " " + str(functions_df["end_column"][edge[0]]) + " " + str(functions_df["returns"][edge[0]]) + " " + str(functions_df["is_async"][edge[0]]) + " " + str(functions_df["number_of_parameters"][edge[0]]) + " " + str(functions_df["parameter_names"][edge[0]]) + " " + str(functions_df["literals"][edge[0]]) + " " + str(edge[1]) + " " + str(functions_df["filename"][edge[1]]) + " " + str(functions_df["function_name"][edge[1]]) + " " + str(functions_df["start_line"][edge[1]]) + " " + str(functions_df["end_line"][edge[1]]) + " " + str(functions_df["start_column"][edge[1]]) + " " + str(functions_df["end_column"][edge[1]]) + " " + str(functions_df["returns"][edge[1]]) + " " + str(functions_df["is_async"][edge[1]]) + " " + str(functions_df["number_of_parameters"][edge[1]]) + " " + str(functions_df["parameter_names"][edge[1]]) + " " + str(functions_df["literals"][edge[1]]) + " " + str(source_indegree) + " " + str(source_outdegree) + " " + str(receiver_indegree) + " " + str(receiver_outdegree) + " " + str(repeated)+ "\n"])