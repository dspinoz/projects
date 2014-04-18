<?php

/**
 * Represents a column in a database table. Typically table fields or members.
 */
class db_column
{
  /**
   * @var String Name of the field
   */
  private $name;

  /**
   * @var String Database data type
   */
  private $type;

  /**
   * @var String Additional attributes that can be set (depending on the data
   * type). Set to null to ignore.
   */
  private $attr;

  public function __construct($name, $type, $attr)
  {
    $this->name = $name;
    $this->type = $type;
    $this->attr = $attr;
  }

  public function __get($name)
  {
    return $this->$name;
  }
}

/**
 * Abstract object that represents a database table to be created.
 */
abstract class db_object
{
  /**
   * @var Integer Unique identifier for the object
   */
  private $id;

  /**
   * @var String Name of the table where the object lives
   */
  private $table;

  /**
   * @param String $name Name of the table where the object lives
   */
  public function __construct($name)
  {
    $this->table = $name;
  }

  public function __get($name)
  {
    return $this->$name;
  }

  /**
   * Defines the columns that are required in this table.
   * @return Array List of db_column's for each of the columns that are required
   */
  public abstract function columns();

  /**
   * Defines the default columns that are included with all tables.
   * @return Array List of db_column's
   */
  private function columns_default()
  {
    // NOTES:
    // For each table in the database, it is recommended to have an 'id'
    // auto-increment field to uniquely identify each record.
    return array(new db_column('id', 'INT', "NOT NULL AUTO_INCREMENT"));
  }

  /**
   * Gets a list of columns for the current table.
   * @return Array List of db_column's for the table definition
   */
  public function get_columns()
  {
    $ret = array();

    $cols = $this->columns_default();

    if ($cols)
    {
      foreach($cols as $c)
      {
        array_push($ret, $c);
      }
    }

    $cols = $this->columns();

    if ($cols)
    {
      foreach($cols as $c)
      {
        array_push($ret, $c);
      }
    }

    return $ret;
  }
}
?>
