-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 08, 2024 at 04:59 AM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `system_authentication`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `user_name` varchar(225) NOT NULL,
  `user_password` varchar(225) NOT NULL,
  `user_role` enum('HR','TimeKeeper','Accountant','Pay Master 1','Pay Master 2','Pay Master 3') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `user_name`, `user_password`, `user_role`) VALUES
(1, 'user_hr', '$2b$12$smYF3uwkMRBSNSOSanAVpuJ5HVuN9R/lWG8zZNlR6Iqpj1VqE5zRa', 'HR'),
(2, 'user_timekeeper', '$2b$12$CkNSJcz6j.abG2zSF5WjFuRD0zLsprFbdbImiQOE7TzITRflRM3pu', 'TimeKeeper'),
(3, 'user_accountant', '$2b$12$FoZp7cnbLCpBugJm8CpoLOttDqneUlDCEl9U7gpgkWYnhjODFhSAC', 'Accountant'),
(4, 'user_paymaster1', '$2b$12$m9hJDC7PrsJib5ao/7SeLeY9FlQMvHFiK0zQ4qpGcICI3OuKqHsdO', 'Pay Master 1'),
(5, 'user_paymaster2', '$2b$12$.ZhuQYQXaq1tIDfdsZAS1uYRpOBwaYrkf5Zs0UuLM3UP/LTdHu/SS', 'Pay Master 2'),
(6, 'user_paymaster3', '$2b$12$Lmw0zP8eeNTqD0AQhnPcbed0WP9Dc5V7OHwFQk41Mm.jOczSMmWIS', 'Pay Master 3');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
