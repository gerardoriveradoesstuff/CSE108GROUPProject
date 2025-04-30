document.addEventListener("DOMContentLoaded", () => {
    console.log("Finance dashboard loaded");

    // Add Transaction
    document.getElementById("transaction-form").addEventListener("submit", async (e) => {
        e.preventDefault();

        const user_id_val = document.getElementById("user-id-add").value;
        const category_id_val = document.getElementById("category-id").value;
        //
        // if (!user_id_val || !category_id_val) {
        //     alert("Both user and category must be selected.");
        //     return;
        // }

        const user_id = parseInt(user_id_val, 10);
        const category_id = parseInt(category_id_val, 10);
        const income = parseFloat(document.getElementById("income").value) || 0;
        const expense = parseFloat(document.getElementById("expense").value) || 0;
        const description = document.getElementById("description").value;
        const date = document.getElementById("date").value;

        if ((income === 0 && expense === 0) || (income > 0 && expense > 0)) {
            alert("Please enter either income or expense, not both.");
            return;
        }

        const res = await fetch("/add-transaction", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({user_id, category_id, income, expense, description, date}),
        });

        const data = await res.json();
        if (res.ok) {
            alert("Transaction added!");
            fetchTransactions();
        } else {
            alert(`Error: ${data.error}`);
        }
    });
    refreshCategories();


    // Create Category
    document.getElementById("create-category-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("category-name-input").value;
        const res = await fetch("/add-category", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name}),
        });

        const data = await res.json();
        if (res.ok) {
            alert("Category created.");
            document.getElementById("category-name-input").value = "";
            refreshCategories();
        } else {
            alert(`Error: ${data.error}`);
        }

    });

    // Generate Report
    document.getElementById("generate-report-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const user_id = document.getElementById("report-user-id").value;
        const year = document.getElementById("report-year").value;
        const month = document.getElementById("report-month").value;

        const res = await fetch("/generate-report", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({user_id, year, month}),
        });

        const data = await res.json();
        if (res.ok) {
            document.getElementById("total-income").textContent = data.total_income.toFixed(2);
            document.getElementById("total-expense").textContent = data.total_expense.toFixed(2);
            document.getElementById("balance").textContent = data.balance.toFixed(2);
            document.getElementById("average-income").textContent = data.average_income.toFixed(2);
            document.getElementById("average-expense").textContent = data.average_expense.toFixed(2);
            document.getElementById("highest-transaction").textContent = data.largest_income?.description || "N/A";
            document.getElementById("smallest-transaction").textContent = data.smallest_expense?.description || "N/A";

            const body = document.getElementById("report-table-body");
            body.innerHTML = "";
            data.transactions.forEach(t => {
                body.innerHTML += `
                <tr>
                    <td>${t.date}</td>
                    <td>${t.income.toFixed(2)}</td>
                    <td>${t.expense.toFixed(2)}</td>
                    <td>${t.description}</td>
                </tr>`;
            });

            new bootstrap.Modal(document.getElementById("reportModal")).show();
        } else {
            alert(`Error: ${data.error}`);
        }
    });

    // Fetch Categories
    async function refreshCategories() {
        try {
            const response = await fetch("/fetch-categories");
            if (response.ok) {
                const categories = await response.json();
                const categorySelect = document.getElementById("category-id");
                categorySelect.innerHTML = `<option value="" disabled selected>Select Category</option>`;

                categories.forEach(category => {
                    const option = document.createElement("option");
                    option.value = category.category_id;
                    option.textContent = category.name;
                    categorySelect.appendChild(option);
                });
            } else {
                console.error("Failed to fetch categories:", await response.text());
            }
        } catch (error) {
            console.error("Error refreshing categories:", error);
        }
    }

    // Initial Fetch
    // fetchCategories();
    fetchTransactions();
    refreshCategories(); // Populate categories dropdown on page load


    async function fetchTransactions() {
        const res = await fetch("/fetch-transactions");
        const data = await res.json();
        const table = document.getElementById("transactions-table").querySelector("tbody");
        table.innerHTML = "";
        data.forEach(tx => {
            table.innerHTML += `
            <tr>
                <td>${tx.transaction_id}</td>
                <td>${tx.date}</td>
                <td>${tx.income.toFixed(2)}</td>
                <td>${tx.expense.toFixed(2)}</td>
                <td>${tx.user_id}</td>
                <td>${tx.category}</td>
                <td>${tx.description}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteTransaction(${tx.transaction_id})">Delete</button>
                </td>
            </tr>`;
        });
    }

    async function deleteTransaction(id) {
        if (!confirm("Delete transaction?")) return;
        const res = await fetch(`/delete-transaction/${id}`, {method: "DELETE"});
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            fetchTransactions();
        } else {
            alert(`Error: ${data.error}`);
        }
    }

    refreshCategories();
    fetchTransactions();


});
