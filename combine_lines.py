import re

def collapse_book_paragraphs(input_filename, output_filename):
	with open(input_filename, "r", encoding="utf-8") as file:
		lines = [line.strip() for line in file]

	paragraphs = []
	current_paragraph_lines = []

	prev_was_header = False
	prev_started_with_quote = False
	prev_ended_with_terminal = ""
	prev_was_header = False
	prev_has_no_ending_punctuation = False
	prev_was_bar = False

	for line in lines:
		if not line:
			if current_paragraph_lines:
				paragraphs.append(" ".join(current_paragraph_lines))
				current_paragraph_lines = []
			continue

		# lines starting with Chapter
		is_chapter_header = line.startswith("Chapter")
		is_after_header = prev_was_header

		# lines starting with “
		starts_with_quote = line.startswith("“")

		# lines starting with emdash
		starts_with_emdash = line.startswith("—")

		# lines immediately after ones that start with “
		is_after_quote = prev_started_with_quote

		# lines starting with …
		starts_with_ellipse = line.startswith("…")

		# horizontal bar
		is_horiz_bar = line == "---"

		# after horizontal bar
		is_after_horiz_bar = prev_was_bar

		# lines starting with a token followed by specific punctuation
		starts_with_token_punct = bool(re.match(r"^[^ ]+[\.!?…;:]", line))

		# lines that end in ! or ? unless the previous line also ended in the same character
		current_terminal = line[-1] if line and line[-1] in "!?" else ""
		is_terminal_rule = False
		if current_terminal:
			if current_terminal != prev_ended_with_terminal:
				is_terminal_rule = True

		# lines with no ending punctuation
		line_has_no_ending_punctuation = bool(re.search(r"[\w\d,…;:]$", line))
		is_after_line_with_no_punc = prev_has_no_ending_punctuation

		# combine rules to check if this line starts a new paragraph
		is_new_paragraph = (
			is_chapter_header or
			is_after_header or
			starts_with_quote or
			starts_with_emdash or
			is_after_quote or
			starts_with_ellipse or
			is_horiz_bar or
			is_after_horiz_bar or
			starts_with_token_punct or
			is_terminal_rule or
			is_after_line_with_no_punc
		)

		if is_new_paragraph and current_paragraph_lines:
			paragraphs.append(" ".join(current_paragraph_lines))
			current_paragraph_lines = []

		current_paragraph_lines.append(line)

		# update tracking state for the next line
		prev_was_header = is_chapter_header
		prev_started_with_quote = starts_with_quote
		prev_was_bar = is_horiz_bar
		prev_ended_with_terminal = current_terminal
		prev_has_no_ending_punctuation = line_has_no_ending_punctuation

	if current_paragraph_lines:
		paragraphs.append(" ".join(current_paragraph_lines))

	with open(output_filename, "w", encoding="utf-8") as file:
		for p in paragraphs:
			file.write(p + "\n")

	print(f"Successfully processed and saved to '{output_filename}'.")

if __name__ == "__main__":
	collapse_book_paragraphs("book.txt", "_processed_book.txt")
