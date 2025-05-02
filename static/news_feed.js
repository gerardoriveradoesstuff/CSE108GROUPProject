
document.addEventListener("DOMContentLoaded", () => {
    const apiKey = "62ae52ee70e4411192f51b79972386cb";  //
    const url = `https://newsapi.org/v2/everything?q=computer%20science%20statistics&language=en&sortBy=publishedAt&pageSize=5&apiKey=${apiKey}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById("news-feed");
            newsContainer.innerHTML = "";  // Clear loading message

            if (data.articles && data.articles.length > 0) {
                data.articles.forEach(article => {
                    const card = document.createElement("div");
                    card.className = "mb-3";

                    card.innerHTML = `
                            <h6><a href="${article.url}" target="_blank" class="text-decoration-none">${article.title}</a></h6>
                            <p class="small text-muted">${new Date(article.publishedAt).toLocaleDateString()} - ${article.source.name}</p>
                        `;
                    newsContainer.appendChild(card);
                });
            } else {
                newsContainer.innerHTML = "<p>No recent articles found.</p>";
            }
        })
        .catch(err => {
            document.getElementById("news-feed").innerHTML = "<p>Error loading news. Please try again later.</p>";
            console.error("NewsAPI error:", err);
        });
});

