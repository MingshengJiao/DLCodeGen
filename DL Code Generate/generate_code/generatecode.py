from abc import ABC, abstractmethod
from openai import AzureOpenAI, OpenAI
from get_retrieve_code import get_code_lines

class BaseCodeGenerator(ABC):
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

        self.system_direct_prompt = '''You are a deep learning expert, and you need to generate the corresponding deep learning code based my requirement using TensorFlow. Only Code is needed.'''
        self.system_ps_prompt = '''You are a deep learning expert, and you need to generate the corresponding deep learning code based on the User Requirement, Code Solution to fulfill the user's needs using TensorFlow. Only Code is needed.'''
        
        self.system_cedar_prompt = '''You are a large language model capable of generating deep learning code tailored to specific user requirements. Based on the following inputs, construct code that fulfills the given requirements:
{User Requirement} - This describes the task or functionality the code must achieve.
{Example Code} - This offers reference code from similar tasks and should be used as a guide for structure and approach.
Ensure the code is modular and well-commented, and format the code to enhance readability. The final code should be ready-to-run, assuming the user has access to the required libraries and dataset. Reply to me only the code.'''
        
        self.system_ccot_prompt = '''You are a large language model capable of generating deep learning code tailored to specific user requirements. Based on the following inputs, construct code that fulfills the given requirements:
{User Requirement} - This describes the task or functionality the code must achieve.
{Code Solution} - This provides specific information about the dataset, preprocessing steps, model architecture, and hyperparameters that should be used.
Ensure the code is modular and well-commented, and format the code to enhance readability. The final code should be ready-to-run, assuming the user has access to the required libraries and dataset. Reply to me only the code.'''
        
        self.system_rag_prompt = '''You are a large language model capable of generating deep learning code tailored to specific user requirements and solution details. Based on the following inputs, construct code that fulfills the given requirements:
{User Requirement} - This describes the task or functionality the code must achieve.
{Code Solution} - This provides specific information about the dataset, preprocessing steps, model architecture, and hyperparameters that should be used.
{Example Code} - This offers reference code from similar tasks and should be used as a guide for structure and approach.
Ensure the code is modular and well-commented, and format the code to enhance readability. The final code should be ready-to-run, assuming the user has access to the required libraries and dataset. Reply to me only the code.'''
        
        self.system_ragTemplate_prompt = '''You are a deep learning expert, and you need to generate the corresponding deep learning code based on the User Requirement, Code Solution and Code Template to fulfill the user's needs using TensorFlow. Only Code is needed.'''

        # '''You are an advanced AI model specializing in generating Kaggle Notebook-style deep learning code. Your task is to create a high-quality solution that fulfills the User Requirement by analyzing two sample code snippets (Code A and Code B).
      
        self.system_comparison_prompt =  '''You are an advanced AI model specializing in generating Kaggle Notebook-style deep learning code. Your task is to create a high-quality solution that fulfills the User Requirement by referring to the provided Code Solution in JSON format and analyzing two sample code snippets (Code A and Code B).
  
Objective: Combine the strengths of Code A and Code B to produce a Kaggle-ready solution that:

1. Meets the user's requirements accurately.
2. Adopts best practices commonly used in Kaggle Notebooks, such as a modular structure and clean, well-commented code.
3. Enhances functionality by integrating or improving upon the best aspects of Code A and Code B.
4. Avoids or corrects weaknesses present in the sample codes.
Expected Output:

Your output should be a complete Kaggle Notebook-style code solution, without additional markdown cells or unnecessary commentary.
Ensure the code is well-organized, modular, and adheres to Kaggle community standards for readability and functionality.
Steps to Follow:

1. Carefully analyze the user requirement to understand the task.
2. Use the JSON-based solution plan as the high-level guideline for structuring your code.
3. Evaluate the two sample code snippets (Code A and Code B) to extract and integrate the best practices and techniques.
4. Generate a fully functional solution that is optimized, clean, and ready to execute on Kaggle.'''

# 1. Carefully analyze the user requirement to understand the task.
# 2. Evaluate the two sample code snippets (Code A and Code B) to extract and integrate the best practices and techniques.
# 3. Generate a fully functional solution that is optimized, clean, and ready to execute on Kaggle.'''

    def __get_direct_prompt(self, user_requirement):
        direct_prompt = f'''User Requirement: 
{user_requirement}
Please generate deep learning code to complete the task:
'''
        return direct_prompt
        
    def __get_ps_prompt(self, user_requirement, solution):
        ps_prompt = f'''User Requirement: 
{user_requirement}
Code Solution: 
{solution}
```
Please refer to the code solution and generate deep learning code to complete the task:
'''
        return ps_prompt
    
    def __get_cedar_prompt(self, user_requirement, example_code):
        cedar_prompt = f'''User Requirement: 
{user_requirement}
Example Code:
{example_code}
Please refer to the context and generate deep learning code to complete the task:
'''
        return cedar_prompt
    
    def __get_rag_prompt(self, user_requirement, solution, example_code):
        rag_prompt = f'''User Requirement: 
{user_requirement}
Code Solution: 
{solution}
Example Code:
{example_code}
Please refer to the context and generate deep learning code to complete the task:
'''
        return rag_prompt
    

    
    def __get_ccot_prompt(self, user_requirement, solution, ccot):
        ccot_prompt = f'''User Requirement: 
{user_requirement}
Code Solution:
{solution}

{ccot}
'''
        return ccot_prompt
    
    def __get_ragTemplate_prompt(self, user_requirement, solution, ragTemplate):
        ragTemplate_prompt = f'''User Requirement: 
{user_requirement}
Code Solution: 
{solution}

{ragTemplate}
Please refer to the code solution & code template and generate deep learning code to complete the task:
'''
        return ragTemplate_prompt
    
    def __get_comparison_prompt(self, user_requirement, solution, ragTemplateResult, ragSolutionResult):


# Code Solution: 
# {solution}
        ragTemplate_prompt = f'''
User Requirement: 
{user_requirement}

Code Solution: 
{solution}

Code A:
{ragTemplateResult}

Code B:
{ragSolutionResult}
Please refer to the context and generate **only the code** for a Kaggle Notebook-style deep learning code that aligns with the user requirement. Focus on combining the strengths of Code A and Code B while adhering to the JSON-based plan. **Do not include markdown or explanations—just the code is needed.**
'''
        
# Please refer to the context and generate **only the code** for a Kaggle Notebook-style deep learning code that aligns with the user requirement. Focus on combining the strengths of Code A and Code B. **Do not include markdown or explanations—just the code is needed.**
# '''

        return ragTemplate_prompt
    
    def __generate_general_answer(self, system_prompt, prompt):   
        completion = self.client.chat.completions.create(
            model=self.model_name,  
            messages=[
                {"role":"system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=10000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            timeout=100,
            n=1
        )
        answer = completion.choices[0].message.content
        return answer
    
    def generate_direct_answer(self, user_requirement):
        direct_prompt = self.__get_direct_prompt(user_requirement=user_requirement)
        answer = self.__generate_general_answer(self.system_direct_prompt, direct_prompt)
        return answer
    
    def generate_ps_answer(self, user_requirement, solution):
        ps_prompt = self.__get_ps_prompt(user_requirement=user_requirement, solution=solution)
        answer = self.__generate_general_answer(self.system_ps_prompt, ps_prompt)
        return answer
    
    def generate_cedar_answer(self, user_requirement, example_code):
        cedar_prompt = self.__get_cedar_prompt(user_requirement=user_requirement, example_code=example_code)
        answer = self.__generate_general_answer(self.system_cedar_prompt, cedar_prompt)
        return answer
    
    def generate_ccot_answer(self, user_requirement, solution, ccot):
        ccot_prompt = self.__get_ccot_prompt(user_requirement=user_requirement, solution=solution, ccot=ccot)
        answer = self.__generate_general_answer(self.system_ccot_prompt, ccot_prompt)
        return answer
    
    def generate_rag_answer(self, user_requirement, solution, example_code):
        rag_prompt = self.__get_rag_prompt(user_requirement=user_requirement, solution=solution, example_code=example_code)
        answer = self.__generate_general_answer(self.system_rag_prompt, rag_prompt)
        return answer
    
    def generate_ragTemplate_answer(self, user_requirement, solution, ragTemplate):
        ragTemplate_prompt = self.__get_ragTemplate_prompt(user_requirement=user_requirement, solution=solution, ragTemplate=ragTemplate)
        answer = self.__generate_general_answer(self.system_ragTemplate_prompt, ragTemplate_prompt)
        return answer
    
    def generate_comparison_answer(self, user_requirement, solution, ragTemplateResult, ragSolutionResult):
        comparison_prompt = self.__get_comparison_prompt(user_requirement=user_requirement, solution=solution, ragTemplateResult=ragTemplateResult, ragSolutionResult=ragSolutionResult)
        answer = self.__generate_general_answer(self.system_comparison_prompt, comparison_prompt)
        return answer
    
    def generate_answer(self, user_requirement, system_prompt=""):
        answer = self.__generate_general_answer(system_prompt, user_requirement)
        return answer
    
class GPT35TurboGenerator(BaseCodeGenerator):
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="",
        )
        super().__init__(client=self.client, model_name="openai/gpt-3.5-turbo-0125")
    

class GPT4oMiNiGenerator(BaseCodeGenerator):
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="",
        )
        super().__init__(client=self.client, model_name="openai/gpt-4o-mini")
        

class DeepSeekCoderGenerator(BaseCodeGenerator):
    def __init__(self):
        self.client = OpenAI(
            api_key="", 
            base_url="https://api.deepseek.com/beta"
        )
        super().__init__(client=self.client, model_name="deepseek-coder")
    
