<?php

class page_formtest extends page
{

  public function submit($query)
  {
    echo "submit request : {$query}";
    return true;
  }

  public function has_submit()
  {
    return true;
  }

  public function get_main()
  {

    echo '

    <form method="POST" action="'.create_uri('submit', $this->name, 'login').'">
      <input type="text" name="name" value="daniel" />
      <input type="text" name="password" value="password" />
      <input type="submit" name="submit" value="login" />
    </form>
    
    A Submit: <a href="'.create_uri('submit', $this->name, 'abc').'">another submit</a>';


  }


}
?>
