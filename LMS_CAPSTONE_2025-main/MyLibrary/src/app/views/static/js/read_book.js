document.addEventListener("DOMContentLoaded", function () {
    let rendition;

    if (typeof ePub === "undefined") {
        console.error("ePub.js is not loaded correctly.");
        return;
    }

    const container = document.getElementById("epub-container");
    const bookElement = document.getElementById("book");
    const epubUrl = bookElement.getAttribute("data-epub-url");

    if (epubUrl) {
        fetchEpub(epubUrl);
    }

    async function fetchEpub(url) {
        try {
            let response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

            let blob = await response.blob();
            console.log("Received EPUB Blob:", blob);

            let epubBlob = new Blob([blob], { type: "application/epub+zip" });
            let blobUrl = URL.createObjectURL(epubBlob);
            console.log("Created Blob URL:", blobUrl);

            const epubBook = ePub(blobUrl, { openAs: "epub" });
            console.log("EPUB Object Created:", epubBook);

            epubBook.ready
                .then(() => console.log("EPUB is ready!"))
                .catch(err => console.error("Error waiting for EPUB ready:", err));

            epubBook.opened
                .then(() => console.log("EPUB fully opened!"))
                .catch(err => console.error("Error waiting for EPUB opened:", err));

            rendition = epubBook.renderTo("epub-container", {
                width: "100%",
                height: "100%"
            });
            rendition.display();

        } catch (error) {
            console.error("Error fetching EPUB:", error);
        }
    }

    document.getElementById("prev").addEventListener("click", () => {
        if (rendition) rendition.prev();
    });

    document.getElementById("next").addEventListener("click", () => {
        if (rendition) rendition.next();
    });
});
