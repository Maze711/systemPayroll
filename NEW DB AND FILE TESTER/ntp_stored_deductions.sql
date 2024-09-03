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
-- Database: `ntp_stored_deductions`
--

-- --------------------------------------------------------

--
-- Table structure for table `deductions`
--

CREATE TABLE `deductions` (
  `ID` int(11) NOT NULL,
  `empNum` int(11) DEFAULT NULL,
  `bioNum` int(11) DEFAULT NULL,
  `empName` varchar(225) DEFAULT NULL,
  `payDed1` int(11) DEFAULT NULL,
  `payDed2` int(11) DEFAULT NULL,
  `payDed3` int(11) DEFAULT NULL,
  `payDed4` int(11) DEFAULT NULL,
  `payDed5` int(11) DEFAULT NULL,
  `payDed6` int(11) DEFAULT NULL,
  `payDed7` int(11) DEFAULT NULL,
  `payDed8` int(11) DEFAULT NULL,
  `payDed9` int(11) DEFAULT NULL,
  `payDed10` int(11) DEFAULT NULL,
  `payDed11` int(11) DEFAULT NULL,
  `payDed12` int(11) DEFAULT NULL,
  `payDed13` int(11) DEFAULT NULL,
  `payDed14` int(11) DEFAULT NULL,
  `deduction_placed_by` varchar(225) DEFAULT NULL,
  `deduction_placed_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `deductions`
--
ALTER TABLE `deductions`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `unique_entry` (`empNum`,`bioNum`,`empName`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `deductions`
--
ALTER TABLE `deductions`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
