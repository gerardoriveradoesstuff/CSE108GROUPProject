document.addEventListener("DOMContentLoaded", () => {
    const apiKey = "YOUR_SERPAPI_API_KEY"; // Replace with your actual SerpAPI key
    const query = "machine learning education";
    const url = `https://serpapi.com/search.json?engine=google_scholar&q=${encodeURIComponent(query)}&num=5&api_key=${apiKey}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById("news-feed");
            newsContainer.innerHTML = "";  // Clear loading message

            if (data.organic_results && data.organic_results.length > 0) {
                data.organic_results.forEach(result => {
                    const card = document.createElement("div");
                    card.className = "mb-3";

                    card.innerHTML = `
                        <h6><a href="${result.link}" target="_blank" class="text-decoration-none">${result.title}</a></h6>
                        <p class="small text-muted">${result.publication || "Unknown Journal"}</p>
                        <p class="small">${result.snippet || ""}</p>
                    `;
                    newsContainer.appendChild(card);
                });
            } else {
                newsContainer.innerHTML = "<p>No scholarly articles found.</p>";
            }
        })
        .catch(err => {
            document.getElementById("news-feed").innerHTML = "<p>Error loading scholarly articles. Please try again later.</p>";
            console.error("Google Scholar API error:", err);
        });
});
