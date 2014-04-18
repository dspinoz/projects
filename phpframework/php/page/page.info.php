<?php
/**
 * Page that displays some information about the server configuration.
 *
 * @author daniel
 */
class page_info extends page {

  public function get_main() {

    if (get_config()->global->debug)
    {
      return phpinfo();
    }
    else
    {
      return "This requires debug mode";
    }
  }
}
?>
