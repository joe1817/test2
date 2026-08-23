import os
import re
import json

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

	chapters_dict = {}
	total_chapters = len(chapter_data)
	for index, ch in enumerate(chapter_data):
		current_num = ch["num"]
		prev_num = chapter_data[index - 1]["num"] if index > 0 else None
		next_num = chapter_data[index + 1]["num"] if index < total_chapters - 1 else None

		chapters_dict[current_num] = {
			"num": current_num,
			"title": ch["title"],
			"paragraphs": ch["paragraphs"],
			"prev": prev_num,
			"next": next_num
		}

	chapters_json = json.dumps(chapters_dict, ensure_ascii=False)

	site_css = """* { box-sizing: border-box; }
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

	.letterbox-top, .letterbox-bottom {
		display: none;
		position: fixed;
		left: 0;
		width: 100%;
		background-color: #181818;
		z-index: 100;
	}
	.letterbox-top {
		height: env(safe-area-inset-top, 0px);
		top: 0;
	}
	.letterbox-bottom {
		height: env(safe-area-inset-bottom, 0px);
		bottom: 0;
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
	}

	.main-wrapper {
		max-width: 800px;
		margin: 0 auto;
		padding: 40px 20px 40px 20px;
	}

	body.mobile-fullscreen .letterbox-top,
	body.mobile-fullscreen .letterbox-bottom {
		display: block;
	}
	body.mobile-fullscreen .progress-bar {
		top: env(safe-area-inset-top, 0px);
	}
	body.mobile-fullscreen .main-wrapper {
		padding: calc(env(safe-area-inset-top, 0px) + 40px) 20px calc(env(safe-area-inset-bottom, 0px) + 40px) 20px;
	}

	.book-title {
		font-family: "Georgia", "Cambria", "Times New Roman", serif;
		color: #ffffff;
		text-align: center;
		font-size: 2.5rem;
		margin-top: 20px;
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
		cursor: pointer;
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
		margin-top: 30px;
	}
	a {
		color: #4863a0;
		text-decoration: none;
		cursor: pointer;
	}
	.chapter-view {
		display: none;
	}
	.chapter-view.active {
		display: block;
	}
	h1.chapter-heading {
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
	.toolbar:first-of-type {
		margin-bottom: 30px;
	}
	.toolbar:not(:first-of-type) {
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

	.drawer {
		position: fixed;
		top: calc(env(safe-area-inset-top, 0px) + 140px);
		right: -80px;
		width: 80px;
		height: fit-content;
		background-color: #181818;
		border: 1px solid #333333;
		border-top-left-radius: 8px;
		border-bottom-left-radius: 8px;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 20px 0;
		gap: 16px;
		z-index: 102;
		transition: right 0.3s ease-in-out;
	}
	.drawer.open {
		right: 0;
	}
	.drawer-btn {
		background-color: #2a2a2a;
		color: #4863a0;
		border: 1px solid #444444;
		width: 48px;
		height: 48px;
		border-radius: 6px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		text-decoration: none;
		font-size: 1.1rem;
		transition: background 0.2s, border-color 0.2s, color 0.2s;
	}
	.drawer-btn:hover {
		background-color: #333333;
		border-color: #4863a0;
		color: #ffffff;
	}
	.drawer-btn.disabled {
		color: #555555;
		pointer-events: none;
		background-color: #161616;
		border-color: #222222;
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
	with open(os.path.join(output_dir, "styles", "index.css"), "w", encoding="utf-8") as f:
		f.write(site_css)

	index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>{book_title}</title>
	<link rel="stylesheet" href="styles/index.css">
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap">
</head>
<body>
	<div class="letterbox-top"></div>
	<div class="letterbox-bottom"></div>
	<div class="progress-bar" id="progressBar"></div>

	<div class="drawer" id="sideDrawer" onclick="event.stopPropagation()">
		<button class="drawer-btn" onclick="goHome()" title="Go Home">
			<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
				<polyline points="9 22 9 12 15 12 15 22"/>
			</svg>
		</button>
		<button class="drawer-btn" id="drawerPrev" title="Prev Chapter">&#9664;</button>
		<button class="drawer-btn" id="drawerNext" title="Next Chapter">&#9654;</button>
		<button class="drawer-btn" onclick="toggleFullScreen()" title="Full Screen">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M8 3H5a2 2 0 0 0-2 2v3" />
				<path d="M21 8V5a2 2 0 0 0-2-2h-3" />
				<path d="M3 16v3a2 2 0 0 0 2 2h3" />
				<path d="M16 21h3a2 2 0 0 0 2-2v-3" />
			</svg>
		</button>
	</div>

	<div class="main-wrapper">
		<div id="home-view">
			<h1 class="book-title">{book_title}</h1>

			<div class="chapter-grid">
"""

	for ch in chapter_data:
		index_html += f'                <a onclick="loadChapter({ch["num"]})" class="chapter-box" data-chapter="{ch["num"]}">Ch. {ch["num"]}</a>\n'

	index_html += f"""            </div>

			<div class="reset-container">
				<button id="reset-progress-btn" onclick="resetProgress()">Reset Reading Progress</button>
			</div>

			<p class="github-link"><a href="https://github.com/joe1817/test2">Github</a></p>
		</div>

		<div id="chapter-container" class="chapter-view"></div>
	</div>

	<script>
		const bookData = {chapters_json};

		document.addEventListener("DOMContentLoaded", () => {{
			loadProgress();

			window.addEventListener("popstate", (event) => {{
				if (event.state && event.state.chapter) {{
					renderChapter(event.state.chapter, false);
				}} else {{
					renderHome(false);
				}}
			}});

			const hash = window.location.hash;
			if (hash.startsWith("#chapter-")) {{
				const chNum = parseInt(hash.replace("#chapter-", ""));
				if (bookData[chNum]) {{
					renderChapter(chNum, false);
				}}
			}}

			window.addEventListener("scroll", () => {{
				updateProgress();
			}});

			document.addEventListener("click", (event) => {{
				const drawer = document.getElementById("sideDrawer");
				if (event.target.closest("button") || event.target.closest("a") || event.target.closest(".drawer")) {{
					drawer.classList.remove("open");
				}} else {{
					drawer.classList.toggle("open");
				}}
			}});

			document.addEventListener("scroll", (event) => {{
				const drawer = document.getElementById("sideDrawer");
				drawer.classList.remove("open");
			}});

			document.addEventListener("fullscreenchange", () => {{
				const isMobile = /Mobi|Android|iPhone/i.test(navigator.userAgent);
				if (document.fullscreenElement && isMobile) {{
					document.body.classList.add("mobile-fullscreen");
				}} else {{
					document.body.classList.remove("mobile-fullscreen");
				}}
				updateProgress();
			}});
		}});

		function toggleFullScreen() {{
			if (!document.fullscreenElement) {{
				document.documentElement.requestFullscreen().catch((err) => {{
					console.error("Error attempting to enable full-screen mode:", err.message);
				}});
			}} else {{
				if (document.exitFullscreen) {{
					document.exitFullscreen();
				}}
			}}
		}}

		function loadChapter(chNum) {{
			renderChapter(chNum, true);
		}}

		function goHome() {{
			renderHome(true);
			const drawer = document.getElementById("sideDrawer");
			drawer.classList.remove("open");
		}}

		function renderHome(pushHistory = true) {{
			if (pushHistory) {{
				history.pushState({{ chapter: null }}, "", window.location.pathname);
			}}
			document.getElementById("chapter-container").classList.remove("active");
			document.getElementById("home-view").style.display = "block";
			window.scrollTo(0, 0);
			updateProgress();
			loadProgress();
		}}

		function renderChapter(chNum, pushHistory = true) {{
			const ch = bookData[chNum];
			if (!ch) return;

			if (pushHistory) {{
				history.pushState({{ chapter: chNum }}, "", `#chapter-${{chNum}}`);
			}}

			const prevLink = ch.prev !== null ? `onclick="loadChapter(${{ch.prev}})"` : `class="btn-link disabled"`;
			const nextLink = ch.next !== null ? `onclick="loadChapter(${{ch.next}})"` : `class="btn-link disabled"`;
			const prevLabel = ch.prev !== null ? `Ch. ${{ch.prev}}` : "Ch. —";
			const nextLabel = ch.next !== null ? `Ch. ${{ch.next}}` : "Ch. —";

			const drawerPrevBtn = document.getElementById("drawerPrev");
			const drawerNextBtn = document.getElementById("drawerNext");

			if (ch.prev !== null) {{
				drawerPrevBtn.setAttribute("onclick", `loadChapter(${{ch.prev}}); document.getElementById("sideDrawer").classList.remove("open");`);
				drawerPrevBtn.classList.remove("disabled");
			}} else {{
				drawerPrevBtn.removeAttribute("onclick");
				drawerPrevBtn.classList.add("disabled");
			}}

			if (ch.next !== null) {{
				drawerNextBtn.setAttribute("onclick", `loadChapter(${{ch.next}}); document.getElementById("sideDrawer").classList.remove("open");`);
				drawerNextBtn.classList.remove("disabled");
			}} else {{
				drawerNextBtn.removeAttribute("onclick");
				drawerNextBtn.classList.add("disabled");
			}}

			let paragraphsHtml = "";
			ch.paragraphs.forEach(p => {{
				paragraphsHtml += `<p>${{p}}</p>`;
			}});

			const toolbarHtml = `
				<div class="toolbar">
					<div class="toolbar-group">
						<a class="btn-link" onclick="goHome()">Home</a>
					</div>
					<div class="toolbar-group">
						<a class="btn-link ${{ch.prev !== null ? '' : 'disabled'}}" ${{prevLink}}>&larr; ${{prevLabel}}</a>
						<a class="btn-link ${{ch.next !== null ? '' : 'disabled'}}" ${{nextLink}}>${{nextLabel}} &rarr;</a>
					</div>
				</div>
			`;

			const container = document.getElementById("chapter-container");
			container.innerHTML = `
				${{toolbarHtml}}
				<p class="chapter-num">Chapter ${{ch.num}}</p>
				<h1 class="chapter-heading">${{ch.title}}</h1>
				${{paragraphsHtml}}
				${{toolbarHtml}}
			`;

			document.getElementById("home-view").style.display = "none";
			container.classList.add("active");
			window.scrollTo(0, 0);

			recordChapterView(ch.num);
			updateProgress();
		}}

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
			document.cookie = "reading_history=" + encodeURIComponent(JSON.stringify(history)) + ";expires=" + d.toUTCString() + ";path=/;";
			loadProgress();
		}}

		function loadProgress() {{
			document.querySelectorAll(".chapter-box").forEach(box => {{
				box.classList.remove("viewed", "latest-viewed");
			}});

			const historyCookie = getCookie("reading_history");
			if (historyCookie) {{
				try {{
					const history = JSON.parse(decodeURIComponent(historyCookie));
					if (Array.isArray(history) && history.length > 0) {{
						const latest = history[history.length - 1];

						history.forEach(chNum => {{
							const box = document.querySelector(`.chapter-box[data-chapter="${{chNum}}"]`);
							if (box) {{
								if (chNum === latest) {{
									box.classList.add("latest-viewed");
								}} else {{
									box.classList.add("viewed");
								}}
							}}
						}});
					}}
				}} catch (e) {{
					console.error("Could not parse reading history cookie", e);
				}}
			}}
		}}

		function resetProgress() {{
			if (window.confirm("Are you sure you want to reset your reading progress?")) {{
				document.cookie = "reading_history=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;";
				loadProgress();
			}}
		}}

		function updateProgress() {{
			const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
			const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
			const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
			document.getElementById("progressBar").style.width = scrolled + "%";
		}}
	</script>
</body>
</html>
"""

	with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
		f.write(index_html)

	with open(os.path.join(output_dir, ".nojekyll"), "a") as f:
		pass

	print(f"Successfully generated single-page HTML site in the '{output_dir}' directory.")

if __name__ == "__main__":
	generate_html_site("_processed_book.txt")
