<?php
/**
 * A page that could not be found because of an incorrect URI.
 * 
 * @author daniel
 */
class page_notfound extends page {

  public function get_main() {
    ?>


      <h2>Page Not Found</h2>
      <p>Invalid page request!</p>

    <?php
  }
}
?>
