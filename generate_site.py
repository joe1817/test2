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
	total_chapters = len(chapter_data)

	for index, ch in enumerate(chapter_data):
		current_num = ch["num"]
		prev_num = chapter_data[index - 1]["num"] if index > 0 else None
		next_num = chapter_data[index + 1]["num"] if index < total_chapters - 1 else None

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

	index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>{book_title}</title>
	<link rel="stylesheet" href="styles/index.css">
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap">
	<link rel="icon" type="image/x-icon" href="favicon.ico">
	<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">
	<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
	<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
	<link rel="manifest" href="site.webmanifest">
</head>
<body>
	<div id="fade-overlay" class="active"></div>

	<div class="letterbox-top"></div>
	<div class="letterbox-bottom"></div>
	<div class="progress-bar" id="progressBar"></div>

	<div class="drawer" id="sideDrawer" onclick="event.stopPropagation()">
		<button class="drawer-btn hidden" id="drawerHome" onclick="renderHome()" title="Go Home">
			<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
				<polyline points="9 22 9 12 15 12 15 22"/>
			</svg>
		</button>
		<button class="drawer-btn hidden" id="drawerPrev" title="Prev Chapter">&#9664;</button>
		<button class="drawer-btn hidden" id="drawerNext" title="Next Chapter">&#9654;</button>
		<button class="drawer-btn" onclick="toggleFullScreenWithFade()" title="Full Screen">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M8 3H5a2 2 0 0 0-2 2v3" />
				<path d="M21 8V5a2 2 0 0 0-2-2h-3" />
				<path d="M3 16v3a2 2 0 0 0 2 2h3" />
				<path d="M16 21h3a2 2 0 0 0 2-2v-3" />
			</svg>
		</button>
		<button class="drawer-btn danger" id="drawerReset" onclick="resetProgress()" title="Reset Progress">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
				<path d="M3 3v5h5"/>
			</svg>
		</button>
		<a href="https://github.com/joe1817/test2" class="drawer-btn" id="drawerGithub" title="Github Repo">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
				<path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
			</svg>
		</a>
	</div>

	<div class="main-wrapper">
		<div id="home-view">
			<h1 class="book-title">{book_title}</h1>
"""

	for subtitle in book_title_data[1:]:
		index_html += f'			<h2 class="book-subtitle">{subtitle}</h2>\n'

	index_html += f'			<div class="chapter-grid">\n'

	for ch in chapter_data:
		index_html += f'                <a onclick="loadChapter({ch["num"]})" class="chapter-box" data-chapter="{ch["num"]}">Ch. {ch["num"]}</a>\n'

	index_html += """            </div>
		</div>

		<div id="chapter-container" class="chapter-view"></div>
	</div>

	<script src="scripts/index.js"></script>
</body>
</html>
"""

	with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
		f.write(index_html)

	shutil.copytree("static", output_dir, dirs_exist_ok=True)

	print(f"Successfully generated single-page HTML site in the '{output_dir}' directory.")

if __name__ == "__main__":
	generate_html_site("_processed_book.txt")
