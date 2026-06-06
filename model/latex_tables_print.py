import pandas as pd
from statistics import mean, median
from matplotlib.pyplot import subplots, show
import numpy as np
def write_latex_table(metric):
    file = open("latex_table_" + metric + ".txt", "w")
    packages = ["stream-http", "string.prototype.padend", "stringstream", "tarjan-graph", "tcomb", "thingies", "timers-browserify", 
                "tiny-inflate", "tlhunter-sorted-set", "to-array", "toposort", "typed-array-byte-offset", "unbzip2-stream", "url-parse", 
                "util-deprecate", "validate.io-function", "vm-browserify", "walkdir", "walker", "warning", "webpack-node-externals", "wrappy", "xml-name-validaton"]
    same_file_df = pd.read_csv("./Figures/Test_Metrics/csv/latest/model_SameFile_metrics.csv")
    indextest_df = pd.read_csv("./Figures/Test_Metrics/csv/latest/model_IndexTest_metrics.csv")
    returns_df = pd.read_csv("./Figures/Test_Metrics/csv/latest/model_Returns_metrics.csv")
    jaccard_df = pd.read_csv("./Figures/Test_Metrics/csv/latest/model_Jaccard_metrics.csv")
    pos_df = pd.read_csv("./Figures/Test_Metrics/csv/latest/model_Position_metrics.csv")
    none_df = pd.read_csv("./Figures/Test_Metrics/csv/latest/model_None_metrics.csv")
    same_file_metric = [round(m1, 3) for m1 in list(same_file_df["calls_" + metric])]
    indextest_metric = [round(m2, 3) for m2 in list(indextest_df["calls_" + metric])]
    returns_metric = [round(m3, 3) for m3 in list(returns_df["calls_" + metric])]
    jaccard_metric = [round(m4, 3) for m4 in list(jaccard_df["calls_" + metric])]
    pos_metric = [round(m5, 3) for m5 in list(pos_df["calls_" + metric])]
    none_metric = [round(m6, 3) for m6 in list(none_df["calls_" + metric])]
    file.writelines(["Package & Same File & Index.js/Test & Returns & Jaccard & Position & None" + "\n"])
    for i in range(len(packages)):
        file.writelines([packages[i] + " & " + str(same_file_metric[i]) + " & " + str(indextest_metric[i]) + " & " + str(returns_metric[i]) + 
                        " & " + str(jaccard_metric[i]) + " & " + str(pos_metric[i]) + " & " + str(none_metric[i]) + "\n"])
    same_file_mean = round(mean(same_file_metric), 3)
    indextest_mean = round(mean(indextest_metric), 3)
    returns_mean = round(mean(returns_metric), 3)
    jaccard_mean = round(mean(jaccard_metric), 3)
    pos_mean = round(mean(pos_metric), 3)
    none_mean = round(mean(none_metric), 3)
    same_file_median = median(same_file_metric)
    indextest_median = median(indextest_metric)
    returns_median = median(returns_metric)
    jaccard_median = median(jaccard_metric)
    pos_median = median(pos_metric)
    none_median = round(mean(none_metric), 3)
    file.writelines(["Mean & " + str(same_file_mean) + " & " + str(indextest_mean) + " & " + str(returns_mean) + " & " + str(jaccard_mean) + " & " + str(pos_mean) + " & " + str(none_mean) + "\n"])
    file.writelines(["Median & " + str(same_file_median) + " & " + str(indextest_median) + " & " + str(returns_median) + " & " + str(jaccard_median) + " & " + str(pos_median) + " & " + str(none_median) + "\n"])
    file.close()
def write_latex_table_for_files(files, metric, name):
    new_file = open(name + "_" + metric + ".txt", "w")
    packages = ["stream-http", "string.prototype.padend", "stringstream", "tarjan-graph", "tcomb", "thingies", "timers-browserify", 
                "tiny-inflate", "tlhunter-sorted-set", "to-array", "toposort", "typed-array-byte-offset", "unbzip2-stream", "url-parse", 
                "util-deprecate", "validate.io-function", "vm-browserify", "walkdir", "walker", "warning", "webpack-node-externals", "wrappy", "xml-name-validaton"]
    metrics = []
    means = []
    medians = []
    header = "Package & "
    for file in files:
        metrics.append(list(pd.read_csv("./Figures/Test_Metrics/csv/latest/model_" + file + "_metrics.csv")["calls_" + metric]))
        header = header + file.replace("_", " ")
        header = header + " & "
    for m in metrics:
        means.append(round(mean(m), 3))
        medians.append(round(median(m), 3))
    new_file.writelines([header + "\n"])
    for i in range(len(packages)):
        line = packages[i] + " & "
        for j in range(len(files)):
            line = line + str(round(metrics[j][i],3)) + " & "
        new_file.writelines([line + "\n"])
    mean_line = "Total Mean & "
    median_line = "Total Median & "
    for k in range(len(means)):
        mean_line = mean_line + str(means[k]) + " & "
        median_line = median_line + str(medians[k]) + " & "
    new_file.writelines(mean_line + "\n")
    new_file.writelines(median_line + "\n")
def write_latex_table_for_file_with_select_means():
    new_file = open("dynamic_comparison.txt", "w")
    files = ["SameFile", "SameFile_with_Dynamic", "IndexTest", "IndexTest_with_Dynamic", "Returns", "Returns_with_Dynamic", "Jaccard", "Jaccard_with_Dynamic", "SameFile_IndexTest", 
             "SameFile_IndexTest_with_Dynamic", "SameFile_Returns", "SameFile_Returns_with_Dynamic", "SameFile_Jaccard", "SameFile_Jaccard_with_Dynamic", "IndexTest_Returns", 
             "IndexTest_Returns_with_Dynamic", "IndexTest_Jaccard", "IndexTest_Jaccard_with_Dynamic", "Returns_Jaccard", "Returns_Jaccard_with_Dynamic", 
             "SameFile_IndexTest_Returns", "SameFile_IndexTest_Returns_with_Dynamic", "SameFile_IndexTest_Jaccard", "SameFile_IndexTest_Jaccard_with_Dynamic", 
             "SameFile_Returns_Jaccard", "SameFile_Returns_Jaccard_with_Dynamic", "IndexTest_Returns_Jaccard", "IndexTest_Returns_Jaccard_with_Dynamic", "All", "All_with_Dynamic", "None", "None_with_Dynamic"]
    numbers = ["1", "1 + Dyn", "2", "2 + Dyn", "3", "3 + Dyn", "4", "4 + Dyn", "5", "5 + Dyn", "6", "6 + Dyn", "7", "7 + Dyn", "8", "8 + Dyn", "9", "9 + Dyn", "10", "10 + Dyn", 
               "11", "11 + Dyn", "12", "12 + Dyn", "13", "13 + Dyn", "14", "14 + Dyn", "15", "15 + Dyn", "16", "16 + Dyn"]
    header = "Version & \\makecell{Mean\\\\Precision} & \\makecell{Median\\\\Precision} & \\makecell{Mean\\\\Recall} & \\makecell{Median\\\\Recall}  & \\makecell{Mean\\\\Accuracy} & \\makecell{Median\\\\Accuracy}"
    new_file.writelines([header + "\\\\\n"])
    for i in range(len(files)):
        dataframe = pd.read_csv("./Figures/Test_Metrics/csv/latest/model_" + files[i] + "_metrics.csv")
        precisions = list(dataframe["calls_precision"])
        recalls = list(dataframe["calls_recall"])
        accuracies = list(dataframe["calls_accuracy"])
        line = numbers[i] + " & " + str(round(mean([precisions[2], precisions[4], precisions[8], precisions[13], precisions[20]]), 3)) + " & " + str(round(median([precisions[2], precisions[4], precisions[8], precisions[13], precisions[20]]), 3))
        line = line + " & " + str(round(mean([recalls[2], recalls[4], recalls[8], recalls[13], recalls[20]]), 3)) + " & " + str(round(median([recalls[2], recalls[4], recalls[8], recalls[13], recalls[20]]), 3))
        line = line + " & " + str(round(mean([accuracies[2], accuracies[4], accuracies[8], accuracies[13], accuracies[20]]), 3)) + " & " + str(round(median([accuracies[2], accuracies[4], accuracies[8], accuracies[13], accuracies[20]]), 3))
        new_file.writelines(line + "\\\n")
    new_file.close()
def plot_dyn():
    #versions = ["1", "2", "3", "4", "5", "6", "7", "8"]
    versions = ["9", "10", "11", "12", "13", "14", "15", "16"]
    #accuracies = {
    #    "Original": (0.538,0.74,0.6, 0.794, 0.705, 0.606, 0.721, 0.77),
    #    "+ Dynamic": (0.764, 0.62 ,0.769, 0.708, 0.788, 0.689, 0.739, 0.692)
    #}
    accuracies = {
        "Original": (0.648, 0.684, 0.656, 0.711, 0.749, 0.732, 0.801, 0.603),
        "+ Dynamic": (0.737, 0.689, 0.733, 0.599, 0.661, 0.669, 0.708, 0.832)
    }
    x = np.arange(8)
    width = 0.15
    multiplier = 1
    fig, ax = subplots(layout="constrained")
    for att, measurement in accuracies.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label = att)
        ax.bar_label(rects, padding = 1)
        multiplier += 1
    ax.set_ylabel("Mean Accuracy")
    ax.set_title("Effect of Adding Dynamic Edges")
    ax.set_xticks(x + width, versions)
    ax.legend(loc="upper left", ncols= 2)
    ax.set_ylim(0, 1)
    show()
def calculate_metrics_per_package():
    files = ["SameFile", "SameFile_with_Dynamic", "IndexTest", "IndexTest_with_Dynamic", "Returns", "Returns_with_Dynamic", "Jaccard", "Jaccard_with_Dynamic", "SameFile_IndexTest", 
             "SameFile_IndexTest_with_Dynamic", "SameFile_Returns", "SameFile_Returns_with_Dynamic", "SameFile_Jaccard", "SameFile_Jaccard_with_Dynamic", "IndexTest_Returns", 
             "IndexTest_Returns_with_Dynamic", "IndexTest_Jaccard", "IndexTest_Jaccard_with_Dynamic", "Returns_Jaccard", "Returns_Jaccard_with_Dynamic", 
             "SameFile_IndexTest_Returns", "SameFile_IndexTest_Returns_with_Dynamic", "SameFile_IndexTest_Jaccard", "SameFile_IndexTest_Jaccard_with_Dynamic", 
             "SameFile_Returns_Jaccard", "SameFile_Returns_Jaccard_with_Dynamic", "IndexTest_Returns_Jaccard", "IndexTest_Returns_Jaccard_with_Dynamic", "All", "All_with_Dynamic", "None", "None_with_Dynamic"]
    packages = ["stream-http", "string.prototype.padend", "stringstream", "tarjan-graph", "tcomb", "thingies", "timers-browserify", 
                "tiny-inflate", "tlhunter-sorted-set", "to-array", "toposort", "typed-array-byte-offset", "unbzip2-stream", "url-parse", 
                "util-deprecate", "validate.io-function", "vm-browserify", "walkdir", "walker", "warning", "webpack-node-externals", "wrappy", "xml-name-validaton"]
    mean_precisions = []
    mean_recalls = []
    mean_accuracies = []
    median_precisions = []
    median_recalls = []
    median_accuracies = []
    for i in range(len(packages)):
        temp_precisions = []
        temp_recalls = []
        temps_accuracies = []
        for file in files:
            temp_precisions.append(list(pd.read_csv("./Figures/Test_Metrics/csv/latest/model_" + file + "_metrics.csv")["calls_precision"])[i])
            temp_recalls.append(list(pd.read_csv("./Figures/Test_Metrics/csv/latest/model_" + file + "_metrics.csv")["calls_recall"])[i])
            temps_accuracies.append(list(pd.read_csv("./Figures/Test_Metrics/csv/latest/model_" + file + "_metrics.csv")["calls_accuracy"])[i])
        mean_precisions.append(round(mean(temp_precisions), 3))
        mean_recalls.append(round(mean(temp_recalls), 3))
        mean_accuracies.append(round(mean(temps_accuracies), 3))
        median_precisions.append(round(median(temp_precisions), 3))
        median_recalls.append(round(median(temp_recalls), 3))
        median_accuracies.append(round(median(temps_accuracies), 3))
    new_file = open("packages_mean_metrics_for_text.txt", "w")
    new_file1 = open("packages_median_metrics_for_text.txt", "w")
    new_file.writelines(["Package & Mean Precision & Mean Recall & Mean Accuracy \\\\\n"])
    new_file1.writelines(["Package & Median Precision & Median Recall & Median Accuracy \\\\\n"])
    for j in range(len(packages)):
        new_file.writelines([packages[j] + " & " + str(mean_precisions[j]) + " & " + str(mean_recalls[j]) + " & " + str(mean_accuracies[j]) + "\\\\\n"])
        new_file1.writelines([packages[j] + " & " + str(median_precisions[j]) + " & " + str(median_recalls[j]) + " & " + str(median_accuracies[j]) + "\\\\\n"])
    new_file.close()
    new_file1.close()
calculate_metrics_per_package()
