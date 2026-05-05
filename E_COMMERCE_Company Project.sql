-- 1. Creating a database
CREATE DATABASE E_COMMERCE_Company;
GO

USE E_COMMERCE_Company;

-- 2. Creating basic tables (without foreign keys to avoid errors))
CREATE TABLE [dbo].[Categories](
	[CategoryID] [int] IDENTITY(1,1) PRIMARY KEY,
	[CategoryName] [nvarchar](100) NOT NULL,
	[ParentCategoryID] [int] NULL,
	[Description] [nvarchar](max) NULL
);

CREATE TABLE [dbo].[Couriers](
	[CourierID] [int] IDENTITY(1,1) PRIMARY KEY,
	[CourierName] [nvarchar](100) NOT NULL,
	[ContactInfo] [nvarchar](150) NULL
);

CREATE TABLE [dbo].[Customers](
	[CustomerID] [int] IDENTITY(1,1) PRIMARY KEY,
	[FirstName] [nvarchar](50) NOT NULL,
	[LastName] [nvarchar](50) NOT NULL,
	[Email] [nvarchar](100) NOT NULL UNIQUE,
	[Phone] [nvarchar](20) NULL,
	[PasswordHash] [nvarchar](255) NOT NULL,
	[RegistrationDate] [datetime2](7) DEFAULT GETDATE(),
	[IsActive] [bit] DEFAULT 1
);

CREATE TABLE [dbo].[Products](
	[ProductID] [int] IDENTITY(1,1) PRIMARY KEY,
	[CategoryID] [int] NOT NULL,
	[SKU] [nvarchar](60) NOT NULL UNIQUE,
	[ProductName] [nvarchar](150) NOT NULL,
	[Description] [nvarchar](max) NULL,
	[Price] [decimal](10, 2) NOT NULL,
	[CostPrice] [decimal](10, 2) NULL,
	[StockQuantity] [int] NOT NULL DEFAULT 0,
	[LowStockThreshold] [int] NULL DEFAULT 10,
	[IsActive] [bit] NULL DEFAULT 1,
	[CreatedAt] [datetime2](7) NULL DEFAULT GETDATE()
);

CREATE TABLE [dbo].[CustomerAddresses](
	[AddressID] [int] IDENTITY(1,1) PRIMARY KEY,
	[CustomerID] [int] NOT NULL,
	[AddressLine1] [nvarchar](150) NOT NULL,
	[AddressLine2] [nvarchar](150) NULL,
	[City] [nvarchar](80) NOT NULL,
	[State] [nvarchar](80) NULL,
	[PostalCode] [nvarchar](20) NULL,
	[Country] [nvarchar](60) NOT NULL,
	[IsDefault] [bit] DEFAULT 0
);

CREATE TABLE [dbo].[Carts](
	[CartID] [int] IDENTITY(1,1) PRIMARY KEY,
	[CustomerID] [int] NOT NULL,
	[CreatedAt] [datetime2](7) DEFAULT GETDATE(),
	[UpdatedAt] [datetime2](7) DEFAULT GETDATE()
);

CREATE TABLE [dbo].[CartItems](
	[CartItemID] [int] IDENTITY(1,1) PRIMARY KEY,
	[CartID] [int] NOT NULL,
	[ProductID] [int] NOT NULL,
	[Quantity] [int] NOT NULL DEFAULT 1
);

CREATE TABLE [dbo].[Orders](
	[OrderID] [int] IDENTITY(1,1) PRIMARY KEY,
	[CustomerID] [int] NOT NULL,
	[CartID] [int] NULL,
	[ShippingAddressID] [int] NOT NULL,
	[OrderDate] [datetime2](7) DEFAULT GETDATE(),
	[Status] [nvarchar](20) NOT NULL DEFAULT 'Pending',
	[TotalAmount] [decimal](10, 2) NOT NULL,
	[Notes] [nvarchar](max) NULL
);

CREATE TABLE [dbo].[OrderItems](
	[OrderItemID] [int] IDENTITY(1,1) PRIMARY KEY,
	[OrderID] [int] NOT NULL,
	[ProductID] [int] NOT NULL,
	[Quantity] [int] NOT NULL,
	[UnitPrice] [decimal](10, 2) NOT NULL,
	[LineTotal] AS ([Quantity]*[UnitPrice]) PERSISTED
);

CREATE TABLE [dbo].[Invoices](
	[InvoiceID] [int] IDENTITY(1,1) PRIMARY KEY,
	[OrderID] [int] NOT NULL UNIQUE,
	[PaymentID] [int] NULL,
	[InvoiceNumber] [nvarchar](50) NOT NULL UNIQUE,
	[IssuedAt] [datetime2](7) DEFAULT GETDATE(),
	[DueDate] [date] NULL,
	[TotalAmount] [decimal](10, 2) NOT NULL
);

CREATE TABLE [dbo].[Payments](
	[PaymentID] [int] IDENTITY(1,1) PRIMARY KEY,
	[OrderID] [int] NOT NULL,
	[PaymentMethod] [nvarchar](20) NOT NULL,
	[Amount] [decimal](10, 2) NOT NULL,
	[Status] [nvarchar](20) NOT NULL DEFAULT 'Pending',
	[PaidAt] [datetime2](7) NULL,
	[TransactionRef] [nvarchar](100) NULL
);

CREATE TABLE [dbo].[Returns](
	[ReturnID] [int] IDENTITY(1,1) PRIMARY KEY,
	[OrderID] [int] NOT NULL,
	[CustomerID] [int] NOT NULL,
	[ProductID] [int] NOT NULL,
	[QuantityReturned] [int] NOT NULL,
	[ReturnReason] [nvarchar](255) NULL,
	[ReturnDate] [datetime2](7) DEFAULT GETDATE(),
	[Status] [nvarchar](20) NOT NULL DEFAULT 'Requested'
);

CREATE TABLE [dbo].[Refunds](
	[RefundID] [int] IDENTITY(1,1) PRIMARY KEY,
	[ReturnID] [int] NOT NULL,
	[RefundAmount] [decimal](10, 2) NOT NULL,
	[RefundStatus] [nvarchar](20) NOT NULL DEFAULT 'Pending',
	[RefundDate] [datetime2](7) NULL
);

CREATE TABLE [dbo].[Shipments](
	[ShipmentID] [int] IDENTITY(1,1) PRIMARY KEY,
	[OrderID] [int] NOT NULL,
	[CourierID] [int] NULL,
	[TrackingNumber] [nvarchar](100) NULL,
	[Status] [nvarchar](20) NOT NULL DEFAULT 'Pending',
	[ShippedDate] [datetime2](7) NULL,
	[ExpectedDate] [date] NULL,
	[DeliveredDate] [datetime2](7) NULL
);

CREATE TABLE [dbo].[SupportTickets](
	[TicketID] [int] IDENTITY(1,1) PRIMARY KEY,
	[CustomerID] [int] NOT NULL,
	[Subject] [nvarchar](200) NOT NULL,
	[Description] [nvarchar](max) NULL,
	[Priority] [nvarchar](10) NOT NULL DEFAULT 'Medium',
	[Status] [nvarchar](20) NOT NULL DEFAULT 'Open',
	[CreatedAt] [datetime2](7) DEFAULT GETDATE(),
	[ClosedAt] [datetime2](7) NULL
);
GO

-- 3. إضافة العلاقات (Foreign Keys)
ALTER TABLE [dbo].[Categories] ADD CONSTRAINT [FK_Category_Parent] FOREIGN KEY([ParentCategoryID]) REFERENCES [dbo].[Categories] ([CategoryID]);
ALTER TABLE [dbo].[Products] ADD CONSTRAINT [FK_Product_Category] FOREIGN KEY([CategoryID]) REFERENCES [dbo].[Categories] ([CategoryID]);
ALTER TABLE [dbo].[CustomerAddresses] ADD CONSTRAINT [FK_Address_Customer] FOREIGN KEY([CustomerID]) REFERENCES [dbo].[Customers] ([CustomerID]);
ALTER TABLE [dbo].[Carts] ADD CONSTRAINT [FK_Cart_Customer] FOREIGN KEY([CustomerID]) REFERENCES [dbo].[Customers] ([CustomerID]);
ALTER TABLE [dbo].[CartItems] ADD CONSTRAINT [FK_CartItem_Cart] FOREIGN KEY([CartID]) REFERENCES [dbo].[Carts] ([CartID]);
ALTER TABLE [dbo].[CartItems] ADD CONSTRAINT [FK_CartItem_Product] FOREIGN KEY([ProductID]) REFERENCES [dbo].[Products] ([ProductID]);
ALTER TABLE [dbo].[Orders] ADD CONSTRAINT [FK_Order_Customer] FOREIGN KEY([CustomerID]) REFERENCES [dbo].[Customers] ([CustomerID]);
ALTER TABLE [dbo].[Orders] ADD CONSTRAINT [FK_Order_Cart] FOREIGN KEY([CartID]) REFERENCES [dbo].[Carts] ([CartID]);
ALTER TABLE [dbo].[Orders] ADD CONSTRAINT [FK_Order_Address] FOREIGN KEY([ShippingAddressID]) REFERENCES [dbo].[CustomerAddresses] ([AddressID]);
ALTER TABLE [dbo].[OrderItems] ADD CONSTRAINT [FK_OrderItem_Order] FOREIGN KEY([OrderID]) REFERENCES [dbo].[Orders] ([OrderID]);
ALTER TABLE [dbo].[OrderItems] ADD CONSTRAINT [FK_OrderItem_Product] FOREIGN KEY([ProductID]) REFERENCES [dbo].[Products] ([ProductID]);
ALTER TABLE [dbo].[Payments] ADD CONSTRAINT [FK_Payment_Order] FOREIGN KEY([OrderID]) REFERENCES [dbo].[Orders] ([OrderID]);
ALTER TABLE [dbo].[Invoices] ADD CONSTRAINT [FK_Invoice_Order] FOREIGN KEY([OrderID]) REFERENCES [dbo].[Orders] ([OrderID]);
ALTER TABLE [dbo].[Returns] ADD CONSTRAINT [FK_Return_Order] FOREIGN KEY([OrderID]) REFERENCES [dbo].[Orders] ([OrderID]);
ALTER TABLE [dbo].[Returns] ADD CONSTRAINT [FK_Return_Customer] FOREIGN KEY([CustomerID]) REFERENCES [dbo].[Customers] ([CustomerID]);
ALTER TABLE [dbo].[Returns] ADD CONSTRAINT [FK_Return_Product] FOREIGN KEY([ProductID]) REFERENCES [dbo].[Products] ([ProductID]);
ALTER TABLE [dbo].[Refunds] ADD CONSTRAINT [FK_Refund_Return] FOREIGN KEY([ReturnID]) REFERENCES [dbo].[Returns] ([ReturnID]);
ALTER TABLE [dbo].[Shipments] ADD CONSTRAINT [FK_Shipment_Order] FOREIGN KEY([OrderID]) REFERENCES [dbo].[Orders] ([OrderID]);
ALTER TABLE [dbo].[Shipments] ADD CONSTRAINT [FK_Shipment_Courier] FOREIGN KEY([CourierID]) REFERENCES [dbo].[Couriers] ([CourierID]);
ALTER TABLE [dbo].[SupportTickets] ADD CONSTRAINT [FK_Ticket_Customer] FOREIGN KEY([CustomerID]) REFERENCES [dbo].[Customers] ([CustomerID]);
GO
--------------------------------------------------

-- ==========================================
-- Q1) Customer Master View
-- ==========================================
CREATE VIEW vw_CustomerMaster AS
SELECT 
    c.CustomerID, 
    c.FirstName + ' ' + c.LastName AS FullName, 
    c.Email, 
    c.Phone, 
    ca.City, 
    c.RegistrationDate,
    COUNT(DISTINCT o.OrderID) AS TotalOrders,
    ISNULL(SUM(p.Amount), 0) AS TotalSpend
FROM Customers c
LEFT JOIN CustomerAddresses ca ON c.CustomerID = ca.CustomerID AND ca.IsDefault = 1
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID AND o.Status != 'Cancelled'
LEFT JOIN Payments p ON o.OrderID = p.OrderID AND p.Status = 'Paid'
GROUP BY c.CustomerID, c.FirstName, c.LastName, c.Email, c.Phone, ca.City, c.RegistrationDate;
GO

SELECT TOP 20 * FROM vw_CustomerMaster ORDER BY TotalSpend DESC;
GO

-- ==========================================
-- Q2) Product Catalog View (with Stock Status)
-- ==========================================
CREATE VIEW vw_ProductCatalog AS
SELECT 
    p.ProductID, 
    p.SKU, 
    p.ProductName, 
    c.CategoryName, 
    p.Price, 
    p.StockQuantity,
    CASE 
        WHEN p.StockQuantity <= 0 THEN 'Out of Stock'
        WHEN p.StockQuantity <= p.LowStockThreshold THEN 'Low Stock'
        ELSE 'In Stock'
    END AS StockStatus
FROM Products p
JOIN Categories c ON p.CategoryID = c.CategoryID;
GO

SELECT * FROM vw_ProductCatalog WHERE StockStatus IN ('Low Stock', 'Out of Stock');
GO

-- ==========================================
-- Q3) Daily Sales Summary (KPIs)
-- ==========================================
SELECT 
    CAST(o.OrderDate AS DATE) AS SalesDate,
    COUNT(DISTINCT o.OrderID) AS OrdersCount,
    ISNULL(SUM(p.Amount), 0) AS TotalRevenue,
    ISNULL(SUM(p.Amount) / NULLIF(COUNT(DISTINCT o.OrderID), 0), 0) AS AverageOrderValue,
    ISNULL(SUM(oi.Quantity), 0) AS ItemsSold
FROM Orders o
LEFT JOIN Payments p ON o.OrderID = p.OrderID AND p.Status = 'Paid'
LEFT JOIN OrderItems oi ON o.OrderID = oi.OrderID
WHERE CAST(o.OrderDate AS DATE) >= DATEADD(month, -1, GETDATE())
GROUP BY CAST(o.OrderDate AS DATE)
ORDER BY SalesDate DESC;
GO

-- ==========================================
-- Q4) Order Details View
-- ==========================================
CREATE VIEW vw_OrderDetails AS
SELECT 
    o.OrderID, 
    o.OrderDate, 
    c.FirstName + ' ' + c.LastName AS CustomerName,
    p.ProductName, 
    oi.Quantity, 
    oi.UnitPrice, 
    oi.LineTotal,
    pay.Status AS PaymentStatus, 
    shp.Status AS ShipmentStatus
FROM OrderItems oi
JOIN Orders o ON oi.OrderID = o.OrderID
JOIN Customers c ON o.CustomerID = c.CustomerID
JOIN Products p ON oi.ProductID = p.ProductID
LEFT JOIN Payments pay ON o.OrderID = pay.OrderID
LEFT JOIN Shipments shp ON o.OrderID = shp.OrderID;
GO

-- ==========================================
-- Q5) Cart-to-Order Conversion (Corrected)
-- ==========================================
SELECT 
    COUNT(c.CartID) AS TotalCartsCreated, -- هنا ضفنا الـ c. قبل CartID
    COUNT(o.OrderID) AS CartsConvertedToOrders,
    CAST(COUNT(o.OrderID) * 100.0 / NULLIF(COUNT(c.CartID), 0) AS DECIMAL(5,2)) AS ConversionRatePercent
FROM Carts c
LEFT JOIN Orders o ON c.CartID = o.CartID;
GO

-- ==========================================
-- Q6) Top Products by Category (Ranking)
-- ==========================================
WITH RankedProducts AS (
    SELECT 
        c.CategoryName,
        p.ProductName,
        SUM(oi.Quantity) AS TotalQuantitySold,
        DENSE_RANK() OVER (PARTITION BY c.CategoryName ORDER BY SUM(oi.Quantity) DESC) AS Rank
    FROM OrderItems oi
    JOIN Products p ON oi.ProductID = p.ProductID
    JOIN Categories c ON p.CategoryID = c.CategoryID
    GROUP BY c.CategoryName, p.ProductName
)
SELECT * FROM RankedProducts WHERE Rank <= 3;
GO

-- ==========================================
-- Q7) Returns & Refunds Analytics View
-- ==========================================
CREATE VIEW vw_ReturnRefundSummary AS
SELECT 
    r.ReturnID, 
    r.OrderID, 
    c.FirstName + ' ' + c.LastName AS CustomerName, 
    p.ProductName, 
    r.QuantityReturned,
    r.ReturnReason, 
    r.ReturnDate,
    rf.RefundAmount, 
    rf.RefundStatus, 
    rf.RefundDate
FROM Returns r
JOIN Customers c ON r.CustomerID = c.CustomerID
JOIN Products p ON r.ProductID = p.ProductID
LEFT JOIN Refunds rf ON r.ReturnID = rf.ReturnID;
GO

SELECT TOP 5 ReturnReason, COUNT(ReturnID) AS CountOfReturns 
FROM vw_ReturnRefundSummary 
GROUP BY ReturnReason ORDER BY CountOfReturns DESC;
GO

-- ==========================================
-- Q8) Delivery Performance & Delay Report
-- ==========================================
SELECT 
    c.CourierName,
    COUNT(s.ShipmentID) AS TotalShipments,
    SUM(CASE WHEN s.DeliveredDate <= s.ExpectedDate THEN 1 ELSE 0 END) AS OnTimeDeliveries,
    SUM(CASE WHEN s.DeliveredDate > s.ExpectedDate THEN 1 ELSE 0 END) AS LateDeliveries,
    AVG(DATEDIFF(day, s.ShippedDate, s.DeliveredDate)) AS AvgDeliveryDays
FROM Shipments s
JOIN Couriers c ON s.CourierID = c.CourierID
WHERE s.ShippedDate >= DATEADD(month, -3, GETDATE()) AND s.Status = 'Delivered'
GROUP BY c.CourierName;
GO

-- ==========================================
-- Q9) Revenue by Payment Method + Outstanding
-- ==========================================
SELECT 
    p.PaymentMethod,
    SUM(CASE WHEN p.Status = 'Paid' THEN p.Amount ELSE 0 END) AS TotalPaid,
    SUM(CASE WHEN p.Status IN ('Failed', 'Cancelled') THEN 1 ELSE 0 END) AS FailedOrCancelledCount,
    SUM(CASE WHEN shp.Status = 'Delivered' AND p.Status != 'Paid' THEN o.TotalAmount ELSE 0 END) AS TotalOutstanding
FROM Orders o
JOIN Payments p ON o.OrderID = p.OrderID
LEFT JOIN Shipments shp ON o.OrderID = shp.OrderID
WHERE FORMAT(o.OrderDate, 'yyyy-MM') = FORMAT(GETDATE(), 'yyyy-MM')
GROUP BY p.PaymentMethod;
GO

-- ==========================================
-- Q10) Customer Support SLA View
-- ==========================================
CREATE VIEW vw_SupportSLA AS
SELECT 
    t.TicketID, 
    c.FirstName + ' ' + c.LastName AS CustomerName, 
    t.CreatedAt, 
    t.ClosedAt, 
    t.Status, 
    t.Priority,
    DATEDIFF(hour, t.CreatedAt, ISNULL(t.ClosedAt, GETDATE())) AS ResolutionHours,
    CASE 
        WHEN t.Priority = 'Critical' AND DATEDIFF(hour, t.CreatedAt, ISNULL(t.ClosedAt, GETDATE())) > 24 THEN 'Yes'
        WHEN t.Priority = 'High' AND DATEDIFF(hour, t.CreatedAt, ISNULL(t.ClosedAt, GETDATE())) > 48 THEN 'Yes'
        WHEN t.Priority = 'Medium' AND DATEDIFF(hour, t.CreatedAt, ISNULL(t.ClosedAt, GETDATE())) > 72 THEN 'Yes'
        ELSE 'No' 
    END AS SLA_Breached
FROM SupportTickets t
JOIN Customers c ON t.CustomerID = c.CustomerID;
GO

SELECT * FROM vw_SupportSLA 
WHERE SLA_Breached = 'Yes' AND CreatedAt >= DATEADD(month, -1, GETDATE());
GO

-- =================================================================
-- 1.  Entering (Categories)
-- =================================================================
BULK INSERT [dbo].[Categories]
FROM 'D:\datamining proj\csv file\Categories.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY -
);
GO
PRINT 'Categories Loaded';

-- =================================================================
-- 2.  Entering (Couriers)
-- =================================================================
BULK INSERT [dbo].[Couriers]
FROM 'D:\datamining proj\csv file\Couriers.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY
);
GO
PRINT 'Couriers Loaded';

-- =================================================================
-- 3.  Entering (Customers)
-- =================================================================
BULK INSERT [dbo].[Customers]
FROM 'D:\datamining proj\csv file\Customers.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY
);
GO
PRINT 'Customers Loaded';

-- =================================================================
-- 4.  Entering CustomerAddresses
-- =================================================================
BULK INSERT [dbo].[CustomerAddresses]
FROM 'D:\datamining proj\csv file\CustomerAddresses.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY
);
GO
PRINT 'CustomerAddresses Loaded';

-- =================================================================
-- 5.   Entering Carts
-- =================================================================
BULK INSERT [dbo].[Carts]
FROM 'D:\datamining proj\csv file\Carts.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY
);
GO
PRINT 'Carts Loaded';

-- =================================================================
-- 6. Entering Orders
-- =================================================================
BULK INSERT [dbo].[Orders]
FROM 'D:\datamining proj\csv file\Orders.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY
);
GO
PRINT 'Orders Loaded';

-- =================================================================
-- 7. Invoice entry
-- =================================================================
BULK INSERT [dbo].[Invoices]
FROM 'D:\datamining proj\csv file\Invoices.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY
);
GO
PRINT 'Invoices Loaded';

-- =================================================================
-- 8.Entering Cart Items - Products must be present first!
-- =================================================================
BULK INSERT [dbo].[CartItems]
FROM 'D:\datamining proj\csv file\CartItems.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY
);
GO
PRINT 'CartItems Loaded';

-- =================================================================
-- 9. Entering order items (OrderItems) 
-- =================================================================
BULK INSERT [dbo].[OrderItems]
FROM 'D:\datamining proj\csv file\OrderItems.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK,
    KEEPIDENTITY
);
GO
PRINT 'OrderItems Loaded';