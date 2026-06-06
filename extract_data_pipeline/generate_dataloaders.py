from torch_geometric.data import HeteroData
from torch_geometric.loader import DataLoader
import torch
import pandas as pd
import pathlib
import pickle as pk
import logging
import random as rand
from sklearn.preprocessing import LabelEncoder

# This project file contains functions to create dataloaders for the data
# Dataloaders are iterables used to pass data to the model

#############
# Script based on https://github.com/pyg-team/pytorch_geometric/blob/master/examples/link_pred.py
# and Graphia
# The following reference was used for logging timestamps
# AdamE, C. Josh, djvg, Gab, gae123, G., Hans, H. James, Michael, paidhima, Toros91, user2176576, Zipp, R. StackOverflow February, 4 2015. Print timestamp for logging in Python.
# https://stackoverflow.com/questions/28330317/print-timestamp-for-logging-in-python. Retrieved on November 20, 2025
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING, datefmt='%Y-%m-%d %H:%M:%S')
#############
# The shuffler function takes a data object and returns a new one where the lists are shuffled so that it's not the case that
# The true edges are always in the first half while the false ones are in the second half
def shuffler(edge_index, edge_attr, edge_label):
    new_edge_index = []
    new_edge_attr = []
    new_edge_label = []
    while edge_index != []:
        index_to_pop = rand.randint(0, len(edge_index) - 1)
        new_edge_index.append(edge_index.pop(index_to_pop))
        if edge_attr != []:
            new_edge_attr.append(edge_attr.pop(index_to_pop))
        new_edge_label.append(edge_label.pop(index_to_pop))
    return new_edge_index, new_edge_attr, new_edge_label

def create_dataset(package_name, pos, same_file, index_test, returns, jaccard_val, dynamic_edges):
    # Create a HeteroData object
    data = HeteroData()
    # Read the dataframes for the nodes, functions edges, edges, negative edges, and negative function edges
    nodes_df = pd.read_csv("./combined_features_asts/" + package_name + "_node.csv")
    fn_edges_df = pd.read_csv("./combined_features_asts/" + package_name + "_function_edges.csv")
    negative_fn_edges_df = pd.read_csv("./combined_features_asts/" + package_name + "_negative_function_edges.csv")
    edges_df = pd.read_csv("./combined_features_asts/" + package_name + "_edges.csv")
    negative_edges_df = pd.read_csv("./combined_features_asts/" + package_name + "_negative_edges.csv")
    # Collect node types, names, and file names
    node_types = list(set(list(nodes_df["type"])))
    node_names = list(set(list(nodes_df["name"])))
    node_file_names = list(set(list(nodes_df["file_name"])))
    # Use a label encoder to store the types, names, and file names
    types_le = LabelEncoder()
    types_le.fit(node_types)
    names_le = LabelEncoder()
    names_le.fit(node_names)
    file_names_le = LabelEncoder()
    file_names_le.fit(node_file_names)
    # Build a dictionary for the nodes
    x_nodes_dict = dict()
    # Initialize the nodes dict (we're only using "ast_node" as a key)
    # (The actual types are included as a feature)
    x_nodes_dict["ast_node"] = []
    # Loop over the nodes and add them with whichever features are marked as true
    for row in nodes_df.iterrows():
        temp = []
        temp.append(types_le.transform([row[1].type])[0].item())
        temp.append(names_le.transform([row[1]["name"]])[0].item()) 
        temp.append(row[1].params_len)
        temp.append(row[1].argument_len)
        if returns == True:
            temp.append(row[1].returns)
        if pos == True:
            temp.append(row[1].start_line)
            temp.append(row[1].start_column)
            temp.append(row[1].end_line)
            temp.append(row[1].end_column)
        temp.append(file_names_le.transform([row[1].file_name])[0].item())
        if index_test == True:
            temp.append(row[1].file_is_index_or_test)
        x_nodes_dict["ast_node"].append(temp)
    # Initialize a dictionary for the function edges, and a second dictionary for their attributes if any
    function_edge_index = dict()
    function_edge_attr = dict()
    function_edge_labels = dict()
    function_edge_index[("ast_node", "calls", "ast_node")] = []
    function_edge_attr[("ast_node", "calls", "ast_node")] = []
    function_edge_labels[("ast_node", "calls", "ast_node")] = []
    # Loop over the function edges
    for fn_edge in fn_edges_df.iterrows():
        # Get the source and destination indices
        src = fn_edge[1].src
        dst = fn_edge[1].dst
        function_edge_index[("ast_node", "calls", "ast_node")].append([src, dst])
        # Get any attributes set to true
        if (same_file == True or jaccard_val == True):
            temp = []
            if same_file == True:
                temp.append(fn_edge[1].same_file)
            if jaccard_val == True:
                temp.append(fn_edge[1].jaccard_val)
            function_edge_attr[("ast_node", "calls", "ast_node")].append(temp)
        function_edge_labels[("ast_node", "calls", "ast_node")].append(1)
    # Loop over the negative function edges
    for negative_fn_edge in negative_fn_edges_df.iterrows():
        # Get the source and destination indices
        src = negative_fn_edge[1].src
        dst = negative_fn_edge[1].dst
        function_edge_index[("ast_node", "calls", "ast_node")].append([src, dst])
        # Get any attributes set to true
        if (same_file == True or jaccard_val == True):
            temp = []
            if same_file == True:
                temp.append(fn_edge[1].same_file)
            if jaccard_val == True:
                temp.append(fn_edge[1].jaccard_val)
            function_edge_attr[("ast_node", "calls", "ast_node")].append(temp)
        function_edge_labels[("ast_node", "calls", "ast_node")].append(0)
    # Loop over the dynamic edges if that's set to true
    dyn_edge_index = dict()
    dyn_edge_attr = dict()
    dyn_edge_labels = dict()
    dyn_edge_index[("ast_node", "calls", "ast_node")] = []
    dyn_edge_attr[("ast_node", "calls", "ast_node")] = []
    dyn_edge_labels[("ast_node", "calls", "ast_node")] = []
    if dynamic_edges == True:
        try:
            dyn_df = pd.read_csv("./dynamic_edges/" + package_name + "_combined_dyn_edges.csv")
            n_dyn_df = pd.read_csv("./dynamic_edges/" + package_name + "_negative_dynamic_edges.csv")
            # Loop over the function edges
            for dyn_edge in dyn_df.iterrows():
                # Get the source and destination indices
                src = dyn_edge[1].src
                dst = dyn_edge[1].dst
                dyn_edge_index[("ast_node", "calls", "ast_node")].append([src, dst])
                # Get any attributes set to true
                if (same_file == True or jaccard_val == True):
                    temp = []
                    if same_file == True:
                        temp.append(fn_edge[1].same_file)
                    if jaccard_val == True:
                        temp.append(fn_edge[1].jaccard_val)
                    dyn_edge_attr[("ast_node", "calls", "ast_node")].append(temp)
                dyn_edge_labels[("ast_node", "calls", "ast_node")].append(1)
            # Loop over the negative function edges
            for n_dyn_edge in n_dyn_df.iterrows():
                # Get the source and destination indices
                src = n_dyn_edge[1].src
                dst = n_dyn_edge[1].dst
                dyn_edge_index[("ast_node", "calls", "ast_node")].append([src, dst])
                # Get any attributes set to true
                if (same_file == True or jaccard_val == True):
                    temp = []
                    if same_file == True:
                        temp.append(fn_edge[1].same_file)
                    if jaccard_val == True:
                        temp.append(fn_edge[1].jaccard_val)
                    dyn_edge_attr[("ast_node", "calls", "ast_node")].append(temp)
                dyn_edge_labels[("ast_node", "calls", "ast_node")].append(0)
        except:
            logging.warning("===========> Package " + package_name + " has not dynamic edges")
    all_function_edge_index = function_edge_index + dyn_edge_index
    all_function_edge_labels = function_edge_labels + dyn_edge_labels
    all_function_edge_attr = function_edge_attr + dyn_edge_attr
    # Add the function, negative function, and dynamic(if true) edges to the data object
    data["ast_node", "calls", "ast_node"].edge_label_index = torch.tensor(all_function_edge_labels, dtype=torch.int64)
    data["ast_node", "calls", "ast_node"].edge_label = torch.tensor(all_function_edge_labels, dtype=torch.int64)
    data["ast_node", "calls", "ast_node"].edge_index = torch.transpose(torch.tensor(all_function_edge_index, dtype=torch.int64), 0, 1)
    if function_edge_attr != []:
        data["ast_node", "calls", "ast_node"].edge_attr = torch.tensor(all_function_edge_attr, dtype=torch.float32)
    # Create a dictionary for the ast edges
    ast_edge_index = dict()
    ast_edge_labels = dict()
    # Initialize the key [("ast_node", "connects_to", "ast_node")] in the dictionary
    ast_edge_index[("ast_node", "connects_to", "ast_node")] = []
    ast_edge_labels[("ast_node", "connects_to", "ast_node")] = []
    # Loop over the ast edges
    for ast_edge in edges_df.iterrows():
        # Get their source and destination indices
        src = ast_edge[1].src
        dst = ast_edge[1].dst
        ast_edge_index[("ast_node", "connects_to", "ast_node")].append([src, dst])
        ast_edge_labels[("ast_node", "connects_to", "ast_node")].append(1)
    # Loop over the negative ast edges
    for negative_ast_edge in negative_edges_df.iterrows():
        # Get their source and destination indices
        src = negative_ast_edge[1].src
        dst = negative_ast_edge[1].dst
        ast_edge_index[("ast_node", "connects_to", "ast_node")].append([src, dst])
        ast_edge_labels[("ast_node", "connects_to", "ast_node")].append(0)
    # Add the edges to the data object
    if (same_file and jaccard_val):
        data["ast_node", "connects_to", "ast_node"].edge_attr = torch.tensor([[-1, -1] for ast_edge in range(len(ast_edge_labels[("ast_node", "connects_to", "ast_node")]))], dtype=torch.float32)
    elif (same_file or jaccard_val):
        data["ast_node", "connects_to", "ast_node"].edge_attr = torch.tensor([[-1] for ast_edge in range(len(ast_edge_labels[("ast_node", "connects_to", "ast_node")]))], dtype=torch.float32)
    data["ast_node", "connects_to", "ast_node"].edge_index = torch.transpose(torch.tensor(ast_edge_index, dtype=torch.int64), 0, 1)
    data["ast_node", "connects_to", "ast_node"].edge_label = torch.tensor(ast_edge_labels, dtype=torch.int64)
    data["ast_node", "connects_to", "ast_node"].edge_label_index = torch.tensor(ast_edge_labels, dtype=torch.int64)
    # Add the nodes to the data
    data["ast_node"].x = torch.tensor(x_nodes_dict["ast_node"])
    # The validate method makes sure the graph is valid/correct
    data.validate()
    # Return object of type HeteroData
    return data
def create_shuffled_dataset(package_name, pos, same_file, index_test, returns, jaccard_val, dynamic_edges):
    # Create a new HeteroData object
    data = HeteroData()
    # Read the nodes into a list
    nodes_df = pd.read_csv("./combined_features_asts/" + package_name + "_node.csv")
    nodes_csv_list = list(nodes_df.iterrows())
    # Read the ast edges into a list
    ast_csv_edges_list = list(pd.read_csv("./shuffled/" + package_name + "_shuffled_ast_edges.csv").iterrows())
    # Read the function edges into a list
    fn_csv_edges_list = list(pd.read_csv("./shuffled/" + package_name + "_shuffled_function_edges.csv").iterrows())
    # Read the dynamic edges into a list
    try:
        dyn_csv_edges_list = list(pd.read_csv("./shuffled/" + package_name + "_shuffled_dyn_edges.csv").iterrows())
    except:
        dyn_csv_edges_list = []
    # Create a list for the nodes
    nodes_list = []
    # Create lists for the ast edges
    ast_edge_index = []
    ast_edge_attr = []
    ast_edge_labels = []
    # Create lists for the function edges
    fn_edge_index = []
    fn_edge_attr = []
    fn_edge_labels = []
    # Fill the nodes list according to the selected features
    # Collect node types, names, and file names
    node_types = list(set(list(nodes_df["type"])))
    node_names = list(set(list(nodes_df["name"])))
    # Use a label encoder to store the types, names, and file names
    types_le = LabelEncoder()
    types_le.fit(node_types)
    names_le = LabelEncoder()
    names_le.fit(node_names)
    for node in nodes_csv_list:
        temp = []
        temp.append(types_le.transform([node[1].type])[0].item())
        temp.append(names_le.transform([node[1]["name"]])[0].item()) 
        temp.append(node[1].params_len)
        temp.append(node[1].argument_len)
        if returns == True:
            temp.append(node[1].returns)
        if pos == True:
            temp.append(node[1].start_line)
            temp.append(node[1].start_column)
            temp.append(node[1].end_line)
            temp.append(node[1].end_column)
        if index_test == True:
            temp.append(node[1].file_is_index_or_test)
        nodes_list.append(temp)
    # Fill the function edges according to the function edges
    for fn_edge in fn_csv_edges_list:
        fn_edge_index.append([fn_edge[1].src, fn_edge[1].dst])
        temp = []
        if same_file == True:
            temp.append(fn_edge[1].same_file)
        if jaccard_val == True:
            temp.append(fn_edge[1].jaccard_val)
        fn_edge_attr.append(temp)
        fn_edge_labels.append(fn_edge[1].label)
    # If the dynamic edges are selected, collect them
    if dynamic_edges == True:
        for dyn_edge in dyn_csv_edges_list:
            fn_edge_index.append([dyn_edge[1].src, dyn_edge[1].dst])
            temp = []
            if same_file == True:
                temp.append(dyn_edge[1].same_file)
            if jaccard_val == True:
                temp.append(dyn_edge[1].jaccard_val)
            fn_edge_attr.append(temp)
            fn_edge_labels.append(dyn_edge[1].label)
    # Fill the ast edges
    for ast_edge in ast_csv_edges_list:
        ast_edge_index.append([ast_edge[1].src, ast_edge[1].dst])
        temp = []
        if same_file == True:
            temp.append(-1)
        if jaccard_val == True:
            temp.append(-1)
        ast_edge_attr.append(temp)
        ast_edge_labels.append(ast_edge[1].label)
    # Initialize values of the object
    data["ast_node"].x = torch.tensor(nodes_list)
    data["ast_node", "calls", "ast_node"].edge_index = torch.transpose(torch.tensor(fn_edge_index, dtype=torch.int64), 0, 1)
    data["ast_node", "calls", "ast_node"].edge_attr = torch.tensor(fn_edge_attr, dtype=torch.float32)
    data["ast_node", "calls", "ast_node"].edge_label = torch.tensor(fn_edge_labels, dtype=torch.int64)
    data["ast_node", "calls", "ast_node"].edge_label_index = torch.tensor(fn_edge_labels, dtype=torch.int64)
    data["ast_node", "connects_to", "ast_node"].edge_index = torch.transpose(torch.tensor(ast_edge_index, dtype=torch.int64), 0, 1)
    data["ast_node", "connects_to", "ast_node"].edge_attr = torch.tensor(ast_edge_attr, dtype=torch.float32)
    data["ast_node", "connects_to", "ast_node"].edge_label = torch.tensor(ast_edge_labels, dtype=torch.int64)
    data["ast_node", "connects_to", "ast_node"].edge_label_index = torch.tensor(ast_edge_labels, dtype=torch.int64)
    # Validate the data object
    data.validate()
    # Return it
    return data
# create_dataloader uses create_dataset to create multiple graph datasets for all the packages
def create_dataloader(file_name, pos, same_file, index_test, returns, jaccard_val, dynamic_edges):
    # Collecting the package names using the nodes directory
    nodes_dir = r"./combined_features_asts/"
    # Hule, V. (February 24, 2024). Python List Files in a Directory. PYnative. https://pynative.com/python-list-files-in-a-directory/. Retrieved on December 6, 2025
    package_names = [file.name.replace("_node.csv", "") for file in pathlib.Path(nodes_dir).iterdir() if "_node.csv" in file.name]
    # Loop over the packages CSV files
    graph_list = []
    logging.warning("===========> Creating Dataloader :)")
    for package in package_names:
        # Logging
        logging.warning(f"===========> Converting Package: {package:s}")
        # For each package, call the create_dataset function
        graph = create_shuffled_dataset(package, pos, same_file, index_test, returns, jaccard_val, dynamic_edges)
        # Add the created graph dataset to a list
        graph_list.append(graph)
    # Create the dataloader using the final list
    dataloader = DataLoader(dataset = graph_list, batch_size = 1, shuffle = False)
    # Store the dataloader object
    # This prevents from needing to do the whole operation again at every run
    dataloader_file = open("./dataloaders/shuffled/" + file_name +".pkl", "wb")
    pk.dump(dataloader, dataloader_file)
    logging.warning("===========> DataLoader Created At: \"./dataloaders/shuffled/" + file_name + ".pkl\"")
    logging.warning("===========> Thank you! :)")
    dataloader_file.close()
# With position
#create_dataloader("Loader_Position_batch1_shuffled", pos = True, same_file = True, index_test = False, returns = False, jaccard_val = False, dynamic_edges = False)
#1.same_file
#create_dataloader("Loader_SameFile_batch1_Shuffled", pos = False, same_file = True, index_test = False, returns = False, jaccard_val = False, dynamic_edges = False)
#2.index_test
#create_dataloader("Loader_IndexTest_batch1_shuffled", pos = False, same_file = False, index_test = True, returns = False, jaccard_val = False, dynamic_edges = False)
#3.returns
#create_dataloader("Loader_Returns_batch1_shuffled", pos = False, same_file = False, index_test=False, returns=True, jaccard_val=False, dynamic_edges=False)
#4.jaccard_val
#create_dataloader("Loader_Jaccard_batch1_shuffled", pos=False, same_file=False, index_test=False, returns=False, jaccard_val=True, dynamic_edges=False)

#5.same_file index_test
#create_dataloader("Loader_SameFile_IndexTest_batch1_shuffled", pos=False, same_file=True, index_test=True, returns=False, jaccard_val=False, dynamic_edges=False)
#6.same_file returns
#create_dataloader("Loader_SameFile_Returns_batch1_shuffled", pos=False, same_file=True, index_test=False, returns=True, jaccard_val=False, dynamic_edges=False)
#7.same_file jaccard_val
#create_dataloader("Loader_SameFile_Jaccard_batch1_shuffled", pos=False, same_file=True, index_test=False, returns=False, jaccard_val=True, dynamic_edges=False)

#8.index_test returns
#create_dataloader("Loader_IndexTest_Returns_batch1_shuffled", pos=False, same_file=False, index_test=True, returns=True, jaccard_val=False, dynamic_edges=False)
#9.index_test jaccard_val
#create_dataloader("Loader_IndexTest_Jaccard_batch1_shuffled", pos=False, same_file=False, index_test=True, returns=False, jaccard_val=True, dynamic_edges=False)
#10.returns jaccard_val
#create_dataloader("Loader_Returns_Jaccard_batch1_shuffled", pos=False, same_file=False, index_test=False, returns=True, jaccard_val=True, dynamic_edges=False)


#11.same_file index_test returns
#create_dataloader("Loader_SameFile_IndexTest_Returns_batch1_shuffled", pos=False, same_file=True, index_test=True, returns=True, jaccard_val=False, dynamic_edges=False)
#12.same_file index_test jaccard_val
#create_dataloader("Loader_SameFile_IndexTest_Jaccard_batch1_shuffled", pos=False, same_file=True, index_test=True, returns=False, jaccard_val=True, dynamic_edges=False)
#13.same_file returns jaccard_val
#create_dataloader("Loader_SameFile_Returns_Jaccard_batch1_shuffled", pos=False, same_file=True, index_test=False, returns=True, jaccard_val=True, dynamic_edges=False)
#14.index_test returns jaccard_val
#create_dataloader("Loader_IndexTest_Returns_Jaccard_batch1_shuffled", pos=False, same_file=False, index_test=True, returns=True, jaccard_val=True, dynamic_edges=False)

#15. same_file index_test returns jaccard_val
#create_dataloader("Loader_All_batch1_shuffled", pos=False, same_file=True, index_test=True, returns=True, jaccard_val=True, dynamic_edges=False)

#16. []
#create_dataloader("Loader_None_batch1_shuffled", pos=False, same_file=False, index_test=False, returns=False, jaccard_val=False, dynamic_edges=False)

#1.same_file with dynamic edges
#create_dataloader("Loader_SameFile_with_Dynamic_batch1_shuffled", pos = False, same_file = True, index_test = False, returns = False, jaccard_val = False, dynamic_edges = True)
#2.index_test with dynamic edges
#create_dataloader("Loader_IndexTest_with_Dynamic_batch1_shuffled", pos = False, same_file = False, index_test = True, returns = False, jaccard_val = False, dynamic_edges = True)
#3.returns with dynamic edges
#create_dataloader("Loader_Returns_with_Dynamic_batch1_shuffled", pos = False, same_file = False, index_test=False, returns=True, jaccard_val=False, dynamic_edges=True)
#4.jaccard_val with dynamic edges
#create_dataloader("Loader_Jaccard_with_Dynamic_batch1_shuffled", pos=False, same_file=False, index_test=False, returns=False, jaccard_val=True, dynamic_edges=True)

#5.same_file index_test with dynamic edges
#create_dataloader("Loader_SameFile_IndexTest_with_Dynamic_batch1_shuffled", pos=False, same_file=True, index_test=True, returns=False, jaccard_val=False, dynamic_edges=True)
#6.same_file returns with dynamic edges
#create_dataloader("Loader_SameFile_Returns_with_Dynamic_batch1_shuffled", pos=False, same_file=True, index_test=False, returns=True, jaccard_val=False, dynamic_edges=True)
#7.same_file jaccard_val with dynamic edges
#create_dataloader("Loader_SameFile_Jaccard_with_Dynamic_batch1_shuffled", pos=False, same_file=True, index_test=False, returns=False, jaccard_val=True, dynamic_edges=True)

#8.index_test returns with dynamic edges
#create_dataloader("Loader_IndexTest_Returns_with_Dynamic_batch1_shuffled", pos=False, same_file=False, index_test=True, returns=True, jaccard_val=False, dynamic_edges=True)
#9.index_test jaccard_val with dynamic edges
#create_dataloader("Loader_IndexTest_Jaccard_with_Dynamic_batch1_shuffled", pos=False, same_file=False, index_test=True, returns=False, jaccard_val=True, dynamic_edges=True)
#10.returns jaccard_val with dynamic edges
#create_dataloader("Loader_Returns_Jaccard_with_Dynamic_batch1_shuffled", pos=False, same_file=False, index_test=False, returns=True, jaccard_val=True, dynamic_edges=True)


#11.same_file index_test returns with dynamic edges
#create_dataloader("Loader_SameFile_IndexTest_Returns_with_Dynamic_batch1_shuffled", pos=False, same_file=True, index_test=True, returns=True, jaccard_val=False, dynamic_edges=True)
#12.same_file index_test jaccard_val with dynamic edges
#create_dataloader("Loader_SameFile_IndexTest_Jaccard_with_Dynamic_batch1_shuffled", pos=False, same_file=True, index_test=True, returns=False, jaccard_val=True, dynamic_edges=True)
#13.same_file returns jaccard_val with dynamic edges
#create_dataloader("Loader_SameFile_Returns_Jaccard_with_Dynamic_batch1_shuffled", pos=False, same_file=True, index_test=False, returns=True, jaccard_val=True, dynamic_edges=True)
#14.index_test returns jaccard_val with dynamic edges
#create_dataloader("Loader_IndexTest_Returns_Jaccard_with_Dynamic_batch1_shuffled", pos=False, same_file=False, index_test=True, returns=True, jaccard_val=True, dynamic_edges=True)

#15. same_file index_test returns jaccard_val with dynamic edges
#create_dataloader("Loader_All_with_Dynamic_batch1_shuffled", pos=False, same_file=True, index_test=True, returns=True, jaccard_val=True, dynamic_edges=True)

#16. [] with dynamic edges
#create_dataloader("Loader_None_with_Dynamic_batch1_shuffled", pos=False, same_file=False, index_test=False, returns=False, jaccard_val=False, dynamic_edges=True)