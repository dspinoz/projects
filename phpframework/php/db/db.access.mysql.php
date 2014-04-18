<?php

/**
 * Access to mysql database as defined in the configuration file.
 *
 * @author Daniel
 */
class db_access_mysql extends db_access
{
  public function __construct()
  {
    $this->resource = mysql_connect(get_config()->database->host,
      get_config()->database->user, get_config()->database->password);

    if ($this->resource)
    {
      log_err_mysql(!mysql_select_db(get_config()->database->dbname),
               'Could not select database');
    }
    else
    {
      log_err_mysql(true, 'Could not connect to database');
    }
  }

  public function __destruct()
  {
    if ($this->resource)
    {
      mysql_close($this->resource);
    }
  }

  /**
   * Builds a SELECT query for use on the specified table.
   * @param String $table Name of the table
   * @param Array $members List of columns to extract
   * @param String $conditions Conditions in the query (WHERE clause)
   * @param Integer $limit Number of records to return, default is 200
   * @return String SQL SELECT query
   */
  private function build_select_query($table, $members, $conditions=NULL, $limit=200)
  {
    $sql = "SELECT ";

    $i = 0;
    $total = count($members);

    foreach($members as $m)
    {
      $sql .= "{$m}";

      $sql .= (($i+1) < $total) ? ", " : "";
      $i ++;
    }

    $sql .= " FROM $table";

    if ($conditions)
    {
      $sql .= " WHERE {$conditions}";
    }

    $sql .= " LIMIT {$limit}";

    log_debug("Select query: {$sql}");

    return $sql;
  }

  /**
   * Performs a SELECT operation on the connected database.
   * @param String $table Name of the table
   * @param Array $members List of columns to extract
   * @param String $conditions Conditions in the query (WHERE clause)
   * @param Integer $limit Number of records to return, default is 200
   * @return db_return_mysql when the query is successful, NULL on error
   */
  public function select($table, $members, $conditions=NULL, $limit=200)
  {
    $r = mysql_query($this->build_select_query($table, $members, $conditions, $limit));
    log_err_mysql(!$r);

    if ($r)
    {
      return new db_return_mysql($r, mysql_affected_rows(), mysql_fetch_assoc($r));
    }

    return NULL;
  }

  /**
   * Builds an INSERT query for adding values into the database.
   * @param String $table Name of the table
   * @param Array $members List of columns and associated values to be inserted
   * @return String SQL INSERT statement
   */
  private function build_insert_query($table, $members)
  {
    $sql = "INSERT INTO {$table} (";

    $i = 0;
    $total = count($members);
    
    foreach($members as $m=>$v)
    {
      $sql .= "{$m}";

      $sql .= (($i+1) < $total) ? ", " : "";
      $i ++;
    }

    $sql .= ") VALUES (";

    $i = 0;
    $total = count($members);

    foreach($members as $m=>$v)
    {
      $v = mysql_str_clean($v);

      $sql .= "'{$v}'";

      $sql .= (($i+1) < $total) ? ", " : "";
      $i ++;
    }

    $sql .= ")";

    log_debug("Insert query: {$sql}");

    return $sql;
  }

  /**
   * Insert data into the provided table.
   * @param String $table Name of the table
   * @param Array $members List of columns and associated values to be inserted
   * @return db_return_mysql where $num set to the number of rows that were affected,
   * and $row['id'] = <insert_id>
   */
  public function insert($table, $members)
  {
    $r = mysql_query($this->build_insert_query($table, $members));
    log_err_mysql(!$r);

    if ($r)
    {
      $fetch = array('id'=>mysql_insert_id());
      
      return new db_return_mysql(NULL, mysql_affected_rows(), $fetch);
    }

    return NULL;
  }

  /**
   * Update a record in the provided table.
   * @param String $table Name of the table
   * @param Integer $id Identifier for the row in the table
   * @param Array $members List of column names and values to be set
   * @param Boolean $collect Determines if the new record should be retrieved
   * from the database and returned, default is false
   * @param Integer $limit Number of records to return, default is 1
   * @return db_return_mysql When $collect is set to false (default): where $num set
   * to the number of rows that were affected, and $row['id'] = <insert_id>.
   * When $collect is true, see select() with $limit set to 1
   */
  public function update($table, $id, $members, $collect=false, $limit=1)
  {
    $sql = "UPDATE {$table} SET ";

    $i = 0;
    $total = count($members);

    foreach($members as $m=>$v)
    {
      $v = mysql_str_clean($v);

      $sql .= "{$m} = '{$v}'";

      $sql .= (($i+1) < $total) ? ", " : "";
      $i ++;
    }

    $sql .= " WHERE id = {$id} LIMIT {$limit}";

    log_debug("Update query: {$sql}");

    $r = mysql_query($sql);
    log_err_mysql(!$r);

    if ($r && !$collect)
    {
      $fetch = array('id'=>"{$id}");

      return new db_return_mysql(NULL, mysql_affected_rows(), $fetch);
    }
    else if ($r && $collect)
    {
      log_debug("Updated row. Collecting new data where id={$id}");

      return $this->select($table, array("*"), "id = {$id}", $limit);
    }

    return NULL;
  }

  /**
   * Deletes a record from the database from the specified table.
   * @param String $table Name of the table
   * @param Integer $id Identifier for the row
   * @param Integer $limit Max number of records returned
   * @return db_return_mysql with $num set to the number of rows that were deleted
   */
  public function delete($table, $id, $limit=1)
  {
    $sql = "DELETE FROM {$table} WHERE id = {$id} LIMIT {$limit}";

    log_debug("Delete query: {$sql}");

    $r = mysql_query($sql);
    log_err_mysql(!$r);

    if ($r)
    {
      return new db_return_mysql(NULL, mysql_affected_rows());
    }

    return NULL;
  }

  /**
   * Removes all rows from the provided table.
   * @param String $table Name of the table to truncate
   * @return Boolean True on success, false on error
   */
  public function truncate($table)
  {
    $sql = "TRUNCATE TABLE {$table}";

    log_debug("Truncate query: {$sql}");

    $r = mysql_query($sql);
    log_err_mysql(!$r);

    return $r;
  }

  /**
   * Removes a table from the database schema.
   * @param String $table Name of the table to remove
   * @return Boolean True on success, false otherwise
   */
  public function drop($table)
  {
    $sql = "DROP TABLE {$table}";
    log_debug("Drop query: {$sql}");

    $r = mysql_query($sql);
    log_err_mysql(!$r);

    return $r;
  }

  /**
   * Buils the CREATE TABLE query.
   * @param db_object $db_object Database object to create
   * @return String SQL CREATE TABLE statement
   */
  private function build_create_table_query($db_object)
  {
    $sql = "CREATE TABLE IF NOT EXISTS {$db_object->table} (";

    $cols = $db_object->get_columns();

    if ($cols)
    {
      foreach($cols as $c)
      {
        if ($c->attr)
        {
          $sql .= " {$c->name} {$c->type} {$c->attr},";
        }
        else
        {
          $sql .= " {$c->name} {$c->type},";
        }
      }
      //still one more attribute to add - PRIMARY KEY (id)
    }

    $sql .= " PRIMARY KEY (id)";
    $sql .= " )";

    log_debug("Create table: {$sql}");

    return $sql;
  }

  /**
   * Executes a query to create a table as defined by the object.
   * @param db_object $db_object Database object to create
   * @return Boolean True on success, false on error
   */
  public function create($db_object)
  {
    $r = mysql_query($this->build_create_table_query($db_object));
    log_err_mysql(!$r);

    return $r;
  }
}
?>
