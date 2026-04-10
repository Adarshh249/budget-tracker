import { useEffect, useState } from "react";
import { PieChart, Pie, Cell } from "recharts";

const BASE_URL = "https://budget-tracker-zcij.onrender.com";
const USER_ID = 1;

function App() {
  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [insights, setInsights] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [budget, setBudget] = useState({});
  const [prediction, setPrediction] = useState(0);

  const [form, setForm] = useState({
    type: "EXPENSE",
    category: "",
    amount: "",
    description: "",
  });

  const fetchData = () => {
    fetch(`${BASE_URL}/transactions?user_id=${USER_ID}`)
      .then((res) => res.json())
      .then((data) => setTransactions(data));

    fetch(`${BASE_URL}/total-expense?user_id=${USER_ID}`)
      .then((res) => res.json())
      .then((data) => setTotal(data.total_expense));

    fetch(`${BASE_URL}/insights?user_id=${USER_ID}`)
      .then((res) => res.json())
      .then((data) => setInsights(data.insights));

    fetch(`${BASE_URL}/category-summary?user_id=${USER_ID}`)
      .then((res) => res.json())
      .then((data) => {
        const formatted = Object.keys(data).map((key) => ({
          name: key,
          value: data[key],
        }));
        setCategoryData(formatted);
      });

    fetch(`${BASE_URL}/alerts?user_id=${USER_ID}`)
      .then((res) => res.json())
      .then((data) => setAlerts(data.alerts));

    fetch(`${BASE_URL}/budget-status?user_id=${USER_ID}`)
      .then((res) => res.json())
      .then((data) => setBudget(data));

    fetch(`${BASE_URL}/prediction?user_id=${USER_ID}`)
      .then((res) => res.json())
      .then((data) => setPrediction(data.predicted_monthly_spend));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    fetch(`${BASE_URL}/transactions?user_id=${USER_ID}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...form,
        amount: parseFloat(form.amount),
      }),
    }).then(() => {
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
            <button style={styles.button}>Add</button>
          </form>
        </div>

        {/* TOTAL */}
        <div style={styles.card}>
          <h2>Total Expense</h2>
          <h3 style={{ color: "green" }}>₹{total}</h3>
        </div>

        {/* BUDGET */}
        <div style={styles.card}>
          <h2>Budget Status</h2>
          <p>Total Budget: ₹{budget.budget}</p>
          <p>Spent: ₹{budget.spent}</p>
          <p>Remaining: ₹{budget.remaining}</p>
          <p>Used: {budget.percentage_used}%</p>
        </div>

        {/* PREDICTION */}
        <div style={styles.card}>
          <h2>Predicted Monthly Spend</h2>
          <h3 style={{ color: "orange" }}>₹{prediction}</h3>
        </div>

        {/* ALERTS */}
        <div style={styles.card}>
          <h2>Smart Alerts</h2>
          <ul>
            {alerts.map((a, index) => (
              <li
                key={index}
                style={{ color: a.includes("⚠") ? "red" : "green" }}
              >
                {a}
              </li>
            ))}
          </ul>
        </div>

        {/* INSIGHTS */}
        <div style={styles.card}>
          <h2>Insights</h2>
          <ul>
            {insights.map((i, index) => (
              <li key={index}>{i}</li>
            ))}
          </ul>
        </div>

        {/* CHART */}
        <div style={styles.card}>
          <h2>Category Chart</h2>
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
        </div>

        {/* TRANSACTIONS */}
        <div style={styles.card}>
          <h2>Transactions</h2>
          <ul>
            {transactions.map((t) => (
              <li key={t.id} style={styles.listItem}>
                {t.category} - ₹{t.amount} ({t.type})
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

/* STYLES */
const styles = {
  page: {
    background: "#f4f6f8",
    minHeight: "100vh",
    padding: "20px",
  },
  container: {
    maxWidth: "700px",
    margin: "auto",
  },
  title: {
    textAlign: "center",
    marginBottom: "20px",
  },
  card: {
    background: "white",
    padding: "15px",
    marginBottom: "20px",
    borderRadius: "10px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },
  input: {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
  },
  button: {
    background: "#007bff",
    color: "white",
    padding: "10px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  listItem: {
    padding: "5px 0",
    borderBottom: "1px solid #eee",
  },
};

export default App;