import subprocess
import logging
import json
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
for pkg in packages_data:
    if pkg[0] not in ["moo-color", "semver", "tslib", "chalk", "commander", "fs-extra", "debug", "typescript", "glob", "lodash", "yargs"] and pkg[1] != "https://github.com/DefinitelyTyped/DefinitelyTyped":
        # Generate its static call graph
        # Zaharia, A. GitHub. (July 5, 2021) Kill a Python subprocess and its children when a timeout is reached.
        # https://alexandra-zaharia.github.io/posts/kill-subprocess-and-its-children-on-timeout-python/. Retrieved on November 22, 2025
        try:
            subprocess.run("mv /mansion/MH000070/bertha_pipeline/packages/" + pkg[0] + "/" + pkg[0] + "_static_cg.json /mansion/MH000070/bertha_pipeline", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0])
        except:
            logging.warning("Failed to move static call graph for: " + pkg[0])
        # Generate its static call graph
        # Zaharia, A. GitHub. (July 5, 2021) Kill a Python subprocess and its children when a timeout is reached.
        # https://alexandra-zaharia.github.io/posts/kill-subprocess-and-its-children-on-timeout-python/. Retrieved on November 22, 2025
        try:
            subprocess.run("mv /mansion/MH000070/bertha_pipeline/packages/" + pkg[0] + "/" + pkg[0] + "_dyn_cg.json.out /mansion/MH000070/bertha_pipeline", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0])
        except:
            logging.warning("Failed to move static call graph for: " + pkg[0])