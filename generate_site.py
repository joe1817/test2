import os
import re
import json
import shutil

def generate_html_site(input_filename, output_dir="docs"):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	chapters_dir = os.path.join(output_dir, "chapters")
	if not os.path.exists(chapters_dir):
		os.makedirs(chapters_dir)

	if not os.path.exists(input_filename):
		print(f"The input file '{input_filename}' does not exist.")
		return

	with open(input_filename, "r", encoding="utf-8") as file:
		lines = [line.strip() for line in file if line.strip()]

	if not lines:
		print("The input file is empty.")
		return

	book_title_data = []
	chapter_data = []
	active_chapter_num = None
	active_chapter_title = None
	active_paragraphs = []

	chapter_pattern = re.compile(r"^Chapter\s+(\d+)\s*-\s*(.+)$", re.IGNORECASE)

	for line in lines:
		match = chapter_pattern.match(line)
		if match:
			if active_chapter_num is not None:
				chapter_data.append({
					"num": active_chapter_num,
					"title": active_chapter_title,
					"paragraphs": active_paragraphs
				})
				active_paragraphs = []
			active_chapter_num = int(match.group(1))
			active_chapter_title = match.group(2)
		else:
			if active_chapter_num is None:
				book_title_data.append(line)
			else:
				active_paragraphs.append(line)

	if active_chapter_num is not None:
		chapter_data.append({
			"num": active_chapter_num,
			"title": active_chapter_title,
			"paragraphs": active_paragraphs
		})

	if not book_title_data:
		print("No title found.")
		return

	if not chapter_data:
		print("No chapters found.")
		return

	book_title = book_title_data[0]
	subtitles = book_title_data[1:]
	total_chapters = len(chapter_data)

	toc_chapters = []
	for index, ch in enumerate(chapter_data):
		current_num = ch["num"]
		prev_num = chapter_data[index - 1]["num"] if index > 0 else None
		next_num = chapter_data[index + 1]["num"] if index < total_chapters - 1 else None

		toc_chapters.append({
			"num": current_num,
			"title": ch["title"],
			"prev": prev_num,
			"next": next_num
		})

		chapter_payload = {
			"num": current_num,
			"title": ch["title"],
			"paragraphs": ch["paragraphs"],
			"prev": prev_num,
			"next": next_num
		}

		chapter_filename = os.path.join(chapters_dir, f"chapter_{current_num}.json")
		with open(chapter_filename, "w", encoding="utf-8") as json_file:
			json.dump(chapter_payload, json_file, ensure_ascii=False)

	toc_payload = {
		"title": book_title,
		"subtitles": subtitles,
		"chapters": toc_chapters
	}

	with open(os.path.join(output_dir, "toc.json"), "w", encoding="utf-8") as toc_file:
		json.dump(toc_payload, toc_file, ensure_ascii=False)

	if os.path.exists("static"):
		shutil.copytree("static", output_dir, dirs_exist_ok=True)

	print(f"Successfully generated site in the '{output_dir}' directory.")

if __name__ == "__main__":
	generate_html_site("_processed_book.txt")
