-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 20, 2024 at 12:40 PM
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
-- Database: `ntp_accountant_notification`
--

-- --------------------------------------------------------

--
-- Table structure for table `paymaster_notification_user`
--

CREATE TABLE `paymaster_notification_user` (
  `ID` int(11) NOT NULL,
  `notif_count` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `surname` varchar(225) NOT NULL,
  `firstname` varchar(255) NOT NULL,
  `mi` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `paymaster_notification_user`
--

INSERT INTO `paymaster_notification_user` (`ID`, `notif_count`, `empl_id`, `surname`, `firstname`, `mi`) VALUES
(1, 1, 20243185, 'sfasf', 'afasf', 'sdasdasd'),
(2, 2, 20243186, 'dfgdfgdfg', 'dfg', 'dfgdfgfdgdfg'),
(3, 3, 20243187, 'asffaf', 'asdasdasd', 'asdasdasd'),
(4, 4, 20243188, 'asdasd', 'asdasdasd', 'asdasdasdasda');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `paymaster_notification_user`
--
ALTER TABLE `paymaster_notification_user`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `paymaster_notification_user`
--
ALTER TABLE `paymaster_notification_user`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
