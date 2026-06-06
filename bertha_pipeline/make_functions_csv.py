import json
import re
import esprima
# Function to check if Jelly jumbled the line numbers
def check_correct_positioning(start_line, end_line, start_column, end_column):
    # If the function starts and ends on the same line make sure the end column is after the start column
    if start_line == end_line:
        if start_column >= end_column:
            return False
        else:
            return True
    else:
        if start_line > end_line:
            return False
        else:
            return True
    # If the function has equal starting and ending lines and columns
# The target dynamic call graph
def make_functions(package, graph_type):
    # Opening the call graph
    print("Collecting " + graph_type + " functions for " + package)
    if graph_type == "dynamic":
        file = open("/mansion/MH000070/bertha_pipeline/raw_callgraphs/" + package + "_dyn_cg.json.out", "r")
    else:
        file = open("/mansion/MH000070/bertha_pipeline/raw_callgraphs/" + package + "_static_cg.json")
    # Reading the json
    json_file = json.load(file)
    # Extracting the files having the functions
    files = json_file["files"]
    # Collecting indices of the dependency files
    out_of_module_files_indices = [i for i in range(len(files)) if (re.findall("node_modules", files[i]) != [] or re.findall("coverage", files[i]) != [])]
    # Extracting the functions
    functions = json_file["functions"]
    # Making a csv file that includes the dynamically identified functions
    if graph_type == "dynamic":
        functions_csv = open("/mansion/MH000070/bertha_pipeline/data/nodes/" + package + "_dyn_functions.csv", "w")
    else:
        functions_csv = open("/mansion/MH000070/bertha_pipeline/data/nodes/" + package + "_static_functions.csv", "w")
    functions_csv.writelines(["index filename function_name start_line end_line start_column end_column returns is_async number_of_parameters parameter_names literals\n"])
    # Extracting features about the functions
    for i in range(len(functions)):
        if graph_type == "dynamic":
            j = i
        else:
            j = str(i)
        if int(functions[j].split(":")[0]) not in out_of_module_files_indices:
            function_file_name = files[int(functions[j].split(":")[0])]
            function_file = open("/mansion/MH000070/bertha_pipeline/packages/" + package + "/" + function_file_name, "r")
            function_start_line = int(functions[j].split(":")[1])
            function_start_column = int(functions[j].split(":")[2])
            function_end_line = int(functions[j].split(":")[3])
            function_end_column = int(functions[j].split(":")[4])
            function_file_lines = function_file.readlines()
            if check_correct_positioning(function_start_line, function_end_line, function_start_column, function_end_column):
                if len(function_file_lines) == (function_end_line - function_start_line) and ((len(list(esprima.tokenize(function_file_lines[0].replace("#", "/").replace("!", "/").replace("@", "/").replace("*", "")))) < 1) or (esprima.tokenize(function_file_lines[0].replace("#", "/").replace("!", "/").replace("$", "").replace("@", "").replace("*", ""))[0].value != "function")):
                    function_name = "whole_file"
                    function_returns = "0"
                    function_async = "0"
                    parameter_names = "parameters_not_found"
                else:
                    function_code = ""
                    j = function_start_line - 1
                    while j < function_end_line:
                        function_code = function_code + function_file_lines[j]
                        j = j + 1
                    # Trimming away any parts that are unrelated to the function
                    function_code_lines = []
                    for k in function_code.split("\n"):
                        function_code_lines.append(k)
                    whole_first_line = function_code_lines[0]
                    first_line = str(function_code_lines[0][function_start_column - 1:])
                    last_line = str(function_code_lines[(function_end_line - function_start_line)][:function_end_column - 1])
                    function_code_lines[0] = first_line
                    function_code_lines[(function_end_line - function_start_line)] = last_line
                    # function_code_fixed is the exact function code in string form
                    function_code_fixed = ""
                    for code in function_code_lines:
                        function_code_fixed = function_code_fixed + code
                    ast = list(esprima.tokenize(function_code_fixed))
                    function_name = ""
                    not_a_function = 0
                    for node in ast:
                        if node.type == "Keyword" and node.value == "class":
                            function_name = "class_constructor"
                            parameter_names = "class_constructor"
                            number_of_par = -1
                            other_tokens = "[]"
                    if function_name == "class_constructor":
                        not_a_function = 1
                    else:
                        if ast != []:
                            if(ast[0].type == "Keyword"):
                                if(ast[1].type == "Identifier"):
                                    function_name = ast[1].value
                                else:
                                    function_name = "no_name"
                            else:
                                function_name = "no_name"
                    # Collecting features from the function
                    # Checking if the function returns
                    function_returns = "0"
                    for node in ast:
                        if node.type == "Keyword" and node.value == "return":
                            function_returns = "1"
                    # Checking if the function is asynchronous
                    first_line_tokenized = esprima.tokenize(first_line.replace("*", "/").replace("@", "/").replace("?", "/").replace("$", "/").replace("&", "/").replace("-", "/").replace("^", "/").replace(":", "/").replace("%", "").replace("\\", "/"))
                    function_async = "0"
                    for node in first_line_tokenized:
                        if node.type == "Identifier" and node.value == "async":
                            function_async = "1"
                    # Check the number of parameters of the functions
                    # If the function has no name, add a temporary name to it
                    # Deals with issues with Esprima
                    if not_a_function != 1 and function_code_fixed.startswith("function") and function_name == "no_name":
                        # Add a placeholder function name to parse the first line and be able to get the number of parameters
                        placeholder_text_lines = function_code_fixed.split(" ")
                        temp = placeholder_text_lines[0][0] + placeholder_text_lines[0][1] + placeholder_text_lines[0][2] + placeholder_text_lines[0][3] + placeholder_text_lines[0][4] + placeholder_text_lines[0][5] + placeholder_text_lines[0][6] + placeholder_text_lines[0][7]
                        temp = temp + " func"
                        rest = 8
                        while rest < len(placeholder_text_lines[0]):
                            temp = temp + placeholder_text_lines[0][rest]
                            rest = rest + 1
                        placeholder_text_lines[0] = temp
                        placeholder_function_code = ""
                        for line in placeholder_text_lines:
                            placeholder_function_code = placeholder_function_code + line
                            placeholder_function_code = placeholder_function_code + " "
                        try:
                            parameter_names = []
                            for piece in esprima.parseScript(placeholder_function_code).body:
                                if piece.type == "FunctionDeclaration":
                                    number_of_par = str(len(piece.params))
                                    for par in piece.params:
                                        parameter_names.append(par.name)
                                    other_tokens = [token.value for token in esprima.parseScript(placeholder_function_code, {"tokens": True}).tokens if (token.type == "String" or token.type == "Identifier" and (token.value not in parameter_names)) and (token.value != "func")]
                                    break
                        except:
                            parameter_names = "parameters_not_found"
                            other_tokens = "no_other_tokens_found"
                            number_of_par = "-1"
                    else:
                        if not_a_function != 1:
                            try:
                                parameter_names = []
                                for piece in esprima.parseScript(function_code_fixed):
                                    if piece.type == "FunctionDeclaration":
                                        number_of_par = str(len(piece.params))
                                        for par in piece.params:
                                            parameter_names.append(par.name)
                                        other_tokens = [token.value for token in esprima.parseScript(placeholder_function_code, {"tokens": True}).tokens if (token.type == "String" or token.type == "Identifier" and (token.value not in parameter_names))]
                                        break
                            except:
                                parameter_names = "parameters_not_found"
                                other_tokens = "no_other_tokens_found"
                                number_of_par = "-1"
                    if number_of_par == 0:
                        parameter_names = "no_parameters"
                    functions_csv.writelines([str(i) + " " + function_file_name + " " + function_name + " " + str(function_start_line) + " " + str(function_end_line) + " " + str(function_start_column) + " " + str(function_end_column) + " " + function_returns + " " + function_async + " " + str(number_of_par) + " " + str(parameter_names).replace(" ", "") + " " + str(other_tokens).replace(" ", "") + "\n"])
                function_file.close()
    functions_csv.close()
