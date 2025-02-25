# **Restaurant Point of Sale (POS) System**

A simple **Point of Sale (POS) system** designed for restaurants, built using **Python**, **SQLAlchemy**, **CustomTkinter**, and **SQLite**. The system allows users to manage inventory, create menu items, place orders, and track sales with basic statistics and visualizations.

## **🛠 Features**

✅ **User Authentication** – Sign in and manage user accounts  
✅ **Inventory Management** – Add and manage stock items  
✅ **Menu Management** – Add and manage menu items  
✅ **Order Processing** – Place and track customer orders  
✅ **Sales Tracking** – View basic statistics with graphs  
✅ **Lightweight Database** – Uses SQLite with SQLAlchemy ORM  

## **🛠 Technologies**

- **Python** – Programming language  
- **SQLAlchemy** – ORM for database
- **CustomTkinter** – Framework for Tkinter  
- **SQLite** – Lightweight database

## **🚀 Installation & Setup**

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/yourusername/pos-system.git
cd pos-system
```

2️⃣ **Install dependencies**  
```bash
pip install -r requirements.txt
```

3️⃣ **Set up the database**  

Run the script to **create the database schema**:  
```bash
python create_db.py
```

Run the script to **seed the database with initial data**:  
```bash
python seed_db.py
```

> **Default Admin Account:**  
> - **Username:** `root`  
> - **Password:** `root`  

4️⃣ **Run the application**  
```bash
python main.py
```

## **📌 Authors**

- **Jozef Tadian** – [@jojo20097](https://github.com/jojo20097)  
- **Richard Truben** – [@RTruben](https://github.com/RTruben)  

- **Jozef Tadian** – Implemented **Database Management (/api; /core)*.*
- **Richard Truben** – Developed the **User Interface (/gui).**  

## **📜 License**  
This project is licensed under the **MIT License**.  
