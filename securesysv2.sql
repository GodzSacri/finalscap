-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 18, 2025 at 02:00 PM
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
-- Database: `securesysv2`
--

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `sender_email` varchar(255) NOT NULL,
  `recipient_email` varchar(255) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `body` text NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_encrypted` tinyint(1) DEFAULT 0,
  `encrypted_key` text DEFAULT NULL,
  `attachment_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id`, `sender_email`, `recipient_email`, `subject`, `body`, `timestamp`, `is_encrypted`, `encrypted_key`, `attachment_path`) VALUES
(1, 'test1@gmail.com', 'test2@gmail.com', 'for capstone', 'hi', '2025-05-29 08:24:44', 0, NULL, NULL),
(2, 'test2@gmail.com', 'test1@gmail.com', 'for capstone', 'hello', '2025-05-29 08:25:34', 0, NULL, NULL),
(3, 'test1@gmail.com', 'test2@gmail.com', 'for capstone', 'hello', '2025-05-29 08:30:31', 0, NULL, NULL),
(4, 'test1@gmail.com', 'test2@gmail.com', 'for capstone', 'hello', '2025-05-29 08:30:47', 0, NULL, NULL),
(6, 'test1@gmail.com', 'test2@gmail.com', 'for capstone', 'p8GCivNsz0kY1czedSbxE5Hpr6pYpJs04gWuan1MWTuly8uHZcGlpbEjQr83AgJDQ34RLLOyjc/hMe+5G7fLR31dnAXOSR1ol8VvF4bTfap3eqR/8S01wOCSGrU3L6aZ7Pd6FYOcVd5PewZG4CpPawTB4EVXD89zQkEn224EFGmEzuaRwQ7uQ1DKMyy7hJwB8EcrIB/CKC1VAFM8caC1RihpbNuVvDIjkjWZsII5zjLGGIYQIBwLY8YY9DU6QU7TyligARXEKr53n6WOvHnp3Gyr+4rUb3Dq5vFtr0HdVUoAoaZURaPtUsDhtzFZ1ZFzNZD3MN5hmfLWUQQWTeTXGw==', '2025-05-29 08:35:30', 0, NULL, NULL),
(7, 'test2@gmail.com', 'test1@gmail.com', 'for capstone', 'HpXsqU9W9UIGjLc4rhKEHYFJEmA5kNuxRZTsIql5kX1+D+OTfMCCopC5k0RFAmBix38do0ef9agwMaSQmbOStWZ4Z/8QsToCG3NSU1KmPyxslSAHm77aS2Sl58ghJhn01RvNaH9NPh/62vagzP8VZT+E15I20a+hhny8SmA+LvyTWMA4uuM86ScMRRrJRRWiEx62b3U9EbWY7lQMoTe0BW2dZReOz0rA9zHdGynpBKvkEOxA8wKpKL8RRbY2/uhWsBMANDSrK7aJD7vJYOOnzTLWucexx10zvtxSknDDjjDO9x41uxIRyWP5CW6A/0NkpspNpfqqMleS1PWWJhdibw==', '2025-05-29 08:38:07', 0, NULL, NULL),
(8, 'test2@gmail.com', 'test1@gmail.com', 'for capstone', 'qqq', '2025-05-29 08:39:30', 0, NULL, NULL),
(9, 'test1@gmail.com', 'test2@gmail.com', 'for capstone', 'tapos muna', '2025-05-29 12:36:10', 0, NULL, NULL),
(10, 'test1@gmail.com', 'test2@gmail.com', 'something', 'happen', '2025-05-29 13:42:27', 0, NULL, NULL),
(11, 'kyru.roque.ui@phinmaed.com', 'monkjow@gmail.com', 'LNDlp5vZjTAspBO1p/LgTCesdvWCj8mEiyiN604GjZyUvlffC7T+yg==', 'K6lgt/MlsORfhNC9aPCLGpzQNw5mtKZY5xmrGiE1le81BM51oZE=', '2025-06-09 05:21:39', 1, 'f274875bde49ff4235525c70efe491f9f90928f3c7c3e5e9093d7175c328dfed', '495267943_1089105486396337_1437113086603602674_n.jpg'),
(12, 'kyru.roque.ui@phinmaed.com', 'monkjow@gmail.com', 'PSBtdEQG8PU6FQimZ/ggzBTjDNno+U/25B+Ow/O2L9wT4L76J7rmNw==', 'YAojTFV8yfc3UX8X48HOvmAgNu+Fx21+ADHnzQ4YcXhbZBRgAsQ=', '2025-06-09 10:23:37', 1, 'f274875bde49ff4235525c70efe491f9f90928f3c7c3e5e9093d7175c328dfed', NULL),
(13, 'monkjow@gmail.com', 'kyru.roque.ui@phinmaed.com', 'u1GZ5QG6qnxXEr+LzAJsm+z9zCBoKwL3x6Pfq6HjFZGzsQU1', 'FD+9apImVbLx7WKPxZ20vHik+IorTa7VdE750UqnsjNmQomGLvSp', '2025-06-11 04:40:04', 1, 'f274875bde49ff4235525c70efe491f9f90928f3c7c3e5e9093d7175c328dfed', NULL),
(14, 'kyru.roque.ui@phinmaed.com', 'monkjow@gmail.com', 'RE: (reply)', 'z8dOSPf7X2enAZPr0pJk+D9Ij7rWuLiWVmYNK+K56J3wOgnLMX8=', '2025-08-04 06:16:25', 1, 'f274875bde49ff4235525c70efe491f9f90928f3c7c3e5e9093d7175c328dfed', NULL),
(15, 'monkjow@gmail.com', 'kyru.roque.ui@phinmaed.com', 'RE: (reply)', 'F8nWH5Rw0r0g+h/rwsdDYogJpx9eNFJmkoqKLhYdLVr9ibkLz/9gFGWrTLz3xjVn', '2025-08-04 06:17:36', 1, 'f274875bde49ff4235525c70efe491f9f90928f3c7c3e5e9093d7175c328dfed', NULL),
(16, 'kyru.roque.ui@phinmaed.com', 'monkjow@gmail.com', 'Cf1WNzQoSkQKG7Kac0hBmp0j/otSNXtdK7+OdLryiiyv4A==', 'JICzKkUtUsfL4t0e7jnYNGJ8irYGHyfmu70ztBsrOT7mpPe0zqjHUPSQ1sQz', '2025-08-18 07:36:07', 1, 'f274875bde49ff4235525c70efe491f9f90928f3c7c3e5e9093d7175c328dfed', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `public_key` text DEFAULT NULL,
  `encryption_salt` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password_hash`, `public_key`, `encryption_salt`, `created_at`) VALUES
(2, 'test2@gmail.com', '$2b$12$vnDR1H6UfrZMlRMtb8jlber2gUiR2X51xERaY3D0NBM0.Xwnvkoy6', '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyv4VSseRLWEG/qXRzg+r\n3D3qlbdZa1L7Naa1GF7Rx1085IfeMCwspdC4buiNOu8Xm6Y3zzqcT1lNS3HNvyvT\npSV4k5DClGyMSlI/TiRjrzgO/iKYpr66m9nICkZW6TQ2sq6FXgswjzIoNpOnzJ8h\nR5GefBLinNsRU9qj3k3FQWr39/AtodDKHFxUp0ebGTdeZ0jHl7lK7GZgA/bL+UWb\nCvF5yj12liu2jMOyM70gQ0rcq/dTgj0mALuA2FBSNLlIvc5pqpM/EXLoDruQlp75\ncJ3+lyWexHUgzimwqUnAVIm46KuAt2NvXMhvZZ6QLGmYaVrqMZLfEIdgHto0+7sU\nCwIDAQAB\n-----END PUBLIC KEY-----\n', '$2b$12$SfCehVlJWw7NII7P1iEseu', '2025-05-29 06:29:51'),
(4, 'test1@gmail.com', '$2b$12$YtaYxqF5DkxxnSuUwHRxVuQHJF2XmddYDGLZRIzPYjZuzE71OOQ.G', '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAmHGk5UnIhWFPd5OftAE4\nana0gnTtqgnRUlnjeVBhVLNPpdHFUUsrh3LKj2Q3arhLPLJUwilez0kOjqC7v04U\nHxlPgyGmzi6PRAge/AiMI0p7lNAV/XLGMQxEOMV54h0fU4nhvLPALQbjpoKarDrs\nyvdlo71NWJ8dERCgzjMr+g7aU54wsrmtMv9vKkDUVy5Ar0zkqtTGo5DlogeRs4iT\nrn5O4gw4FnMY/zZq3y4cf+fvZQdEWAeuv1WellWqA+vLys481jZsmYTVQDS1YbSK\nfX3dlZWp4EEZJtihLyCMwYHJY568NND2tPkdB0HqYAvgyPPKEaIr9HhYFuFJCDpW\nmQIDAQAB\n-----END PUBLIC KEY-----\n', '$2b$12$Jum3lE7nk0H28MI3/jvm5u', '2025-05-29 08:09:46'),
(5, 'kyru.roque.ui@phinmaed.com', '$2b$12$5GJn5Rkp6fyYtjl7e4OjWeHc2u/cNFcKhCXe0Bni4unlByKnKQFa6', NULL, NULL, '2025-06-09 05:15:11'),
(6, 'monkjow@gmail.com', '$2b$12$AMen5ATwdg9cwfFxLdNUQux4vMA7/ZAzsjxmySWjenGhu8IFPF.vO', NULL, NULL, '2025-06-09 05:15:21');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_email` (`sender_email`),
  ADD KEY `recipient_email` (`recipient_email`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_email`) REFERENCES `users` (`email`),
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`recipient_email`) REFERENCES `users` (`email`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
