-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 27, 2024 at 11:40 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `InvoiceDB`
--

-- --------------------------------------------------------

--
-- Table structure for table `groups`
--

CREATE TABLE `groups` (
  `group_id` int(11) NOT NULL,
  `group_name` varchar(100) NOT NULL,
  `code` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `groups`
--

INSERT INTO `groups` (`group_id`, `group_name`, `code`) VALUES
(1, 'test1', 'C784RTE'),
(2, 'test2', '9IC67TJ');

-- --------------------------------------------------------

--
-- Table structure for table `Invoice`
--

CREATE TABLE `Invoice` (
  `InvoiceID` int(11) NOT NULL,
  `OrderNumber` varchar(20) NOT NULL,
  `Date` date NOT NULL,
  `Total` decimal(10,2) NOT NULL,
  `Tax` decimal(10,2) DEFAULT 0.00,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Invoice`
--

INSERT INTO `Invoice` (`InvoiceID`, `OrderNumber`, `Date`, `Total`, `Tax`, `group_id`) VALUES
(126, '451', '2024-11-19', 123.00, 12.00, 1),
(128, '4', '2024-11-19', 123.00, 12.00, 1),
(129, '14', '2024-11-19', 123.00, 12.00, 1),
(140, '2000127-21418074', '2024-11-19', 190.85, 2.44, 1);

-- --------------------------------------------------------

--
-- Table structure for table `InvoiceDetails`
--

CREATE TABLE `InvoiceDetails` (
  `DetailID` int(11) NOT NULL,
  `InvoiceID` int(11) NOT NULL,
  `ItemName` varchar(255) NOT NULL,
  `Quantity` int(11) NOT NULL,
  `Price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `InvoiceDetails`
--

INSERT INTO `InvoiceDetails` (`DetailID`, `InvoiceID`, `ItemName`, `Quantity`, `Price`) VALUES
(37, 140, 'Fresh Cauliflower, Each Weight-adjusted', 1, 3.42),
(38, 140, 'Fresh Green Seedless Grapes (2.25 lbs/Bag Est.) Weight-adjusted', 1, 4.02),
(39, 140, 'Fresh Whole Carrots, 1 lb Bag Weight-adjusted', 2, 1.96),
(40, 140, 'Fresh Roma Tomato, Each Weight-adjusted', 23, 5.34),
(41, 140, 'Marketside Fresh Organic Bananas, Bunch Weight-adjusted', 1, 2.12),
(42, 140, 'Fresh Yellow Onions, 3 lb Bag Weight-adjusted', 2, 5.36),
(43, 140, 'Fresh Banana, Each Weight-adjusted', 11, 1.88),
(44, 140, 'Fresh Gala Apples, 3 lb Bag Weight-adjusted', 1, 3.48),
(45, 140, 'Great Value Aluminum Foil, 25 sq ft Shopped', 1, 1.42),
(46, 140, 'Fresh Hass Avocados, Each Shopped', 5, 2.90),
(47, 140, 'Marketside Organic Cage-Free Large Brown Eggs, 12 Count Shopped', 1, 5.86),
(48, 140, 'Great Value Toilet Bowl Cleaners, Fresh Scent, 24 Fluid Ounce Shopped', 1, 1.92),
(49, 140, 'Marketside Fresh Spinach, 10 oz Bag, Fresh Shopped', 1, 1.98),
(50, 140, 'Marketside Fresh Green Beans, 12 oz Shopped', 1, 2.47),
(51, 140, 'Fresh Chile De Arbol, 4 Ounce Tray Shopped', 1, 2.98),
(52, 140, 'Great Value Peanut Oil, 1 gal Shopped', 1, 17.16),
(53, 140, 'Pompeian Made Easy Drizzle Extra Virgin Olive Oil - 16 fl oz Shopped', 1, 7.38),
(54, 140, 'Pepperidge Farm Farmhouse Hearty White Bread, 24 oz Loaf Shopped', 1, 3.84),
(55, 140, 'Great Value Drawstring Trash Bags 4 Gallon White Unscented 1 Pack 40 Count Shopped', 1, 4.98),
(56, 140, 'Pepsi Cola Soda Pop, 2 Liter Bottle Shopped', 2, 4.96),
(57, 140, 'Imperial Sugar Extra Fine Granulated Sugar, 4 lb Shopped', 1, 3.64),
(58, 140, 'Nescaf&reg; Clasico Dark Roast Instant Coffee, 10.5 oz Shopped', 1, 9.98),
(59, 140, '1lb Baby Peeled Carrots Shopped', 1, 1.32),
(60, 140, 'Yakult Non-Fat Live &Active Probiotic Drink Family Pack, 2.7 fl oz, 20 Count ,No Gluten, Plastic Bottle Shopped', 1, 12.52),
(61, 140, 'Great Value Purified Drinking Water, 16.9 fl oz Bottles, 40 Count Shopped', 3, 16.08),
(62, 140, 'Angel Soft 2-Ply Toilet Paper, 9 Mega Rolls Shopped', 1, 6.36),
(63, 140, 'Mainstays Lint Roller, 60 Sheets, 1-Count Shopped', 1, 0.98),
(64, 140, 'Great Value Premium Original Shells & Cheese, 12 oz Shelf Stable Shopped', 3, 4.44),
(65, 140, 'Fresh Red Onions, 3 lb Bag Shopped', 1, 3.98),
(66, 140, 'Great Value 1% Low-fat Chocolate Milk Gallon, Plastic, Jug, 128 Fl Oz Shopped', 2, 5.66),
(67, 140, 'Great Value 1% Low-fat Chocolate Milk Half Gallon, Plastic, Jug, 64 Fl Oz Shopped', 1, 1.72),
(68, 140, 'Great Value Milk Whole Vitamin D, Half Gallon, Plastic, Jug, 64oz Shopped', 2, 3.44),
(69, 140, 'Great Value Whole Vitamin D Milk, Gallon, Plastic, Jug, 128 Fl Oz Shopped', 4, 11.32),
(70, 140, 'Axe Apollo Long Lasting Men\'s Antiperspirant Deodorant Stick, Sage and Cedarwood, 2.7 oz Return complete', 1, 4.97),
(71, 140, 'AXE Phoenix 48H Anti Sweat High Definition Scent Men\'s Antiperspirant Deodorant, 2.7 oz Return complete', 1, 4.97),
(72, 140, 'Nov 19, 2024 order Genicook Bamboo Lid Sustainable Borosilicate Glass Container (22 oz) Return by mail', 1, 8.99);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `email`, `password`) VALUES
(1, 'asd', 'asd@asd.com', 'asd'),
(2, 'asdasdasa', 'asda@asda.com', 'asdasdasd'),
(3, 'asdaasda', 'asdasd@asdaad.com', 'Asdasdasd'),
(4, 'test', 'testDoc@gmail.com', 'asdasdasd'),
(5, 'asdasd', 'asd@asd.gmaill.com', 'asdasdsd'),
(6, 'testa', 'asd@gmail.com', 'asd'),
(7, 'testtest', 'test@test.com', 'asd'),
(8, 'avi', 'avi@test.com', 'avi');

-- --------------------------------------------------------

--
-- Table structure for table `user_groups`
--

CREATE TABLE `user_groups` (
  `user_group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `joined_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_groups`
--

INSERT INTO `user_groups` (`user_group_id`, `user_id`, `group_id`, `joined_at`) VALUES
(1, 1, 1, '2024-12-13 00:54:26'),
(2, 3, 1, '2024-12-13 00:54:26'),
(3, 1, 2, '2024-12-13 00:54:48'),
(4, 2, 2, '2024-12-13 00:54:48');

-- --------------------------------------------------------

--
-- Table structure for table `user_item_splits`
--

CREATE TABLE `user_item_splits` (
  `splitID` int(11) NOT NULL,
  `DetailID` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `split_amount` decimal(10,2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_item_splits`
--

INSERT INTO `user_item_splits` (`splitID`, `DetailID`, `user_id`, `split_amount`, `created_at`) VALUES
(5, 37, 1, 1.71, '2024-12-27 03:17:56'),
(6, 37, 2, 1.71, '2024-12-27 03:17:56'),
(7, 39, 1, 1.96, '2024-12-27 03:17:56'),
(8, 41, 2, 2.12, '2024-12-27 03:17:56');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `groups`
--
ALTER TABLE `groups`
  ADD PRIMARY KEY (`group_id`);

--
-- Indexes for table `Invoice`
--
ALTER TABLE `Invoice`
  ADD PRIMARY KEY (`InvoiceID`),
  ADD UNIQUE KEY `OrderNumber` (`OrderNumber`),
  ADD KEY `group_id_FK` (`group_id`);

--
-- Indexes for table `InvoiceDetails`
--
ALTER TABLE `InvoiceDetails`
  ADD PRIMARY KEY (`DetailID`),
  ADD KEY `InvoiceID` (`InvoiceID`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `user_groups`
--
ALTER TABLE `user_groups`
  ADD PRIMARY KEY (`user_group_id`),
  ADD UNIQUE KEY `unique_user_group` (`user_id`,`group_id`),
  ADD KEY `group_id` (`group_id`);

--
-- Indexes for table `user_item_splits`
--
ALTER TABLE `user_item_splits`
  ADD PRIMARY KEY (`splitID`),
  ADD UNIQUE KEY `unique_user_item` (`DetailID`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `groups`
--
ALTER TABLE `groups`
  MODIFY `group_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `Invoice`
--
ALTER TABLE `Invoice`
  MODIFY `InvoiceID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=142;

--
-- AUTO_INCREMENT for table `InvoiceDetails`
--
ALTER TABLE `InvoiceDetails`
  MODIFY `DetailID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=73;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `user_groups`
--
ALTER TABLE `user_groups`
  MODIFY `user_group_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `user_item_splits`
--
ALTER TABLE `user_item_splits`
  MODIFY `splitID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Invoice`
--
ALTER TABLE `Invoice`
  ADD CONSTRAINT `group_id_FK` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`);

--
-- Constraints for table `InvoiceDetails`
--
ALTER TABLE `InvoiceDetails`
  ADD CONSTRAINT `invoicedetails_ibfk_1` FOREIGN KEY (`InvoiceID`) REFERENCES `Invoice` (`InvoiceID`);

--
-- Constraints for table `user_groups`
--
ALTER TABLE `user_groups`
  ADD CONSTRAINT `user_groups_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `user_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`);

--
-- Constraints for table `user_item_splits`
--
ALTER TABLE `user_item_splits`
  ADD CONSTRAINT `user_item_splits_ibfk_1` FOREIGN KEY (`DetailID`) REFERENCES `InvoiceDetails` (`DetailID`),
  ADD CONSTRAINT `user_item_splits_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
