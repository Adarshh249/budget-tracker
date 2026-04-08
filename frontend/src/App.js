import { useEffect, useState } from "react";
import { PieChart, Pie, Cell } from "recharts";

const BASE_URL = "https://budget-tracker-zcij.onrender.com";

function App() {
  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [insights, setInsights] = useState([]);
  const [categoryData, setCategoryData] = useState([]);

  const [form, setForm] = useState({
    type: "EXPENSE",
    category: "",
    amount: "",
    description: "",
  });

  const fetchData = () => {
    fetch(`${BASE_URL}/transactions`)
      .then((res) => res.json())
      .then((data) => setTransactions(data));

    fetch(`${BASE_URL}/total-expense`)
      .then((res) => res.json())
      .then((data) => setTotal(data.total_expense));

    fetch(`${BASE_URL}/insights`)
      .then((res) => res.json())
      .then((data) => setInsights(data.insights));

    fetch(`${BASE_URL}/category-summary`)
      .then((res) => res.json())
      .then((data) => {
        const formatted = Object.keys(data).map((key) => ({
          name: key,
          value: data[key],
        }));
        setCategoryData(formatted);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    fetch(`${BASE_URL}/transactions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...form,
        amount: parseFloat(form.amount),
      }),
    })
      .then((res) => res.json())
      .then(() => {
        fetchData();
        setForm({
          type: "EXPENSE",
          category: "",
          amount: "",
          description: "",
        });
      });
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.title}>💰 Smart Budget Tracker</h1>
        <p style={styles.subtitle}>
          Track your expenses and gain insights instantly
        </p>

        {/* FORM */}
        <div style={styles.card}>
          <h2>Add Transaction</h2>
          <form onSubmit={handleSubmit}>
            <input
              style={styles.input}
              name="category"
              placeholder="Category"
              value={form.category}
              onChange={handleChange}
            />

            <input
              style={styles.input}
              name="amount"
              placeholder="Amount"
              value={form.amount}
              onChange={handleChange}
            />

            <input
              style={styles.input}
              name="description"
              placeholder="Description"
              value={form.description}
              onChange={handleChange}
            />

            <button style={styles.button}>Add Transaction</button>
          </form>
        </div>

        {/* TOTAL */}
        <div style={styles.card}>
          <h2>Total Expense</h2>
          <h3 style={styles.total}>₹{total}</h3>
        </div>

        {/* INSIGHTS */}
        <div style={styles.card}>
          <h2>Insights</h2>
          {insights.length === 0 ? (
            <p>No insights yet</p>
          ) : (
            <ul>
              {insights.map((i, index) => (
                <li key={index}>{i}</li>
              ))}
            </ul>
          )}
        </div>

        {/* CHART */}
        <div style={styles.card}>
          <h2>Category Chart</h2>
          {categoryData.length === 0 ? (
            <p>No data to display</p>
          ) : (
            <PieChart width={350} height={300}>
              <Pie
                data={categoryData}
                dataKey="value"
                nameKey="name"
                outerRadius={120}
                label
              >
                {categoryData.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={
                      ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"][
                        index % 4
                      ]
                    }
                  />
                ))}
              </Pie>
            </PieChart>
          )}
        </div>

        {/* TRANSACTIONS */}
        <div style={styles.card}>
          <h2>Transactions</h2>
          {transactions.length === 0 ? (
            <p>No transactions yet</p>
          ) : (
            <ul>
              {transactions.map((t) => (
                <li key={t.id} style={styles.listItem}>
                  {t.category} - ₹{t.amount} ({t.type})
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

/* 🎨 STYLES */
const styles = {
  page: {
    background: "#f4f6f8",
    minHeight: "100vh",
    padding: "20px",
    fontFamily: "Arial, sans-serif",
  },
  container: {
    maxWidth: "700px",
    margin: "auto",
  },
  title: {
    textAlign: "center",
    color: "#2c3e50",
  },
  subtitle: {
    textAlign: "center",
    color: "#7f8c8d",
    marginBottom: "20px",
  },
  card: {
    background: "white",
    padding: "20px",
    marginBottom: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
  },
  input: {
    width: "100%",
    padding: "12px",
    marginBottom: "12px",
    borderRadius: "8px",
    border: "1px solid #ddd",
  },
  button: {
    background: "#4CAF50",
    color: "white",
    padding: "12px",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    width: "100%",
    fontWeight: "bold",
  },
  total: {
    color: "#27ae60",
    fontSize: "24px",
  },
  listItem: {
    padding: "8px 0",
    borderBottom: "1px solid #eee",
  },
};

export default App;