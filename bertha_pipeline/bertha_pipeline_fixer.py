from repos import clone_repo
from make_functions_csv import make_functions
from make_static_edges_csv import make_static_edges
from make_dyn_edges_csv import make_dyn_edges
from index_functions import index_functions
from turn_into_geo_graphs import turn_into_geo_graphs
import json
import logging
import subprocess
from multiprocessing import Process
import time
import re
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
    data_file = open("/mansion/MH000070/repos_data.txt", "a")
    if (pkg[0] not in ["moo-color", "semver", "tslib", "chalk", "commander", "fs-extra", "debug", "typescript", "glob", "lodash", "yargs", "base64-js", "anymatch"]) and (pkg[1] != "https://github.com/DefinitelyTyped/DefinitelyTyped") and (re.findall("@", pkg[0]) == []):
        # Clone it
        try:
            clone_repo(pkg[0], pkg[1], "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0])
        except:
            logging.warning("Failed to clone repository: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
                data_file.close()
                continue
        # Install its dependencies
        # Zaharia, A. GitHub. (July 5, 2021) Kill a Python subprocess and its children when a timeout is reached.
        # https://alexandra-zaharia.github.io/posts/kill-subprocess-and-its-children-on-timeout-python/. Retrieved on November 22, 2025
        try:
            sp = subprocess.run("npm install", shell= True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], timeout=300)
        except:
            logging.warning("Failed to install dependencies for: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
            data_file.close()
            continue
        # Generate its static call graph
        # Zaharia, A. GitHub. (July 5, 2021) Kill a Python subprocess and its children when a timeout is reached.
        # https://alexandra-zaharia.github.io/posts/kill-subprocess-and-its-children-on-timeout-python/. Retrieved on November 22, 2025
        try:
            sp = subprocess.run("/mansion/MH000070/jelly/lib/main.js -j /mansion/MH000070/bertha_pipeline/raw_callgraphs/" + pkg[0] + "_static_cg.json" + " /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell= True, cwd = "/mansion/MH000070/bertha_pipeline/packages", timeout=300)
        except:
            logging.warning("Failed to generate static call graph for: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
            data_file.close()
            continue
        # Generate its dynamic call graph
        # Zaharia, A. GitHub. (July 5, 2021) Kill a Python subprocess and its children when a timeout is reached.
        # https://alexandra-zaharia.github.io/posts/kill-subprocess-and-its-children-on-timeout-python/. Retrieved on November 22, 2025
        command = "docker run --entrypoint jelly --rm -v /mansion/MH000070/bertha_pipeline/packages/" + pkg[0] + ":/workspace -v /mansion/MH000070/bertha_pipeline/raw_callgraphs" + ":/output -d jelly --npm-test /workspace -d /output/" + pkg[0] + "_dyn_cg.json.out"
        try:
            docker_id = subprocess.run(command, shell= True, cwd ="/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], timeout=300, stdout = subprocess.PIPE)
            time.sleep(300)
            subprocess.run("docker stop " + docker_id, shell=True, cwd ="/mansion/MH000070/bertha_pipeline/packages/" + pkg[0])
        except:
            logging.warning("Failed to generate dynamic call graph for: " + pkg[0])
        # The following tasks require calling functions from other files
        # The timeout setting mechanism is taken from the repos.py file provided by Opdebeeck, R. D. from the VUB in their latest study at the time of usage in 2025
        # Collect static functions
        try:
            p1 = Process(target= make_functions, args = (pkg[0], "static"))
            p1.start()
            p1.join(timeout=300)
        except:
            logging.warning("Failed to make static functions for: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
                data_file.close()
                continue
        # Save commit hash of the package if everything goes successfully and delete the package
        # Collect dynamic functions
        try:
            p2 = Process(target= make_functions, args = (pkg[0], "dynamic"))
            p2.start()
            p2.join(timeout=300)
        except:
            logging.warning("Failed to make dynamic functions for: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
                data_file.close()
                continue
        # Collect static edges
        # Balter, A., Knechtel, K., Otkidach, pygabriel, D., Rooney P., Smashery (October 13, 2009). How can I pass tuple with a single string as an argument (e.g. to mulitprocessing.Process)? [duplicate]. StackOverflow.
        # Retrieved on November 29, 2025
        try:
            p3 = Process(target = make_static_edges, args=(pkg[0],))
            p3.start()
            p3.join(timeout=300)
        except:
            logging.warning("Failed to make static edges for: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
                data_file.close()
                continue
        # Collect dynamic edges
        # Balter, A., Knechtel, K., Otkidach, pygabriel, D., Rooney P., Smashery (October 13, 2009). How can I pass tuple with a single string as an argument (e.g. to mulitprocessing.Process)? [duplicate]. StackOverflow.
        # Retrieved on November 29, 2025
        try:
            p4 = Process(target = make_dyn_edges, args =(pkg[0],))
            p4.start()
            p4.join(timeout=300)
        except:
            logging.warning("Failed to make dynamic edges for: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
                data_file.close()
                continue
        # Index the data
        # Balter, A., Knechtel, K., Otkidach, pygabriel, D., Rooney P., Smashery (October 13, 2009). How can I pass tuple with a single string as an argument (e.g. to mulitprocessing.Process)? [duplicate]. StackOverflow.
        # Retrieved on November 29, 2025
        try:
            p5 = Process(target = index_functions, args =(pkg[0],))
            p5.start()
            p5.join(timeout=300)
        except:
            logging.warning("Failed to make index functions for: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
                data_file.close()
                continue
        # Turn the csv data into a PyTorch Geometric format
        # Balter, A., Knechtel, K., Otkidach, pygabriel, D., Rooney P., Smashery (October 13, 2009). How can I pass tuple with a single string as an argument (e.g. to mulitprocessing.Process)? [duplicate]. StackOverflow.
        # Retrieved on November 29, 2025
        try:
            p6 = Process(target = turn_into_geo_graphs, args =(pkg[0],))
            p6.start()
            p6.join(timeout=300)
        except:
            logging.warning("Failed to make static functions for: " + pkg[0])
            # Save commit hash of the package if everything goes successfully and delete the package
            try:
                # Writing the information onto a file
                # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
                # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
                #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
                res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
                data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
                subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
            except:
                logging.warning("Failed to get commit hashes for: " + pkg[0])
                data_file.close()
                continue
        # Save commit hash of the package if everything goes successfully and delete the package
        # Writing the information onto a file
        # Andreas, D., Caron, A., Çelik, S. H., cloud8bits, Correia, J., Dekker, F.,  Digio, Enderle, J. S., Graham, S.,  Isidore, J., Jerry T, Khan, A., Miller, M., Semnodime, Silver Light, static_rtti
        # tripleee, user14745999, Vasilis, WestCoastProjects, ... Zitrax. (January 21, 2011) Running shell commmand and capturing the output. StackOverflow
        #  https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. Retrieved on November 26, 2025
        res = subprocess.run("git rev-parse HEAD", shell=True, cwd = "/mansion/MH000070/bertha_pipeline/packages/" + pkg[0], stdout=subprocess.PIPE)
        data_file.writelines([pkg[0] + ", " + pkg[1] + ": " + res.stdout.decode("utf-8") + "\n"])
        subprocess.run("rm -rf /mansion/MH000070/bertha_pipeline/packages/" + pkg[0], shell=True, cwd="/mansion/MH000070/bertha_pipeline/packages/")
        logging.warning("Failed to get commit hashes for: " + pkg[0])
        data_file.close()
    data_file.close()
