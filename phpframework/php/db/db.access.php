<?php
/**
 * Placeholder for database functions.
 */
abstract class db_access
{
  /**
   * @var Resource Mysql resource
   */
  private static $resource;

  public function __get($name)
  {
    return $this->$name;
  }

  /**
   * Performs a SELECT operation on the connected database.
   * @param String $table Name of the table
   * @param Array $members List of columns to extract
   * @param String $conditions Conditions in the query (WHERE clause)
   * @param Integer $limit Number of records to return, default is 200
   * @return db_return when the query is successful, NULL on error
   */
  public abstract function select($table, $members, $conditions=NULL, $limit=200);


  /**
   * Insert data into the provided table.
   * @param String $table Name of the table
   * @param Array $members List of columns and associated values to be inserted
   * @return db_return_mysql where $num set to the number of rows that were affected,
   * and $row['id'] = <insert_id>
   */
  public abstract function insert($table, $members);


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
  public abstract function update($table, $id, $members, $collect=false, $limit=1);


  /**
   * Deletes a record from the database from the specified table.
   * @param String $table Name of the table
   * @param Integer $id Identifier for the row
   * @param Integer $limit Max number of records returned
   * @return db_return_mysql with $num set to the number of rows that were deleted
   */
  public abstract function delete($table, $id, $limit=1);


  /**
   * Removes all rows from the provided table.
   * @param String $table Name of the table to truncate
   * @return Boolean True on success, false on error
   */
  public abstract function truncate($table);

  /**
   * Removes a table from the database schema.
   * @param String $table Name of the table to remove
   * @return Boolean True on success, false otherwise
   */
  public abstract function drop($table);


  /**
   * Executes a query to create a table as defined by the object.
   * @param db_object $db_object Database object to create
   * @return Boolean True on success, false on error
   */
  public abstract function create($db_object);
}
?>
