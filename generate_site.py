import os
import re

def generate_html_site(input_filename, output_dir="docs"):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	with open(input_filename, "r", encoding="utf-8") as file:
		lines = [line.strip() for line in file if line.strip()]

	if not lines:
		print("The input file is empty.")
		return

	book_title = lines[0]
	chapter_data = []
	active_chapter_num = None
	active_chapter_title = None
	active_paragraphs = []

	chapter_pattern = re.compile(r"^Chapter\s+(\d+)\s*-\s*(.+)$", re.IGNORECASE)

	idx = 1
	while idx < len(lines):
		line = lines[idx]
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
			if active_chapter_num is not None:
				active_paragraphs.append(line)
		idx += 1

	if active_chapter_num is not None:
		chapter_data.append({
			"num": active_chapter_num,
			"title": active_chapter_title,
			"paragraphs": active_paragraphs
		})

	if not chapter_data:
		print("No chapters found in the specified format.")
		return

	index_css = """body {
		background-color: #121212;
		color: #e0e0e0;
		font-family: sans-serif;
		max-width: 800px;
		margin: 40px auto;
		padding: 0 20px;
		line-height: 1.6;
	}
	h1 {
		font-family: "Georgia", "Cambria", "Times New Roman", serif;
		color: #ffffff;
		text-align: center;
	}
	.chapter-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
		gap: 12px;
		padding: 20px 0;
	}
	.chapter-box {
		background: #1e1e1e;
		color: #4863a0;
		border: 1px solid #333333;
		padding: 15px 10px;
		border-radius: 5px;
		text-align: center;
		text-decoration: none;
		font-weight: bold;
		font-size: 1rem;
		transition: background 0.2s, border-color 0.2s;
	}
	.chapter-box:hover {
		background: #2a2a2a;
		border-color: #4863a0;
	}
	.chapter-box.viewed {
		background: #252b3b;
		color: #7b9ad7;
		border-color: #3b5080;
	}
	.chapter-box.latest-viewed {
		background: #344a7c;
		color: #ffffff;
		border-color: #6a8cdb;
		box-shadow: 0 0 8px rgba(106, 140, 219, 0.4);
	}
	.reset-container {
		text-align: center;
		margin: 40px 0 20px 0;
	}
	#reset-progress-btn {
		background-color: #1e1e1e;
		color: #a04848;
		border: 1px solid #443333;
		padding: 10px 20px;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: background 0.2s, border-color 0.2s;
	}
	#reset-progress-btn:hover {
		background-color: #2a1e1e;
		border-color: #a04848;
	}
	.github-link {
		text-align: center;
	}
	a {
		color: #4863a0;
		text-decoration: none;
	}
"""

	chapter_css = """* { box-sizing: border-box; }
	html {
		background-color: #121212;
		color: #e0e0e0;
		font-family: sans-serif;
		height: 100vh;
		overflow-y: auto;
		scrollbar-gutter: stable;
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
	html::-webkit-scrollbar {
		display: none;
	}
	body {
		background-color: #121212;
		color: #e0e0e0;
		font-family: 'Inter', sans-serif;
		margin: 0;
		padding: 0;
		min-height: 100vh;
		overflow-x: hidden;
	}
	#content-container {
		max-width: 800px;
		margin: 0 auto;
		padding: 40px 20px 60px 20px;
		display: flex;
		flex-direction: column;
		justify-content: flex-start;
		min-height: 100vh;
	}
	h1 {
		font-family: "Georgia", "Cambria", "Times New Roman", serif;
		color: #ffffff;
		margin-top: 0;
		margin-bottom: 30px;
		text-align: center;
	}
	.chapter-num {
		font-size: 16px;
		color: #ffffff;
		margin-top: 0;
		margin-bottom: 10px;
		text-align: center;
	}
	p {
		margin-top: 0;
		margin-bottom: 20px;
		text-align: justify;
		line-height: 1.8;
	}
	.toolbar {
		width: 100%;
		background-color: #1e1e1e;
		border: 1px solid #333333;
		border-radius: 6px;
		padding: 14px 18px;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.toolbar.top-toolbar {
		margin-bottom: 30px;
	}
	.toolbar.bottom-toolbar {
		margin-top: 40px;
	}
	.toolbar-group {
		display: flex;
		gap: 12px;
		align-items: center;
	}
	.btn-link {
		background-color: #2a2a2a;
		color: #4863a0;
		border: 1px solid #444444;
		padding: 10px 14px;
		border-radius: 6px;
		cursor: pointer;
		text-decoration: none;
		font-size: 1rem;
	}
	.btn-link:hover {
		background-color: #333333;
	}
	.btn-link.disabled {
		color: #555555;
		pointer-events: none;
		background-color: #161616;
		border-color: #222222;
	}
	.progress-bar {
		position: fixed;
		top: 0;
		left: 0;
		height: 3px;
		background-color: #4863a0;
		width: 0%;
		z-index: 101;
		transform-origin: left;
		transition: width 0.1s ease-out;
	}
	.progress-bar.no-transition {
		transition: none;
	}

	@media (min-width: 768px) {
		.toolbar {
			padding: 16px 24px;
		}
		.btn-link {
			padding: 12px 18px;
			font-size: 1.05rem;
		}
	}
"""

	os.makedirs(os.path.join(output_dir, "styles"), exist_ok=True)
	with open(os.path.join(output_dir, "styles", "chapter.css"), "w", encoding="utf-8") as f:
		f.write(chapter_css)
	with open(os.path.join(output_dir, "styles", "index.css"), "w", encoding="utf-8") as f:
		f.write(index_css)

	total_chapters = len(chapter_data)

	for index, ch in enumerate(chapter_data):
		current_num = ch["num"]
		filename = f"chapter_{current_num}.html"

		prev_num = chapter_data[index - 1]["num"] if index > 0 else None
		next_num = chapter_data[index + 1]["num"] if index < total_chapters - 1 else None

		prev_link = f"chapter_{prev_num}.html" if prev_num is not None else "#"
		next_link = f"chapter_{next_num}.html" if next_num is not None else "#"

		prev_ch_label = f"Ch. {prev_num}" if prev_num is not None else "Ch. —"
		next_ch_label = f"Ch. {next_num}" if next_num is not None else "Ch. —"

		paragraphs_html = "".join([f"<p>{p}</p>" for p in ch["paragraphs"]])

		chapter_js_content = f"""
const currentChapterNum = {current_num};

window.addEventListener("DOMContentLoaded", () => {{
	recordChapterView(currentChapterNum);
	updateProgress();

	window.addEventListener("scroll", () => {{
		updateProgress();
	}});
}});

function getCookie(name) {{
	const value = `; ${{document.cookie}}`;
	const parts = value.split(`; ${{name}}=`);
	if (parts.length === 2) return parts.pop().split(";").shift();
	return "";
}}

function recordChapterView(chNum) {{
	let history = [];
	const cookieVal = getCookie("reading_history");
	if (cookieVal) {{
		try {{
			history = JSON.parse(decodeURIComponent(cookieVal));
		}} catch(e) {{
			history = [];
		}}
	}}
	history = history.filter(num => num !== chNum);
	history.push(chNum);
	const d = new Date();
	d.setTime(d.getTime() + (365*24*60*60*1000));
	document.cookie = "reading_history=" + encodeURIComponent(JSON.stringify(history)) + ";expires=" + d.toUTCString() + ";path=/";
}}

function updateProgress() {{
	const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
	const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
	const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
	document.getElementById("progressBar").style.width = scrolled + "%";
}}
"""

		chapter_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>{ch["title"]} - {book_title}</title>
	<link rel="stylesheet" href="styles/chapter.css">
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap">
</head>
<body>
	<div class="progress-bar no-transition" id="progressBar"></div>

	<div id="content-container">
		<div class="toolbar top-toolbar">
			<div class="toolbar-group">
				<a class="btn-link" href="index.html">Home</a>
			</div>
			<div class="toolbar-group">
				<a class="btn-link {'' if prev_num is not None else 'disabled'}" href="{prev_link}">&larr; {prev_ch_label}</a>
				<a class="btn-link {'' if next_num is not None else 'disabled'}" href="{next_link}">{next_ch_label} &rarr;</a>
			</div>
		</div>

		<p class="chapter-num">Chapter {ch["num"]}</p>
		<h1 id="chapter-title">{ch["title"]}</h1>
		{paragraphs_html}

		<div class="toolbar bottom-toolbar">
			<div class="toolbar-group">
				<a class="btn-link" href="index.html">Home</a>
			</div>
			<div class="toolbar-group">
				<a class="btn-link {'' if prev_num is not None else 'disabled'}" href="{prev_link}">&larr; {prev_ch_label}</a>
				<a class="btn-link {'' if next_num is not None else 'disabled'}" href="{next_link}">{next_ch_label} &rarr;</a>
			</div>
		</div>
	</div>

	<script>
	{chapter_js_content}
	</script>
	<script>
		window.addEventListener("load", () => {{
			setTimeout(() => {{
				document.getElementById("progressBar").classList.remove("no-transition");
			}}, 50);
		}});
	</script>
</body>
</html>
"""

		with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
			f.write(chapter_html)

	index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>{book_title}</title>
	<link rel="stylesheet" href="styles/index.css">
</head>
<body>
	<h1>{book_title}</h1>
	<div class="chapter-grid">
"""

	for ch in chapter_data:
		filename = f"chapter_{ch['num']}.html"
		index_html += f'        <a href="{filename}" class="chapter-box" data-chapter="{ch["num"]}">Ch. {ch["num"]}</a>\n'

	index_html += """    </div>

	<div class="reset-container">
		<button id="reset-progress-btn" onclick="resetProgress()">Reset Reading Progress</button>
	</div>
	<p class="github-link"><a href="https://github.com/joe1817/test2">Github</a></p>

	<script>
		document.addEventListener("DOMContentLoaded", () => {
			loadProgress();
		});

		function getCookie(name) {
			const value = `; ${document.cookie}`;
			const parts = value.split(`; ${name}=`);
			if (parts.length === 2) return parts.pop().split(";").shift();
			return "";
		}

		function loadProgress() {
			document.querySelectorAll(".chapter-box").forEach(box => {
				box.classList.remove("viewed", "latest-viewed");
			});

			const historyCookie = getCookie("reading_history");
			if (historyCookie) {
				try {
					const history = JSON.parse(decodeURIComponent(historyCookie));
					if (Array.isArray(history) && history.length > 0) {
						const latest = history[history.length - 1];

						history.forEach(chNum => {
							const box = document.querySelector(`.chapter-box[data-chapter="${chNum}"]`);
							if (box) {
								if (chNum === latest) {
									box.classList.add("latest-viewed");
								} else {
									box.classList.add("viewed");
								}
							}
						});
					}
				} catch (e) {
					console.error("Could not parse reading history cookie", e);
				}
			}
		}

		function resetProgress() {
			if (window.confirm("Are you sure you want to reset your reading progress?")) {
				document.cookie = "reading_history=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;";
				loadProgress();
			}
		}
	</script>
</body>
</html>
"""

	with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
		f.write(index_html)

	with open(os.path.join(output_dir, ".nojekyll"), "a") as f:
		pass

	print(f"Successfully generated HTML site in the '{output_dir}' directory.")

if __name__ == "__main__":
	generate_html_site("_processed_book.txt")
