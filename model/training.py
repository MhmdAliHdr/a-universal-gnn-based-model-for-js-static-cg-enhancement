import torch
from torch_geometric.nn import to_hetero
from model import GNN
from torch_geometric.data import HeteroData
from statistics import mean
from matplotlib.pyplot import savefig, scatter, clf, title, figtext, ylim, xlim
import math
import pickle as pk
import logging
import copy
# The following reference was used for logging timestamps
# AdamE, C. Josh, djvg, Gab, gae123, G., Hans, H. James, Michael, paidhima, Toros91, user2176576, Zipp, R. StackOverflow February, 4 2015. Print timestamp for logging in Python.
# https://stackoverflow.com/questions/28330317/print-timestamp-for-logging-in-python. Retrieved on November 20, 2025
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING, datefmt='%Y-%m-%d %H:%M:%S')
device = torch.get_default_device()
torch.set_grad_enabled(True)
# Script based on https://github.com/pyg-team/pytorch_geometric/blob/master/examples/link_pred.py by Fey, M. and Niketan, N. (2023). Retrieved February 23, 2026
# and Graphia by Bhuiyan, M. H. M. (2025). Call Me Maybe: Enhancing JavaScript Call Graph Construction using Graph Neural Network
# https://arxiv.org/abs/2506.18191. Retrieved February 25, 2026
learning_rate = 0.0001
hidden_channels = 3
num_layers = 1
model = GNN(hidden_channels = hidden_channels, num_layers = num_layers)
model = to_hetero(model, metadata = (["ast_node"], [("ast_node", "calls", "ast_node"), ("ast_node", "connects_to", "ast_node")]))
optimizer = torch.optim.Adam(params = model.parameters(), lr = learning_rate)
criterion = torch.nn.BCELoss()
def train(dataloader):
    losses = []
    training_end_index = math.ceil(0.8 * len(dataloader)) - 1
    for i, data in enumerate(dataloader):
        if i <= training_end_index:
            logging.warning(f"=============> Package {i:04d}/{training_end_index}")
            # The features need to be cast to float, so they're the same dtype as the weights
            casted_data = HeteroData()
            casted_data["ast_node"].x = data["ast_node"].x.to(torch.float32)
            casted_data[("ast_node", "calls", "ast_node")].edge_index = data[("ast_node", "calls", "ast_node")].edge_index
            casted_data[("ast_node", "connects_to", "ast_node")].edge_index = data[("ast_node", "connects_to", "ast_node")].edge_index
            #casted_data[("ast_node", "calls", "ast_node")].edge_attr = data[("ast_node", "calls", "ast_node")].edge_attr
            #casted_data[("ast_node", "connects_to", "ast_node")].edge_attr = data[("ast_node", "connects_to", "ast_node")].edge_attr
            casted_data[("ast_node", "calls", "ast_node")].edge_label = data[("ast_node", "calls", "ast_node")].edge_label
            casted_data[("ast_node", "connects_to", "ast_node")].edge_label = data[("ast_node", "connects_to", "ast_node")].edge_label
            x = casted_data.x_dict
            edge_index = casted_data.edge_index_dict
            #edge_attr = casted_data.edge_attr_dict
            #out = model.forward(x = x, edge_index = edge_index, edge_attr = edge_attr)
            out = model.forward(x = x, edge_index = edge_index)
            out = torch.concat((out[("ast_node", "calls", "ast_node")], out[("ast_node", "connects_to", "ast_node")]))
            call_labels = torch.transpose(casted_data[("ast_node", "calls", "ast_node")].edge_label.unsqueeze(0), 0, 1).to(torch.float32)
            connection_labels = torch.transpose(casted_data[("ast_node", "connects_to", "ast_node")].edge_label.unsqueeze(0), 0, 1).to(torch.float32)
            labels = torch.concat((call_labels, connection_labels))
            loss = criterion(out, labels)
            losses.append(loss.item())
            loss.backward()
            optimizer.step()
    return mean(losses)

def train_for_epochs(dataloader, epochs, model_name):
    model.train(True)
    losses = []
    snapshots = []
    for epoch in range(epochs):
        logging.warning(f"=============> Epoch {epoch + 1:04d}/{epochs}")
        losses.append(train(dataloader))
        # Snapshot ensembles implementation is based on CodeGenes.net's implementation at https://www.codegenes.net/blog/snapshot-ensembles-pytorch/ (2024).
        # Retrieved on April 24, 2026
        snapshots.append(copy.deepcopy(model.state_dict()))
    logging.warning(f"Done! :)")
    scatter([i for i in range(epochs)], losses)
    ylim(0, 1)
    title("Loss Averages Per Epoch")
    figtext(0.02, 0.02, s = "Learning Rate: " + str(learning_rate) + "      Hidden Layers: " + str(hidden_channels) + "      Num Layers: " + str(num_layers))
    savefig("./Figures/Fixed_Model_Losses/latest/Training_Loss_" + model_name + ".png")
    clf()
    model_file = open("./Pickles/latest/" + model_name, "wb")
    losses_file = open("./Figures/Fixed_Model_Losses/latest/Training_losses/" + model_name + "_losses.txt", "w")
    losses_file.writelines([str(losses) + "\n"])
    losses_file.close()
    best_parameters = snapshots[losses.index(min(losses))]
    model.load_state_dict(best_parameters)
    pk.dump(model, model_file)
    model_file.close()
