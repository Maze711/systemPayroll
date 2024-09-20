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
-- Database: `ntp_emp_rate`
--

-- --------------------------------------------------------

--
-- Table structure for table `emp_rate`
--

CREATE TABLE `emp_rate` (
  `ID` int(11) NOT NULL,
  `empl_no` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `empid` int(11) NOT NULL,
  `idnum` int(11) NOT NULL,
  `rph` int(16) NOT NULL,
  `rate` int(16) NOT NULL,
  `mth_salary` int(16) NOT NULL,
  `dailyallow` int(16) NOT NULL,
  `mntlyallow` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `emp_rate`
--

INSERT INTO `emp_rate` (`ID`, `empl_no`, `empl_id`, `empid`, `idnum`, `rph`, `rate`, `mth_salary`, `dailyallow`, `mntlyallow`) VALUES
(1, 1, 1, 1, 1, 1, 11, 1, 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `user_info`
--

CREATE TABLE `user_info` (
  `ID` int(11) NOT NULL,
  `empl_no` varchar(225) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `empid` int(11) NOT NULL,
  `idnum` int(11) NOT NULL,
  `surname` varchar(255) NOT NULL,
  `firstname` varchar(255) NOT NULL,
  `mi` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_info`
--

INSERT INTO `user_info` (`ID`, `empl_no`, `empl_id`, `empid`, `idnum`, `surname`, `firstname`, `mi`) VALUES
(1, '1', 1, 1, 1, 'TEST', 'TEST', 'TEST');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `emp_rate`
--
ALTER TABLE `emp_rate`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `user_info`
--
ALTER TABLE `user_info`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `emp_rate`
--
ALTER TABLE `emp_rate`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `user_info`
--
ALTER TABLE `user_info`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
