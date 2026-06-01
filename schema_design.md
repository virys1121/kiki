# Database Schema Design

## Entities and Attributes

1. **Roles**
   - RoleID (PK, Integer): Unique identifier for the role.
   - RoleName (String): Name of the role (e.g., Administrator, Manager, Client, Guest).

2. **Users**
   - UserID (PK, Integer): Unique identifier for the user.
   - UserFullName (String): Full name of the user.
   - UserLogin (String, Unique): Login name for the user.
   - UserPassword (String): Password for the user.
   - UserRole (FK, Integer): Reference to the Roles table.

3. **Products**
   - ProductArticleNumber (PK, String): Unique article number for the product.
   - ProductName (String): Name of the product.
   - ProductDescription (String): Description of the product.
   - ProductPrice (Decimal): Price of the product at the current time.
   - ProductQuantityInStock (Integer): Current stock quantity.

4. **Orders**
   - OrderID (PK, Integer): Unique identifier for the order.
   - OrderDate (DateTime): Date when the order was placed.
   - OrderStatus (String): Current status of the order.
   - OrderUserID (FK, Integer): Reference to the Users table.

5. **OrderItems**
   - OrderID (PK, FK, Integer): Reference to the Orders table.
   - ProductArticleNumber (PK, FK, String): Reference to the Products table.
   - ItemQuantity (Integer): Quantity of the product in the order.
   - ItemPrice (Decimal): Price of the product at the time of ordering.

## Relationships

- **Roles to Users**: One-to-Many. One role can be assigned to many users.
- **Users to Orders**: One-to-Many. One user can place many orders.
- **Orders to OrderItems**: One-to-Many. One order can contain multiple items.
- **Products to OrderItems**: One-to-Many. One product can be part of multiple orders.
- **Orders to Products**: Many-to-Many through **OrderItems**.

## Normalization (3NF)

- **1NF**: All tables have primary keys, and all columns contain atomic values.
- **2NF**: All non-key attributes are fully functionally dependent on the primary key.
- **3NF**: There are no transitive dependencies. Non-key attributes depend only on the primary key.
