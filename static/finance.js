document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM fully loaded"); // Debugging

    // Handle Add User
    document.getElementById("add-user-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("user-name").value;
        const email = document.getElementById("user-email").value;

        try {
            const response = await fetch("/add-user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email }),
            });
            const result = await response.json();
            if (response.ok) {
                fetchRecentUsers(); // Refresh the users table
                alert(`User created with ID: ${result.user_id}`);
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error("Error adding user:", error);
        }
    });

    // Handle Add Transaction
    document.getElementById("transaction-form").addEventListener("submit", async (e) => {
        e.preventDefault();

        // Debugging: Check all inputs
        console.log("User ID Input:", document.getElementById("user-id-add"));
        console.log("Category Input:", document.getElementById("category-id"));
        console.log("Income Input:", document.getElementById("income"));
        console.log("Expense Input:", document.getElementById("expense"));
        console.log("Description Input:", document.getElementById("description"));
        console.log("Date Input:", document.getElementById("date"));

        const user_id = parseInt(document.getElementById("user-id-add").value, 10);
        const category_id = parseInt(document.getElementById("category-id").value, 10);
        const income = parseFloat(document.getElementById("income").value) || 0;
        const expense = parseFloat(document.getElementById("expense").value) || 0;
        const description = document.getElementById("description").value;
        const date = document.getElementById("date").value || new Date().toISOString().split("T")[0];

        console.log({ user_id, category_id, income, expense, description, date });

        if ((income === 0 && expense === 0) || (income > 0 && expense > 0)) {
            alert("Please provide either Income or Expense, but not both.");
            return;
        }

        try {
            const response = await fetch("/add-transaction", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id, category_id, income, expense, description, date }),
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                fetchTransactions(); // Refresh the transactions table
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error("Error adding transaction:", error);
        }
    });

    // Handle Create Category
    document.getElementById("create-category-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const categoryName = document.getElementById("category-name-input").value;

        try {
            const response = await fetch("/add-category", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: categoryName }),
            });

            if (response.ok) {
                alert("Category added successfully!");
                document.getElementById("category-name-input").value = ""; // Clear input field
                refreshCategories(); // Refresh the category dropdown
            } else {
                const error = await response.json();
                alert(`Error: ${error.error}`);
            }
        } catch (error) {
            console.error("Error adding category:", error);
        }
    });

    // Handle Generate Report
    document.getElementById("generate-report-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const user_id = document.getElementById("report-user-id").value;
        const year = document.getElementById("report-year").value;
        const month = document.getElementById("report-month").value;

        try {
            const response = await fetch("/generate-report", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id, year, month }),
            });

            if (response.ok) {
                const data = await response.json();

                // Populate modal content
                document.getElementById("total-income").textContent = data.total_income.toFixed(2);
                document.getElementById("total-expense").textContent = data.total_expense.toFixed(2);
                document.getElementById("balance").textContent = data.balance.toFixed(2);
                document.getElementById("average-income").textContent = data.average_income.toFixed(2);
                document.getElementById("average-expense").textContent = data.average_expense.toFixed(2);

                document.getElementById("highest-transaction").textContent =
                    `ID: ${data.largest_income.transaction_id}, Amount: $${data.largest_income.amount}, Date: ${data.largest_income.date}`;
                document.getElementById("smallest-transaction").textContent =
                    `ID: ${data.smallest_expense.transaction_id}, Amount: $${data.smallest_expense.amount}, Date: ${data.smallest_expense.date}`;

                // Populate table rows for transactions
                const tableBody = document.getElementById("report-table-body");
                tableBody.innerHTML = "";
                data.transactions.forEach(t => {
                    const row = `
                    <tr>
                        <td>${t.date}</td>
                        <td>${t.income.toFixed(2)}</td>
                        <td>${t.expense.toFixed(2)}</td>
                        <td>${t.description}</td>
                    </tr>`;
                    tableBody.innerHTML += row;
                });

                // Show the Bootstrap modal
                const reportModal = new bootstrap.Modal(document.getElementById("reportModal"));
                reportModal.show();
            } else {
                const error = await response.json();
                alert(`Error: ${error.error}`);
            }
        } catch (error) {
            console.error("Error generating report:", error);
            alert("Failed to generate the report.");
        }
    });


    // Fetch Users
    async function fetchRecentUsers() {
        const spinner = document.getElementById("user-loading-spinner");
        const recentUsersTable = document.getElementById("recent-users-table").querySelector("tbody");

        try {
            // Show the spinner
            spinner.classList.remove("d-none");
            recentUsersTable.innerHTML = ""; // Clear previous rows

            const response = await fetch("/fetch-recent-users"); // Add endpoint for recent users
            const users = await response.json();

            // Populate the table with recent users
            users.forEach(user => {
                const row = document.createElement("tr");
                row.innerHTML = `
                <td>${user.user_id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
            `;
                recentUsersTable.appendChild(row);
            });
        } catch (error) {
            console.error("Error fetching recent users:", error);
        } finally {
            // Hide the spinner
            spinner.classList.add("d-none");
        }
    }

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
    // fetchUsers();
    // fetchCategories();
    fetchTransactions();
    fetchRecentUsers(); // Fetch recently added users
    refreshCategories(); // Populate categories dropdown on page load
});

// Function to open the Edit Transaction Modal and populate fields
function editTransaction(transaction_id) {
    fetch(`/get-transaction/${transaction_id}`)
        .then(response => response.json())
        .then(transaction => {
            // Populate the modal fields with transaction data
            document.getElementById("edit-transaction-id").value = transaction.transaction_id;
            document.getElementById("edit-income").value = transaction.income || 0.0;
            document.getElementById("edit-expense").value = transaction.expense || 0.0;
            document.getElementById("edit-category-id").value = transaction.category_id || "";
            document.getElementById("edit-description").value = transaction.description || "";
            document.getElementById("edit-date").value = transaction.date || "";

            // Show the Bootstrap modal
            const editModal = new bootstrap.Modal(document.getElementById("editTransactionModal"));
            editModal.show();
        })
        .catch(error => {
            console.error("Error fetching transaction details:", error);
            alert("Failed to fetch transaction details.");
        });
}

// Function to update the transaction
function updateTransaction() {
    const transaction_id = document.getElementById("edit-transaction-id").value;
    const updatedTransaction = {
        income: parseFloat(document.getElementById("edit-income").value) || 0,
        expense: parseFloat(document.getElementById("edit-expense").value) || 0,
        category_id: parseInt(document.getElementById("edit-category-id").value, 10),
        description: document.getElementById("edit-description").value,
        date: document.getElementById("edit-date").value
    };

    // Debugging
    console.log("Transaction ID:", transaction_id);
    console.log("Updated Transaction Data:", updatedTransaction);

    if (!transaction_id || isNaN(updatedTransaction.category_id)) {
        alert("Error: Missing required fields for update.");
        return;
    }

    fetch(`/update-transaction/${transaction_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedTransaction)
    })
        .then(response => response.json())
        .then(result => {
            if (result.message) {
                alert("Transaction updated successfully!");
                fetchTransactions(); // Refresh transactions table
                const editModal = bootstrap.Modal.getInstance(document.getElementById("editTransactionModal"));
                editModal.hide();
            } else {
                alert(`Error: ${result.error}`);
            }
        })
        .catch(error => {
            console.error("Error updating transaction:", error);
            alert("Failed to update transaction.");
        });
}

function deleteTransaction(transaction_id) {
    if (confirm("Are you sure you want to delete this transaction?")) {
        fetch(`/delete-transaction/${transaction_id}`, { method: "DELETE" })
            .then(response => {
                console.log("Raw Response:", response); // Debug raw response
                return response.json();
            })
            .then(result => {
                console.log("Result from server:", result); // Debug parsed result
                if (result.message) {
                    alert("Transaction deleted successfully!");
                    fetchTransactions(); // Refresh transactions table
                } else {
                    alert(`Error: ${result.error}`);
                }
            })
            .catch(error => {
                console.error("Error deleting transaction:", error);
                alert("Failed to delete transaction.");
            });
    }
}

// Fetch Transactions
async function fetchTransactions() {
    try {
        const response = await fetch("/fetch-transactions");
        const transactions = await response.json();

        console.log("Fetched Transactions:", transactions); // Debugging

        const transactionsTable = document.getElementById("transactions-table").querySelector("tbody");
        transactionsTable.innerHTML = ""; // Clear existing rows

        transactions.forEach(transaction => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${transaction.transaction_id}</td>
                <td>${transaction.date}</td>
                <td>${parseFloat(transaction.income).toFixed(2)}</td>
                <td>${parseFloat(transaction.expense).toFixed(2)}</td>
                <td>${transaction.user_id}</td>
                <td>${transaction.category}</td>
                <td>${transaction.description}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editTransaction(${transaction.transaction_id})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteTransaction(${transaction.transaction_id})">Delete</button>
                </td>
            `;
            transactionsTable.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching transactions:", error);
    }
}




