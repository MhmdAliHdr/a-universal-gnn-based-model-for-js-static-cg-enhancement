import subprocess
import logging
import json
from pathlib import Path
# The following reference was used for logging timestamps
# AdamE, C. Josh, djvg, Gab, gae123, G., Hans, H. James, Michael, paidhima, Toros91, user2176576, Zipp, R. StackOverflow February, 4 2015. Print timestamp for logging in Python.
# https://stackoverflow.com/questions/28330317/print-timestamp-for-logging-in-python. Retrieved on November 20, 2025
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING, datefmt='%Y-%m-%d %H:%M:%S')
# Open the json file containing the package information
file = open("/mansion/MH000070/bertha_pipeline/most_popular_packages.json", encoding="utf-8")
packages_json = json.load(file)
packages_data = []
for i in packages_json:
    try:
        packages_data.append((i["name"], i["links"]["repository"]))
    except:
        print("Package " + i["name"] + " is missing a repository")
# For each package
data_file = open("/mansion/MH000070/bertha_pipeline/repos_data.txt", "w")
for pkg in packages_data:
        if pkg[0] not in ["lodash", "glob", "typescript"] and pkg[1] != "https://github.com/DefinitelyTyped/DefinitelyTyped":
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
data_file.close()