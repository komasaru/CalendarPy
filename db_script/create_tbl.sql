-- MySQL dump 10.16  Distrib 10.2.12-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: calendar
-- ------------------------------------------------------
-- Server version	10.2.12-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dat_calendars`
--

DROP TABLE IF EXISTS `dat_calendars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dat_calendars` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gc_year` smallint(4) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `jd` decimal(10,3) NOT NULL,
  `yobi` tinyint(1) NOT NULL,
  `holiday` tinyint(2) NOT NULL,
  `kokei_sun` decimal(11,8) NOT NULL,
  `kokei_moon` decimal(11,8) NOT NULL,
  `moon_age` decimal(10,8) NOT NULL,
  `oc_year` smallint(4) NOT NULL,
  `oc_leap` tinyint(1) NOT NULL,
  `oc_month` smallint(2) NOT NULL,
  `oc_day` smallint(2) NOT NULL,
  `rokuyo` tinyint(1) NOT NULL,
  `kanshi` tinyint(2) NOT NULL,
  `sekki_24` smallint(3) NOT NULL,
  `zassetsu_1` tinyint(2) NOT NULL,
  `zassetsu_2` tinyint(2) NOT NULL,
  `sekku` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_1` (`gc_year`,`gc_month`,`gc_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dat_etcs`
--

DROP TABLE IF EXISTS `dat_etcs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dat_etcs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gc_year` smallint(4) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `jd` decimal(10,3) NOT NULL,
  `yobi` tinyint(1) NOT NULL,
  `kanshi` tinyint(2) NOT NULL,
  `moon_age` decimal(10,8) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_1` (`gc_year`,`gc_month`,`gc_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dat_holidays`
--

DROP TABLE IF EXISTS `dat_holidays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dat_holidays` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gc_year` smallint(4) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `holiday` tinyint(2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_1` (`gc_year`,`gc_month`,`gc_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dat_kokeis`
--

DROP TABLE IF EXISTS `dat_kokeis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dat_kokeis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gc_year` smallint(4) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `kokei_sun` decimal(11,8) NOT NULL,
  `kokei_moon` decimal(11,8) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_1` (`gc_year`,`gc_month`,`gc_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dat_moons`
--

DROP TABLE IF EXISTS `dat_moons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dat_moons` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gc_year` smallint(4) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `diff_kokei` smallint(3) NOT NULL,
  `gc_datetime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_1` (`gc_year`,`gc_month`,`gc_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dat_old_calendars`
--

DROP TABLE IF EXISTS `dat_old_calendars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dat_old_calendars` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gc_year` smallint(4) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `oc_year` smallint(4) NOT NULL,
  `oc_leap` tinyint(1) NOT NULL,
  `oc_month` smallint(2) NOT NULL,
  `oc_day` smallint(2) NOT NULL,
  `rokuyo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_1` (`gc_year`,`gc_month`,`gc_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dat_sekki24s`
--

DROP TABLE IF EXISTS `dat_sekki24s`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dat_sekki24s` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gc_year` smallint(4) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `kokei` smallint(3) NOT NULL,
  `gc_datetime` datetime DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `idx_1` (`gc_year`,`gc_month`,`gc_day`),
  KEY `idx_2` (`gc_year`,`kokei`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dat_zassetsus`
--

DROP TABLE IF EXISTS `dat_zassetsus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dat_zassetsus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gc_year` smallint(4) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `zassetsu_1` tinyint(2) NOT NULL,
  `zassetsu_2` tinyint(2) NOT NULL DEFAULT 99,
  PRIMARY KEY (`id`),
  KEY `idx_1` (`gc_year`,`gc_month`,`gc_day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_gengos`
--

DROP TABLE IF EXISTS `mst_gengos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_gengos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gengo` varchar(4) NOT NULL DEFAULT '',
  `kana` varchar(16) NOT NULL DEFAULT '',
  `date_fr` varchar(10) NOT NULL DEFAULT '0000-00-00',
  `date_to` varchar(10) NOT NULL DEFAULT '0000-00-00',
  `nanboku` varchar(1) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_gengo` (`gengo`),
  KEY `idx_kana` (`kana`),
  KEY `idx_date_ft` (`date_fr`),
  KEY `idx_date_to` (`date_to`),
  KEY `idx_nanboku` (`nanboku`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_holidays`
--

DROP TABLE IF EXISTS `mst_holidays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_holidays` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` smallint(2) NOT NULL,
  `gc_month` smallint(2) NOT NULL,
  `gc_day` smallint(2) NOT NULL,
  `etc` smallint(2) NOT NULL,
  `name` varchar(20) NOT NULL,
  `memo` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_kanshis`
--

DROP TABLE IF EXISTS `mst_kanshis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_kanshis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kbn` smallint(1) NOT NULL DEFAULT 9,
  `code` smallint(2) NOT NULL DEFAULT 99,
  `name` varchar(10) NOT NULL,
  `name_on` varchar(10) NOT NULL,
  `name_kun` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_1` (`kbn`,`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_months`
--

DROP TABLE IF EXISTS `mst_months`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_months` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `month` smallint(2) NOT NULL,
  `month_en` varchar(20) NOT NULL,
  `month_oc` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_month` (`month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_rokuyos`
--

DROP TABLE IF EXISTS `mst_rokuyos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_rokuyos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` smallint(1) NOT NULL DEFAULT 0,
  `name` varchar(20) NOT NULL,
  `memo` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_sekki24s`
--

DROP TABLE IF EXISTS `mst_sekki24s`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_sekki24s` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kokei` smallint(3) NOT NULL DEFAULT 0,
  `name` varchar(20) NOT NULL,
  `name_kana` varchar(20) NOT NULL,
  `setsu_chu` varchar(2) NOT NULL,
  `oc_month` smallint(2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_kokei` (`kokei`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_sekkus`
--

DROP TABLE IF EXISTS `mst_sekkus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_sekkus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` smallint(1) NOT NULL DEFAULT 0,
  `gc_month` smallint(2) NOT NULL DEFAULT 0,
  `gc_day` smallint(2) NOT NULL DEFAULT 0,
  `name` varchar(20) NOT NULL,
  `name_kana` varchar(20) NOT NULL,
  `memo` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_warekis`
--

DROP TABLE IF EXISTS `mst_warekis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_warekis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` smallint(1) NOT NULL,
  `name` varchar(20) NOT NULL,
  `year_f` smallint(4) NOT NULL,
  `month_f` smallint(2) NOT NULL,
  `day_f` smallint(2) NOT NULL,
  `year_t` smallint(4) NOT NULL,
  `month_t` smallint(2) NOT NULL,
  `day_t` smallint(2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_year_t` (`year_t`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_yobis`
--

DROP TABLE IF EXISTS `mst_yobis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_yobis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` smallint(1) NOT NULL DEFAULT 0,
  `name` varchar(2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mst_zassetsus`
--

DROP TABLE IF EXISTS `mst_zassetsus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mst_zassetsus` (
  `code` smallint(2) NOT NULL DEFAULT 99,
  `name` varchar(20) NOT NULL,
  `memo` varchar(250) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
