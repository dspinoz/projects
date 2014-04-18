<?php
/* Utility methods for mysql database access */

/**
 * Logs an error message with a mysql message.
 * @param Boolean $cond Condition for when the message should be displayed
 * @param String $message Message to prepend the mysql message
 */
function log_err_mysql($cond=true, $message=NULL)
{
  if ($message == NULL)
  {
    log_err(mysql_error(), $cond);
  }
  else
  {
    log_err($message .': '. mysql_error(), $cond);
  }
}


/**
 * Cleans a string for use in SQL queries.
 * @param String $orig Original string value
 * @return New string value that has html code removed and special characters
 * escaped
 */
function mysql_str_clean($orig)
{
  $new = htmlentities($orig);

  if (get_magic_quotes_gpc())
  {
    //guard against SQL injection
    $new = stripslashes($new);
  }

  $new = mysql_real_escape_string($new);

  return $new;
}
?>
