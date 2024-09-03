-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 03, 2024 at 01:10 PM
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
-- Table structure for table `employee_notifications`
--

CREATE TABLE `employee_notifications` (
  `id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `message` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employee_notifications`
--

INSERT INTO `employee_notifications` (`id`, `employee_id`, `message`, `created_at`) VALUES
(1, 1, 'New employee added: TEST TEST', '2024-09-03 11:07:45');

-- --------------------------------------------------------

--
-- Table structure for table `paymaster_notification_user`
--

CREATE TABLE `paymaster_notification_user` (
  `ID` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `surname` varchar(225) NOT NULL,
  `firstname` varchar(255) NOT NULL,
  `mi` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `paymaster_notification_user`
--

INSERT INTO `paymaster_notification_user` (`ID`, `empl_id`, `surname`, `firstname`, `mi`) VALUES
(1, 20243182, 'TEST', 'TEST', 'TEST');

--
-- Triggers `paymaster_notification_user`
--
DELIMITER $$
CREATE TRIGGER `after_employee_insert` AFTER INSERT ON `paymaster_notification_user` FOR EACH ROW BEGIN
    INSERT INTO employee_notifications (employee_id, message)
    VALUES (NEW.id, CONCAT('New employee added: ', NEW.firstname, ' ', NEW.surname));
END
$$
DELIMITER ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `employee_notifications`
--
ALTER TABLE `employee_notifications`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `paymaster_notification_user`
--
ALTER TABLE `paymaster_notification_user`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `employee_notifications`
--
ALTER TABLE `employee_notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `paymaster_notification_user`
--
ALTER TABLE `paymaster_notification_user`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
