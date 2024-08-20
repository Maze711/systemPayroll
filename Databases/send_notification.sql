-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 20, 2024 at 09:55 AM
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
-- Database: `system_notification`
--

-- --------------------------------------------------------

--
-- Table structure for table `send_notification`
--

CREATE TABLE `send_notification` (
  `ID` int(11) NOT NULL,
  `time` time NOT NULL,
  `message` text NOT NULL,
  `user_name` varchar(225) NOT NULL,
  `from_role` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `send_notification`
--

INSERT INTO `send_notification` (`ID`, `time`, `message`, `user_name`, `from_role`) VALUES
(1, '01:06:58', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(2, '01:12:53', 'File processed successfully: 1_attlogB.dat', 'user_timekeeper', 'TimeKeeper'),
(3, '01:14:45', 'File processed successfully: 1_attlogB.dat', 'user_timekeeper', 'TimeKeeper'),
(4, '01:17:18', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(5, '01:19:04', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(6, '01:20:10', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(7, '01:20:10', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(8, '01:34:38', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(9, '01:37:08', 'File processed successfully: 1_attlogA.dat', 'user_timekeeper', 'TimeKeeper'),
(10, '01:37:08', 'File processed successfully: 1_attlogB.dat', 'user_timekeeper', 'TimeKeeper'),
(11, '01:52:58', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(12, '01:53:53', 'File processed successfully: 1_attlogB.dat', 'user_timekeeper', 'TimeKeeper'),
(13, '07:17:28', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(14, '07:20:03', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(15, '07:20:03', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(16, '08:38:26', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(17, '08:43:18', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(18, '08:43:18', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(19, '10:08:05', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(20, '13:35:33', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(21, '14:57:16', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(22, '16:37:22', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(23, '16:54:55', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(24, '16:56:52', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(25, '17:03:00', 'Failed to process file: 1_attlogLeft.dat', 'user_timekeeper', 'TimeKeeper'),
(26, '17:03:00', 'Failed to process file: 1_attlogLeft.dat', 'user_timekeeper', 'TimeKeeper'),
(27, '17:03:00', 'File processed successfully: 1_attlogLeft.dat', 'user_timekeeper', 'TimeKeeper'),
(28, '17:03:00', 'File processed successfully: 1_attlogLeft.dat', 'user_timekeeper', 'TimeKeeper'),
(29, '17:12:34', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(30, '17:14:03', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(31, '17:21:01', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(32, '17:25:39', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(33, '17:29:42', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(34, '17:32:58', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(35, '17:34:02', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(36, '18:38:53', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(37, '20:00:26', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(38, '12:21:13', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(39, '12:23:15', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(40, '11:36:52', 'File processed successfully: 1_attlogLeft (1).dat', 'user_timekeeper', 'TimeKeeper'),
(41, '11:45:28', 'Failed to process file: 1_attlogLeft (1).dat', 'user_timekeeper', 'TimeKeeper'),
(42, '11:57:28', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(43, '11:57:28', 'File processed successfully: 1_attlog1.dat', 'user_timekeeper', 'TimeKeeper'),
(44, '11:57:28', 'File processed successfully: 1_attlog2.dat', 'user_timekeeper', 'TimeKeeper'),
(45, '11:57:28', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(46, '11:57:28', 'File processed successfully: 1_attlogLeft (1).dat', 'user_timekeeper', 'TimeKeeper'),
(47, '12:06:36', 'Failed to process file: 1_attlogB.dat', 'user_timekeeper', 'TimeKeeper'),
(48, '12:09:23', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(49, '12:32:07', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(50, '12:32:54', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(51, '12:50:40', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(52, '12:50:40', 'File processed successfully: 1_attlog2.dat', 'user_timekeeper', 'TimeKeeper'),
(53, '13:02:34', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(54, '13:06:03', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(55, '13:06:58', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(56, '13:09:25', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(57, '13:26:08', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(58, '14:00:56', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper'),
(59, '14:25:00', 'File processed successfully: 1_attlog3.dat', 'user_timekeeper', 'TimeKeeper');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `send_notification`
--
ALTER TABLE `send_notification`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `send_notification`
--
ALTER TABLE `send_notification`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=60;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
