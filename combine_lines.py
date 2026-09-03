import re

def read_file(file_path):
	with open(file_path, "r", encoding="utf-8") as file:
		return file.read().splitlines()

def write_file(file_path, lines):
	with open(file_path, "w", encoding="utf-8") as file:
		for line in lines:
			file.write(line + "\n")

def split_into_chapters(lines):
	chapters = []
	current_header = None
	current_body = []

	for idx, line in enumerate(lines):
		if line.startswith("Chapter "):
			if current_header is not None:
				chapters.append((current_header, current_body))
			current_header = (idx + 1, line)
			current_body = []
		else:
			if current_header is not None:
				current_body.append((idx + 1, line))
	if current_header is not None:
		chapters.append((current_header, current_body))
	return chapters

def extract_blocks(chapter_body_lines, is_source=True):
	start_delim = "「" if is_source else "“"

	blocks = []
	current_block_type = "narrative"
	current_block = []

	for line_num, line in chapter_body_lines:
		is_dialogue = line.startswith(start_delim)

		if is_dialogue and current_block_type != "dialogue":
			if current_block:
				blocks.append((current_block_type, current_block))
			current_block = [(line_num, line)]
			current_block_type = "dialogue"
		elif not is_dialogue and current_block_type == "dialogue":
			if current_block:
				blocks.append((current_block_type, current_block))
			current_block = [(line_num, line)]
			current_block_type = "narrative"
		else:
			current_block.append((line_num, line))

	if current_block:
		blocks.append((current_block_type, current_block))
	return blocks

def align_dialogues(source_dialogues, trans_dialogues):
	matches = []
	s_idx, t_idx = 0, 0

	while s_idx < len(source_dialogues) and t_idx < len(trans_dialogues):
		s_block = source_dialogues[s_idx][1]
		t_block = trans_dialogues[t_idx][1]

		if abs(len(s_block) - len(t_block)) <= 1:
			matches.append((s_idx, t_idx))
			s_idx += 1
			t_idx += 1
		else:
			cost_skip_t = float("inf")
			if t_idx + 1 < len(trans_dialogues):
				cost_skip_t = abs(len(s_block) - len(trans_dialogues[t_idx + 1][1]))

			cost_skip_s = float("inf")
			if s_idx + 1 < len(source_dialogues):
				cost_skip_s = abs(len(source_dialogues[s_idx + 1][1]) - len(t_block))

			if cost_skip_t < cost_skip_s and cost_skip_t < abs(len(s_block) - len(t_block)):
				t_idx += 1
			elif cost_skip_s < abs(len(s_block) - len(t_block)):
				s_idx += 1
			else:
				matches.append((s_idx, t_idx))
				s_idx += 1
				t_idx += 1

	return matches

def count_non_blank(block_lines):
	return sum(1 for _, line in block_lines if line != "")

def auto_collapse(lines):
	result = [""]

	prev_was_header = False
	prev_started_with_quote = False
	prev_ended_with_terminal = ""
	prev_was_header = False
	prev_has_no_ending_punctuation = False
	prev_was_bar = False

	for line in lines:
		if not line:
			if result[-1] != "":
				result.append("")
			continue
		if result[-1] == "":
			result[-1] = line
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

		if is_new_paragraph:
			result.append(line)
		else:
			result[-1] = result[-1] + " " + line

		# update tracking state for the next line
		prev_was_header = is_chapter_header
		prev_started_with_quote = starts_with_quote
		prev_was_bar = is_horiz_bar
		prev_ended_with_terminal = current_terminal
		prev_has_no_ending_punctuation = line_has_no_ending_punctuation

	if result[-1] == "":
		result = result[:-1]
	return result

def apply_spacing_to_block(source_block, trans_block_lines):
	source_non_blank_count = count_non_blank(source_block)
	trans_non_blank_count = sum(1 for line in trans_block_lines if line != "")

	if source_non_blank_count == trans_non_blank_count:
		result = [""]
		trans_iter = iter(trans_block_lines)
		for _, s_line in source_block:
			if s_line == "":
				if result[-1] != "":
					result.append("")
			else:
				while True:
					t_line = next(trans_iter)
					if t_line != "":
						if result[-1] == "":
							result[-1] = t_line
						else:
							result[-1] = result[-1] + " " + t_line
						break
					else:
						continue

		if result[-1] == "":
			result = result[:-1]

		return result
	else:
		return auto_collapse(trans_block_lines)

def process_chapter(s_chap, t_chap):
	s_header, s_body = s_chap
	t_header, t_body = t_chap

	source_blocks = extract_blocks(s_body, is_source=True)
	trans_blocks = extract_blocks(t_body, is_source=False)

	s_diag_indices = [i for i, b in enumerate(source_blocks) if b[0] == "dialogue"]
	t_diag_indices = [i for i, b in enumerate(trans_blocks) if b[0] == "dialogue"]

	matches = align_dialogues(
		[source_blocks[i] for i in s_diag_indices],
		[trans_blocks[i] for i in t_diag_indices]
	)

	# Use only the translation chapter header
	new_chapter_lines = [t_header[1]]

	absolute_matches = []
	for s_pos, t_pos in matches:
		absolute_matches.append((s_diag_indices[s_pos], t_diag_indices[t_pos]))

	full_matches = [(-1, -1)] + absolute_matches + [(len(source_blocks), len(trans_blocks))]

	for idx in range(len(full_matches) - 1):
		s_curr_s, t_curr_s = full_matches[idx]
		s_next_s, t_next_s = full_matches[idx + 1]

		s_narratives = [source_blocks[i] for i in range(s_curr_s + 1, s_next_s) if source_blocks[i][0] == "narrative"]
		t_narratives = [trans_blocks[i] for i in range(t_curr_s + 1, t_next_s) if trans_blocks[i][0] == "narrative"]

		if len(s_narratives) == len(t_narratives) and len(s_narratives) > 0:
			for s_narr, t_narr in zip(s_narratives, t_narratives):
				pure_t_lines = [line for _, line in t_narr[1]]
				new_chapter_lines.extend(apply_spacing_to_block(s_narr[1], pure_t_lines))
		else:
			for s_narr, t_narr in zip(s_narratives, t_narratives):
				source_line_num = s_narr[1][0][0] if s_narr[1] else s_header[0]
				pure_t_lines = [line for _, line in t_narr[1]]
				collapsed = auto_collapse(pure_t_lines)
				new_chapter_lines.extend(collapsed)

		if idx < len(full_matches) - 2:
			s_d_idx, t_d_idx = full_matches[idx + 1]
			for _, line in trans_blocks[t_d_idx][1]:
				new_chapter_lines.append(line)

	return new_chapter_lines

def apply_spacing_to_translation(source_path, trans_path, output_path):
	source_lines = read_file(source_path)
	trans_lines = read_file(trans_path)

	output_lines = []
	for line in trans_lines:
		if not line.startswith("Chapter"):
			output_lines.append(line)
		else:
			break


	source_chapters = split_into_chapters(source_lines)
	trans_chapters = split_into_chapters(trans_lines)

	for s_chap, t_chap in zip(source_chapters, trans_chapters):
		processed = process_chapter(s_chap, t_chap)
		output_lines.extend(processed)

	write_file(output_path, output_lines)

if __name__ == "__main__":
	apply_spacing_to_translation("book_jpn_min.txt", "book.txt", "_processed_book.txt")
