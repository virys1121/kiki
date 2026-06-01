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

-- Products table updated for Module 2
CREATE TABLE Products (
    ProductArticleNumber TEXT PRIMARY KEY,
    ProductName TEXT NOT NULL,
    ProductCategory TEXT NOT NULL,
    ProductDescription TEXT,
    ProductManufacturer TEXT NOT NULL,
    ProductSupplier TEXT NOT NULL,
    ProductPrice REAL NOT NULL,
    ProductUnit TEXT NOT NULL,
    ProductQuantityInStock INTEGER NOT NULL DEFAULT 0,
    ProductDiscount INTEGER NOT NULL DEFAULT 0,
    ProductPhoto TEXT -- Path to image or NULL
);

-- Orders table
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    OrderStatus TEXT NOT NULL,
    OrderUserID INTEGER NOT NULL,
    FOREIGN KEY (OrderUserID) REFERENCES Users(UserID)
);

-- OrderItems table
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

-- Insert Sample Products with varied discounts and stock levels
INSERT INTO Products (ProductArticleNumber, ProductName, ProductCategory, ProductDescription, ProductManufacturer, ProductSupplier, ProductPrice, ProductUnit, ProductQuantityInStock, ProductDiscount, ProductPhoto)
VALUES ('T001', 'Конструктор Лего', 'Игрушки', 'Большой набор для сборки города', 'LEGO Group', 'Lego Russia', 5000.00, 'шт.', 10, 20, NULL);

INSERT INTO Products (ProductArticleNumber, ProductName, ProductCategory, ProductDescription, ProductManufacturer, ProductSupplier, ProductPrice, ProductUnit, ProductQuantityInStock, ProductDiscount, ProductPhoto)
VALUES ('T002', 'Кукла Барби', 'Игрушки', 'Модная кукла с аксессуарами', 'Mattel', 'ToyWorld', 1500.00, 'шт.', 25, 10, NULL);

INSERT INTO Products (ProductArticleNumber, ProductName, ProductCategory, ProductDescription, ProductManufacturer, ProductSupplier, ProductPrice, ProductUnit, ProductQuantityInStock, ProductDiscount, ProductPhoto)
VALUES ('T003', 'Машинка Хот Вилс', 'Игрушки', 'Гоночный автомобиль', 'Mattel', 'ToyWorld', 300.00, 'шт.', 0, 5, NULL);

INSERT INTO Products (ProductArticleNumber, ProductName, ProductCategory, ProductDescription, ProductManufacturer, ProductSupplier, ProductPrice, ProductUnit, ProductQuantityInStock, ProductDiscount, ProductPhoto)
VALUES ('T004', 'Мягкий медведь', 'Игрушки', 'Плюшевый мишка', 'PlushToys', 'PlushToys', 1000.00, 'шт.', 5, 0, NULL);

-- Insert Sample Orders
INSERT INTO Orders (OrderID, OrderStatus, OrderUserID) VALUES (1, 'Новый', 3);
INSERT INTO OrderItems (OrderID, ProductArticleNumber, ItemQuantity, ItemPrice) VALUES (1, 'T001', 1, 5000.00);
