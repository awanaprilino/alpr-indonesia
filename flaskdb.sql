-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 29, 2023 at 08:02 PM
-- Server version: 10.4.20-MariaDB
-- PHP Version: 7.4.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `flaskdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `apps`
--

CREATE TABLE `apps` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `app_name` varchar(255) NOT NULL,
  `token` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `apps`
--

INSERT INTO `apps` (`id`, `user_id`, `app_name`, `token`, `created_at`) VALUES
(1, 1, 'test', 'o4VwCwTHK7QjijPapW7P', '2022-03-14 13:55:50');

-- --------------------------------------------------------

--
-- Table structure for table `license_plate`
--

CREATE TABLE `license_plate` (
  `id` bigint(20) NOT NULL,
  `app_id` bigint(20) NOT NULL,
  `plate_number` varchar(10) NOT NULL,
  `file` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `license_plate`
--

INSERT INTO `license_plate` (`id`, `app_id`, `plate_number`, `file`, `created_at`, `updated_at`) VALUES
(1, 1, 'PA61KK', 'static/storage/o4VwCwTHK7QjijPapW7P/2022-03-14-20-57-44.jpg', '2022-03-14 13:57:46', NULL),
(2, 1, 'PA61KK', 'static/storage/o4VwCwTHK7QjijPapW7P/2023-03-30-00-52-54.jpg', '2023-03-29 17:52:55', NULL),
(3, 1, '1909NR', 'static/storage/o4VwCwTHK7QjijPapW7P/2023-03-30-00-53-21.jpg', '2023-03-29 17:53:21', NULL),
(5, 1, 'B234KIL', 'static/storage/o4VwCwTHK7QjijPapW7P/2023-03-30-00-55-25.jpg', '2023-03-29 17:55:26', NULL),
(6, 1, '888S', 'static/storage/o4VwCwTHK7QjijPapW7P/2023-03-30-00-55-44.jpg', '2023-03-29 17:55:45', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` bigint(20) NOT NULL,
  `privilege` char(1) NOT NULL,
  `fname` varchar(255) NOT NULL,
  `lname` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `privilege`, `fname`, `lname`, `email`, `password`, `created_at`, `updated_at`) VALUES
(1, '1', 'Awan', 'Aprilino', 'admin@alpr.id', '$2b$12$Hha/Eo1pNAjXvhOVcwnqR.w23o/UNmELdTOyPkniIa5Y5coz52heC', '2022-03-14 13:54:33', '2022-03-14 13:54:48');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `apps`
--
ALTER TABLE `apps`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `license_plate`
--
ALTER TABLE `license_plate`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `apps`
--
ALTER TABLE `apps`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `license_plate`
--
ALTER TABLE `license_plate`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
