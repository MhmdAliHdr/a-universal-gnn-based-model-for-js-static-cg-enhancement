import pathlib
import pandas as pd
nodes_dir = r"./combined_features_asts/"
# Hule, V. (February 24, 2024). Python List Files in a Directory. PYnative. https://pynative.com/python-list-files-in-a-directory/. Retrieved on December 6, 2025
package_names = [file.name.replace("_node.csv", "") for file in pathlib.Path(nodes_dir).iterdir() if "_node.csv" in file.name]
for package in package_names[96:]:
    nodes_dataframe = pd.read_csv("./combined_features_asts/" + package + "_node.csv")
    ast_edges_dataframe = pd.read_csv("./shuffled/" + package + "_shuffled_ast_edges.csv")
    fun_edges_dataframe = pd.read_csv("./shuffled/" + package + "_shuffled_function_edges.csv")
    function_declarations = len([node for node in nodes_dataframe.iterrows() if node[1]["type"] == "FunctionDeclaration"])
    function_expressions = len([node for node in nodes_dataframe.iterrows() if (node[1]["type"] == "FunctionExpression" or node[1]["type"] == "ArrowFunctionExpression")])
    call_expression = len([node for node in nodes_dataframe.iterrows() if node[1]["type"] == "CallExpression"])
    new_expression = len([node for node in nodes_dataframe.iterrows() if node[1]["type"] == "NewExpression"])
    nodes = len([node for node in nodes_dataframe.iterrows()])
    pos_static_edges = len([pos_static_edge for pos_static_edge in fun_edges_dataframe.iterrows() if (pos_static_edge[1]["label"] == 1)])
    negative_static_edges = len([negative_static_edge for negative_static_edge in fun_edges_dataframe.iterrows() if (negative_static_edge[1]["label"] == 0)])
    pos_ast_edges = len([pos_ast_edge for pos_ast_edge in ast_edges_dataframe.iterrows() if (pos_ast_edge[1]["label"] == 1)])
    negative_ast_edges = len([negative_ast_edge for negative_ast_edge in ast_edges_dataframe.iterrows() if (negative_ast_edge[1]["label"] == 0)])
    try:
        dyn_edges_dataframe = pd.read_csv("./shuffled/" + package + "_shuffled_dyn_edges.csv")
        pos_dyn_edges = len([pos_dyn_edge for pos_dyn_edge in dyn_edges_dataframe.iterrows() if (pos_dyn_edge[1]["label"] == 1)])
        negative_dyn_edges = len([negative_dyn_edge for negative_dyn_edge in dyn_edges_dataframe.iterrows() if (negative_dyn_edge[1]["label"] == 0)])
    except:
        pos_dyn_edges = 0
        negative_dyn_edges = 0
    print(package)
    print("Nodes: " + str(nodes))
    print("Function Declarations: " + str(function_declarations))
    print("(Arrow)Function Expressions: " + str(function_expressions))
    print("Call Expressions: " + str(call_expression))
    print("New Expressions: " + str(new_expression))
    print("Positive Static Edges: " + str(pos_static_edges))
    print("Negative Static Edges: " + str(negative_static_edges))
    print("Positive AST Edges: " + str(pos_ast_edges))
    print("Negative AST Edges: " + str(negative_ast_edges))
    print("Positive Dynamic Edges: " + str(pos_dyn_edges))
    print("Negative Dynamic Edges: " + str(negative_dyn_edges))