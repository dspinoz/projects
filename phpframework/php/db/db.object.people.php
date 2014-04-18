<?php

class db_object_people extends db_object
{
  private $name;

  public function __construct()
  {
    parent::__construct('people');
  }

  public function columns()
  {
    return array(new db_column('name', 'VARCHAR(100)', 'NOT NULL'),
                 new db_column('bday', 'date', ''));
  }
}
?>
