<?php

/**
 * A database return value.
 */
abstract class db_return
{
  /**
   * @var Integer Number of records
   */
  private $num;

  /**
   * @var Resource MySQL resource that should be destroyed once used
   */
  private $resource;

  /**
   * @var Array List of columns and associated values for the current row
   */
  private $row;

  /**
   * Creates a new return value to be used with database operations.
   * @param Resource $resource Database resource to be freed
   * @param Integer $rows Number of rows in the result set
   * @param Array $first List of column names and values
   */
  public function __construct($resource=NULL, $rows=NULL, $first=NULL)
  {
    $this->resource = $resource;
    $this->num = $rows;
    $this->row = $first;
  }

  public function __get($name)
  {
    return $this->$name;
  }

  /**
   * Move the resource to the next item in the result set.
   * @return Boolean True on success, false when reached the end
   */
  public abstract function next();

  /**
   * Free the resources used in this return value.
   */
  public abstract function free_resource();

  /**
   * Destroys the resources that have been allocated
   */
  public function __destruct()
  {
    $this->free_resource();
  }
}
?>
