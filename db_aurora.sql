-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 26, 2025 at 11:15 AM
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
-- Table structure for table `master_color`
--

CREATE TABLE `master_color` (
  `id` int(11) NOT NULL,
  `color_name` varchar(100) NOT NULL,
  `color_hex_code` varchar(10) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `master_color`
--

INSERT INTO `master_color` (`id`, `color_name`, `color_hex_code`, `status`) VALUES
(1, 'Red', '#BE2D25', 1),
(2, 'Green', '#38BE25', 1),
(5, 'white', '#FFFFFF', 1),
(6, 'silver', '#E0E0E0', 1),
(7, 'violet', '#AB47BC', 1),
(8, 'yellow', '#FDD835', 1),
(9, 'Blue', '#03A9F4', 1),
(10, 'pink', '#F938FC', 1);

-- --------------------------------------------------------

--
-- Table structure for table `master_shape`
--

CREATE TABLE `master_shape` (
  `id` int(11) NOT NULL,
  `shape_name` varchar(100) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `master_shape`
--

INSERT INTO `master_shape` (`id`, `shape_name`, `status`) VALUES
(1, 'Oval', 1),
(2, 'sprial', 1),
(5, 'heart', 1),
(6, 'Pear', 1);

-- --------------------------------------------------------

--
-- Table structure for table `master_weight_unit`
--

CREATE TABLE `master_weight_unit` (
  `id` int(11) NOT NULL,
  `unit_name` varchar(50) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `master_weight_unit`
--

INSERT INTO `master_weight_unit` (`id`, `unit_name`, `status`) VALUES
(3, 'carat(ct)', 1);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_admin_notifications`
--

CREATE TABLE `tbl_admin_notifications` (
  `id` int(11) NOT NULL,
  `message` text NOT NULL,
  `link_url` varchar(255) DEFAULT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_admin_notifications`
--

INSERT INTO `tbl_admin_notifications` (`id`, `message`, `link_url`, `is_read`, `created_at`) VALUES
(1, 'adithyanair2002324@gmail.com added an item to their cart for approval.', '/admin/admin-carts', 1, '2025-07-26 04:45:50'),
(2, 'New Order #26 was placed by A user.', '/admin/admin-order-details/26', 1, '2025-07-26 04:59:54'),
(3, 'adithyanair2002324@gmail.com added an item to their cart for approval.', '/admin/admin-carts', 1, '2025-07-26 06:05:19'),
(4, 'User adithyanair2002324@gmail.com requested a stock alert for: 1.37 ct Tanzanian Unheated Spinel – Vivid Cobalt-Blue Cushion (Size: 1.22 cm).', 'http://127.0.0.1:5001/admin/admin-update-stock', 1, '2025-07-26 07:49:53'),
(5, 'adithyanair2002324@gmail.com added an item to their cart for approval.', '/admin/admin-carts', 1, '2025-07-26 07:53:53'),
(6, 'adithyanair2002324@gmail.com added an item to their cart for approval.', '/admin/admin-carts', 1, '2025-07-26 07:54:11'),
(7, 'adithyanair2002324@gmail.com added an item to their cart for approval.', '/admin/admin-carts', 1, '2025-07-26 07:54:18'),
(8, 'adithyanair2002324@gmail.com added an item to their cart for approval.', '/admin/admin-carts', 1, '2025-07-26 07:54:31'),
(9, 'adithyanair2002324@gmail.com added an item to their cart for approval.', '/admin/admin-carts', 1, '2025-07-26 07:54:41'),
(10, 'User adithyanair2002324@gmail.com requested a stock alert for: 1.95ct Steel-Colored Heart-Shaped Tanzania Spinel | Rare & Untreated Gemstone (Size: 12.2 cm).', 'http://127.0.0.1:5001/admin/admin-update-stock', 1, '2025-07-26 07:55:04');

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
(2, 'Crafted by\nEarth, Perfected by Art', 'Discover unique treasures that tell a story. Each piece is selected for its unparalleled beauty and energetic properties.', '/static/uploads/banners/d1bb880f62ec4f37ad8fd284c9335863_freepik__the-style-is-candid-image-photography-with-natural__38869.jpeg', 1, 2, '2025-07-10 09:34:57');

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
  `status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  `admin_message` text DEFAULT NULL,
  `order_status` varchar(20) DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_cart`
--

INSERT INTO `tbl_cart` (`id`, `login_id`, `product_id`, `product_size_id`, `quantity`, `created_at`, `updated_at`, `prize`, `status`, `admin_message`, `order_status`) VALUES
(40, 4, 28, 18, 1, '2025-07-17 10:46:34', '2025-07-17 10:46:34', 19445.00, 'pending', NULL, 'pending'),
(54, 2, 29, 19, 1, '2025-07-24 10:48:27', '2025-07-24 11:01:39', 32234.00, 'approved', NULL, 'pending'),
(56, 2, 28, 18, 1, '2025-07-24 11:01:32', '2025-07-24 11:01:32', 19445.00, 'pending', NULL, 'pending'),
(63, 3, 23, 17, 1, '2025-07-26 07:54:31', '2025-07-26 07:54:31', 122232.00, 'pending', NULL, 'pending');

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
-- Table structure for table `tbl_inquiries`
--

CREATE TABLE `tbl_inquiries` (
  `id` int(11) NOT NULL,
  `type` varchar(50) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `message` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_inquiries`
--

INSERT INTO `tbl_inquiries` (`id`, `type`, `name`, `email`, `message`, `created_at`) VALUES
(1, 'Subscription', 'Adithya Nair', 'adithyanair2002324@gmail.com', NULL, '2025-07-26 05:40:46'),
(2, 'Contact', 'Adithya Nair', 'adithyanair2002324@gmail.com', 'contact me ', '2025-07-26 05:41:12'),
(3, 'Contact', 'Adithya Nair', 'adithyanair2002324@gmail.com', 'xaxzx', '2025-07-26 07:26:52'),
(4, 'Subscription', 'Adithya Nair', 'adithyanair2003324@gmail.com', NULL, '2025-07-26 07:27:10');

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
(3, 'adithyanair2002324@gmail.com', '123', NULL, 'user'),
(4, 'ad@gmail.com', '2414', NULL, 'user');

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
  `updated_by` int(11) DEFAULT NULL,
  `color_id` int(11) DEFAULT NULL,
  `shape_id` int(11) DEFAULT NULL,
  `videos` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`videos`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_product`
--

INSERT INTO `tbl_product` (`id`, `name`, `description`, `style`, `images`, `sub_category_id`, `status`, `category_id`, `created_on`, `updated_on`, `updated_by`, `color_id`, `shape_id`, `videos`) VALUES
(19, 'Neon-Red Spinel', 'Cushion Cut, Vivid Hot‑Pink Rare & Untreated Gemstone', 'neon', '[\"admin/img/027eec41e5cd4d8ebd04fe80671b5aba_0.95.webp\", \"admin/img/80ce68db38514bcf93a63c027f35446a_0.95-3.webp\", \"admin/img/d973f3fecc1e4a5e94ac8c0607520e45_0.95-4.webp\"]', 2, 'active', 1, '2025-07-09 10:17:31', '2025-07-11 09:58:57', 1, 1, 2, NULL),
(20, '0.95 ct Neon-Red Spinel – Natural Burmese Oval-Cushion Brilliant', '0.95 ct Neon-Red Spinel – Natural Burmese Oval-Cushion Brilliant', 'redish', '[\"admin/img/a3aca582dd1440d893caaa00c49cbefc_1.02.webp\", \"admin/img/d2a48b7174a444399f1196cbfa45efbe_1.02-3.webp\", \"admin/img/d15f6a6bf700446fbcf102bd2b644798_1.02-4.webp\"]', 2, 'active', 2, '2025-07-11 11:38:06', '2025-07-11 11:38:06', 1, 7, 2, NULL),
(22, '1.95ct Steel-Colored Heart-Shaped Tanzania Spinel | Rare & Untreated Gemstone', '1.95ct Steel-Colored Heart-Shaped Tanzania Spinel | Rare & Untreated Gemstone', 'Crystal', '[\"admin/img/e2a2dd9d6be24b97a527b950de46bdcf_1.95-2-1.webp\", \"admin/img/29d4e9f4e3dc4eefa6455ecbface9932_1.95-1-1.webp\", \"admin/img/09d4d9315cbb4d699fd857ce368ba738_1.95-4-1.webp\"]', 3, 'active', 3, '2025-07-12 08:58:23', '2025-07-12 08:58:23', 1, 6, 5, NULL),
(23, '1.09 ct Burmese Unheated Spinel – Candy-Pink Cushion', '1.09 ct Burmese Unheated Spinel – Candy-Pink Cushion', 'pinky', '[\"admin/img/449b42b0345349679425b46084ed06f4_1.09-1.webp\", \"admin/img/ec68b1a8e81d49a49d89ae31281318ce_1.09-3.webp\", \"admin/img/007b1c4a376443b5965b600212dbb743_1.09-4.webp\"]', 2, 'active', 2, '2025-07-14 06:40:18', '2025-07-25 05:21:38', 1, 10, 2, NULL),
(28, '1.22 ct Burmese Unheated Spinel – Candy-Pink Cushion', ' nasmqlq,lqzl,qz', 'gemstone', '[\"admin/img/59ffbdeb396c476aa846534ad49fa370_greencrytsl.jpeg\"]', 1, 'active', 2, '2025-07-17 05:18:25', '2025-07-17 05:18:25', 1, 2, 6, '[\"admin/vid/54a9adf150dd4901ac8227e39b6a585e_IMG_9388_compressed.mp4\", \"admin/vid/87ed1196229c4165bfa010f40405a334_IMG_9389_compressed.mp4\", \"admin/vid/6fd1521e37fd4acabd9909b0cc5e0aa3_IMG_9387_compressed.mp4\"]'),
(29, '1.37 ct Tanzanian Unheated Spinel – Vivid Cobalt-Blue Cushion', '1.37 ct Tanzanian Unheated Spinel – Vivid Cobalt-Blue Cushion', 'Crystal', '[\"admin/img/0c4ee42cd78b42e4b2b8f4dfd4c30f05_1.37.webp\", \"admin/img/ec60a57318c2429abcd9e6284415a444_1.37-3.webp\", \"admin/img/ee927e3c034e4ba5b4ae7020ff02e7bc_1.37-4.webp\"]', 3, 'active', 2, '2025-07-17 06:28:50', '2025-07-17 06:28:50', 1, 9, 6, '[\"admin/vid/15d0a354371f42edb48076a5bd396607_IMG_9389_compressed.mp4\", \"admin/vid/c8411ebfd0914c7c910854c8a7b60421_IMG_9388_compressed.mp4\"]');

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
  `updated_by` int(11) DEFAULT NULL,
  `weight` decimal(10,2) DEFAULT 0.00,
  `weight_unit_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_product_size`
--

INSERT INTO `tbl_product_size` (`id`, `product_id`, `size`, `prize`, `offer_prize`, `discount`, `created_on`, `updated_on`, `updated_by`, `weight`, `weight_unit_id`) VALUES
(11, 19, '10.9 cm', 65545.00, 60301.40, 8.00, '2025-07-09 10:41:08', '2025-07-25 05:20:25', 1, 2.30, 3),
(12, 20, '0.95 cm', 34756.00, 34408.44, 1.00, '2025-07-11 11:42:15', '2025-07-25 05:19:39', 1, 2.40, 3),
(14, 19, '10.3 cm', 56786.00, 49971.68, 12.00, '2025-07-12 05:05:05', '2025-07-25 05:20:25', 1, 1.30, 3),
(15, 22, '12.2 cm', 34543.00, 33852.14, 2.00, '2025-07-12 09:04:18', '2025-07-25 05:20:45', 1, 2.00, 3),
(16, 23, '1.09 cm', 23456.00, 22986.88, 2.00, '2025-07-14 07:07:43', '2025-07-25 05:20:05', 1, 2.50, 3),
(17, 23, '1.9 cm', 122232.00, 121009.68, 1.00, '2025-07-14 12:48:50', '2025-07-25 05:20:05', 1, 2.60, 3),
(18, 28, '12.4 cm', 19445.00, 19056.10, 2.00, '2025-07-17 05:33:19', '2025-07-25 05:21:11', 1, 1.40, 3),
(19, 29, '1.22 cm', 32234.00, 31589.32, 2.00, '2025-07-22 10:19:01', '2025-07-25 05:21:22', 1, 1.22, 3),
(20, 28, '3.4 cm', 234562.00, 180612.74, 23.00, '2025-07-22 10:28:34', '2025-07-25 05:21:11', 1, 1.50, 3);

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
(17, 18, 15, 1, 34543.00, 34543.00, 0.00, 34543.00),
(18, 19, 16, 1, 23456.00, 23456.00, 0.00, 23456.00),
(19, 20, 11, 1, 65545.00, 65545.00, 0.00, 65545.00),
(20, 20, 12, 1, 34756.00, 34756.00, 0.00, 34756.00),
(23, 22, 12, 1, 34756.00, 34756.00, 0.00, 34756.00),
(24, 22, 19, 1, 32234.00, 32234.00, 0.00, 32234.00),
(25, 23, 16, 1, 23456.00, 23456.00, 0.00, 23456.00),
(27, 25, 18, 1, 19445.00, 19445.00, 0.00, 19445.00),
(28, 26, 12, 1, 34756.00, 34756.00, 0.00, 34756.00);

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
  `payment_verify` enum('open','true','false') NOT NULL DEFAULT 'open',
  `purchase_date` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_purchase_master`
--

INSERT INTO `tbl_purchase_master` (`id`, `user_id`, `shipping_address`, `sub_total`, `tax`, `taxed_subtotal`, `status`, `payment_image`, `payment_verify`, `purchase_date`) VALUES
(18, 4, 'abdulkkkshjmcmjm\r\nkkaii', 34543.00, 0.00, 34543.00, '', '/static/uploads/3_18_Screenshot_2023-11-09_142836.png', 'true', '2025-07-12 15:44:24'),
(19, 4, 'abdulkkkshjmcmjm\r\nkkaii', 23456.00, 0.00, 23456.00, '', '/static/uploads/3_19_image_1.jpg', 'true', '2025-07-14 13:12:33'),
(20, 4, 'abdulkkkshjmcmjm\r\nkkaii', 100301.00, 0.00, 100301.00, '', '/static/uploads/3_20_image_1.jpg', 'true', '2025-07-14 18:11:17'),
(22, 4, 'kkaii', 66990.00, 0.00, 66990.00, '', '/static/uploads/3_22_distribution_form.jpg', 'true', '2025-07-23 18:31:22'),
(23, 7, 'mkmskmlsa', 23456.00, 0.00, 23456.00, '', '/static/uploads/2_23_Screenshot_9-4-2024_125921_echallan.parivahan.gov.in.jpeg', 'open', '2025-07-24 16:31:08'),
(25, 4, 'kkaii', 19445.00, 0.00, 19445.00, '', '/static/uploads/3_25_Screenshot_9-4-2024_125921_echallan.parivahan.gov.in.jpeg', 'true', '2025-07-25 10:16:37'),
(26, 4, 'santhosh bhavan muttar p.o alappuzha ', 34756.00, 0.00, 34756.00, '', '/static/uploads/3_26_Screenshot_2023-11-09_141459.png', 'open', '2025-07-26 10:29:54');

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
(11, 11, 9, 1, '2025-07-10 07:06:14', '2025-07-14 12:41:17', 1),
(12, 12, 7, 4, '2025-07-11 11:44:45', '2025-07-26 04:59:54', 1),
(14, 15, 1, 1, '2025-07-12 09:04:53', '2025-07-12 10:14:24', 1),
(15, 16, 3, 3, '2025-07-14 07:07:55', '2025-07-24 11:01:08', 1),
(16, 18, 5, 5, '2025-07-17 05:33:30', '2025-07-25 04:46:37', 1),
(17, 19, 5, 5, '2025-07-22 10:23:42', '2025-07-25 04:30:25', 1),
(18, 20, 3, 1, '2025-07-22 10:28:52', '2025-07-22 10:29:29', 1),
(19, 17, 2, 1, '2025-07-24 09:51:36', '2025-07-25 06:30:13', 1);

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
(9, 18, '', '2025-07-12 10:14:24'),
(10, 19, '', '2025-07-14 07:42:33'),
(11, 20, '', '2025-07-14 12:41:17'),
(13, 22, '', '2025-07-23 13:01:23'),
(14, 23, '', '2025-07-24 11:01:08'),
(16, 25, '', '2025-07-25 04:46:37'),
(17, 26, '', '2025-07-26 04:59:54');

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
  `phone_number` varchar(15) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `pincode` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_user`
--

INSERT INTO `tbl_user` (`id`, `login_id`, `first_name`, `last_name`, `shipping_address`, `phone_number`, `city`, `state`, `country`, `pincode`) VALUES
(4, 3, 'Adithya', 'Nair', 'santhosh bhavan muttar p.o alappuzha ', '9074997569', 'alappuzha', 'Kerala', 'India', '689574'),
(7, 2, 'aadhii', 'Nair', 'mkmskmlsa', '09074997569', 'alappuzha', 'Afrikaans', 'India', '689474');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `master_color`
--
ALTER TABLE `master_color`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `master_shape`
--
ALTER TABLE `master_shape`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `master_weight_unit`
--
ALTER TABLE `master_weight_unit`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_admin_notifications`
--
ALTER TABLE `tbl_admin_notifications`
  ADD PRIMARY KEY (`id`);

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
-- Indexes for table `tbl_inquiries`
--
ALTER TABLE `tbl_inquiries`
  ADD PRIMARY KEY (`id`);

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
  ADD KEY `updated_by` (`updated_by`),
  ADD KEY `color_id` (`color_id`),
  ADD KEY `shape_id` (`shape_id`);

--
-- Indexes for table `tbl_product_size`
--
ALTER TABLE `tbl_product_size`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `product_id` (`product_id`,`size`),
  ADD KEY `updated_by` (`updated_by`),
  ADD KEY `weight_unit_id` (`weight_unit_id`);

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
-- AUTO_INCREMENT for table `master_color`
--
ALTER TABLE `master_color`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `master_shape`
--
ALTER TABLE `master_shape`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `master_weight_unit`
--
ALTER TABLE `master_weight_unit`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tbl_admin_notifications`
--
ALTER TABLE `tbl_admin_notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `tbl_banner`
--
ALTER TABLE `tbl_banner`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tbl_cart`
--
ALTER TABLE `tbl_cart`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- AUTO_INCREMENT for table `tbl_category`
--
ALTER TABLE `tbl_category`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tbl_inquiries`
--
ALTER TABLE `tbl_inquiries`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tbl_login`
--
ALTER TABLE `tbl_login`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tbl_product`
--
ALTER TABLE `tbl_product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `tbl_product_size`
--
ALTER TABLE `tbl_product_size`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `tbl_purchase_child`
--
ALTER TABLE `tbl_purchase_child`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `tbl_purchase_master`
--
ALTER TABLE `tbl_purchase_master`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `tbl_stock`
--
ALTER TABLE `tbl_stock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `tbl_subcategory`
--
ALTER TABLE `tbl_subcategory`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tbl_tracking`
--
ALTER TABLE `tbl_tracking`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `tbl_user`
--
ALTER TABLE `tbl_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_product`
--
ALTER TABLE `tbl_product`
  ADD CONSTRAINT `tbl_product_ibfk_1` FOREIGN KEY (`sub_category_id`) REFERENCES `tbl_subcategory` (`id`),
  ADD CONSTRAINT `tbl_product_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `tbl_category` (`id`),
  ADD CONSTRAINT `tbl_product_ibfk_3` FOREIGN KEY (`updated_by`) REFERENCES `tbl_login` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `tbl_product_ibfk_4` FOREIGN KEY (`color_id`) REFERENCES `master_color` (`id`),
  ADD CONSTRAINT `tbl_product_ibfk_5` FOREIGN KEY (`shape_id`) REFERENCES `master_shape` (`id`);

--
-- Constraints for table `tbl_product_size`
--
ALTER TABLE `tbl_product_size`
  ADD CONSTRAINT `tbl_product_size_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `tbl_product` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `tbl_product_size_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `tbl_login` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `tbl_product_size_ibfk_3` FOREIGN KEY (`weight_unit_id`) REFERENCES `master_weight_unit` (`id`);

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
