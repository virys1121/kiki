-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Roles table
CREATE TABLE Roles (
    RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoleName TEXT NOT NULL
);

-- Users table
CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserFullName TEXT NOT NULL,
    UserLogin TEXT NOT NULL UNIQUE,
    UserPassword TEXT NOT NULL,
    UserRole INTEGER NOT NULL,
    FOREIGN KEY (UserRole) REFERENCES Roles(RoleID)
);

-- Products table
CREATE TABLE Products (
    ProductArticleNumber TEXT PRIMARY KEY,
    ProductName TEXT NOT NULL,
    ProductDescription TEXT,
    ProductPrice REAL NOT NULL,
    ProductQuantityInStock INTEGER NOT NULL DEFAULT 0
);

-- Orders table
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    OrderStatus TEXT NOT NULL,
    OrderUserID INTEGER NOT NULL,
    FOREIGN KEY (OrderUserID) REFERENCES Users(UserID)
);

-- OrderItems table (Many-to-Many junction)
CREATE TABLE OrderItems (
    OrderID INTEGER NOT NULL,
    ProductArticleNumber TEXT NOT NULL,
    ItemQuantity INTEGER NOT NULL DEFAULT 1,
    ItemPrice REAL NOT NULL,
    PRIMARY KEY (OrderID, ProductArticleNumber),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductArticleNumber) REFERENCES Products(ProductArticleNumber)
);

-- Insert Roles
INSERT INTO Roles (RoleName) VALUES ('Администратор');
INSERT INTO Roles (RoleName) VALUES ('Менеджер');
INSERT INTO Roles (RoleName) VALUES ('Клиент');
INSERT INTO Roles (RoleName) VALUES ('Гость');

-- Insert Sample Users
INSERT INTO Users (UserFullName, UserLogin, UserPassword, UserRole) VALUES ('Иванов Иван Иванович', 'admin', 'admin123', 1);
INSERT INTO Users (UserFullName, UserLogin, UserPassword, UserRole) VALUES ('Петров Петр Петрович', 'manager', 'manager123', 2);
INSERT INTO Users (UserFullName, UserLogin, UserPassword, UserRole) VALUES ('Сидоров Сидор Сидорович', 'client', 'client123', 3);

-- Insert Sample Products
INSERT INTO Products (ProductArticleNumber, ProductName, ProductDescription, ProductPrice, ProductQuantityInStock)
VALUES ('T001', 'Конструктор Лего', 'Большой набор для сборки города', 5000.00, 10);
INSERT INTO Products (ProductArticleNumber, ProductName, ProductDescription, ProductPrice, ProductQuantityInStock)
VALUES ('T002', 'Кукла Барби', 'Модная кукла с аксессуарами', 1500.00, 25);
INSERT INTO Products (ProductArticleNumber, ProductName, ProductDescription, ProductPrice, ProductQuantityInStock)
VALUES ('T003', 'Машинка Хот Вилс', 'Гоночный автомобиль', 300.00, 50);

-- Insert Sample Orders
INSERT INTO Orders (OrderID, OrderStatus, OrderUserID) VALUES (1, 'Новый', 3);
INSERT INTO Orders (OrderID, OrderStatus, OrderUserID) VALUES (2, 'В обработке', 3);

-- Insert Order Items
INSERT INTO OrderItems (OrderID, ProductArticleNumber, ItemQuantity, ItemPrice) VALUES (1, 'T001', 1, 5000.00);
INSERT INTO OrderItems (OrderID, ProductArticleNumber, ItemQuantity, ItemPrice) VALUES (1, 'T003', 2, 300.00);
INSERT INTO OrderItems (OrderID, ProductArticleNumber, ItemQuantity, ItemPrice) VALUES (2, 'T002', 1, 1500.00);
