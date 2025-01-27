# This code needs the generated results of both ragTemplate mothod and rag-solution method.
# Then the LLM generate new answer depending on both answers, comparing them and gets more accurate answer.

# rag Solution here means getting code and augmenting with solution, not using rag to generate solution.

from check_transfer_json import *
from codetemplate import CodeTemplate
from generatecode import *
import re
import argparse

def get_category_from_string(line):
    # define regex rule to get value of "Task Category"
    match = re.search(r'"Task Category":\s*"([^"]*)"', line)
    if match:
        task_category = match.group(1)
        return task_category
    else:
        return ""

def process_input(data):
    # if is 'str', return
    if isinstance(data, str):
        return data
    # if is 'dict'，transform to "key1: value1, key2: value2" format
    elif isinstance(data, dict):
        # using list comprehension to transform all key value pairs to "key: value" format
        return ', '.join([f'{key}: {value}' for key, value in data.items()])
    else:
        # Not 'str' nor 'dict', return null str
        return ""
    
def get_code_lines(source_file):
    lines = []

    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    tmp = ""
    final_lines = []
    for line in lines:
        if '------------------------------------- ' in line:
            final_lines.append(tmp)
            tmp = ""
        else:
            tmp += line
    return final_lines

def get_client(client_name):
    if client_name == "gpt-3.5-turbo":
        return GPT35TurboGenerator()
    if client_name == "gpt-4o-mini":
        return GPT4oMiNiGenerator()
    if client_name == "deepseekcoder":
        return DeepSeekCoderGenerator()
    else:
        return None
    

def generate_code_using_comparison(client_name, generate_method_name, 
                                  test_file_path, solution_file_path, 
                                  ragTemplate_result_path, ragSolution_result_path, 
                                  target_file_path):
    questions = []
    with open(test_file_path, "r", encoding="utf-8") as f1:
        questions = f1.readlines()
        
    solutions = []
    with open(solution_file_path, 'r', encoding="utf-8") as f2:
        solutions = f2.readlines()

    # ragTemplate results & ragSolution results
    ragTemplateResults = get_code_lines(ragTemplate_result_path)
    ragSolutionResults = get_code_lines(ragSolution_result_path)

    for i, ques in enumerate(questions):
        # user requirement
        # ques_dict["Dataset Attributes"] might be 'dict' type
        ques_dict = ast.literal_eval(ques)
        user_requirement = ques_dict["User Requirement"] + " " + process_input(ques_dict["Dataset Attributes"])

        # solution
        solution = solutions[i]

        # rag Template
        ragTemplateResult = ragTemplateResults[i]
        ragSolutionResult = ragSolutionResults[i]

        generator_client = get_client(client_name=client_name)
        generated_answer = ""

        try: 
            if generator_client is None:
                raise ValueError("Client is not defined!")
            if generate_method_name == "comparison":
                comparison_answer = generator_client.generate_comparison_answer(user_requirement=user_requirement, solution=solution, 
                                                                                ragTemplateResult=ragTemplateResult, ragSolutionResult=ragSolutionResult)
                generated_answer = comparison_answer
            print(f"Chat {i} success. {client_name}-{generate_method_name}")
        except Exception as e:
            print(f"---------! Chat {i} {client_name}-{generate_method_name} Error: {e} !---------")

        with open(target_file_path, 'a', encoding="utf-8") as fc:
            fc.writelines(generated_answer)
            fc.write(f"\n-------------------------------------\n")

if __name__ == "__main__":
    
    test_file_path = ""
    solution_file_path = ""

    parser = argparse.ArgumentParser(description='Get cilent name and generate method.')
    parser.add_argument('--client_name', type=str, required=True, help="LLM client name in ['gpt-3.5-turbo', 'gpt-4o-mini', 'deepseekcoder']")
    parser.add_argument('--generate_method_name', type=str, required=True)
    parser.add_argument('--target_file_path', type=str, required=True, help="Full file path where the generated code shall be stored")
    args = parser.parse_args()

    model_name = args.client_name
    if model_name not in ["gpt-3.5-turbo", "gpt-4o-mini", "deepseekcoder"]:
        print("Wrong client name!")
        exit(1)
    
    ragTemplate_result_path = f""
    ragSolution_result_path = f""


    generate_code_using_comparison(client_name=args.client_name,
                                  generate_method_name=args.generate_method_name,
                                  test_file_path=test_file_path,
                                  solution_file_path=solution_file_path,
                                  ragTemplate_result_path=ragTemplate_result_path,
                                  ragSolution_result_path=ragSolution_result_path,
                                  target_file_path=args.target_file_path)