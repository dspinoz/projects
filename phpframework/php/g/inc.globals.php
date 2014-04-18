<?php
/** Global variables */

/** Specifies where the users' custom site files live */
define('G_USER_FILES', './usr');
/** Specifies where the php files live */
define('G_USER_PHP_FILES', G_USER_FILES .'/php');

/**
 * Configuration settings.
 */
$g_config = parse_ini_file("config/site.ini", true);

//print the configuration if told to do so
if ($g_config['global']['print_config'])
{
  print_r($g_config);
  exit;
}

$g_config = new config_builder($g_config);


?>
