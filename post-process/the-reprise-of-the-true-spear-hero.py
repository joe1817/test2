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
	rules = [
		(r"(the |my |your |his |her |their )father", "Father", re.IGNORECASE),
		(r"(the |my |your |his |her |their )fiancée", "Fiancée", re.IGNORECASE),
		(r"(the |my |your |his |her |their )rival", "Rival", re.IGNORECASE),
		(r"(the |my |your |his |her |their )(big )?sister", "Big Sister", re.IGNORECASE),
		#(r"(the |my |your |his |her |their )older sister", "Older Sister", re.IGNORECASE),
	]
	
	compiled_rules = [
		(re.compile(pattern, options), replacement)
		for pattern, replacement, options in rules
	]
	
	header = True
	for line in lines:
		if line.startswith("Chapter"):
			yield line
			header = False
		elif header:
			yield line
		else:
			for pattern, replacement in compiled_rules:
				line = pattern.sub(replacement, line)
			yield line

if __name__ == "__main__":
	fix(*sys.argv[1:])
