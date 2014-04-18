<?php
/**
 * Description of classpagehome
 *
 * @author Daniel
 */
class page_home extends page
{

  public function __construct()
  {
    parent::__construct();
    $this->title = "Hello";
  }

  public function has_submit()
  {
    return true;
  }

  public function submit($query)
  {
    if ($query == 'login')
    {
      if ($this->site->login($_POST['username'], $_POST['password']))
      {
        echo "success";
      }
      else
      {
        $this->site->set_user_message("incorrect authentication!");
      }
    }
    else if ($query == 'logout')
    {
      $this->site->logout();

      $this->add_data('method', 'logout');
      $this->add_data('success', true);

      return true;
    }

    return NULL;
  }

  public function get_main()
  {
    ?>


      Hello World.
      <br/>
      <br/>
      <?php echo $this->site->is_authenticated() ? "Im in!" : "Bad luck"; ?>

    <?php

    if (!$this->site->is_authenticated())
    {
      return '
      <form method="POST" action="'.create_uri('submit', $this->name, 'login').'">
        <input type="text" name="username" />
        <input type="password" name="password"/>
        <input type="submit" name="submit" value="login"/>
      </form>

    ';
    }
    else
    {
      return '
      <form method="POST" action="'.create_uri('submit', $this->name, 'logout').'">
        <input type="radio" name="format" value="json" />json <br>
        <input type="radio" name="format" value="xml" checked />xml <br>
        <input type="radio" name="format" value="html" />html <br>
        <input type="submit" name="submit" value="logout"/>
      </form>
      
    ';
    }
  }

  public function get_title()
  {
    return "Home Page with Login";
  }

  public function has_title()
  {
    return true;
  }
}
?>
