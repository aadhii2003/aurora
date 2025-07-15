-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 09, 2025 at 10:38 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_aurora`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_banner`
--

CREATE TABLE `tbl_banner` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text DEFAULT NULL,
  `image_url` varchar(255) NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `sort_order` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_banner`
--

INSERT INTO `tbl_banner` (`id`, `title`, `content`, `image_url`, `is_active`, `sort_order`, `created_at`) VALUES
(1, 'New Offers', 'the dream come with u form us ', '/static/uploads/banners/c07232b00b5843b0ae7ac2c6bce338c8_greenstone.jpg', 1, 1, '2025-07-09 07:33:21');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_cart`
--

CREATE TABLE `tbl_cart` (
  `id` int(11) NOT NULL,
  `login_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `product_size_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `prize` decimal(10,2) DEFAULT NULL,
  `order_status` varchar(20) DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_cart`
--

INSERT INTO `tbl_cart` (`id`, `login_id`, `product_id`, `product_size_id`, `quantity`, `created_at`, `updated_at`, `prize`, `order_status`) VALUES
(23, 3, 2, 10, 1, '2025-07-09 06:12:48', '2025-07-09 06:12:48', 99999999.99, 'pending'),
(24, 3, 4, 3, 1, '2025-07-09 06:23:18', '2025-07-09 06:23:18', 22222.00, 'pending');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_category`
--

CREATE TABLE `tbl_category` (
  `id` int(11) NOT NULL,
  `category_name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_category`
--

INSERT INTO `tbl_category` (`id`, `category_name`) VALUES
(2, 'daimonds'),
(3, 'gemstones'),
(1, 'normal stone');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_login`
--

CREATE TABLE `tbl_login` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `otp` varchar(6) DEFAULT NULL,
  `role` enum('admin','user') NOT NULL DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_login`
--

INSERT INTO `tbl_login` (`id`, `email`, `password`, `otp`, `role`) VALUES
(1, 'admin@gmail.com', '1234', '1234', 'admin'),
(2, 'adithyanair2003324@gmail.com', '123', NULL, 'user'),
(3, 'adithyanair2002324@gmail.com', '123', NULL, 'user');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_product`
--

CREATE TABLE `tbl_product` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `style` varchar(100) DEFAULT NULL,
  `images` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`images`)),
  `sub_category_id` int(11) NOT NULL,
  `status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `category_id` int(11) NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_on` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `updated_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_product`
--

INSERT INTO `tbl_product` (`id`, `name`, `description`, `style`, `images`, `sub_category_id`, `status`, `category_id`, `created_on`, `updated_on`, `updated_by`) VALUES
(2, 'ruby', 'RUBY GEM', 'redish', '[\"admin/img/40b1909f9ca840f9a08c1f9c54369685_rubey1.jpeg\"]', 1, 'active', 1, '2025-07-01 07:04:43', '2025-07-01 09:43:42', 1),
(4, 'Greenruby', 'mamamam', 'gemstone', '[\"admin/img/0e398ac906734bd0928f54e5d97f7fe8_greenruby.jpg\"]', 1, 'active', 3, '2025-07-01 07:13:44', '2025-07-01 07:13:44', 1),
(5, 'pearl', 'stylish', 'sssss', '[\"admin/img/40ff124e6632458bb60e00605236cbd5_pearl.jpg\"]', 1, 'active', 3, '2025-07-01 09:30:40', '2025-07-01 10:25:22', 1),
(8, 'december stone', 'mxskmxks', 'redish', '[\"admin/img/accd9ff8122a418cb195e17d232cbc55_greenstone.jpg\"]', 3, 'active', 3, '2025-07-03 09:02:59', '2025-07-03 09:06:41', 1),
(17, 'April Daimond', 'aaaaaqwswxexedc', 'Crystal', '[\"admin/img/cde0d5c70f5b4eed8a6a6cf62c719a47_april.webp\"]', 2, 'active', 1, '2025-07-03 09:28:49', '2025-07-03 09:28:49', 1);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_product_size`
--

CREATE TABLE `tbl_product_size` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `size` varchar(50) NOT NULL,
  `prize` decimal(10,2) NOT NULL,
  `offer_prize` decimal(10,2) DEFAULT NULL,
  `discount` decimal(5,2) DEFAULT NULL,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_on` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `updated_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_product_size`
--

INSERT INTO `tbl_product_size` (`id`, `product_id`, `size`, `prize`, `offer_prize`, `discount`, `created_on`, `updated_on`, `updated_by`) VALUES
(2, 5, '11.5 cm', 17777.00, 15999.30, 10.00, '2025-07-01 09:55:32', '2025-07-01 10:36:25', 1),
(3, 4, '12 cm', 22222.00, 19555.36, 12.00, '2025-07-01 10:32:54', '2025-07-01 10:32:54', 1),
(4, 5, '13.5 cm', 33222.00, 32889.78, 1.00, '2025-07-01 10:36:43', '2025-07-01 10:36:43', 1),
(5, 2, '12 cm', 2222333.00, 2200109.67, 1.00, '2025-07-03 08:41:46', '2025-07-03 08:41:46', 1),
(6, 2, '7.7 cm', 145567.00, 132465.97, 9.00, '2025-07-03 08:55:56', '2025-07-03 08:55:56', 1),
(7, 17, '5.4 cm', 123424.00, 120955.52, 2.00, '2025-07-03 09:39:32', '2025-07-03 09:39:32', 1),
(8, 8, '12.4 cm', 234455.00, 232110.45, 1.00, '2025-07-08 07:21:27', '2025-07-08 07:21:27', 1),
(9, 8, '11 cm', 124522.00, 109579.36, 12.00, '2025-07-08 07:21:43', '2025-07-08 07:21:43', 1),
(10, 2, '45 cm', 99999999.99, 99999999.99, 0.00, '2025-07-08 10:14:21', '2025-07-08 10:14:21', 1);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_purchase_child`
--

CREATE TABLE `tbl_purchase_child` (
  `id` int(11) NOT NULL,
  `purchase_id` int(11) NOT NULL,
  `product_size_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_prize` decimal(10,2) NOT NULL,
  `total_prize` decimal(10,2) NOT NULL,
  `tax` decimal(10,2) NOT NULL,
  `taxed_prize` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_purchase_child`
--

INSERT INTO `tbl_purchase_child` (`id`, `purchase_id`, `product_size_id`, `quantity`, `unit_prize`, `total_prize`, `tax`, `taxed_prize`) VALUES
(2, 6, 4, 2, 33222.00, 66444.00, 0.00, 66444.00),
(3, 6, 3, 2, 22222.00, 44444.00, 0.00, 44444.00),
(4, 6, 5, 1, 2222333.00, 2222333.00, 0.00, 2222333.00),
(5, 7, 3, 2, 22222.00, 44444.00, 0.00, 44444.00),
(7, 9, 4, 1, 33222.00, 33222.00, 0.00, 33222.00),
(11, 13, 3, 1, 22222.00, 22222.00, 0.00, 22222.00),
(12, 14, 9, 1, 124522.00, 124522.00, 0.00, 124522.00),
(13, 14, 10, 1, 99999999.99, 99999999.99, 0.00, 99999999.99),
(14, 15, 10, 1, 99999999.99, 99999999.99, 0.00, 99999999.99),
(15, 16, 3, 1, 22222.00, 22222.00, 0.00, 22222.00);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_purchase_master`
--

CREATE TABLE `tbl_purchase_master` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `shipping_address` text NOT NULL,
  `sub_total` decimal(10,2) NOT NULL,
  `tax` decimal(10,2) NOT NULL,
  `taxed_subtotal` decimal(10,2) NOT NULL,
  `status` enum('open','close') NOT NULL DEFAULT 'open',
  `payment_image` varchar(255) DEFAULT NULL,
  `payment_verify` enum('open','true','false') NOT NULL DEFAULT 'open'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_purchase_master`
--

INSERT INTO `tbl_purchase_master` (`id`, `user_id`, `shipping_address`, `sub_total`, `tax`, `taxed_subtotal`, `status`, `payment_image`, `payment_verify`) VALUES
(6, 1, 'santhosh bhavan muttar p.o alappuzha\r\nmuttar', 2333221.00, 0.00, 2333221.00, '', 'uploads/2_6_Screenshot_2023-11-09_142845.png', 'open'),
(7, 1, 'santhosh bhavan muttar p.o alappuzha\r\nmuttar', 44444.00, 0.00, 44444.00, '', 'uploads/2_7_Screenshot_2023-11-09_142836.png', 'open'),
(9, 4, 'santhosh bhavan muttar p.o alappuzha\r\nmuttar', 33222.00, 0.00, 33222.00, '', 'uploads/3_9_distribution_form.jpg', 'true'),
(13, 4, 'abdulkkkshjmcmjm\r\nkkaii', 22222.00, 0.00, 22222.00, '', '/static/uploads/3_13_WhatsApp_Image_2025-06-26_at_20.38.54_642a9313.jpg', 'false'),
(14, 4, 'abdulkkkshjmcmjm\r\nkkaii', 99999999.99, 0.00, 99999999.99, '', '/static/uploads/3_14_image.jpg', 'true'),
(15, 4, 'abdulkkkshjmcmjm\r\nkkaii', 99999999.99, 0.00, 99999999.99, '', '/static/uploads/3_15_distribution_form.jpg', 'true'),
(16, 4, 'abdulkkkshjmcmjm\r\nkkaii', 22222.00, 0.00, 22222.00, '', '/static/uploads/3_16_demo_resume.jpeg', 'open');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_stock`
--

CREATE TABLE `tbl_stock` (
  `id` int(11) NOT NULL,
  `product_size_id` int(11) NOT NULL,
  `stock_count` int(11) NOT NULL DEFAULT 0,
  `purchase_count` int(11) NOT NULL DEFAULT 0,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_on` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `updated_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_stock`
--

INSERT INTO `tbl_stock` (`id`, `product_size_id`, `stock_count`, `purchase_count`, `created_on`, `updated_on`, `updated_by`) VALUES
(1, 4, 5, 4, '2025-07-01 10:40:07', '2025-07-08 09:46:47', 1),
(2, 3, 13, 10, '2025-07-01 10:55:25', '2025-07-09 05:33:31', 1),
(5, 9, 21, 2, '2025-07-08 07:21:56', '2025-07-08 10:16:51', 1),
(6, 8, 11, 1, '2025-07-08 07:22:11', '2025-07-08 07:22:11', 1),
(7, 4, 10, 0, '2025-07-08 07:44:48', '2025-07-08 09:46:47', 1),
(9, 10, 3, 2, '2025-07-08 10:14:21', '2025-07-08 10:50:01', 1);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_subcategory`
--

CREATE TABLE `tbl_subcategory` (
  `id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `sub_category_name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_subcategory`
--

INSERT INTO `tbl_subcategory` (`id`, `category_id`, `sub_category_name`) VALUES
(3, 2, 'birth stone'),
(1, 3, 'green stone'),
(2, 3, 'red stone');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_tracking`
--

CREATE TABLE `tbl_tracking` (
  `id` int(11) NOT NULL,
  `purchase_id` int(11) NOT NULL,
  `status` enum('packed','shipped','delivered','returned','cancelled') NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_tracking`
--

INSERT INTO `tbl_tracking` (`id`, `purchase_id`, `status`, `date`) VALUES
(1, 9, '', '2025-07-08 05:26:46'),
(4, 13, '', '2025-07-08 07:53:34'),
(5, 14, '', '2025-07-08 10:16:51'),
(6, 15, '', '2025-07-08 10:50:01'),
(7, 16, '', '2025-07-09 05:33:31');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_user`
--

CREATE TABLE `tbl_user` (
  `id` int(11) NOT NULL,
  `login_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `shipping_address` text DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_user`
--

INSERT INTO `tbl_user` (`id`, `login_id`, `first_name`, `last_name`, `shipping_address`, `phone_number`) VALUES
(1, 2, 'Adithya', 'Nair', 'santhosh bhavan muttar p.o alappuzha\r\nmuttar', '09074997569'),
(4, 3, 'Adithya', 'Nair', 'abdulkkkshjmcmjm\r\nkkaii', '9074997569');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbl_banner`
--
ALTER TABLE `tbl_banner`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_cart`
--
ALTER TABLE `tbl_cart`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_category`
--
ALTER TABLE `tbl_category`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `category_name` (`category_name`);

--
-- Indexes for table `tbl_login`
--
ALTER TABLE `tbl_login`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `tbl_product`
--
ALTER TABLE `tbl_product`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sub_category_id` (`sub_category_id`),
  ADD KEY `category_id` (`category_id`),
  ADD KEY `updated_by` (`updated_by`);

--
-- Indexes for table `tbl_product_size`
--
ALTER TABLE `tbl_product_size`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `product_id` (`product_id`,`size`),
  ADD KEY `updated_by` (`updated_by`);

--
-- Indexes for table `tbl_purchase_child`
--
ALTER TABLE `tbl_purchase_child`
  ADD PRIMARY KEY (`id`),
  ADD KEY `purchase_id` (`purchase_id`),
  ADD KEY `product_size_id` (`product_size_id`);

--
-- Indexes for table `tbl_purchase_master`
--
ALTER TABLE `tbl_purchase_master`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `tbl_stock`
--
ALTER TABLE `tbl_stock`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_size_id` (`product_size_id`),
  ADD KEY `updated_by` (`updated_by`);

--
-- Indexes for table `tbl_subcategory`
--
ALTER TABLE `tbl_subcategory`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `category_id` (`category_id`,`sub_category_name`);

--
-- Indexes for table `tbl_tracking`
--
ALTER TABLE `tbl_tracking`
  ADD PRIMARY KEY (`id`),
  ADD KEY `purchase_id` (`purchase_id`);

--
-- Indexes for table `tbl_user`
--
ALTER TABLE `tbl_user`
  ADD PRIMARY KEY (`id`),
  ADD KEY `login_id` (`login_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tbl_banner`
--
ALTER TABLE `tbl_banner`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_cart`
--
ALTER TABLE `tbl_cart`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `tbl_category`
--
ALTER TABLE `tbl_category`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tbl_login`
--
ALTER TABLE `tbl_login`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tbl_product`
--
ALTER TABLE `tbl_product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `tbl_product_size`
--
ALTER TABLE `tbl_product_size`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `tbl_purchase_child`
--
ALTER TABLE `tbl_purchase_child`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `tbl_purchase_master`
--
ALTER TABLE `tbl_purchase_master`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `tbl_stock`
--
ALTER TABLE `tbl_stock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `tbl_subcategory`
--
ALTER TABLE `tbl_subcategory`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tbl_tracking`
--
ALTER TABLE `tbl_tracking`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `tbl_user`
--
ALTER TABLE `tbl_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_product`
--
ALTER TABLE `tbl_product`
  ADD CONSTRAINT `tbl_product_ibfk_1` FOREIGN KEY (`sub_category_id`) REFERENCES `tbl_subcategory` (`id`),
  ADD CONSTRAINT `tbl_product_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `tbl_category` (`id`),
  ADD CONSTRAINT `tbl_product_ibfk_3` FOREIGN KEY (`updated_by`) REFERENCES `tbl_login` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `tbl_product_size`
--
ALTER TABLE `tbl_product_size`
  ADD CONSTRAINT `tbl_product_size_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `tbl_product` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `tbl_product_size_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `tbl_login` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `tbl_purchase_child`
--
ALTER TABLE `tbl_purchase_child`
  ADD CONSTRAINT `tbl_purchase_child_ibfk_1` FOREIGN KEY (`purchase_id`) REFERENCES `tbl_purchase_master` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `tbl_purchase_child_ibfk_2` FOREIGN KEY (`product_size_id`) REFERENCES `tbl_product_size` (`id`);

--
-- Constraints for table `tbl_purchase_master`
--
ALTER TABLE `tbl_purchase_master`
  ADD CONSTRAINT `tbl_purchase_master_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tbl_user` (`id`);

--
-- Constraints for table `tbl_stock`
--
ALTER TABLE `tbl_stock`
  ADD CONSTRAINT `tbl_stock_ibfk_1` FOREIGN KEY (`product_size_id`) REFERENCES `tbl_product_size` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `tbl_stock_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `tbl_login` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `tbl_subcategory`
--
ALTER TABLE `tbl_subcategory`
  ADD CONSTRAINT `tbl_subcategory_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `tbl_category` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `tbl_tracking`
--
ALTER TABLE `tbl_tracking`
  ADD CONSTRAINT `tbl_tracking_ibfk_1` FOREIGN KEY (`purchase_id`) REFERENCES `tbl_purchase_master` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `tbl_user`
--
ALTER TABLE `tbl_user`
  ADD CONSTRAINT `tbl_user_ibfk_1` FOREIGN KEY (`login_id`) REFERENCES `tbl_login` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
