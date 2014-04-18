<?php
session_start();

include "php/g/config.php";
include "php/g/inc.globals.php";
include "php/g/site.php";
include "php/g/inc.utils.php";
include "php/db/inc.db.utils.mysql.php";
include "php/db/db.access.php";
include "php/db/db.object.php";
include "php/db/db.object.names.php";
include "php/db/db.object.people.php";
include "php/db/db.return.php";
include "php/db/db.access.mysql.php";
include "php/db/db.return.mysql.php";
include "php/page/page.php";
include "php/page/page.db.php";
include "php/page/page.formtest.php";
include "php/page/page.home.php";
include "php/page/page.info.php";
include "php/page/page.newpage.php";
include "php/page/page.notfound.php";
include "php/page/page.wizard.php";
include "php/page/page.wizard.newcustomer.php";

// Load the default site configuration
$site = new site();

calc_gen_time();

// Process page/ajax/submit requests before generating the actual page html.
// Makes a central point of contact for the client
if (!$site->process_mode())
{
  exit;
}

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
  
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />

    <?php
    if ($site->page->has_style()) {
      foreach ($site->page->styles as $s)
      {
      ?>
    <link rel="Stylesheet" type="text/css" href="<?php echo get_config()->utils->install_dir . $s; ?>" />
    <?php
      }

    }
    ?>


    <?php
    if ($site->page->has_script()) {
      foreach ($site->page->scripts as $s)
      {
      ?>
    <script type="text/javascript" src="<?php echo get_config()->utils->install_dir . $s; ?>"></script>
    <?php
      }
      
    } else { ?>

    <?php }
    ?>
    
    <title><?php echo $site->get_title(); ?></title>

  </head>
  <body>

    <div id="navigation">
      <ul><?php
      foreach ($site->navigation as $k=>$v)
      {
      echo "\n        <li><a href=\"".create_uri('page', $k)."\">{$v}</a></li>";
      }
      echo "\n      ";
      ?></ul>
    </div>

    <div id="user_message"><?php
      if ($site->get_user_message())
      {
        echo "\n          ";
        echo $site->get_user_message();
        $site->set_user_message(); // clear
        echo "\n        ";
      }
    ?></div>

    <div id="main"><?php echo $site->ajax_response; echo $site->page->get_main(); ?></div>
    
    <div id="submain"><?php echo $site->page->get_submain(); ?></div>
        
    <div id="footer">
      Generated in <span id="load_time"><?php echo number_format(abs(calc_gen_time()),3); ?></span> sec
    </div>

  </body>
</html>
