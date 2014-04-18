<?php

/**
 * A database return value for use with mysql databases.
 */
class db_return_mysql extends db_return
{
  public function free_resource()
  {
    if ($this->resource)
    {
      mysql_free_result($this->resource);
    }
  }

  public function next()
  {
    $this->row = mysql_fetch_assoc($this->resource);

    //do we have any more rows to process?
    if (!$this->row)
    {
      return false;
    }

    return true;
  }

}
?>
