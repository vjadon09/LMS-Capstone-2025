document.addEventListener("DOMContentLoaded", function () {
    const audioPlayer = document.getElementById("audio-player");
    const container = document.getElementById("container");

    const bookElement = document.getElementById("book");
    const audiobookUrl = bookElement.getAttribute("data-audio-url");

    if (audiobookUrl) {
        loadAudio(audiobookUrl);
    }

    // Function to fetch and load the audiobook file into the audio player
    async function loadAudio(url) {
        try {
            let response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            container.innerText = "Loading audiobook...";

            let audioBlob = await response.blob();
            let audioUrl = URL.createObjectURL(audioBlob);
            audioPlayer.src = audioUrl;

            // Once the audio is loaded, set the container text to empty
            audioPlayer.oncanplaythrough = () => {
                container.innerText = "";
            };

            console.log("Audiobook loaded and ready to play!");

        } catch (error) {
            console.error("Error fetching audiobook:", error);
        }
    }
});
