document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("scholar-form");
    const newsContainer = document.getElementById("google-scholar");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

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
            // console.log("API data received:", data);

            newsContainer.innerHTML = "";

            if (data.organic_results && data.organic_results.length > 0) {
                data.organic_results.forEach(result => {
                    const card = document.createElement("div");
                    card.className = "mb-4";

                    const title = result.title || "No title";
                    const link = result.link || "#";
                    const snippet = result.snippet || "No summary available.";
                    const publication = result.publication_info?.summary || "Unknown source";

                    card.className = "card mb-3 p-3 border shadow-sm";
                    card.innerHTML = `
                        <h6><a href="${link}" target="_blank" class="text-decoration-none">${title}</a></h6>
                        <p class="small text-muted">${publication}</p>
                        <p class="small">${snippet}</p>
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
