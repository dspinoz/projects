<?php

/**
 * Page to demonstrate database connectivity.
 */
class page_db extends page
{
  public $db;
  
  public function __construct()
  {
    parent::__construct();
    $this->db = new db_access_mysql();
  }

  public function __get($name)
  {
    echo "$name";
  }

  public function get_main()
  {
    $woopa = new db_object_people();
    $this->db->create($woopa);

    $people = $this->db->select('people', array('name', 'id', 'bday'));

    if ($people->num)
    {
      do
      {
        print_r($people->row);
      }
      while ($people->next());
    }

    $elizabeth = $this->db->insert('people', array('name'=>'elizabeth', 'bday'=>'1986-01-16'));
    echo "elizabeth has id = {$elizabeth->row['id']}<br>";

    print_r($this->db->update('people', $elizabeth->row['id'], array('name'=>'daniel'), true, 1));

    $this->db->delete('people', $elizabeth->row['id']);


    $woopa = new db_object_names();
    $this->db->create($woopa);
  }


}

?>