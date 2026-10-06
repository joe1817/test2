import sys
import re

def read_file(file_path):
	with open(file_path, "r", encoding="utf-8") as file:
		return file.read().splitlines()

def write_file(file_path, lines):
	with open(file_path, "w", encoding="utf-8") as file:
		for line in lines:
			file.write(line + "\n")

def fix(trans_path, output_path):
	trans_lines = read_file(trans_path)
	write_file(output_path, make_replacements(trans_lines))

def make_replacements(lines):
	no_flags = 0
	rules = [
		(r"Atlas", "Atla", no_flags),
		(r"Firo Rial", "Filolial", no_flags),
	]
	
	compiled_rules = [
		(re.compile(pattern, options), replacement)
		for pattern, replacement, options in rules
	]
	
	for line in lines:
		for pattern, replacement in compiled_rules:
			line = pattern.sub(replacement, line)
		yield line

if __name__ == "__main__":
	fix(*sys.argv[1:])
