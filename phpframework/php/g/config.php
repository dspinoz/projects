<?php

/**
 * Base configuration.
 */
class config_base
{
  public function __get($name)
  {
    return $this->$name;
  }
}

/**
 * Global configuration applicable to many components.
 */
class config_global extends config_base
{
  /**
   * @var Boolean True enables debug messages to be printed
   */
  private $debug;

  /**
   * @var String Path and name of a file to store debug messages. When set to
   * nothing (empty) should output using echo
   */
  private $debug_filename;

  /**
   * @var Boolean Determines if a unique log file should be created for each
   * unique request
   */
  private $debug_unique_log;

  /**
   * @var Boolean True prints the configuration settings and exits
   */
  private $print_config;

  public function __construct($array)
  {
    $this->debug = $array['debug'];
    $this->debug_filename = $array['debug_filename'];
    $this->print_config = $array['print_config'];
    $this->debug_unique_log = $array['debug_unique_log'];
  }

  public function __set($name,  $value)
  {
    if ($name == 'debug_filename')
    {
      $this->debug_filename = $value;
      return;
    }

    throw new Exception("Not allowed to access member {$name}");
  }

  public function __get($name)
  {
    return $this->$name;
  }
}

/**
 * Configuration applicable to utils package.
 */
class config_utils extends config_base
{
  /**
   * @var String Date format to use when printing log messages
   * @see date()
   */
  private $log_date_format;

  /**
   * @var Boolean Determines if "nice" URLs should be used.
   * This requires the htaccess.txt to be renamed to .htaccess
   */
  private $use_modrewrite;

  /**
   * @var String Relative path for where the framework is installed.
   * All links to pages are relative to this position
   */
  private $install_dir;

  public function __construct($array)
  {
    $this->log_date_format = $array['log_date_format'];
    $this->use_modrewrite = $array['use_modrewrite'];
    $this->install_dir = $array['install_dir'];
  }

  public function __get($name)
  {
    return $this->$name;
  }
}

/**
 * Configuration applicable for database functions.
 */
class config_db extends config_base
{
  /**
   * @var String database vendor, eg. mysql
   */
  private $vendor;

  /**
   * @var String Database host
   */
  private $host;

  /**
   * @var String Database user
   */
  private $user;

  /**
   * @var String Database password
   */
  private $password;

  /**
   * @var String Name of the database to connect
   */
  private $dbname;

  /**
   * @var String Version of the schema that has been installed
   */
  private $schema;

  public function __construct($array)
  {
    $this->vendor = $array['vendor'];
    $this->host = $array['host'];
    $this->user = $array['user'];
    $this->password = $array['password'];
    $this->dbname = $array['dbname'];
    $this->schema = $array['schema'];
  }

  public function __get($name)
  {
    return $this->$name;
  }
}

/**
 * Configuration for users of the site.
 */
class config_users extends config_base
{
  /**
   * @var Array List of valid usernames that have an associated entry in the passwords array
   */
  private $users;

  /**
   * @var Array List of passwords for each user
   */
  private $passwords;

  public function __construct($array)
  {
    $this->users = $array['users'];
    $this->passwords = $array['passwords'];

    if (count($this->users) != count($this->passwords))
    {
      throw new Exception("User configuration is incorrect");
    }
  }

  public function __get($name)
  {
    return $this->$name;
  }
}

/**
 * Configuration settings for the site.
 */
class config_site extends config_base
{
  /**
   * @var String Main title page for the site
   */
  private $title;
  
  /**
   * @var Array List of names for links to the "page" element in the URL
   */
  private $pages;

  /**
   * @var Array List of links that appear for each page
   */
  private $pagenames;

  /**
   * @var Array List of classes that are used to load the individual pages
   */
  private $pageclasses;

  public function __construct($array)
  {
    $this->title = $array['title'];
    $this->pages = $array['pages'];
    $this->pagenames = $array['pagenames'];
    $this->pageclasses = $array['pageclasses'];

    //ensure pages are setup correctly
    if (count($this->pages) != count ($this->pagenames) &&
      count($this->pages) != count($this->pageclasses))
    {
      throw new Exception("Page configuration is incorrect");
    }
  }

  public function __get($name)
  {
    return $this->$name;
  }
}

/**
 * Builds a list of configuration options.
 */
class config_builder
{
  private $global;
  private $site;
  private $database;
  private $users;
  private $utils;

  /**
   * Creates a new config_builder.
   * Throws an exception if an error occurs parsing configuration options.
   * @param Array $array List of configuration options
   */
  public function __construct($array)
  {
    try
    {
      $this->global = new config_global($array['global']);
      $this->site = new config_site($array['site']);
      $this->database = new config_db($array['database']);
      $this->users = new config_users($array['users']);
      $this->utils = new config_utils($array['utils']);
    }
    catch (Exception $e)
    {
      log_err($e->getMessage());
      die("Could not read site configuration");
    }
  }

  public function __get($name)
  {
    return $this->$name;
  }
}

?>
