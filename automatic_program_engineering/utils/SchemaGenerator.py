
import os
def create_new_schema(fields_in_schema: list[str], class_name: str) -> str:
	"""
	Generates a Pydantic BaseModel with the given fields (all as str with empty description)
	and writes it to a Python file named after the class_name in the same directory.
	"""
	# Sanitize class and file names
	safe_class = ''.join(x for x in class_name if x.isalnum())
	safe_file = f"{safe_class}.py"
	lines = [
		"from pydantic import BaseModel, Field\n\n",
		f"class {safe_class}(BaseModel):\n"
	]
	for field in fields_in_schema:
		safe_field = field.strip().replace(' ', '_')
		lines.append(f"    {safe_field}: str = Field(description=\"\")\n")

	model_code = ''.join(lines)

	def write_schema_to(output_dir=None):
		if output_dir is None:
			output_dir = os.path.join(os.path.dirname(__file__), "..", "basic_schemas")
		os.makedirs(output_dir, exist_ok=True)
		out_path = os.path.join(output_dir, safe_file)
		with open(out_path, "w", encoding="utf-8") as f:
			f.write(model_code)
		return out_path

	# For backward compatibility, write to default location and return path
	return write_schema_to


def add_descriptions_to_schema(file_path: str, field_descriptions: dict[str, str]) -> None:
	"""
	Adds descriptions to the fields in the given Pydantic BaseModel file.
	Modifies the file in place. Handles relative paths robustly.
	"""
	
	# If file_path is not absolute, resolve relative to the current working directory
	if not os.path.isabs(file_path):
		file_path = os.path.abspath(file_path)

	with open(file_path, "r", encoding="utf-8") as f:
		lines = f.readlines()

	for i, line in enumerate(lines):
		for field, description in field_descriptions.items():
			if line.strip().startswith(f"{field}: str = Field("):
				lines[i] = f"    {field}: str = Field(description=\"{description}\")\n"

	with open(file_path, "w", encoding="utf-8") as f:
		f.writelines(lines)


# Example usage:
# A new file named 'TestSchema' will be created in the 'basic_schemas' directory with the specified field.
# create_new_schema(['example'], 'TestSchema')


# Add descriptions to the previously created schema
add_descriptions_to_schema(
	'D:\\DOCUMENTS\\self_study\\Agents\\langchain_learning\\automatic_program_engineering\\basic_schemas\\TestSchema.py',
	{'example': 'This is an example field.'}
)