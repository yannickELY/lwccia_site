// --- Lecteur audio ---

const player = document.getElementById("audio-player");
let currentBtn = null;

document.querySelectorAll(".play-btn").forEach(btn => {
    btn.addEventListener("click", function() {
        const src = this.dataset.src;

        if (currentBtn && currentBtn !== this) {
            currentBtn.textContent = "▶";
            currentBtn.classList.remove("playing");
        }

        if (player.src.endsWith(src) && !player.paused) {
            player.pause();
            this.textContent = "▶";
            this.classList.remove("playing");
        } else {
            player.src = src;
            player.play();
            this.textContent = "■";
            this.classList.add("playing");
            currentBtn = this;
        }
    });
});

// --- Filtres ---

const genreSelect = document.getElementById("genre-select");
const bpmSelect = document.getElementById("bpm-select");
const prodItems = document.querySelectorAll(".prod-item");

let activeGenre = "all";
let activeBpm = "all";

function filterProds() {
    prodItems.forEach(item => {
        const genre = item.dataset.genre;
        const bpm = parseInt(item.dataset.bpm);

        const genreMatch = activeGenre === "all" || genre === activeGenre;

        let bpmMatch = true;
        if (activeBpm === "hundred_less") bpmMatch = bpm < 100;
        else if (activeBpm === "hundred") bpmMatch = bpm >= 100 && bpm < 110;
        else if (activeBpm === "hundred_ten") bpmMatch = bpm >= 110 && bpm < 120;
        else if (activeBpm === "hundred_twenty") bpmMatch = bpm >= 120 && bpm < 130;
        else if (activeBpm === "hundred_thirty") bpmMatch = bpm >= 130 && bpm < 140;
        else if (activeBpm === "hundred_forty") bpmMatch = bpm >= 140 && bpm < 150;
        else if (activeBpm === "hundred_fifty") bpmMatch = bpm >= 150 && bpm < 160;
        else if (activeBpm === "hundred_sixty") bpmMatch = bpm >= 160 && bpm < 170;
        else if (activeBpm === "hundred_seventy") bpmMatch = bpm >= 170 && bpm < 180;
        else if (activeBpm === "hundred_more") bpmMatch = bpm >= 180;

        if (genreMatch && bpmMatch) {
            item.classList.remove("hidden");
        } else {
            item.classList.add("hidden");
        }
    });
}

genreSelect.addEventListener("change", function() {
    activeGenre = this.value;
    filterProds();
});

bpmSelect.addEventListener("change", function() {
    activeBpm = this.value;
    filterProds();
});
