<?php

/**
 * A single step as part of the wizard.
 */
class page_wizard_step
{
  public $name;
  public $method;
  
  public function __construct($name, $method)
  {
    $this->name = $name;
    $this->method = $method;
  }
}

/**
 * A page that provides a series of steps to fulfil a single purpose.
 */
abstract class page_wizard extends page
{
  /**
   * @var Integer Current action number
   */
  public $action;

  /**
   * @var Array Methods that define the 'steps' for the wizard
   */
  public $steps;

  /**
   * @var Boolean Determines if this is the last step. The last function should
   * call this method so renders the wizard correctly.
   */
  private $is_last_step;

  private $submit_msg;

  private $show_next;
  private $show_done;
  private $show_cancel;

  /**
   * Gets the title for the wizard.
   * @return String Text description of the wizard
   */
  abstract public function get_wizard_title();

  public function __construct($array)
  {
    parent::__construct();
    
    $this->is_last_step = false;
    $this->show_next = true;
    $this->show_done = true;
    $this->show_cancel = true;
    $this->submit_msg = '';
    $this->steps = $array;

    if (key_exists('action', $_GET))
    {
      $this->action = $_GET['action'] == NULL ? 0 : $_GET['action'];
    }
    else
    {
      $this->action = 0;
    }

    //$this->forced_continue();
  }

  public function last_step()
  {
    $this->is_last_step = true;
  }

  public function hide_next()
  {
    $this->show_next = false;
  }
  public function show_next()
  {
    $this->show_next = true;
  }

  public function hide_cancel()
  {
    $this->show_cancel = false;
  }
  public function show_cancel()
  {
    $this->show_cancel = true;
  }

  public function hide_done()
  {
    $this->show_done = false;
  }
  public function show_done()
  {
    $this->show_done = true;
  }

  private function get_breadcrumbs()
  {
    $out = '';
    for ($i = 0 ; $i < count($this->steps) ; $i++) {

      if ($i == $this->action)
      {
        $out .= '<b>';
      }

      $out .= $this->steps[$i]->name;

      if ($i == $this->action)
      {
        $out .= '</b>';
      }

      if (($i+1) < count($this->steps))
      {
        $out .= '&nbsp;&nbsp;&nbsp;&middot;&nbsp;&nbsp;&nbsp;';
      }
    }
    return $out;
  }

  public function next()
  {
    if ($this->action+1 < count($this->steps))
    {
      $this->action++;
    }
  }
  public function cancel()
  {
      $this->action = 0;
  }
  public function done()
  {
      $this->action = 0;
  }

  public function has_submit()
  {
    return true;
  }
  
  public function submit($query)
  {
    if ($query == 'Next')
    {
      $this->next();
    }
    else if ($query == 'Cancel')
    {
      $this->cancel();
    }
    else if ($query == 'Done')
    {
      $this->done();
    }

    return NULL;
  }

  public function get_main()
  {
    if ($this->action < count($this->steps))
    {
      $method = $this->steps[$this->action];
      $method = "{$method->method}";

      return 
        "<h2>". $this->get_wizard_title() ."</h2>".
        '<p>'. $this->get_breadcrumbs() .'</p>'.
        '<p>'. $this->$method() .'</p>';
    }
    else
    {
      return '<h2>Error</h2>Incorrect usage.';
    }
  }

  //message only displayed once
  public function set_submit_message($html)
  {
    $this->submit_msg = $html;
  }

  public function wizard_done($button_name = "Done")
  {
    return '<form method="GET" action="index.php"><input type="hidden" name="mode" value="submit"/><input type="hidden" name="page" value="'.$this->name.'"/><input type="hidden" name="action" value="'.$this->action.'"/><input type="submit" value="'.$button_name.'" class="button" name="submit"/></form>';
  }

  public function wizard_next($button_name = "Next")
  {
    return '<form method="GET" action="index.php"><input type="hidden" name="mode" value="submit"/><input type="hidden" name="page" value="'.$this->name.'"/><input type="hidden" name="action" value="'.$this->action.'"/><input type="submit" value="'.$button_name.'" class="button" name="submit"/></form>';
  }
  public function wizard_cancel($button_name = "Cancel")
  {
    return '<form method="GET" action="index.php"><input type="hidden" name="mode" value="submit"/><input type="hidden" name="page" value="'.$this->name.'"/><input type="hidden" name="action" value="'.$this->action.'"/><input type="submit" value="'.$button_name.'" class="button" name="submit"/></form>';
  }

  public function get_submain()
  {
    if ($this->action < count($this->steps))
    {
      $html = $this->submit_msg;

      if ($this->is_last_step && $this->show_done)
      {
        $html = ($html . (empty($html) ? '' : '<p>') . $this->wizard_done() . (empty($html) ? '' : '</p>'));
      }
      else
      {
        if ($this->show_next)
        {
          $html = ($html . (empty($html) ? '' : '<p>') . $this->wizard_next() . (empty($html) ? '' : '</p>'));
        }

        if ($this->show_cancel)
        {
          $html = ($html . (empty($html) ? '' : '<p>') . $this->wizard_cancel() . (empty($html) ? '' : '</p>'));
        }
      }

      $this->submit_msg = '';
      return empty($html) ? '' : '<p>'.$html.'</p>';
    }
    else if ($this->show_cancel)
    {
      return "<p>{$this->wizard_cancel()}</p>";
    }
  }
}
?>
