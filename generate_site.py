import os
import re
import json
import shutil
import subprocess

def slugify(text):
	return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def process_book(input_filename, output_dir):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	book_data_dir = os.path.join(output_dir, "data")
	if not os.path.exists(book_data_dir):
		os.makedirs(book_data_dir)

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
	active_chapter_date = None
	active_paragraphs = []

	chapter_pattern = re.compile(r"^Chapter\s+(\d+)\s*-\s*(.+?)(\s*\[(.+)\])?$", re.IGNORECASE)

	for line in lines:
		match = chapter_pattern.match(line)
		if match:
			if active_chapter_num is not None:
				chapter_data.append({
					"num": active_chapter_num,
					"title": active_chapter_title,
					"date": active_chapter_date,
					"paragraphs": active_paragraphs,
				})
				active_paragraphs = []
			active_chapter_num = int(match.group(1))
			active_chapter_title = match.group(2)
			active_chapter_date = match.group(4)
		else:
			if active_chapter_num is None:
				book_title_data.append(line)
			else:
				active_paragraphs.append(line)

	if active_chapter_num is not None:
		chapter_data.append({
			"num": active_chapter_num,
			"title": active_chapter_title,
			"date": active_chapter_date,
			"paragraphs": active_paragraphs,
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
	book_slug = os.path.splitext(os.path.basename(input_filename))[0]

	specific_book_dir = os.path.join(book_data_dir, book_slug)
	if not os.path.exists(specific_book_dir):
		os.makedirs(specific_book_dir)

	toc_chapters = []
	for index, ch in enumerate(chapter_data):
		current_num = ch["num"]
		prev_num = chapter_data[index - 1]["num"] if index > 0 else None
		next_num = chapter_data[index + 1]["num"] if index < total_chapters - 1 else None

		toc_chapters.append({
			"num": current_num,
			"title": ch["title"],
			"date": ch["date"],
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

		chapter_filename = os.path.join(specific_book_dir, f"chapter_{current_num}.json")
		with open(chapter_filename, "w", encoding="utf-8") as json_file:
			json.dump(chapter_payload, json_file, ensure_ascii=False)

	toc_payload = {
		"title": book_title,
		"slug": book_slug,
		"subtitles": subtitles,
		"chapters": toc_chapters
	}

	with open(os.path.join(specific_book_dir, "toc.json"), "w", encoding="utf-8") as toc_file:
		json.dump(toc_payload, toc_file, ensure_ascii=False)

	catalog_path = os.path.join(book_data_dir, "catalog.json")
	catalog = []
	if os.path.exists(catalog_path):
		with open(catalog_path, "r", encoding="utf-8") as cat_file:
			try:
				catalog = json.load(cat_file)
			except json.JSONDecodeError:
				catalog = []

	if not any(b["slug"] == book_slug for b in catalog):
		catalog.append({"title": book_title, "slug": book_slug})
		with open(catalog_path, "w", encoding="utf-8") as cat_file:
			json.dump(catalog, cat_file, ensure_ascii=False)

def main():
	static_dir = "static"
	output_dir = "docs"
	books_dir = "books"
	process_dir = "post-process"
	
	preprocessors = os.listdir(process_dir)
	
	for book in sorted(os.listdir(books_dir)):
		book_slug = os.path.splitext(book)[0]
		book_path = os.path.join(books_dir, book)
		processor_path = os.path.join(process_dir, f"{book_slug}.py")
		data_path = os.path.join(process_dir, f"{book_slug}.dat")
		tmp_path = os.path.join(process_dir, "_tmp", f"{book_slug}.tmp")
		
		print(f"Processing {book_slug}")
		
		if os.path.isfile(processor_path):
			os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
			if os.path.isfile(data_path):
				subprocess.run(["python", processor_path, book_path, data_path, tmp_path])
				process_book(tmp_path, output_dir)
			else:
				subprocess.run(["python", processor_path, book_path, tmp_path])
				process_book(tmp_path, output_dir)
			os.remove(tmp_path)
		else:
			process_book(book_path, output_dir)

	if os.path.exists(static_dir):
		shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)

	print(f"Successfully generated site in the '{output_dir}' directory.")

if __name__ == "__main__":
	main()
