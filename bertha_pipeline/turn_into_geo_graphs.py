import torch
import pandas as pd
import pickle as pk
from sklearn.preprocessing import LabelEncoder
from torch_geometric.data import Data
func_name_le = LabelEncoder()
file_name_le = LabelEncoder()
parameters_le = LabelEncoder()
literals_le = LabelEncoder()

# Nodes csv file
def turn_into_geo_graphs(package):
    nodes_filename = "/mansion/MH000070/bertha_pipeline/model_data/nodes/" + package + "_indexed_nodes.csv"
    enc_nodes_filename = "/mansion/MH000070/bertha_pipeline/model_data/encoded_nodes/" + package + "_encoded_nodes.csv"
    nodes_file = pd.read_csv(nodes_filename, delimiter = " ")
    # Reading the nodes from the csv file
    x_array = []
    y_array = []
    edge_attr_array = []
    edge_label_array = []
    func_le_array = []
    file_le_array = []
    par_le_array = []
    litr_le_array = []
    for row in nodes_file.itertuples():
        func_le_array.append(row.function_name)
        file_le_array.append(row.filename)
        par_le_array.append(row.parameter_names)
        litr_le_array.append(row.literals)
    func_name_le.fit(func_le_array)
    file_name_le.fit(list(set(file_le_array)))
    parameters_le.fit(list(set(par_le_array)))
    literals_le.fit(list(set(litr_le_array)))
    # Pickle file names
    pk_le = "/mansion/MH000070/bertha_pipeline/model_data/encoders/" + package + "_encoders.pkl"
    with open(pk_le, "wb") as file:
        pk.dump([func_name_le, file_name_le, parameters_le, literals_le], file, pk.HIGHEST_PROTOCOL)
    for row in nodes_file.itertuples():
        x_array.append([row.index, file_name_le.transform([row.filename])[0].item(), func_name_le.transform([row.function_name])[0].item(), row.start_line, row.end_line, row.start_column, row.end_column, row.returns, row.is_async, row.number_of_parameters, parameters_le.transform([row.parameter_names])[0].item(), literals_le.transform([row.literals])[0].item(), row.jelly, row.label])
    x = torch.tensor(x_array, dtype=torch.int64)
    # Edges csv file
    edges_filename = "/mansion/MH000070/bertha_pipeline/model_data/edges/" + package + "_indexed_edges.csv"
    edges_file = pd.read_csv(edges_filename, delimiter = " ")
    # Reading edge indices from the csv file
    edges_index_array = []
    for row in edges_file.itertuples():
        edges_index_array.append([row.index1, row.index2])
        edge_attr_array.append([row.jelly])
        edge_label_array.append(row.label)
    edge_index = torch.tensor(edges_index_array, dtype=torch.long)
    edge_attr = torch.tensor(edge_attr_array, dtype=torch.int64)
    edge_label = torch.tensor(edge_label_array, dtype=torch.long)
    # Building the data
    data = Data()
    # Nodes as a list of list of features
    data.x = x
    # Edges
    data.edge_index = edge_index.t().contiguous()
    # Edge attributes
    data.edge_attr = edge_attr
    # Edge labels
    # Whether the edge exists or not
    data.edge_label = edge_label
    # Making sure the structure of the data is correct
    data.validate(raise_on_error=True)
    # Saving the data as a binary file to be used in the model
    pk_data = "/mansion/MH000070/bertha_pipeline/torch_geometric_data/" + package + "_graph.pkl"
    with open(pk_data, "wb") as file2:
        pk.dump(data, file2, pk.HIGHEST_PROTOCOL)