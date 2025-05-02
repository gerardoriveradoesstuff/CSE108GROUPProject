document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("scholar-form");
    const newsContainer = document.getElementById("news-feed");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const apiKey = "YOUR_SERPAPI_API_KEY"; // Replace this
        const query = document.getElementById("query").value.trim();
        const as_ylo = document.getElementById("from-year").value;
        const as_yhi = document.getElementById("to-year").value;

        let url = `https://serpapi.com/search.json?engine=google_scholar&q=${encodeURIComponent(query)}&num=5&api_key=${apiKey}`;

        if (as_ylo) url += `&as_ylo=${as_ylo}`;
        if (as_yhi) url += `&as_yhi=${as_yhi}`;

        newsContainer.innerHTML = "<p>Loading articles...</p>";

        try {
            const response = await fetch(url);
            const data = await response.json();

            newsContainer.innerHTML = "";

            if (data.organic_results && data.organic_results.length > 0) {
                data.organic_results.forEach(result => {
                    const card = document.createElement("div");
                    card.className = "mb-4";

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
