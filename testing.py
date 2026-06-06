import torch
from torch_geometric.nn import to_hetero
from torch_geometric.data import HeteroData
from statistics import mean
from matplotlib.pyplot import savefig, scatter, clf, title, figtext
import math
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import pickle as pk
import logging

# and Graphia by Bhuiyan, M. H. M. (2025). Call Me Maybe: Enhancing JavaScript Call Graph Construction using Graph Neural Network
# https://arxiv.org/abs/2506.18191
# The following reference was used for logging timestamps
# AdamE, C. Josh, djvg, Gab, gae123, G., Hans, H. James, Michael, paidhima, Toros91, user2176576, Zipp, R. StackOverflow February, 4 2015. Print timestamp for logging in Python.
# https://stackoverflow.com/questions/28330317/print-timestamp-for-logging-in-python. Retrieved on November 20, 2025
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING, datefmt='%Y-%m-%d %H:%M:%S')
# Script based on https://github.com/pyg-team/pytorch_geometric/blob/master/examples/link_pred.py by Fey, M. and Niketan, N. (2023). Retrieved February 23, 2026
# and Graphia by Bhuiyan, M. H. M. (2025). Call Me Maybe: Enhancing JavaScript Call Graph Construction using Graph Neural Network
# https://arxiv.org/abs/2506.18191. Retrieved February 25, 2026
device = torch.get_default_device()
def test(dataloader, model_name):
    # Load the model
    model_file = open("./Pickles/latest/" + model_name + ".pkl", "rb")
    model = pk.load(model_file)
    # Set the model in evaluation mode
    model.eval()
    # Create a file to write the precision and recall values to
    metrics_file = open("./Figures/Test_Metrics/csv/latest/" + model_name + "_metrics.csv", "w")
    metrics_file.writelines(["package,calls_precision,calls_recall,calls_f1_score,calls_accuracy,ast_precision,ast_recall,ast_f1_score,ast_accuracy,total_precision,total_recall,total_f1_score,total_accuracy" + "\n"])
    # The testing happens from the training index of the dataset till its end (20%)
    training_end_index = math.ceil(0.8 * len(dataloader)) - 1
    for i, data in enumerate(dataloader):
        if i > training_end_index:
            logging.warning(f"=============> Package {i:04d}/{training_end_index}")
            # The features need to be cast to float, so they're the same dtype as the weights
            casted_data = HeteroData()
            casted_data["ast_node"].x = data["ast_node"].x.to(torch.float32)
            casted_data[("ast_node", "calls", "ast_node")].edge_index = data[("ast_node", "calls", "ast_node")].edge_index
            casted_data[("ast_node", "connects_to", "ast_node")].edge_index = data[("ast_node", "connects_to", "ast_node")].edge_index
            casted_data[("ast_node", "calls", "ast_node")].edge_label = data[("ast_node", "calls", "ast_node")].edge_label
            casted_data[("ast_node", "connects_to", "ast_node")].edge_label = data[("ast_node", "connects_to", "ast_node")].edge_label
            x = casted_data.x_dict
            edge_index = casted_data.edge_index_dict
            out = model.forward(x = x, edge_index = edge_index)
            # Rounding the output of the model to be able to calculate precision and recall scores
            call_preds = []
            connections_preds = []
            for call_pred in out[("ast_node", "calls", "ast_node")]:
                if call_pred >= 0.5:
                    call_preds.append(1)
                else:
                    call_preds.append(0)
            for connect_pred in out[("ast_node", "connects_to", "ast_node")]:
                if connect_pred >= 0.5:
                    connections_preds.append(1)
                else:
                    connections_preds.append(0)
            out_all = call_preds + connections_preds
            call_labels = torch.transpose(casted_data[("ast_node", "calls", "ast_node")].edge_label.unsqueeze(0), 0, 1).to(torch.float64)
            connection_labels = torch.transpose(casted_data[("ast_node", "connects_to", "ast_node")].edge_label.unsqueeze(0), 0, 1).to(torch.float64)
            all_labels = torch.concat((call_labels, connection_labels))
            # Calculating the different labels
            calls_precision = precision_score(call_labels, call_preds)
            calls_recall = recall_score(call_labels, call_preds)
            calls_f1_score = f1_score(call_labels, call_preds)
            calls_accuracy = accuracy_score(call_labels, call_preds)
            connections_precision = precision_score(connection_labels, connections_preds)
            connections_recall = recall_score(connection_labels, connections_preds)
            connections_f1_score = f1_score(connection_labels, connections_preds)
            connections_accuracy = accuracy_score(connection_labels, connections_preds)
            total_precision = precision_score(all_labels, out_all)
            total_recall = recall_score(all_labels, out_all)
            total_f1_score = f1_score(all_labels, out_all)
            total_accuracy = accuracy_score(all_labels, out_all)
            # Writing the calculated metrics to the CSV file
            metrics_file.writelines([str(i) + "," + str(calls_precision) + "," + str(calls_recall) + "," + str(calls_f1_score) + "," + str(calls_accuracy) + "," + 
                                     str(connections_precision) + "," + str(connections_recall) + "," + str(connections_f1_score) + "," + str(connections_accuracy) + "," +
                                     str(total_precision) + "," + str(total_recall) + "," + str(total_f1_score) + "," + str(total_accuracy) + "\n"])
    metrics_file.close()
    model_file.close()
    logging.warning(f"=============> Done :)")
def test_with_attr(dataloader, model_name):
    # Load the model
    model_file = open("./Pickles/latest/" + model_name + ".pkl", "rb")
    model = pk.load(model_file)
    # Set the model in evaluation mode
    model.eval()
    # Create a file to write the precision and recall values to
    metrics_file = open("./Figures/Test_Metrics/csv/latest/" + model_name + "_metrics.csv", "w")
    metrics_file.writelines(["package,calls_precision,calls_recall,calls_f1_score,calls_accuracy,ast_precision,ast_recall,ast_f1_score,ast_accuracy,total_precision,total_recall,total_f1_score,total_accuracy" + "\n"])
    # The testing happens from the training index of the dataset till its end (20%)
    training_end_index = math.ceil(0.8 * len(dataloader)) - 1
    for i, data in enumerate(dataloader):
        if i > training_end_index:
            logging.warning(f"=============> Package {i:04d}/{training_end_index}")
            # The features need to be cast to float, so they're the same dtype as the weights
            casted_data = HeteroData()
            casted_data["ast_node"].x = data["ast_node"].x.to(torch.float32)
            casted_data[("ast_node", "calls", "ast_node")].edge_index = data[("ast_node", "calls", "ast_node")].edge_index
            casted_data[("ast_node", "connects_to", "ast_node")].edge_index = data[("ast_node", "connects_to", "ast_node")].edge_index
            casted_data[("ast_node", "calls", "ast_node")].edge_attr = data[("ast_node", "calls", "ast_node")].edge_attr
            casted_data[("ast_node", "connects_to", "ast_node")].edge_attr = data[("ast_node", "connects_to", "ast_node")].edge_attr
            casted_data[("ast_node", "calls", "ast_node")].edge_label = data[("ast_node", "calls", "ast_node")].edge_label
            casted_data[("ast_node", "connects_to", "ast_node")].edge_label = data[("ast_node", "connects_to", "ast_node")].edge_label
            x = casted_data.x_dict
            edge_index = casted_data.edge_index_dict
            edge_attr = casted_data.edge_attr_dict
            out = model.forward(x = x, edge_index = edge_index, edge_attr = edge_attr)
            # Rounding the output of the model to be able to calculate precision and recall scores
            call_preds = []
            connections_preds = []
            for call_pred in out[("ast_node", "calls", "ast_node")]:
                if call_pred >= 0.5:
                    call_preds.append(1)
                else:
                    call_preds.append(0)
            for connect_pred in out[("ast_node", "connects_to", "ast_node")]:
                if connect_pred >= 0.5:
                    connections_preds.append(1)
                else:
                    connections_preds.append(0)
            out_all = call_preds + connections_preds
            call_labels = torch.transpose(casted_data[("ast_node", "calls", "ast_node")].edge_label.unsqueeze(0), 0, 1).to(torch.float64)
            connection_labels = torch.transpose(casted_data[("ast_node", "connects_to", "ast_node")].edge_label.unsqueeze(0), 0, 1).to(torch.float64)
            all_labels = torch.concat((call_labels, connection_labels))
            # Calculating the different labels
            calls_precision = precision_score(call_labels, call_preds)
            calls_recall = recall_score(call_labels, call_preds)
            calls_f1_score = f1_score(call_labels, call_preds)
            calls_accuracy = accuracy_score(call_labels, call_preds)
            connections_precision = precision_score(connection_labels, connections_preds)
            connections_recall = recall_score(connection_labels, connections_preds)
            connections_f1_score = f1_score(connection_labels, connections_preds)
            connections_accuracy = accuracy_score(connection_labels, connections_preds)
            total_precision = precision_score(all_labels, out_all)
            total_recall = recall_score(all_labels, out_all)
            total_f1_score = f1_score(all_labels, out_all)
            total_accuracy = accuracy_score(all_labels, out_all)
            # Writing the calculated metrics to the CSV file
            metrics_file.writelines([str(i) + "," + str(calls_precision) + "," + str(calls_recall) + "," + str(calls_f1_score) + "," + str(calls_accuracy) + "," + 
                                     str(connections_precision) + "," + str(connections_recall) + "," + str(connections_f1_score) + "," + str(connections_accuracy) + "," +
                                     str(total_precision) + "," + str(total_recall) + "," + str(total_f1_score) + "," + str(total_accuracy) + "\n"])
    metrics_file.close()
    model_file.close()
    logging.warning(f"=============> Done :)")