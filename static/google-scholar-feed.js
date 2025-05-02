document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("scholar-form");
    const newsContainer = document.getElementById("news-feed");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const apiKey = "e0100edc7eec7c730ab914cb6f2050e251ed0c270a5b8060dbbc22519d22ee8c"; // Replace this
        // QUERY THE API
        const query = document.getElementById("query").value.trim();
        // YEAR LOW
        const as_ylo = document.getElementById("from-year").value;
        // YEAR HIGH
        const as_yhi = document.getElementById("to-year").value;

        let url = `/api/scholar?q=${encodeURIComponent(query)}&as_ylo=${as_ylo}&as_yhi=${as_yhi}`;


        if (as_ylo) url += `&as_ylo=${as_ylo}`;
        if (as_yhi) url += `&as_yhi=${as_yhi}`;

        // IF all that, then inject the content into container
        newsContainer.innerHTML = "<p>Loading articles...</p>";

        try {
            const response = await fetch(url);
            const data = await response.json();

            newsContainer.innerHTML = "";

            if (data.organic_results && data.organic_results.length > 0) {
                data.organic_results.forEach(result => {
                    const card = document.createElement("div");
                    // identifier for specific card
                    card.className = "mb-4";
                   // IF all that, then inject the content into container
                    card.innerHTML = `
                        <h6><a href="${result.link}" target="_blank" class="text-decoration-none">${result.title}</a></h6>
                        <p class="small text-muted">${result.publication || "Unknown Source"}</p>
                        <p class="small">${result.snippet || ""}</p>
                    `;
                    newsContainer.appendChild(card);
                });
            } else {
                newsContainer.innerHTML = "<p>No scholarly articles found.</p>";
            }
        } catch (err) {
            console.error("API error:", err);
            newsContainer.innerHTML = "<p>Error loading articles. Please try again later.</p>";
        }
    });
});
