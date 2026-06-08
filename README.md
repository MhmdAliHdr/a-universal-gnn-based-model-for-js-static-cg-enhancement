# This Repository goes over our implementation of a Universal GNN-Based Model for JavaScript Static Call Graph Enhancement
The directories are as follows:
## bertha_pipeline
Contains the scripts needed to clone packages and extract their call graphs. Note that this might take a considerable amount of time depending on the chosen packages.
The commit hashes for each packages are then saved if the steps are done successfully in order to allow replication.
## extract_data_pipeline
This directory includes the functionalities needed to extract the different features and construct the CSV files for the packages. Note that this makes use of the commit hashes previously presented to reclone the packages for AST construction.
This directory also contains the code needed to convert the CSV files into dataloaders usable by the model.
## model
The model directory requires the dataloaders constructed in the "extract_data_pipeline" directory. The "training" and testing scripts are also available there. 
The different dataloaders train the different versions of the model.
