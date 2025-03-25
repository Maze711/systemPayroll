-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 25, 2025 at 12:04 PM
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
-- Database: `ntp_holiday_list`
--

-- --------------------------------------------------------

--
-- Table structure for table `type_of_dates`
--

CREATE TABLE `type_of_dates` (
  `ID` int(11) NOT NULL,
  `holidayName` varchar(225) NOT NULL,
  `holidayDate` varchar(225) NOT NULL,
  `dateType` enum('Regular Holiday','Special Holiday') NOT NULL,
  `holidayIsMovable` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `type_of_dates`
--

INSERT INTO `type_of_dates` (`ID`, `holidayName`, `holidayDate`, `dateType`, `holidayIsMovable`) VALUES
(1, 'New Year\'s Day', '2024-01-01', 'Regular Holiday', 0),
(2, 'Maundy Thursday', '2024-03-28', 'Regular Holiday', 1),
(3, 'Good Friday', '2024-03-29', 'Regular Holiday', 1),
(4, 'Araw ng Kagitingan', '2024-04-09', 'Regular Holiday', 0),
(5, 'Labor Day', '2024-05-01', 'Regular Holiday', 0),
(6, 'Independence Day', '2024-06-12', 'Regular Holiday', 0),
(7, 'National Heroes Day', '2024-08-26', 'Regular Holiday', 0),
(8, 'Bonifacio Day', '2024-11-30', 'Regular Holiday', 0),
(9, 'Christmas Day', '2024-12-25', 'Regular Holiday', 0),
(10, 'Rizal Day', '2024-12-30', 'Regular Holiday', 0),
(11, 'Chinese New Year', '2024-02-10', 'Special Holiday', 1),
(12, 'EDSA Revolution ', '2024-02-25', 'Special Holiday', 0),
(13, 'Black Saturday', '2024-03-30', 'Special Holiday', 1),
(14, 'Ninoy Aquino Day', '2024-08-21', 'Special Holiday', 0),
(15, 'All Saints\' Day', '2024-11-01', 'Special Holiday', 0),
(16, 'All Souls\' Day', '2024-11-02', 'Special Holiday', 0),
(17, 'Feast of the Immaculate Conception', '2024-12-08', 'Special Holiday', 0),
(18, 'Christmas Eve', '2024-12-24', 'Special Holiday', 0),
(19, 'Last Day of the Year', '2024-12-31', 'Special Holiday', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `type_of_dates`
--
ALTER TABLE `type_of_dates`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `type_of_dates`
--
ALTER TABLE `type_of_dates`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
