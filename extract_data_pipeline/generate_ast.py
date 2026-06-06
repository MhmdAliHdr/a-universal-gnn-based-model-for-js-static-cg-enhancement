import esprima as parser
import pathlib
import json
import pandas as pd
from repos import clone_repo
from pathlib import Path
import random as rand
import logging
import numpy as np
from distancia import Jaccard
import re
import time
# Directory including the packages
PACKAGES_DIR = "./packages/"
# Directory including the ASTs
AST_DIR = "./asts/"
CALLGRAPHS_DIR = "./callgraphs/"
# The following reference was used for logging timestamps
# AdamE, C. Josh, djvg, Gab, gae123, G., Hans, H. James, Michael, paidhima, Toros91, user2176576, Zipp, R. StackOverflow February, 4 2015. Print timestamp for logging in Python.
# https://stackoverflow.com/questions/28330317/print-timestamp-for-logging-in-python. Retrieved on November 20, 2025
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING, datefmt='%Y-%m-%d %H:%M:%S')
# This function clear duplicate entries in the repos_data.txt file keeping the latest entry
def clear_dup_hashes():
    new_file = open("clean_repos_data.txt", "w")
    new_file.writelines(["package,repo_link,commit_hash" + "\n"])
    old_file = open("repos_data.txt", "r")
    packages_data = dict()
    # Takes advantage of overwriting a key's data to make sure only the latest commit hash is included
    for line in old_file.readlines():
        data = line.split(" ")
        if len(data) == 3:
            package_name = data[0].replace(",", "")
            repo_link = data[1].replace(":", "")
            commit_hash = data[2].replace("\n", "")
            packages_data[package_name] = (repo_link, commit_hash)
    for package in packages_data.keys():
        new_file.writelines(str(package) + "," + str(packages_data[package][0]) + "," + str(packages_data[package][1]) + "\n")
    new_file.close()
    old_file.close()
def build_static_csvs_for_pkg(package_name):
    # Create a csv file for the package's AST nodes
    ast_nodes_file = open(AST_DIR + package_name + "_node.csv", "w")
    ast_nodes_file.writelines(["id,type,name,params_len,argument_len,start_line,start_column,end_line,end_column,file_name" + "\n"])
    ast_edges_file = open(AST_DIR + package_name + "_edges.csv", "w")
    ast_edges_file.writelines(["src,dst" + "\n"])
    ast_function_edges_file = open(AST_DIR + package_name + "_function_edges.csv", "w")
    ast_function_edges_file.writelines(["src,dst" + "\n"])
    # Initialize the ID
    id = 1
    # Collect all the JavaScript file paths in the package
    package_dir = pathlib.Path(PACKAGES_DIR + package_name)
    dir_queue = []
    file_list = []
    edges = []
    dir_queue.append(package_dir)
    while dir_queue != []:
            current_dir = dir_queue.pop(0)
            for file in current_dir.iterdir():
                if file.is_dir() and file.name != "node_modules":
                    dir_queue.append(file)
                if file.name.endswith(".js"):
                    file_list.append(str(file))
    ids = [1]
    ast_nodes = []
    # Generate the AST for each file
    while file_list != []:
        current_file_path = file_list.pop(0)
        current_file = open(current_file_path, "r")
        ast = parser.parseScript(current_file.read(), {"loc": True})
        # Loop over the AST and extract for each node
        if max(ids) == 1:
            nodes_queue = [(max(ids), ast)]
        else:
            nodes_queue = [(max(ids) + 1, ast)]
            ids.append(max(ids) + 1)
        while nodes_queue != []:
            try:
                current_node = nodes_queue.pop(0)
                # its id
                node_id = current_node[0]
                # its type
                node_type = current_node[1].type
                # its name
                if current_node[1].name != None:
                    node_name = current_node[1].name
                elif node_type == "CallExpression":
                    if current_node[1].callee.name != None:
                        node_name = current_node[1].callee.name
                    elif current_node[1].callee.object.name != None:
                        node_name = current_node[1].callee.object.name
                else:
                    node_name = ""
                if current_node[1].id != None:
                    # Give the inserted node an id to add an edge from the current node to the newly found one
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].id))
                # its parameter numbers
                try:
                    node_param_len = len(list(current_node[1].params))
                    for param in current_node[1].params:
                        new_id = max(ids) + 1
                        ids.append(new_id)
                        edges.append([node_id, new_id])
                        ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                        nodes_queue.append((new_id, param))
                except:
                    node_param_len = -1
                # its argument length
                if current_node[1].arguments != None:
                    node_arg_len = len(list(current_node[1].arguments))
                    for arg in current_node[1].arguments:
                        new_id = max(ids) + 1
                        ids.append(new_id)
                        edges.append([node_id, new_id])
                        ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                        nodes_queue.append((new_id, arg))
                elif current_node[1].argument != None:
                    node_arg_len = 1
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].argument))
                else:
                    node_arg_len = -1
                if current_node[1].expression != None:
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].expression))
                if current_node[1].consequent != None:
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].consequent))
                if current_node[1].left != None:
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].left))
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].right))
                if current_node[1].callee != None:
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].callee))
                if current_node[1].test != None:
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].test))
                # start line
                node_start_line = current_node[1].loc.start.line
                # start column
                node_start_column = current_node[1].loc.start.column
                # end line
                node_end_line = current_node[1].loc.end.line
                # end column
                node_end_column = current_node[1].loc.end.column
                # file name
                node_filename = str(current_file_path)
                if isinstance(current_node[1].body, list):
                    for node in current_node[1].body:
                        new_id = max(ids) + 1
                        ids.append(new_id)
                        edges.append([node_id, new_id])
                        ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                        nodes_queue.append((new_id, node))
                elif current_node[1].body != None:    
                    new_id = max(ids) + 1
                    ids.append(new_id)
                    edges.append([node_id, new_id])
                    ast_edges_file.writelines([str(node_id) + "," + str(new_id) + "\n"])
                    nodes_queue.append((new_id, current_node[1].body))
                # Collect the current information about the nodes in a list
                ast_nodes.append([str(node_id), str(node_type), str(node_name), str(node_arg_len), str(node_param_len), str(node_start_line), str(node_start_column), str(node_end_line), str(node_end_column), str(node_filename), ])
                # Excluding the following node types as per Graphia
                if node_type not in ["ExpressionStatement", "Literal", "BinaryExpression"]:
                    ast_nodes_file.writelines([str(node_id) + "," + str(node_type) + "," + str(node_name) + "," + str(node_param_len) + "," + str(node_arg_len) + "," + str(node_start_line) + "," + str(node_start_column) + "," + str(node_end_line) + "," + str(node_end_column) + "," + str(node_filename) + "\n"])
            except:
                continue
    # Read the static call graph
    static_callgraph_file = open(CALLGRAPHS_DIR + package_name + "_static_cg.json")
    static_callgraph = json.load(static_callgraph_file)
    # Collect the call edges
    static_call_edges = static_callgraph["call2fun"]
    # Loop over the static call edges
    for edge in static_call_edges:
    # Get a call edge
    # Retrace the vertices of the edge to find:
        out_vertex = edge[0]
        in_vertex = edge[1]
        # The file they belong to
        out_vertex_file = static_callgraph["files"][int(static_callgraph["calls"][str(out_vertex)].split(":")[0])]
        in_vertex_file = static_callgraph["files"][int(static_callgraph["functions"][str(in_vertex)].split(":")[0])]
        # The start line
        out_vertex_start_line = int(static_callgraph["calls"][str(out_vertex)].split(":")[1])
        in_vertex_start_line = int(static_callgraph["functions"][str(in_vertex)].split(":")[1])
        # The start column
        out_vertex_start_column = int(static_callgraph["calls"][str(out_vertex)].split(":")[2])
        in_vertex_start_column = int(static_callgraph["functions"][str(in_vertex)].split(":")[2])
        # The end line
        out_vertex_end_line = int(static_callgraph["calls"][str(out_vertex)].split(":")[3])
        in_vertex_end_line = int(static_callgraph["functions"][str(in_vertex)].split(":")[3])
        # And the end column
        out_vertex_end_column = int(static_callgraph["calls"][str(out_vertex)].split(":")[4])
        in_vertex_end_column = int(static_callgraph["functions"][str(in_vertex)].split(":")[4])
        in_node_index = -1
        out_node_index = -1
        # Compare the vertices to the collected nodes using the collected information
        for node in ast_nodes:
            current_node_file = node[9].replace("\\", "/").replace("extract_data_for_graphia/packages/" + package_name, "")[1:]
            current_node_start_line = int(node[5])
            current_node_start_column = int(node[6])
            current_node_end_line = int(node[7])
            current_node_end_column = int(node[8])
            # Excluding dependencies
            if in_vertex_file.split("/")[0] != "node_modules":
                if (current_node_file.replace("ackages/" + package_name + "/", "") == in_vertex_file) and (current_node_start_line == in_vertex_start_line) and (current_node_end_line == in_vertex_end_line) and ((current_node_start_column + 1) == in_vertex_start_column) and ((current_node_end_column + 1) == in_vertex_end_column):
                    in_node_index = node[0]
        for node in ast_nodes:
            current_node_file = node[9].replace("\\", "/").replace("extract_data_for_graphia/packages/" + package_name, "")[1:]
            current_node_start_line = int(node[5])
            current_node_start_column = int(node[6])
            current_node_end_line = int(node[7])
            current_node_end_column = int(node[8])
            # Excluding dependencies
            if out_vertex_file.split("/")[0] != "node_modules":
                if (current_node_file.replace("ackages/" + package_name + "/", "") == out_vertex_file) and (current_node_start_line == out_vertex_start_line) and (current_node_end_line == out_vertex_end_line) and ((current_node_start_column + 1) == out_vertex_start_column) and ((current_node_end_column + 1) == out_vertex_end_column):
                    out_node_index = node[0]
        if (in_node_index != -1) and (out_node_index != -1):
            ast_function_edges_file.writelines([str(out_node_index) + "," + str(in_node_index) + "\n"])
    # The out vertex should belong to a node of the type "CallExpression" or similar
    # The in vertex should belong to a node of the type "FunctionDeclaration" or similar
    # Close the files
    ast_nodes_file.close()
    ast_edges_file.close()
    ast_function_edges_file.close()
    return ids
# The assign_new_ids function assigns new ids to the nodes from 0 from the number of nodes - 1
# The function then adds a column "new_id" with the new ids and changes the edges in the function_edges csv file so they refer to the new_id column
# As in Graphia
def assign_new_ids(package_name):
    # Read the nodes file
    nodes_df = pd.read_csv("./asts/" + package_name + "_node.csv")
    # Read its ids
    # Put all the ids in a list
    list_nodes = list(nodes_df["id"])
    # Read the function edges file
    fn_edges_df = pd.read_csv("./asts/" + package_name + "_function_edges.csv")
    # Create a list for the "new" edges (we're just changing the ids, the actual edges are the same)
    new_edges = []
    # Use the index of the ids in the list to create the new edges
    for edge in fn_edges_df.iterrows():
        new_edges.append([list_nodes.index(edge[1]["src"]), list_nodes.index(edge[1]["dst"])])
    # Note: The list itself has all the ids and is indexed from 0 to (number of nodes - 1), so we take advantage of that
    # Rewrite the csv files:
    nodes_csv = open("./asts/" + package_name + "_node.csv", "w")
    nodes_csv.writelines(["id,type,name,params_len,argument_len,start_line,start_column,end_line,end_column,file_name,new_id" + "\n"])
    fn_edges_csv = open("./asts/" + package_name + "_function_edges.csv", "w")
    fn_edges_csv.writelines(["src,dst" + "\n"])
    #   The nodes one with the "new_id" column
    for node in nodes_df.iterrows():
        if node[1]["name"] == "nan":
            node_name = ""
        else:
            node_name = node[1]["name"]
        nodes_csv.writelines([str(node[1]["id"]) + "," + str(node[1]["type"]) + "," + str(node_name) + "," + str(node[1]["params_len"]) + "," + str(node[1]["argument_len"]) + "," + str(node[1]["start_line"]) + "," + str(node[1]["start_column"]) + "," + str(node[1]["end_line"]) + "," + str(node[1]["end_column"]) + "," + str(node[1]["file_name"]) + "," + str(node[0]) + "\n"])
    nodes_csv.close()
    #   The function edges one with the new ids
    for new_edge in new_edges:
        fn_edges_csv.writelines([str(new_edge[0]) + "," + str(new_edge[1]) + "\n"])
    fn_edges_csv.close()
    # Do the same for the regular ast edges
    # Read the function edges file
    ast_edges_df = pd.read_csv("./asts/" + package_name + "_edges.csv")
    # Create a list for the "new" edges (we're just changing the ids, the actual edges are the same)
    new_ast_edges = []
    # Use the index of the ids in the list to create the new edges
    for edge in ast_edges_df.iterrows():
        try:
            new_ast_edges.append([list_nodes.index(edge[1]["src"]), list_nodes.index(edge[1]["dst"])])
        except:
            continue
    ast_edges_csv = open("./asts/" + package_name + "_edges.csv", "w")
    ast_edges_csv.writelines(["src,dst" + "\n"])
    for new_ast_edge in new_ast_edges:
        ast_edges_csv.writelines([str(new_ast_edge[0]) + "," + str(new_ast_edge[1]) + "\n"])
    ast_edges_csv.close()
# Dynamic edges
def build_dynamic_edges_csv(package_name):
    # Create a file for the dynamic edges
    dyn_file = open("./dynamic_edges/prune_dynamic_edges_" + package_name + ".csv", "w")
    dyn_file.writelines(["src,dst" + "\n"])
    # Read the dynamic call graph
    dyn_callgraph_file = open("./callgraphs/" + package_name + "_dyn_cg.json.out", "r")
    dyn_callgraph = json.load(dyn_callgraph_file)
    # Read the nodes csv file into a dataframe
    nodes_df = pd.read_csv("./asts/" + package_name + "_node.csv")
    # For each dynamic call2fun edge
    dyn_edges = dyn_callgraph["call2fun"]
    for edge in dyn_edges:
        # Compare the out_node to the nodes in the dataframe
        out_node_file = dyn_callgraph["files"][int(dyn_callgraph["calls"][edge[0]].split(":")[0])]
        out_node_start_line = int(dyn_callgraph["calls"][edge[0]].split(":")[1])
        out_node_start_column = int(dyn_callgraph["calls"][edge[0]].split(":")[2])
        out_node_end_line = int(dyn_callgraph["calls"][edge[0]].split(":")[3])
        out_node_end_column = int(dyn_callgraph["calls"][edge[0]].split(":")[4])
        out_node_id = -1
        # If the file, lines, and columns are the same, add the "new_id" of the out_node to the source of the current edge
        if out_node_file.split("/")[0] != "node_modules":
            for node in nodes_df.iterrows():
                if (node[1]["file_name"].replace("packages\\" + package_name + "\\", "").replace("\\", "/") == out_node_file) and (node[1]["start_line"] == out_node_start_line) and (node[1]["start_column"] == (out_node_start_column - 1)) and (node[1]["end_line"] == out_node_end_line) and (node[1]["end_column"] == (out_node_end_column - 1)):
                    out_node_id = node[1]["new_id"]
        # Do the same for the in_node/destination of the current edge
        in_node_file = dyn_callgraph["files"][int(dyn_callgraph["functions"][edge[1]].split(":")[0])]
        in_node_start_line = int(dyn_callgraph["functions"][edge[1]].split(":")[1])
        in_node_start_column = int(dyn_callgraph["functions"][edge[1]].split(":")[2])
        in_node_end_line = int(dyn_callgraph["functions"][edge[1]].split(":")[3])
        in_node_end_column = int(dyn_callgraph["functions"][edge[1]].split(":")[4])
        in_node_id = -1
        # If the file, lines, and columns are the same, add the "new_id" of the out_node to the source of the current edge
        if in_node_file.split("/")[0] != "node_modules":
            for node in nodes_df.iterrows():
                if (node[1]["file_name"].replace("packages\\" + package_name + "\\", "").replace("\\", "/") == in_node_file) and (node[1]["start_line"] == in_node_start_line) and (node[1]["start_column"] == (in_node_start_column - 1)) and (node[1]["end_line"] == in_node_end_line) and (node[1]["end_column"] == (in_node_end_column - 1)):
                    in_node_id = node[1]["new_id"]
        # Write the source and destination for the current edge in the file
        if out_node_id != -1 and in_node_id != -1:
            dyn_file.writelines([str(out_node_id) + "," + str(in_node_id) + "\n"])
    dyn_file.close()
def generate_files_for_package(package_name):
    build_static_csvs_for_pkg(package_name)
    assign_new_ids(package_name)
    build_dynamic_edges_csv(package_name)
# Selects random packages as long as at least their static call graphs exist and aren't empty
def select_random_packages(number_of_packages):
    packages_df = pd.read_csv("./clean_repos_data.txt")
    package_names = list(packages_df["package"])
    valid_packages = []
    # Storing the valid packages in a file to keep them noted
    packages_to_use_file = open("./selected_packages.txt", "w")
    already_done_file = open("done_packages.txt", "r")
    already_done = [pkg.replace("\n", "") for pkg in already_done_file.readlines()]
    already_done_file.close()
    while number_of_packages > 0:
        # Randomly select a package
        rand_package = package_names[rand.randint(0, len(package_names) - 1)]
        # If the package has at least a static call graph that isn't empty, it's valid for use
        try:
            file = open("./callgraphs/" + rand_package + "_static_cg.json", "r")
            json_data = json.load(file)
            if json_data["files"] != [] and (rand_package not in valid_packages) and (rand_package not in already_done):
                valid_packages.append(rand_package)
                number_of_packages = number_of_packages - 1
        except:
            logging.warning("Package " + rand_package + " is not eligible")
    # Writing the collected valid packages to the file
    already_done_file = open("done_packages.txt", "a")
    for pkg in valid_packages:
        packages_to_use_file.writelines([pkg + "\n"])
        already_done_file.writelines([pkg + "\n"])
    already_done_file.close()
    packages_to_use_file.close()
# A function to clone the selected packages, relies on the cloning code provided by Ruben Opdebeeck
def clone_selected_packages():
    file = open("selected_packages.txt", "r")
    packages_df = pd.read_csv("./clean_repos_data.txt")
    selected_packages = file.readlines()
    print(selected_packages)
    for pkg in selected_packages:
        # Getting the repository link and the commit hash of the package
        repo_link = list(packages_df.loc[packages_df["package"] == pkg.replace("\n", "")]["repo_link"])[0].replace("https", "https:")
        print(repo_link)
        commit_hash = list(packages_df.loc[packages_df["package"] == pkg.replace("\n", "")]["commit_hash"])[0]
        Path("./packages/" + pkg.replace("\n", "")).mkdir(parents = True, exist_ok = True)
        clone_repo(pkg, repo_link, "./packages/" + pkg.replace("\n", ""), commit_hash)
def generate_data_for_selected_packages():
    file = open("selected_packages.txt", "r")
    selected_packages = file.readlines()
    for pkg in selected_packages:
        try:
            generate_files_for_package(pkg.replace("\n", ""))
        except:
            logging.warning("Failed to fully parse package:" + pkg.replace("\n", ""))
# Removes csv files that lack function_edges, ast edges, or nodes
def remove_bad_csvs():
    dir = r"./asts"
    for file in Path(dir).iterdir():
        content = open(file, "r")
        lines = content.readlines()
        content.close()
        if (len(lines) == 0) or (len(lines) == 1):
            to_delete = file.name.split("_")[0]
            try:
                Path("C:/Users/moham/Desktop/VUB/MyGNN/OneDriveThesis/Thesis_Convincing/extract_data_for_graphia/asts/" + to_delete + "_function_edges.csv").unlink()
            except:
                logging.warning("Error deleting one of the files")
            try:
                    Path("C:/Users/moham/Desktop/VUB/MyGNN/OneDriveThesis/Thesis_Convincing/extract_data_for_graphia/asts/" + to_delete + "_edges.csv").unlink()
            except:
                logging.warning("Error deleting one of the files")
            try:
                Path("C:/Users/moham/Desktop/VUB/MyGNN/OneDriveThesis/Thesis_Convincing/extract_data_for_graphia/asts/" + to_delete + "_node.csv").unlink()
            except:
                logging.warning("Error deleting one of the files")
# Function to get the CallExpression's Function name
def __get_call_function_name(ast, functions, calls):
    if hasattr(ast, "body"):
        if type(ast.body) == type([]):
            for node in ast.body:
                __get_call_function_name(node, functions, calls)
        else:
            __get_call_function_name(ast.body, functions, calls)
    if hasattr(ast, "expression"):
        __get_call_function_name(ast.expression, functions, calls)
    if hasattr(ast, "callee"):
        __get_call_function_name(ast.callee, functions, calls)
    if hasattr(ast, "test"):
        __get_call_function_name(ast.test, functions, calls)
    if hasattr(ast, "left"):
        __get_call_function_name(ast.left, functions, calls)
    if hasattr(ast, "right"):
        __get_call_function_name(ast.right, functions, calls)
    if hasattr(ast, "arguments") and ast.arguments != None:
        for arg in ast.arguments:
            __get_call_function_name(arg, functions, calls)
    if hasattr(ast, "argument"):
        __get_call_function_name(ast.argument, functions, calls)
    if hasattr(ast, "id"):
        __get_call_function_name(ast.id, functions, calls)
    if hasattr(ast, "name"):
        __get_call_function_name(ast.name, functions, calls)
    if hasattr(ast, "consequent"):
        __get_call_function_name(ast.consequent, functions, calls)
    if hasattr(ast, "type"):
        if ast.type == "FunctionDeclaration":
            for i in range(len(calls)):
                if len(calls[i].split("-")) == 1:
                    calls[i] = calls[i] + "-" + ast.id.name + "@" + str(ast.loc.start.line) + "/" + str(ast.loc.start.column) + "/" + str(ast.loc.end.line) + "/" + str(ast.loc.end.column)
            functions.append(ast.id.name + "@" + str(ast.loc.start.line) + "/" + str(ast.loc.start.column) + "/" + str(ast.loc.end.line) + "/" + str(ast.loc.end.column))
        if (ast.type == "FunctionExpression") or (ast.type == "ArrowFunctionExpression"):
            for i in range(len(calls)):
                if len(calls[i].split("-")) == 1:
                    calls[i] = calls[i] + "-" + "nan"
        if ((ast.type == "CallExpression") or (ast.type == "NewExpression")) and hasattr(ast, "callee") and hasattr(ast.callee, "name") and ast.callee.name != None:
            calls.append(ast.callee.name + "@" + str(ast.loc.start.line) + "/" + str(ast.loc.start.column) + "/" + str(ast.loc.end.line) + "/" + str(ast.loc.end.column))
        elif ((ast.type == "CallExpression") or (ast.type == "NewExpression")) and hasattr(ast, "callee") and hasattr(ast.callee, "property") and hasattr(ast.callee.property, "name") and ast.callee.property.name != None:
            calls.append(ast.callee.property.name + "@" + str(ast.loc.start.line) + "/" + str(ast.loc.start.column) + "/" + str(ast.loc.end.line) + "/" + str(ast.loc.end.column))
        if ast.type == "Program":
            for i in range(len(calls)):
                if len(calls[i].split("-")) == 1:
                    calls[i] = calls[i] + "-" + "nan"
            return (functions, calls)
def remove_duplicate_rows(filename):
    df = pd.read_csv(filename)
    df_tupled = list(set([(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11]) for i in df.to_numpy().tolist()]))
    print(len(df_tupled))
# The following function takes function names in the form "showResult" and "show_result", and splits them into a list of words (["show", "result"]) for Jaccard similarity calculation
def fix_function_name(fn_name):
    cap_letters = re.findall("[A-Z]", fn_name)
    temp = re.split("[A-Z]", fn_name)
    new_fn_name = []
    new_fn_name.append(temp[0])
    for i in range(len(cap_letters)):
        new_fn_name.append(cap_letters[i].lower() + temp[i + 1])
    temp_fn_name = []
    for j in range(len(new_fn_name)):
        temp_fn_name = temp_fn_name + new_fn_name[j].split("_")
    final_fn_name = []
    for word in temp_fn_name:
        if word != "":
            final_fn_name.append(word)
    return final_fn_name
def get_call_function_name(package_name, static, dyn):
    # Collect all the JavaScript file paths in the package
    package_dir = pathlib.Path(PACKAGES_DIR + package_name)
    nodes_df = pd.read_csv("./asts/" + package_name + "_node.csv")
    if static == True:
        old_edges_df = pd.read_csv("./asts/" + package_name + "_function_edges.csv")
        new_edges_csv = open("./asts/" + package_name + "_edges_with_lv_value.csv", "w")
    if dyn == True:
        old_edges_df = pd.read_csv("./dynamic_edges/prune_dynamic_edges_" + package_name + ".csv")
        new_edges_csv = open("./dynamic_edges/prune_dynamic_edges_with_jaccard_" + package_name + ".csv", "w")
    new_edges_csv.writelines(["src,jaccard_val,dst" + "\n"])
    # Loop over the old function edges
    for edge in old_edges_df.iterrows():
        # For each pair of vertices
        src = edge[1]["src"]
        dst = edge[1]["dst"]
        # Generate the ast of the file the node belongs to
        src_file_name = list(nodes_df.loc[nodes_df["new_id"] == src]["file_name"])[0]
        dst_file_name = list(nodes_df.loc[nodes_df["new_id"] == dst]["file_name"])[0]
        src_file = open(src_file_name, "r")
        dst_file = open(dst_file_name, "r")
        src_ast = parser.parseScript(src_file.read(), {"loc": True})
        dst_ast = parser.parseScript(dst_file.read(), {"loc": True})
        # For the src index (callexpression), do a post-order walk of the tree to extract the calling function
        functions, calls = __get_call_function_name(src_ast, [], [])
        src_name = "nan"
        for call in calls:
            callee_name = call.split("@")[0]
            call_start_line = int(call.split("@")[1].split("/")[0])
            call_start_col = int(call.split("@")[1].split("/")[1])
            call_end_line = int(call.split("@")[1].split("/")[2])
            call_end_col = int(call.split("@")[1].split("/")[3].split("-")[0])
            node_start_line = int(list(nodes_df.loc[nodes_df["new_id"] == src]["start_line"])[0])
            node_start_col = int(list(nodes_df.loc[nodes_df["new_id"] == src]["start_column"])[0])
            node_end_line = int(list(nodes_df.loc[nodes_df["new_id"] == src]["end_line"])[0])
            node_end_col = int(list(nodes_df.loc[nodes_df["new_id"] == src]["end_column"])[0])
            if (call_start_line == node_start_line) and (call_start_col == node_start_col) and (call_end_line == node_end_line) and (call_end_col == node_end_col):
                src_name = callee_name
        # For the dst index, if it's a functiondeclaration, do a postorder walk as well to extract the function name
        functions, calls = __get_call_function_name(dst_ast, [], [])
        dst_name = "nan"
        for function in functions:
            function_name = function.split("@")[0]
            function_start_line = int(function.split("@")[1].split("/")[0])
            function_start_col = int(function.split("@")[1].split("/")[1])
            function_end_line = int(function.split("@")[1].split("/")[2])
            function_end_col = int(function.split("@")[1].split("/")[3])
            node_start_line = int(list(nodes_df.loc[nodes_df["new_id"] == dst]["start_line"])[0])
            node_start_col = int(list(nodes_df.loc[nodes_df["new_id"] == dst]["start_column"])[0])
            node_end_line = int(list(nodes_df.loc[nodes_df["new_id"] == dst]["end_line"])[0])
            node_end_col = int(list(nodes_df.loc[nodes_df["new_id"] == dst]["end_column"])[0])
            if (function_start_line == node_start_line) and (function_start_col == node_start_col) and (function_end_line == node_end_line) and (function_end_col == node_end_col):
                dst_name = function_name
        # Otherwise the value is nan
        if (src_name == "nan") or (dst_name == "nan"):
            new_edges_csv.writelines([str(src) + ",-1," + str(dst) + "\n"])
        else:
            src_name_wordified = fix_function_name(src_name)
            dst_name_wordified = fix_function_name(dst_name)
            val = Jaccard.similarity(src_name_wordified, dst_name_wordified) 
            new_edges_csv.writelines([str(src) + "," + str(val) + "," + str(dst) + "\n"])
    new_edges_csv.close()
# Function that does a post order traversal of an AST to find a specific node
# Function to get the CallExpression's Function name
def __get_node(ast, node_to_find):
    if hasattr(ast, "body"):
        if type(ast.body) == type([]):
            for node in ast.body:
                __get_node(node, node_to_find)
        else:
            __get_node(ast.body, node_to_find)
    if hasattr(ast, "expression"):
        __get_node(ast.expression, node_to_find)
    if hasattr(ast, "callee"):
        __get_node(ast.callee, node_to_find)
    if hasattr(ast, "test"):
        __get_node(ast.test, node_to_find)
    if hasattr(ast, "left"):
        __get_node(ast.left, node_to_find)
    if hasattr(ast, "right"):
        __get_node(ast.right, node_to_find)
    if hasattr(ast, "arguments") and ast.arguments != None:
        for arg in ast.arguments:
            __get_node(arg, node_to_find)
    if hasattr(ast, node_to_find):
        __get_node(ast.argument, node_to_find)
    if hasattr(ast, "id"):
        __get_node(ast.id, node_to_find)
    if hasattr(ast, "name"):
        __get_node(ast.name, node_to_find)
    if hasattr(ast, "consequent"):
        __get_node(ast.consequent, node_to_find)
    if hasattr(ast, "type"): 
        if ast.type == "Program":
            return 1
def returns_or_not(node):
    # Check if the node given has a return statement
    if ("FunctionExpression" in str(node)) or ("ArrowFunctionExpression" in str(node)):
        # Look if the main node has a return value
        print("Hey")
    elif "ReturnStatement" in str(node):
        return 1
    else:
        return 0
            # Use "return_value" on the node to get its return value
def add_belongs_to_index_or_test(package_name):
    # Read the nodes file
    nodes_df = pd.read_csv("./original_graphia_data/" + package_name + "_node.csv")
    # Create a new nodes file to include the new data
    new_nodes_file = open("./original_graphia_data/" + package_name + "_node_index_test.csv", "w")
    new_nodes_file.writelines(["id,type,name,params_len,argument_len,start_line,start_column,end_line,end_column,file_name,file_is_index_or_test,new_id" + "\n"])
    # Go over the nodes
    for node in nodes_df.iterrows():
        # Get each node's file name
        file_name = node[1].file_name
        # If the file includes "index.js" or "test" in its name
        if ("index.js" in file_name) or ("test" in file_name):
            # Set its value to 1
            val = 1
        else:
            # Otherwise set its value to 0
            val = 0
        # Write the row to the new file
        new_nodes_file.writelines(str(node[1].id) + "," + str(node[1].type) + "," + str(node[1].name) + "," + str(node[1].params_len) + "," 
                                  + str(node[1].argument_len) + "," + str(node[1].start_line) + "," + str(node[1].start_column) + "," + str(node[1].end_line) + ","
                                  + str(node[1].end_column) + "," + str(node[1].file_name) + "," + str(val) + "," + str(node[1].new_id) + "\n")
    # Close the file
    new_nodes_file.close()
def add_belongs_to_same_file(package_name, static, dyn):
    # Read the nodes file
    nodes_df = pd.read_csv("./original_graphia_data/" + package_name + "_node_index_test.csv")
    # Read the edges file
    if static == True:
        edges_df = pd.read_csv("./original_graphia_data/" + package_name + "_function_edges.csv")
        # Create a new edges file including the feature
        new_edges_file = open("./original_graphia_data/" + package_name + "_function_edges_same_file.csv", "w")
    if dyn == True:
        edges_df = pd.read_csv("./original_graphia_data/dynamic_edges/prune_dynamic_edges_" + package_name + ".csv")
        # Create a new edges file including the feature
        new_edges_file = open("./original_graphia_data/dynamic_edges/prune_dynamic_edges_same_file_" + package_name + ".csv", "w")
    new_edges_file.writelines(["src,same_file,dst" + "\n"])
    # Loop over the edges
    for edge in edges_df.iterrows():
        # For each edge
        # Get the src node's file_name
        src_file_name = list(nodes_df.loc[nodes_df["new_id"] == edge[1].src]["file_name"])[0]
        # Get the dst node's file_name
        dst_file_name = list(nodes_df.loc[nodes_df["new_id"] == edge[1].dst]["file_name"])[0]
        # Compare them
        # If they're the same
        if src_file_name == dst_file_name:
            # The value is 1
            val = 1
        # If they're different
        else:
            # The value is 0
            val = 0
        # Write the row to the new file
        new_edges_file.writelines([str(edge[1].src) + "," + str(val) + "," + str(edge[1].dst) + "\n"])
    # Close the file
    new_edges_file.close()
# Traverses a node's AST, including all the nodes except the ones under a FunctionExpression or ArrowFunctionExpression
# (This is used to make sure the given node is the one that returns, not some expression in it)
def breadth_first_search_no_fn(ast):
    queue = [ast]
    root = ast
    nodes = []
    while queue != []:
        current_node = queue.pop(0)
        if (current_node != None) and (type(current_node) != type(False)) and ((current_node == root) or (current_node.type not in ["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"])):
            nodes.append(current_node.type)
            if hasattr(current_node, "body"):
                if type(current_node.body) == type([]):
                    for node in current_node.body:
                        queue.append(node)
                else:
                    queue.append(current_node.body)
            if current_node.arguments != None:
                for arg in current_node.arguments:
                    queue.append(arg)
            if current_node.argument != None:
                queue.append(current_node.argument)
            if current_node.expression != None:
                queue.append(current_node.expression)
            if current_node.consequent != None:
                queue.append(current_node.consequent)
            if current_node.left != None:
                queue.append(current_node.left)
            if current_node.right != None:
                queue.append(current_node.right)
            if current_node.callee != None:
                queue.append(current_node.callee)
            if current_node.test != None:
                queue.append(current_node.test)
            if current_node.declarations != None:
                for d in current_node.declarations:
                    queue.append(d)
            if current_node.init != None:
                queue.append(current_node.init)
    return str(nodes)
def return_in_node(node):
    if "ReturnStatement" not in str(node):
        return 0
    elif "ReturnStatement" not in breadth_first_search_no_fn(node):
        return 0
    else:
        return 1
# A function that traverses the AST breadth first till it finds the specified node and returns it
def find_node(ast, node_to_find_type, node_to_find_loc):
    queue = [ast]
    while queue != []:
        current_node = queue.pop(0)
        if (current_node != None) and (type(current_node) != type(False)) and (current_node.type == node_to_find_type) and (current_node.loc.start.line == node_to_find_loc[0]) and (current_node.loc.start.column == node_to_find_loc[1]) and (current_node.loc.end.line == node_to_find_loc[2]) and (current_node.loc.end.column == node_to_find_loc[3]):
            return current_node
        elif (current_node != None) and (type(current_node) != type(False)):
            if hasattr(current_node, "body"):
                if type(current_node.body) == type([]):
                    for node in current_node.body:
                        queue.append(node)
                else:
                    queue.append(current_node.body)
            if current_node.arguments != None:
                for arg in current_node.arguments:
                    queue.append(arg)
            if current_node.argument != None:
                queue.append(current_node.argument)
            if current_node.expression != None:
                queue.append(current_node.expression)
            if current_node.consequent != None:
                queue.append(current_node.consequent)
            if current_node.left != None:
                queue.append(current_node.left)
            if current_node.right != None:
                queue.append(current_node.right)
            if current_node.callee != None:
                queue.append(current_node.callee)
            if current_node.test != None:
                queue.append(current_node.test)
            if current_node.declarations != None:
                for d in current_node.declarations:
                    queue.append(d)
            if current_node.init != None:
                queue.append(current_node.init)
    return None
def add_returns(package_name):
    # Collect all the JavaScript file paths in the package
    package_dir = pathlib.Path(PACKAGES_DIR + package_name)
    old_nodes_df = pd.read_csv("./asts/" + package_name + "_node.csv")
    new_nodes_csv = open("./asts/" + package_name + "_nodes_with_returns.csv", "w")
    new_nodes_csv.writelines(["id,type,name,params_len,argument_len,start_line,start_column,end_line,end_column,file_name,returns,new_id" + "\n"])
    # Loop over the old function edges
    for node in old_nodes_df.iterrows():
        if node[1]["type"] in ["FunctionExpression", "ArrowFunctionExpression", "FunctionDeclaration"]:
        # If the node is a function
            # Generate the ast of the file the node belongs to
            file_name = node[1]["file_name"]
            file = open(file_name, "r")
            ast = parser.parseScript(file.read(), {"loc": True})
            # Locate the node in the ast
            node_in_ast = find_node(ast, node[1]["type"], [node[1]["start_line"], node[1]["start_column"], node[1]["end_line"], node[1]["end_column"]])
            val = return_in_node(node_in_ast)
            new_nodes_csv.writelines(str(node[1]["id"]) + "," + str(node[1]["type"]) + "," + str(node[1]["name"]) + "," + str(node[1]["params_len"]) + "," 
                                     + str(node[1]["argument_len"]) + "," + str(node[1]["start_line"]) + "," + str(node[1]["start_column"]) + "," + str(node[1]["end_line"])
                                       + "," + str(node[1]["end_column"])
                                     + "," + str(node[1]["file_name"]) + "," + str(val) + "," + str(node[1]["new_id"]) + "\n")
        else:
            new_nodes_csv.writelines(str(node[1]["id"]) + "," + str(node[1]["type"]) + "," + str(node[1]["name"]) + "," + str(node[1]["params_len"]) + "," 
                                     + str(node[1]["argument_len"]) + "," + str(node[1]["start_line"]) + "," + str(node[1]["start_column"]) + "," + str(node[1]["end_line"])
                                       + "," + str(node[1]["end_column"])
                                     + "," + str(node[1]["file_name"]) + "," + str(-1) + "," + str(node[1]["new_id"]) + "\n")
    new_nodes_csv.close()
# This function combines all the features collected into 3 files (nodes, edges, and function edges)
def combine_features(package_name, static, dyn):
    if static == True:
        # Read all three node files
        old_nodes_df = pd.read_csv("./asts/" + package_name + "_node.csv")
        nodes_index_test = pd.read_csv("./asts/" + package_name + "_node_index_test.csv")
        nodes_returns = pd.read_csv("./asts/" + package_name + "_nodes_with_returns.csv")
        # Create a new nodes files
        new_nodes_file = open("./combined_features_asts/" + package_name + "_node.csv", "w")
        new_nodes_file.writelines(["id,type,name,params_len,argument_len,returns,start_line,start_column,end_line,end_column,file_name,file_is_index_or_test,new_id" + "\n"])
        # Transform each CSV into a list of lists
        old_nodes_list = list(old_nodes_df.iterrows())
        nodes_index_test_list = list(nodes_index_test.iterrows())
        nodes_returns_list = list(nodes_returns.iterrows())
        # Loop over them, writing one line per node into the new nodes file
        for i in range(len(old_nodes_list)):
            data = str(old_nodes_list[i][1]["id"]) + "," + str(old_nodes_list[i][1]["type"]) + "," + str(old_nodes_list[i][1]["name"]) + "," + str(old_nodes_list[i][1]["params_len"]) + "," + str(old_nodes_list[i][1]["argument_len"]) + "," + str(nodes_returns_list[i][1]["returns"]) + "," + str(old_nodes_list[i][1]["start_line"]) + "," + str(old_nodes_list[i][1]["start_column"]) + "," + str(old_nodes_list[i][1]["end_line"]) + "," + str(old_nodes_list[i][1]["end_column"]) + "," + str(old_nodes_list[i][1]["file_name"]) + "," + str(nodes_index_test_list[i][1]["file_is_index_or_test"]) + "," + str(old_nodes_list[i][1]["new_id"])
            new_nodes_file.writelines([data + "\n"])
        new_nodes_file.close()
        same_file_edges_name = "./asts/" + package_name + "_function_edges_same_file.csv"
        jaccard_file_edges_name = "./asts/" + package_name + "_edges_with_lv_value.csv"
        new_edges_file_name = "./combined_features_asts/" + package_name + "_function_edges.csv"
    if dyn == True:
        same_file_edges_name = "./dynamic_edges/prune_dynamic_edges_same_file_" + package_name + ".csv"
        jaccard_file_edges_name = "./dynamic_edges/prune_dynamic_edges_with_jaccard_" + package_name + ".csv"
        new_edges_file_name = "./dynamic_edges/" + package_name + "_combined_dyn_edges.csv"
    # Read the two function edges files
    same_file_edges_df = pd.read_csv(same_file_edges_name)
    jaccard_val_edges_df = pd.read_csv(jaccard_file_edges_name)
    # Create a new edges file
    function_edges = open(new_edges_file_name, "w")
    function_edges.writelines(["src" + "," + "same_file" + "," + "jaccard_val" + "," + "dst" + "\n"])
    # Transform each CSV into a list of lists
    same_file_edges_list = list(same_file_edges_df.iterrows())
    jaccard_val_edges_list = list(jaccard_val_edges_df.iterrows())
    # Loop over them, writing one line per edge into the new edges file
    for j in range(len(same_file_edges_list)):
        edge_data = str(same_file_edges_list[j][1]["src"]) + "," + str(same_file_edges_list[j][1]["same_file"]) + "," + str(jaccard_val_edges_list[j][1]["jaccard_val"]) + "," + str(same_file_edges_list[j][1]["dst"])
        function_edges.writelines([edge_data + "\n"])
    function_edges.close()
def compare_names_for_negative_sampled_edges(src_node, dst_node):
    # Generate the ast of the file the node belongs to
    src_file_name = src_node["file_name"]
    dst_file_name = dst_node["file_name"]
    src_file = open(src_file_name, "r")
    dst_file = open(dst_file_name, "r")
    src_ast = parser.parseScript(src_file.read(), {"loc": True})
    dst_ast = parser.parseScript(dst_file.read(), {"loc": True})
    # For the src index (callexpression), do a post-order walk of the tree to extract the calling function
    functions, calls = __get_call_function_name(src_ast, [], [])
    src_name = "nan"
    val = -1
    for call in calls:
        callee_name = call.split("@")[0]
        call_start_line = int(call.split("@")[1].split("/")[0])
        call_start_col = int(call.split("@")[1].split("/")[1])
        call_end_line = int(call.split("@")[1].split("/")[2])
        call_end_col = int(call.split("@")[1].split("/")[3].split("-")[0])
        node_start_line = int(src_node["start_line"])
        node_start_col = int(src_node["start_column"])
        node_end_line = int(src_node["end_line"])
        node_end_col = int(src_node["end_column"])
        if (call_start_line == node_start_line) and (call_start_col == node_start_col) and (call_end_line == node_end_line) and (call_end_col == node_end_col):
            src_name = callee_name
        # For the dst index, if it's a functiondeclaration, do a postorder walk as well to extract the function name
        functions, calls = __get_call_function_name(dst_ast, [], [])
        dst_name = "nan"
        for function in functions:
            function_name = function.split("@")[0]
            function_start_line = int(function.split("@")[1].split("/")[0])
            function_start_col = int(function.split("@")[1].split("/")[1])
            function_end_line = int(function.split("@")[1].split("/")[2])
            function_end_col = int(function.split("@")[1].split("/")[3])
            node_start_line = int(dst_node["start_line"])
            node_start_col = int(dst_node["start_column"])
            node_end_line = int(dst_node["end_line"])
            node_end_col = int(dst_node["end_column"])
            if (function_start_line == node_start_line) and (function_start_col == node_start_col) and (function_end_line == node_end_line) and (function_end_col == node_end_col):
                dst_name = function_name
        if (src_name != "nan") and (dst_name != "nan"):
            src_name_wordified = fix_function_name(src_name)
            dst_name_wordified = fix_function_name(dst_name)
            val = Jaccard.similarity(src_name_wordified, dst_name_wordified)
    return val
def fn_negative_sampling(package_name, static, dyn):
    # Read the function edges
    if static == True:
        fn_edges_df = pd.read_csv("./original_graphia_data/" + package_name + "_function_edges_same_file.csv")
    if dyn == True:
        fn_edges_df = pd.read_csv("./original_graphia_data/dynamic_edges/prune_dynamic_edges_same_file_" + package_name + ".csv")
    # Turn the edges into a list of lists of format [[1, 2], [3, 5], [2, 7]]
    fn_edges_list = [[int(i[1]["src"]), int(i[1]["dst"])] for i in fn_edges_df.iterrows()]
    # Read the nodes
    nodes_df = pd.read_csv("./original_graphia_data/" + package_name + "_node_index_test.csv")
    # Filter the nodes by "NewExpression"/"CallExpression" in one list and "FunctionDeclaration"/"FunctionExpression"/"ArrowFunctionExpression" in a second list
    calls_list = [j[1] for j in nodes_df.iterrows() if (j[1]["type"] == "CallExpression" or j[1]["type"] == "NewExpression")]
    fns_list = [k[1] for k in nodes_df.iterrows() if (k[1]["type"] in ["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"])]
    # Calculate the number of possible combinations, used in case we can't negatively sample and equal amount of edges
    no_possibilities = np.pow(float(len(calls_list)), float(len(fns_list))) - len(fns_list)
    # Create a list for the negative edges
    negative_edges = []
    # While the negative edges are not equal to the existing ones
    # Set a timer (for larger packages)
    start = time.time()
    broken = False
    while ((len(fn_edges_list) != len(negative_edges)) and (len(negative_edges) != no_possibilities)):
        # Randomly pick a node from the call list and a node from the functions list
        call_node = calls_list[rand.randint(0, len(calls_list) - 1)]
        call_node_index = call_node["new_id"]
        fn_node = fns_list[rand.randint(0, len(fns_list) - 1)]
        fn_node_index = fn_node["new_id"]
        # Check if the edge exists in the existing edges list
        if ([int(call_node_index), int(fn_node_index)] not in fn_edges_list):
            # If not, calculate the features and add the negative edge to the list
            #jaccard_val = compare_names_for_negative_sampled_edges(call_node, fn_node)
            same_file = 0
            if call_node["file_name"] == fn_node["file_name"]:
                same_file = 1
            negative_edges.append([int(call_node_index), int(same_file), int(fn_node_index)])
        current_time = time.time()
        elapsed_time = current_time - start
        if elapsed_time > 1800:
            broken = True
            break
    # Write the collected edges to a separate file
    if static == True:
        file = open("./original_graphia_data/" + package_name + "_negative_function_edges.csv", "w")
    if dyn == True:
        file = open("./original_graphia_data/dynamic_edges/" + package_name + "_negative_dynamic_edges.csv", "w")
    file.writelines(["src,same_file,dst" + "\n"])
    for fn_edge in negative_edges:
        file.writelines([str(fn_edge[0]) + "," + str(fn_edge[1]) + "," + str(fn_edge[2]) + "\n"])
    file.close()
    return broken
def ast_negative_sampling(package_name):
    # Read the edges file
    edges_df = pd.read_csv("./original_graphia_data/" + package_name + "_edges.csv")
    # Turn the edges into a list of lists of format [[1, 2], [3, 5], [2, 7]]
    edges_list = [[int(i[1]["src"]), int(i[1]["dst"])] for i in edges_df.iterrows()]
    # Read the nodes file
    nodes_df = pd.read_csv("./original_graphia_data/" + package_name + "_node_index_test.csv")
    # Turn the nodes into a list
    nodes_list = [j[1] for j in nodes_df.iterrows()]
    # Create a list for the negative edges
    negative_edges = []
    # While the negative edges and the real edges are not the same number
    while len(edges_list) != len(negative_edges):
        # Randomly select two nodes, a source and a destination node
        src_node = nodes_list[rand.randint(0, (len(nodes_list) - 1))]
        dst_node = nodes_list[rand.randint(0, (len(nodes_list) - 1))]
        # If the source is not a call (CallExpression/New Expression) and the destination is not a function (FunctionDeclaration/FuntionExpression/ArrowFunctionExpression), proceed
        # (Filtering out the function edges)
        if (src_node["new_id"] != dst_node["new_id"]) and (not (src_node["type"] in ["CallExpression", "NewExpression"]) and (dst_node["type"] in ["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"])):
            # If the edge doesn't exist, add it to the negative edges list
            if [src_node["new_id"], dst_node["new_id"]] not in edges_list:
                negative_edges.append([src_node["new_id"], dst_node["new_id"]])
    # Write the collected edges to a separate file
    file = open("./original_graphia_data/" + package_name + "_negative_edges.csv", "w")
    file.writelines(["src,dst" + "\n"])
    for edge in negative_edges:
        file.writelines([str(edge[0]) + "," + str(edge[1]) + "\n"])
    file.close()
# shuffle_data creates csv files with shuffled edges, so that there isn't a clear split in the middle between positive and negative edges
def shuffle_data(package_name):
    # Read the negative function edges into a list
    n_fn_edges = list(pd.read_csv("./original_graphia_data/" + package_name + "_negative_function_edges.csv").iterrows())
    # Read the positive function edges into a list
    fn_edges = list(pd.read_csv("./original_graphia_data/" + package_name + "_function_edges_same_file.csv").iterrows())
    # Create a new file
    new_function_edges_file = open("./original_graphia_data/shuffled/" + package_name + "_shuffled_function_edges.csv", "w")
    new_function_edges_file.writelines(["src,same_file,dst,label" + "\n"])
    # Randomly write edges to the file until both lists are empty
    while n_fn_edges != [] or fn_edges != []:
        choice = rand.randint(0, 1)
        if (n_fn_edges != [] and fn_edges != []):
            if choice == 0:
                edge = n_fn_edges.pop()[1]
                new_function_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.same_file)) + "," + str(int(edge.dst)) + ",0" + "\n"])
            else:
                edge = fn_edges.pop()[1]
                new_function_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.same_file)) + "," + str(int(edge.dst)) + ",1" + "\n"])
        elif n_fn_edges != []:
            edge = n_fn_edges.pop()[1]
            new_function_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.same_file)) + "," + str(int(edge.dst)) + ",0" + "\n"])
        else:
            edge = fn_edges.pop()[1]
            new_function_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.same_file)) + "," + str(int(edge.dst)) + ",1" + "\n"])
    new_function_edges_file.close()
    # Do the same for the ast edges
    # Read the negative ast edges into a list
    n_edges = list(pd.read_csv("./original_graphia_data/" + package_name + "_negative_edges.csv").iterrows())
    # Read the positive ast edges into a list
    edges = list(pd.read_csv("./original_graphia_data/" + package_name + "_edges.csv").iterrows())
    # Create a new file
    new_ast_edges_file = open("./original_graphia_data/shuffled/" + package_name + "_shuffled_ast_edges.csv", "w")
    new_ast_edges_file.writelines(["src,dst,label" + "\n"])
    # Randomly write edges to the file until both lists are empty
    while n_edges != [] or edges != []:
        choice = rand.randint(0, 1)
        if (n_edges != [] and edges != []):
            if choice == 0:
                edge = n_edges.pop()[1]
                new_ast_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.dst)) + ",0" + "\n"])
            else:
                edge = edges.pop()[1]
                new_ast_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.dst)) + ",1" + "\n"])
        elif n_edges != []:
            edge = n_edges.pop()[1]
            new_ast_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.dst)) + ",0" + "\n"])
        else:
            edge = edges.pop()[1]
            new_ast_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.dst)) + ",1" + "\n"])
    new_ast_edges_file.close()
    # Do the same for the dynamic edges
    # Read the negative ast edges into a list
    try:
        n_dyn_edges = list(pd.read_csv("./original_graphia_data/dynamic_edges/" + package_name + "_negative_dynamic_edges.csv").iterrows())
        # Read the positive ast edges into a list
        dyn_edges = list(pd.read_csv("./original_graphia_data/dynamic_edges/" + package_name + "_combined_dyn_edges.csv").iterrows())
        # Create a new file
        new_dyn_edges_file = open("./original_graphia_data/shuffled/" + package_name + "_shuffled_dyn_edges.csv", "w")
        new_dyn_edges_file.writelines(["src,same_file,dst,label" + "\n"])
        # Randomly write edges to the file until both lists are empty
        while n_dyn_edges != [] or dyn_edges != []:
            choice = rand.randint(0, 1)
            if (n_dyn_edges != [] and dyn_edges != []):
                if choice == 0:
                    edge = n_dyn_edges.pop()[1]
                    new_dyn_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.same_file)) + "," + str(int(edge.dst)) + ",0" + "\n"])
                else:
                    edge = dyn_edges.pop()[1]
                    new_dyn_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.same_file)) + "," + str(int(edge.dst)) + ",1" + "\n"])
            elif n_dyn_edges != []:
                edge = n_dyn_edges.pop()[1]
                new_dyn_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.same_file)) + "," + str(int(edge.dst)) + ",0" + "\n"])
            else:
                edge = dyn_edges.pop()[1]
                new_dyn_edges_file.writelines([str(int(edge.src)) + "," + str(int(edge.same_file)) + "," + str(int(edge.dst)) + ",1" + "\n"])
        new_dyn_edges_file.close()
    except:
        logging.warning("Package " + package_name + " has no dynamic edges")