# ShopWiz — Smart AI-Powered Ecommerce Recommendation System 🛍️✨

ShopWiz is a modern, high-performance E-Commerce platform built with **Python Flask** and **Machine Learning**. It features a premium, responsive UI/UX and an AI recommendation engine that learns product similarities to provide a personalized shopping experience.

---

## 🌟 Key Features

*   **🤖 AI Recommendation Engine**: Real-time product suggestions using TF-IDF Vectorization and Cosine Similarity.
*   **🎨 Premium UI/UX**: Sleek, modern design with Glassmorphism, smooth animations, and a responsive layout.
*   **🌓 Dark Mode**: Built-in visual theme toggle with persistent user preference.
*   **🔍 Live Search**: Instant autocomplete suggestions as you type in the search bar.
*   **👤 User Authentication**: Full Signup and Login system with session-based tracking.
*   **💖 Wishlist & Cart**: Save favorite products and manage a dynamic shopping cart (localStorage based).
*   **📦 Dynamic Catalog**: Paginated product listings with filtering by category and sorting by price/rating.
*   **📱 Fully Responsive**: Optimized for desktops, tablets, and smartphones.

---

## 🛠️ Tech Stack

*   **Backend**: Python, Flask
*   **Machine Learning**: Scikit-learn (TF-IDF, Cosine Similarity), Pandas, NumPy
*   **Database**: SQLite (SQLAlchemy ORM)
*   **Frontend**: HTML5, Vanilla CSS3 (Modern tokens & variables), JavaScript (ES6+), Jinja2 Templates
*   **Icons**: Bootstrap Icons
*   **Fonts**: Google Fonts (Inter, Poppins)

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   pip (Python package manager)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/DEEPAK-317/E-Commerce-Recommendation-System.git
    cd E-Commerce-Recommendation-System
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    python app.py
    ```

4.  **Access the App**
    Open your browser and navigate to `http://127.0.0.1:5000`

---

## 📁 Project Structure

```text
├── app.py              # Main Flask application & AI logic
├── requirements.txt    # Project dependencies
├── models/             # Dataset & pre-cleaned CSVs
├── static/
│   ├── css/            # Premium style sheets
│   ├── js/             # Interactive frontend logic
│   └── img/            # Product assets & visuals
├── templates/          # Jinja2 HTML templates
└── instance/           # Local SQLite database
```

---

## 🧠 How the AI Works

The recommendation system uses **Content-Based Filtering**. It analyzes product titles and categories to create a feature matrix using **TF-IDF**. When a user views a product, the system calculates the **Cosine Similarity** between that product and every other item in the catalog to suggest the most relevant alternatives in real-time.

---

## 📜 License & Author

Crafted with ❤️ by **Deepak Kumar**.

This project is open-source and available under the MIT License.
