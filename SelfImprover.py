import os
import re
import subprocess
from openai import OpenAI  # Adjust if your library import differs

class SelfImprovingAgent:
    def __init__(self, model="MODELHERE", iterations=5):
        self.model = model
        self.iterations = iterations
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="",
        )
    
    def extract_code(self, text):
        """
        Extracts the code from a Markdown code block if present.
        If no code block is found, returns the stripped text.
        """
        # This regex looks for a code block (optionally labeled with python)
        code_block = re.search(r"```(?:python)?\n(.*?)\n```", text, re.DOTALL)
        if code_block:
            return code_block.group(1).strip()
        return text.strip()
    
    def generate_code(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an AI code generator."},
                {"role": "user", "content": prompt}
            ]
        )
        # Extract only the code part from the response
        code = response.choices[0].message.content
        return self.extract_code(code)
    
    def evaluate_code(self, file_name):
        try:
            # Use "python3" if that's what you use in your shell
            result = subprocess.run(["python3", file_name], capture_output=True, text=True)
            return result.stdout, result.stderr
        except Exception as e:
            return "", str(e)
    
    def refine_code(self, code, feedback):
        prompt = (
            f"Refine this code based on the following feedback:\n{feedback}\n\n"
            f"Code:\n{code}"
        )
        return self.generate_code(prompt)
    
    def run(self):
        base_prompt = "Write a Python function that sorts a list efficiently. Include a test case."
        code = self.generate_code(base_prompt)
        file_name = "generated_script.py"

        for i in range(self.iterations):
            # Write the generated/refined code to a file
            with open(file_name, "w") as f:
                f.write(code)
            
            # Run the generated code and capture output/errors
            output, error = self.evaluate_code(file_name)
            feedback = error if error else f"Success! Output: {output}"
            code = self.refine_code(code, feedback)

        print("Final Version:")
        print(code)

if __name__ == "__main__":
    agent = SelfImprovingAgent()
    agent.run()

