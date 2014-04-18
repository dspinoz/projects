<?php

/** Utility functions */

/**
 * Converts a given name of a file to something that is more widely supported.
 * Only allows alphanumeric characters.
 * @param String $name Original name of the file/directory
 * @return String New name of the file, where non-alphanumeric characters have
 * been replaced with a '_'
 */
function nice_filename($name)
{
  return preg_replace("(\W)", '_', strtolower($name));
}

/**
 * Create a link to a page as per the setup described in the configuration file.
 * @param String $mode The mode for the request; either page, ajax or submit
 * @param String $page The name of the page that is handling the mode
 * @param String $request The name of a specific request (when in submit or ajax mode)
 * @param String $extra Extra arguments posted in URL format
 * @return The URI that correctly describes the link and additional parameters
 * that may be required as part of the request
 */
function create_uri($mode='page', $page='home', $request=NULL, $extra='')
{
  $uri = get_config()->utils->install_dir;

  if (get_config()->utils->use_modrewrite)
  {
    //use nice urls
    $uri .= "{$mode}/{$page}";
    
    if ($mode == 'submit' || $mode == 'ajax')
    {
      $uri .= "/{$request}";
    }
    
    if (!empty($extra))
    {
      $uri .= "/{$extra}";
    }
    else
    {
      $uri .= "/";
    }
  }
  else
  {
    //use default urls - naughty
    $uri .= "index.php?mode={$mode}&page={$page}";

    if ($mode == 'submit')
    {
      $uri .= "&submit={$request}";
    }
    else if ($mode == 'ajax')
    {
      $uri .= "&request={$request}";
    }

    if (!empty($extra))
    {
      $uri .= "{$extra}";
    }
  }

  $uri = htmlentities($uri);
  
  log_debug("Creating uri for mode:{$mode}, page:{$page} [{$uri}]",
    $request == NULL && empty($extra));
  log_debug("Creating uri for mode:{$mode}, page:{$page}, request:{$request} [{$uri}]",
    !empty($request) && empty($extra));
  log_debug("Creating uri for mode:{$mode}, page:{$page}, request:{$request}, extra:{$extra} [{$uri}]",
    $request != NULL && !empty($extra));
  
  return $uri;
}

/**
 * Includes user php files.
 * @param String $dir Directory to load user files from. Recursive beginning
 * from G_USER_PHP_FILES.
 */
function include_user_files($dir=G_USER_PHP_FILES)
{
  log_debug("include_user_files( {$dir} )");

  if (file_exists($dir) && is_dir($dir))
  {
    $usr = opendir($dir);

    if ($usr)
    {
      while (false !== ($f = readdir($usr)))
      {
        if ($f == '.' || $f == '..')
        {
          continue;
        }

        $fn = "{$dir}/{$f}";

        if (is_dir($fn))
        {
          include_user_files($fn);
        }
        else if (is_file($fn))
        {
          log_debug("Including file {$fn}");
          include_once($fn);
        }
      }

      closedir($usr);
    }
  }
}


/**
 * Gets the global configuration options.
 * @global config_builder $g_config
 * @return config_builder that contains the configuration for the site
 */
function get_config()
{
  global $g_config;
  return $g_config;
}

/**
 * Utility method to split the input and return an array of tokens.
 * @param String $input Input string
 * @param String $tokens List of tokens to split the input
 * @return Array Containing all the token values
 */
function get_tokens($input, $tokens)
{
  $ret = array();
  $tok = strtok($input, $tokens);
  while ($tok !== false)
  {
    array_push($ret, $tok);
    $tok = strtok($tokens);
  }
  return $ret;
}

/**
 * Write a message to the log file.
 * @param String $msg Message to write
 * @param Boolean $condition Determines if the message is written,
 *   default = true.
 * @param String $mode Text to appear at the front of the log record,
 *   default = ERROR.
 */
function log_err($msg, $condition=true, $mode='ERROR')
{
  log_msg($msg, $condition, $mode);
}

/**
 * Write a message to the log file.
 * @param String $msg Message to write
 * @param Boolean $condition Determines if the message is written,
 *   default = true.
 * @param String $mode Text to appear at the front of the log record,
 *   default = DEBUG.
 */
function log_debug($msg, $condition=true, $mode='DEBUG')
{
  log_msg($msg, $condition, $mode);
}

/**
 * Write a message to the log file.
 * @param String $msg Message to write
 * @param Boolean $condition Determines if the message is written,
 *   default = true.
 * @param String $mode Text to appear at the front of the log record,
 *   default = WARN.
 */
function log_warn($msg, $condition=true, $mode='WARN')
{
  log_msg($msg, $condition, $mode);
}

/**
 * Write a message to the log file.
 * @param String $msg Message to write
 * @param Boolean $condition Determines if the message is written,
 *   default = true.
 * @param String $mode Text to appear at the front of the log record,
 *   default = INFO.
 * @return Boolean True if successful, false on error
 */
function log_msg($msg, $condition=true, $mode='INFO')
{
	if ($mode == 'DEBUG' && !get_config()->global->debug)
	{
		// mode disabled
		return true;
	}

  if (get_config()->global->debug_filename && $condition)
  {
    $log_entry = date(get_config()->utils->log_date_format) .' '. $mode .' '. $msg;
    
    $df = get_config()->global->debug_filename;

    if (!empty($df))
    {
      if (!file_exists($df))
      {
        if (!touch($df))
        {
          echo 'ERROR: Could not create debug_filename: '. $df ."\n";
          return false;
        }
      }

      $f = fopen($df, 'a');

      if (!$f)
      {
        echo 'ERROR: Could not open debug_filename: '. $df ."\r\n";
        return false;
      }

      if (!fwrite($f, $log_entry."\r\n"))
      {
        echo 'ERROR: Could not write to debug_filename: '. $df ."\r\n";
        fclose($f);
        return false;
      }

      if (!fclose($f))
      {
        echo 'ERROR: Could not close debug_filename: '. $df ."\r\n";
        return false;
      }
    }
    else
    {
      echo '<pre class="debug">'.$log_entry.'<br>'.'</pre>';
    }
  }

  return true;
}

/**
 * Generates an information message with the correct styles.
 * @param String $html HTML code within the message
 * @return String HTML code wrapped in an information message style
 */
function msg_info($html)
{
  return '<div class="msg-info">'.$html.'</div>';
}

/**
 * Generates an error message with the correct styles.
 * @param String $html HTML code within the message
 * @return String HTML code wrapped in an error message style
 */
function msg_error($html)
{
  return '<div class="msg-error">'.$html.'</div>';
}

/**
 * Calculate the time taken to generate the page.
 * @staticvar Previous $a First time the function was called
 * @return Number of seconds taken to generate the page
 */
function calc_gen_time()
{
  static $a = NULL;

  if ($a == NULL)
  {
    $a = microtime(true);
  }
  else
  {
    $b = (microtime(true) - $a);
    $a = NULL;

    log_debug('Page generated in '. number_format($b, 3) .' sec');

    return $b;
  }
}

/**
 * Generate a random string.
 * @param Number $length Number of characters
 * @param String $chars Characters to include
 * @return String A random string
 */
function rand_str(
  $length = 32,
  $chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890')
{
  // Length of character list
  $chars_length = (strlen($chars) - 1);

  // Start our string
  $string = $chars{rand(0, $chars_length)};

  // Generate random string
  for ($i = 1; $i < $length; $i = strlen($string))
  {
    // Grab a random character from our list
    $r = $chars{rand(0, $chars_length)};

    // Make sure the same two characters don't appear next to each other
    if ($r != $string{$i - 1}) $string .=  $r;
  }

  return $string;
}

/**
 * @Push and element onto the end of an array with associative key
 * @param array $array Array to append the element
 * @string $key Key to the value
 * @mixed $value Value
 * @return array Array with new element appended
 * @see http://www.phpro.org/examples/Array-Push-Assoc.html
 */
function array_push_assoc($array, $key, $value)
{
  $array[$key] = $value;
  return $array;
}


/**
 * Generates a String description of the time from the number of seconds.
 * @param Long $seconds Number of seconds, from 0
 * @return String Description in the form days, hours, minutes, seconds
 */
function get_time_description($seconds)
{
  $weeks = (int) ($seconds / 604800);
  $weeks_p = $weeks > 1 ? 'weeks' : 'week';
  $days=(int)($seconds/86400);
  $days_p = $days > 1 ? 'days' : 'day';
  $hours = (int)(($seconds-($days*86400))/3600);
  $mins = (int)(($seconds-$days*86400-$hours*3600)/60);
  $secs = (int)($seconds - ($days*86400)-($hours*3600)-($mins*60));

  //build a string
  $ret = "$secs sec";
  if ($mins > 0 && $sec >= 0)
    $ret = "$mins min $ret";
  if ($hours > 0 && $min >= 0 && sec >=0)
    $ret = "$hours hours $ret";
  if ($days > 0 && $hours >= 0 && $min >= 0 && sec >= 0)
    $ret = "$days $days_p $ret";

  return $ret;
}

/**
 * Format the file size into human readable numbers.
 * @param Long $size Number of bytes in the file
 * @return String Number of bytes formatted appropriately for intervals of 1024
 */
function format_filesize($size)
{

  // Measure & Number of decimals
  $measures = array (
    0 => array ( "B", 0 ),
    1 => array ( "KB", 0 ),
    2 => array ( "MB", 0 ),
    3 => array ( "GB", 2 ),
    4 => array ( "TB", 3 )
  );

  $file_size = (double)$size;

  for ( $i = 0; $file_size >= 1024; $i++ )
  {
    $file_size = (double)$file_size / 1024;
  }

  $file_size = number_format ( $file_size, $measures[$i][1] );

  return $file_size." ".$measures[$i][0];
}

/**
 * Export the data array in the desired format.
 * @param Array $data Data members
 * @param String $format Type of format to export. Supported formats are json,
 * html and xml. Default is json
 * @return String Data in new format
 */
function export_format($data, $format='json')
{
  $out = '';

  if ($format == 'json')
  {
    $out = json_encode($data);
  }
  else if ($format == 'html')
  {
    $out = print_r_slim($data, true);
  }
  else if ($format == 'xml')
  {
    $out = print_r_xml($data, true);
  }

  log_debug("Exporting {$format} data: ". (!empty($out) ? $out : "no data"));

  return $out;
}

/**
 * Collect a value for the page that is to be displayed on a form. Checks GET
 * and POST variables.
 * @param String $key Name of the input field
 * @param String $default Default value to use if neither GET or POST
 * variables are set
 * @param Boolean $getfirst Determines if GET or POST variables should be
 * checked first. Defaults to check GET first.
 * @return Empty string '' when invalid, or the value if defined.
 */
function get_form_val($key, $default='', $getfirst=TRUE)
{
  if ($getfirst)
  {
    return (empty($_GET[$key]) ? (empty($_POST[$key]) ? $default : $_POST[$key]) : $_GET[$key]);
  }
  else
  {
    return (empty($_POST[$key]) ? (empty($_GET[$key]) ? $default : $_GET[$key]) : $_POST[$key]);
  }
}

/**
 * Print an array as an XML data structure.
 * @param Array $arr Array filled with data members
 * @param Boolean $first Determines if this is the only data on the XML page
 * @return String XML output describing the data members and values
 * @author thbley at gmail dot com
 * @see http://php.net/manual/en/function.print-r.php
 */
function print_r_xml($arr,$first=true)
{
  $output = "";
  if ($first) $output .= "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<data>\n";
  foreach($arr as $key => $val)
  {
    if (is_numeric($key)) $key = "arr_".$key; // <0 is not allowed
    switch (gettype($val))
    {
      case "array":
        $output .= "<".htmlspecialchars($key)." type='array' size='".count($val)."'>".
          print_r_xml($val,false)."</".htmlspecialchars($key).">\n";
        break;
      case "boolean":
        $output .= "<".htmlspecialchars($key)." type='bool'>".($val?"true":"false").
          "</".htmlspecialchars($key).">\n";
        break;
      case "integer":
        $output .= "<".htmlspecialchars($key)." type='integer'>".
          htmlspecialchars($val)."</".htmlspecialchars($key).">\n";
        break;
      case "double":
        $output .= "<".htmlspecialchars($key)." type='double'>".
          htmlspecialchars($val)."</".htmlspecialchars($key).">\n";
        break;
      case "string":
        $output .= "<".htmlspecialchars($key)." type='string' size='".strlen($val)."'>".
          htmlspecialchars($val)."</".htmlspecialchars($key).">\n";
        break;
      default:
        $output .= "<".htmlspecialchars($key)." type='unknown'>".gettype($val).
          "</".htmlspecialchars($key).">\n";
        break;
    }
  }
  if ($first) $output .= "</data>\n";
  return $output;
}

/**
 * Print the contents of an array or object without annoyances of newlines.
 * @param Any $arr Data item to print
 * @param Boolean $no_print Set to true does not print using echo
 * @return String Return the output when $no_print set to true
 */
function print_r_slim($arr, $no_print=false)
{
  $out = print_r($arr, true);

  $out = str_replace(" ", "", $out);
  $out = str_replace("\n", ", ", $out);
  $out = str_replace(", )", "), ", $out);
  $out = str_replace(", , ", "", $out);
  $out = str_replace(", (, ", "(", $out);
  $out = str_replace("Array, ", "Array", $out);
  $out = str_replace("Object", " Object", $out);

  if (!$no_print)
  {
    echo $out;
    return;
  }

  return $out;
}




?>