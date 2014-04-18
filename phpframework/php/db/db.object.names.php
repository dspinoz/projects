<?php
class db_object_names extends db_object
{
  private $name;

  public function __construct()
  {
    parent::__construct('names');
  }

  public function columns()
  {
    return array(new db_column('name', 'VARCHAR(5000)', 'NOT NULL'));
  }
}
?>
