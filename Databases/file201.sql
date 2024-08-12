-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 12, 2024 at 03:06 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `file201`
--

-- --------------------------------------------------------

--
-- Table structure for table `educ_information`
--

CREATE TABLE `educ_information` (
  `ID` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `college` varchar(255) NOT NULL,
  `highSchool` varchar(255) NOT NULL,
  `elemSchool` varchar(255) NOT NULL,
  `collegeAdd` varchar(255) NOT NULL,
  `highschoolAdd` varchar(255) NOT NULL,
  `elemAdd` varchar(255) NOT NULL,
  `collegeCourse` varchar(255) NOT NULL,
  `highschoolStrand` varchar(255) NOT NULL,
  `collegeYear` varchar(255) NOT NULL,
  `highschoolYear` varchar(255) NOT NULL,
  `elemYear` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `emergency_list`
--

CREATE TABLE `emergency_list` (
  `ID` int(11) NOT NULL,
  `empl_no` varchar(225) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `emer_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `emp_info`
--

CREATE TABLE `emp_info` (
  `empl_no` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `idnum` int(11) NOT NULL,
  `surname` varchar(255) NOT NULL,
  `firstname` varchar(255) NOT NULL,
  `mi` varchar(255) NOT NULL,
  `suffix` varchar(255) NOT NULL,
  `street` varchar(255) NOT NULL,
  `barangay` varchar(255) NOT NULL,
  `city` varchar(225) NOT NULL,
  `province` varchar(255) NOT NULL,
  `zipcode` int(11) NOT NULL,
  `birthday` varchar(225) DEFAULT NULL,
  `birthplace` varchar(255) NOT NULL,
  `religion` varchar(225) NOT NULL,
  `citizenship` varchar(225) NOT NULL,
  `status` varchar(255) NOT NULL,
  `sex` enum('Male','Female') NOT NULL,
  `height` varchar(255) NOT NULL,
  `weight` varchar(255) NOT NULL,
  `mobile` varchar(225) NOT NULL,
  `email` varchar(225) NOT NULL,
  `blood_type` varchar(225) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `emp_list_id`
--

CREATE TABLE `emp_list_id` (
  `ID` int(11) NOT NULL,
  `empl_no` varchar(225) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `taxstat` int(16) NOT NULL,
  `sss` int(16) NOT NULL,
  `tin` int(16) NOT NULL,
  `pagibig` int(16) NOT NULL,
  `philhealth` int(16) NOT NULL,
  `account_no` int(16) NOT NULL,
  `bank_code` int(16) NOT NULL,
  `cola` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `emp_posnsched`
--

CREATE TABLE `emp_posnsched` (
  `ID` int(11) NOT NULL,
  `empl_no` varchar(225) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `pos_descr` varchar(255) NOT NULL,
  `sched_in` varchar(255) NOT NULL,
  `sched_out` varchar(225) NOT NULL,
  `dept_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `emp_rate`
--

CREATE TABLE `emp_rate` (
  `ID` int(11) NOT NULL,
  `empl_no` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `rph` int(16) NOT NULL,
  `rate` int(16) NOT NULL,
  `mth_salary` int(16) NOT NULL,
  `dailyallow` int(16) NOT NULL,
  `mnthallow` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `emp_status`
--

CREATE TABLE `emp_status` (
  `ID` int(11) NOT NULL,
  `empl_no` varchar(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `compcode` int(11) NOT NULL,
  `dept_code` int(11) NOT NULL,
  `position` varchar(225) NOT NULL,
  `emp_stat` varchar(225) NOT NULL,
  `date_hired` varchar(225) NOT NULL,
  `resigned` varchar(225) NOT NULL,
  `dtresign` varchar(225) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `family_background`
--

CREATE TABLE `family_background` (
  `ID` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `fathersLastName` varchar(255) NOT NULL,
  `fathersFirstName` varchar(255) NOT NULL,
  `fathersMiddleName` varchar(255) NOT NULL,
  `mothersLastName` varchar(255) NOT NULL,
  `mothersFirstName` varchar(255) NOT NULL,
  `mothersMiddleName` varchar(255) NOT NULL,
  `spouseLastName` varchar(255) NOT NULL,
  `spouseFirstName` varchar(255) NOT NULL,
  `spouseMiddleName` varchar(255) NOT NULL,
  `beneficiaryLastName` varchar(255) NOT NULL,
  `beneficiaryFirstName` varchar(255) NOT NULL,
  `beneficiaryMiddleName` varchar(255) NOT NULL,
  `dependentsName` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tech_skills`
--

CREATE TABLE `tech_skills` (
  `ID` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `techSkill1` varchar(255) NOT NULL,
  `certificate1` varchar(255) NOT NULL,
  `validationDate1` varchar(255) NOT NULL,
  `techSkill2` varchar(255) NOT NULL,
  `certificate2` varchar(255) NOT NULL,
  `validationDate2` varchar(255) NOT NULL,
  `techSkill3` varchar(255) NOT NULL,
  `certificate3` varchar(255) NOT NULL,
  `validationDate3` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vacn_sick_count`
--

CREATE TABLE `vacn_sick_count` (
  `ID` int(11) NOT NULL,
  `empl_id` varchar(255) NOT NULL,
  `max_vacn` varchar(255) NOT NULL,
  `max_sick` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `work_exp`
--

CREATE TABLE `work_exp` (
  `ID` int(11) NOT NULL,
  `empl_id` int(11) NOT NULL,
  `fromDate` varchar(255) NOT NULL,
  `toDate` varchar(255) NOT NULL,
  `companyName` varchar(255) NOT NULL,
  `companyAdd` varchar(255) NOT NULL,
  `empPosition` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `educ_information`
--
ALTER TABLE `educ_information`
  ADD PRIMARY KEY (`ID`) USING BTREE;

--
-- Indexes for table `emergency_list`
--
ALTER TABLE `emergency_list`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `emp_info`
--
ALTER TABLE `emp_info`
  ADD PRIMARY KEY (`empl_no`);

--
-- Indexes for table `emp_list_id`
--
ALTER TABLE `emp_list_id`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `emp_posnsched`
--
ALTER TABLE `emp_posnsched`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `emp_rate`
--
ALTER TABLE `emp_rate`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `emp_status`
--
ALTER TABLE `emp_status`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `family_background`
--
ALTER TABLE `family_background`
  ADD PRIMARY KEY (`ID`) USING BTREE;

--
-- Indexes for table `tech_skills`
--
ALTER TABLE `tech_skills`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `vacn_sick_count`
--
ALTER TABLE `vacn_sick_count`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `work_exp`
--
ALTER TABLE `work_exp`
  ADD PRIMARY KEY (`ID`) USING BTREE;

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `educ_information`
--
ALTER TABLE `educ_information`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `emergency_list`
--
ALTER TABLE `emergency_list`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `emp_info`
--
ALTER TABLE `emp_info`
  MODIFY `empl_no` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `emp_list_id`
--
ALTER TABLE `emp_list_id`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `emp_posnsched`
--
ALTER TABLE `emp_posnsched`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `emp_rate`
--
ALTER TABLE `emp_rate`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `emp_status`
--
ALTER TABLE `emp_status`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `family_background`
--
ALTER TABLE `family_background`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tech_skills`
--
ALTER TABLE `tech_skills`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `vacn_sick_count`
--
ALTER TABLE `vacn_sick_count`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `work_exp`
--
ALTER TABLE `work_exp`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
