import os
import json

# path_to_json_file = "D:/DOCUMENTS/self_study/Agents/langchain_learning/automatic_program_engineering/blueprints"
path_to_json_file = "D:/DOCUMENTS/self_study/Agents/langchain_learning/automatic_program_engineering/assets/desired_output/output_auto_chubb_few_incomplete.json"

def generate_blueprint_from_json(json_path: str, class_name: str):
	"""
	Generates a Pydantic BaseModel class from a JSON file and saves it to the blueprints folder.
	All fields are str|None, default None, description="".
	"""
	# Read the JSON file
	with open(json_path, 'r', encoding='utf-8') as f:
		data = json.load(f)
	# If the JSON is a list, use the first item
	if isinstance(data, list) and data:
		data = data[0]
	if not isinstance(data, dict):
		raise ValueError("JSON must be an object or a list of objects.")

	# Prepare class code
	lines = ["from pydantic import BaseModel, Field\n\n"]
	lines.append(f"class {class_name}(BaseModel):\n")
	for key in data.keys():
		lines.append(f"    {key}: str|None = Field(default=None, description=\"\")\n")

	# Ensure blueprints directory exists
	blueprints_dir = os.path.join(os.path.dirname(__file__), '..', 'blueprints')
	os.makedirs(blueprints_dir, exist_ok=True)

	# Write to file
	# file_path = os.path.join(blueprints_dir, f"{class_name}.py")
	file_path = os.path.join(blueprints_dir, f"BlueprintSchema.py")
	with open(file_path, 'w', encoding='utf-8') as f:
		f.writelines(lines)
	print(f"Blueprint saved to {file_path}")


generate_blueprint_from_json(path_to_json_file, "BlueprintSchema")