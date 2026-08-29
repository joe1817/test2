document.addEventListener("DOMContentLoaded", () => {
	loadProgress();

	window.addEventListener("popstate", (event) => {
		if (event.state && event.state.chapter) {
			fetchAndRenderChapter(event.state.chapter, false);
		} else {
			renderHome(false);
		}
	});

	const hash = window.location.hash;
	if (hash.startsWith("#chapter-")) {
		const chNum = parseInt(hash.replace("#chapter-", ""));
		if (!isNaN(chNum)) {
			fetchAndRenderChapter(chNum, false).then(() => {
				document.getElementById("fade-overlay").classList.remove("active");
			});
		}
	} else {
		document.getElementById("fade-overlay").classList.remove("active");
	}

	window.addEventListener("scroll", () => {
		updateProgress();
	});

	document.addEventListener("click", (event) => {
		const drawer = document.getElementById("sideDrawer");
		if (event.target.closest("button") || event.target.closest("a") || event.target.closest(".drawer")) {
			drawer.classList.remove("open");
		} else {
			drawer.classList.toggle("open");
		}
	});

	document.addEventListener("scroll", (event) => {
		const drawer = document.getElementById("sideDrawer");
		drawer.classList.remove("open");
	});

	document.addEventListener("fullscreenchange", () => {
		const isMobile = /Mobi|Android|iPhone/i.test(navigator.userAgent);
		if (document.fullscreenElement && isMobile) {
			document.body.classList.add("mobile-fullscreen");
		} else {
			document.body.classList.remove("mobile-fullscreen");
		}
		updateProgress();
	});
});

function toggleFullScreenWithFade() {
	const isMobile = /Mobi|Android|iPhone/i.test(navigator.userAgent);
	if (isMobile) {
		const overlay = document.getElementById("fade-overlay");
		overlay.classList.add("active");
		setTimeout(() => {
			toggleFullScreen();
			setTimeout(() => {
				overlay.classList.remove("active");
			}, 150);
		}, 150)
	} else {
		toggleFullScreen();
	}
}

function toggleFullScreen() {
	if (!document.fullscreenElement) {
		document.documentElement.requestFullscreen().catch((err) => {
			console.error("Error attempting to enable full-screen mode:", err.message);
		});
	} else {
		if (document.exitFullscreen) {
			document.exitFullscreen();
		}
	}
}

function loadChapter(chNum) {
	fetchAndRenderChapter(chNum, true);
}

function renderHome(pushHistory = true) {
	if (pushHistory) {
		history.pushState({ chapter: null }, "", window.location.pathname);
	}

	const drawer = document.getElementById("sideDrawer");
	const delay = drawer.classList.contains("open") ? 300 : 0;
	drawer.classList.remove("open");

	setTimeout(() => {
		const drawerHomeBtn = document.getElementById("drawerHome");
		const drawerPrevBtn = document.getElementById("drawerPrev");
		const drawerNextBtn = document.getElementById("drawerNext");
		const drawerResetBtn = document.getElementById("drawerReset");
		const drawerGithubBtn = document.getElementById("drawerGithub");

		drawerPrevBtn.classList.remove("disabled");
		drawerNextBtn.classList.remove("disabled");
		drawerHomeBtn.classList.add("hidden");
		drawerPrevBtn.classList.add("hidden");
		drawerNextBtn.classList.add("hidden");
		drawerResetBtn.classList.remove("hidden");
		drawerGithubBtn.classList.remove("hidden");
	}, delay);

	document.getElementById("chapter-container").classList.remove("active");
	document.getElementById("home-view").style.display = "block";
	window.scrollTo(0, 0);
	updateProgress();
	loadProgress();
}

async function fetchAndRenderChapter(chNum, pushHistory = true) {
	try {
		const response = await fetch(`chapters/chapter_${chNum}.json`);
		if (!response.ok) throw new Error("Chapter file missing");
		const ch = await response.json();

		if (pushHistory) {
			history.pushState({ chapter: chNum }, "", `#chapter-${chNum}`);
		}

		const drawer = document.getElementById("sideDrawer");
		const delay = drawer.classList.contains("open") ? 300 : 0;
		drawer.classList.remove("open");

		setTimeout(() => {
			const drawerHomeBtn = document.getElementById("drawerHome");
			const drawerPrevBtn = document.getElementById("drawerPrev");
			const drawerNextBtn = document.getElementById("drawerNext");
			const drawerResetBtn = document.getElementById("drawerReset");
			const drawerGithubBtn = document.getElementById("drawerGithub");

			drawerHomeBtn.classList.remove("hidden");
			drawerPrevBtn.classList.remove("hidden");
			drawerNextBtn.classList.remove("hidden");
			drawerResetBtn.classList.add("hidden");
			drawerGithubBtn.classList.add("hidden");

			if (ch.prev !== null) {
				drawerPrevBtn.setAttribute("onclick", `loadChapter(${ch.prev}); document.getElementById("sideDrawer").classList.remove("open");`);
				drawerPrevBtn.classList.remove("disabled");
			} else {
				drawerPrevBtn.removeAttribute("onclick");
				drawerPrevBtn.classList.add("disabled");
			}

			if (ch.next !== null) {
				drawerNextBtn.setAttribute("onclick", `loadChapter(${ch.next}); document.getElementById("sideDrawer").classList.remove("open");`);
				drawerNextBtn.classList.remove("disabled");
			} else {
				drawerNextBtn.removeAttribute("onclick");
				drawerNextBtn.classList.add("disabled");
			}
		}, delay);

		const prevLink = ch.prev !== null ? `onclick="loadChapter(${ch.prev})"` : `class="btn-link disabled"`;
		const nextLink = ch.next !== null ? `onclick="loadChapter(${ch.next})"` : `class="btn-link disabled"`;
		const prevLabel = ch.prev !== null ? `Ch. ${ch.prev}` : "Ch. —";
		const nextLabel = ch.next !== null ? `Ch. ${ch.next}` : "Ch. —";

		const toolbarHtml = `
			<div class="toolbar">
				<div class="toolbar-group">
					<a class="btn-link" onclick="renderHome()">Home</a>
				</div>
				<div class="toolbar-group">
					<a class="btn-link ${ch.prev !== null ? '' : 'disabled'}" ${prevLink}>&larr; ${prevLabel}</a>
					<a class="btn-link ${ch.next !== null ? '' : 'disabled'}" ${nextLink}>${nextLabel} &rarr;</a>
				</div>
			</div>
		`;

		let paragraphsHtml = "";
		ch.paragraphs.forEach(p => {
			paragraphsHtml += `<p>${p}</p>`;
		});

		const container = document.getElementById("chapter-container");
		container.innerHTML = `
			${toolbarHtml}
			<p class="chapter-num">Chapter ${ch.num}</p>
			<h1 class="chapter-heading">${ch.title}</h1>
			${paragraphsHtml}
			${toolbarHtml}
		`;

		document.getElementById("home-view").style.display = "none";
		container.classList.add("active");
		window.scrollTo(0, 0);

		recordChapterView(ch.num);
		updateProgress();
	} catch (error) {
		console.error("Failed to load chapter:", error);
		renderHome(true);
	}
}

function getCookie(name) {
	const value = `; ${document.cookie}`;
	const parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(";").shift();
	return "";
}

function recordChapterView(chNum) {
	let history = [];
	const cookieVal = getCookie("reading_history");
	if (cookieVal) {
		try {
			history = JSON.parse(decodeURIComponent(cookieVal));
		} catch(e) {
			history = [];
		}
	}
	history = history.filter(num => num !== chNum);
	history.push(chNum);
	const d = new Date();
	d.setTime(d.getTime() + (365*24*60*60*1000));
	document.cookie = "reading_history=" + encodeURIComponent(JSON.stringify(history)) + ";expires=" + d.toUTCString() + ";path=/;";
	loadProgress();
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

function updateProgress() {
	const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
	const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
	const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
	document.getElementById("progressBar").style.width = scrolled + "%";
}
