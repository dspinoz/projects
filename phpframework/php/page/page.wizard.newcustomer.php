<?php

class page_wizard_newcustomer extends page_wizard
{
  public function get_wizard_title()
  {
    return "New Customer";
  }
  
  public function has_title()
  {
    return true;
  }

  public function get_title()
  {
    return "Create new Customer";
  }

  public function submit($query)
  {
    $ret = page_wizard::submit($query);

    return $ret;
  }

  public function __construct()
  {
    page_wizard::__construct(array(
        new page_wizard_step('Welcome', 'welcome'),
        new page_wizard_step("Enter Details", 'enter_details'),
        new page_wizard_step("Create", 'create'),
        new page_wizard_step("Finish", 'finish')));
  }

  public function welcome()
  {
    return "step1";
  }

  public function enter_details()
  {
    return "step2";
  }

  public function create()
  {
    return "step3";
  }

  public function finish()
  {
    $this->last_step();
    return "done";
  }

}
?>
