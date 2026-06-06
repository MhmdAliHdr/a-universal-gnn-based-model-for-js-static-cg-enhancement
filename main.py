import pickle as pk
from training import train_for_epochs
from testing import test, test_with_attr
import torch
from pathlib import Path
from torch_geometric.loader import DataLoader
from torch_geometric.data import HeteroData
import logging

# The following reference was used for logging timestamps
# AdamE, C. Josh, djvg, Gab, gae123, G., Hans, H. James, Michael, paidhima, Toros91, user2176576, Zipp, R. StackOverflow February, 4 2015.
# Print timestamp for logging in Python. https://stackoverflow.com/questions/28330317/print-timestamp-for-logging-in-python. Retrieved on November 20, 2025
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING, datefmt='%Y-%m-%d %H:%M:%S')
# Pick the model to train/test
name = "All"
# Read the dataloader
dataloader_file = open("./DataLoaders/shuffled/Loader_" + name + "_batch1_shuffled.pkl" , "rb")
dataloader = pk.load(dataloader_file)
# Train the model, if testing with models that require edge features, uncomment the lines in training.py
train_for_epochs(dataloader, 500, "model_" + name + ".pkl")
# Test the model, test_with_attr is for models that make use of edge features
#test(dataloader, "model_" + name)
test_with_attr(dataloader, "model_" + name)
dataloader_file.close()