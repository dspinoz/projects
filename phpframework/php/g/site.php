<?php
/**
 * The site represents the single entry point for all pages.
 *
 * @author daniel
 */
class site
{
  /**
   * @var Page The page that is currently processing the request
   */
  public $page;

  /**
   * @var Text/HTML/Json response from ajax
   */
  public $ajax_response;

  /**
   * @var Text/HTML/Json response from submit
   */
  public $submit_response;

  /**
   * @var Array Map between the naviation headings and a page to visit
   */
  public $navigation;

  /**
   * The current mode of the request. Typically one of page, ajax or submit.
   * @var String the mode
   */
  public $mode;

  /**
   * @var String Response format that has been requested. Either HTML, JSON or
   * XML. Default is HTML.
   */
  public $format;

  /**
   * Processes the current request.
   */
  public function __construct()
  {
    $this->preprocess();

    $pages = get_config()->site->pages;
    $pagenames = get_config()->site->pagenames;

    $this->navigation = array();
    for ($i = 0; $i < count($pages); $i++)
    {
      $this->navigation = array_push_assoc(
        $this->navigation, $pages[$i], $pagenames[$i]);
    }

    //TODO keep stats of page requests either in log file or database table

    $this->page = $this->determine_page();
    $this->page->site = $this;
  }

  /**
   * Performs some pre-processing before the processing of page requests starts.
   */
  private function preprocess()
  {
    //generate a unique log file name and set into the configuration
    if (get_config()->global->debug_unique_log)
    {
      $time = '';
      {
        //parse the time value to create something new
        $time = date(get_config()->utils->log_date_format);
        $mtime = microtime();

        $time = split(" ", $time);
        $mtime = split(" ", $mtime);

        $tempt = '';
        foreach ($time as $t)
        {
          $tempt .= $t .'-';
        }
        $tempt .= number_format(abs($mtime[0] * 1000),0);
        $time = $tempt;
      }

      $new_file_name = $_SERVER['REMOTE_ADDR'].'-'.$time;

      $df = get_config()->global->debug_filename;

      if (!empty($df))
      {
        $new_file_name .= '.'.$df;
      }
      else
      {
        $new_file_name .= '.log';
      }

      //log file is enabled
      get_config()->global->debug_filename = $new_file_name;
    }

    //log the get/post requests
    log_debug($_SERVER['REQUEST_METHOD'] .' '. $_SERVER['PHP_SELF'] . (!empty($_SERVER['QUERY_STRING']) ? '?'.$_SERVER['QUERY_STRING'] : '').' '. $_SERVER['REMOTE_ADDR'] );
    log_debug("GET: ". print_r_slim($_GET, true), !empty($_GET));
    log_debug("POST: ". print_r_slim($_POST, true), !empty($_POST));
    log_debug("SESSION: ". print_r_slim($_SESSION, true), !empty($_SESSION));
    log_debug("SERVER: ". print_r_slim($_SERVER, true), !empty($_SERVER));

    /* Load usr php classes */
    include_user_files();
  }

  /**
   * Determines if the current request has a valid mode.
   * @return Boolean True if valid, otherwise false
   */
  private function has_mode()
  {
    $resp = empty($_GET['mode']) ? (empty($_POST['mode']) ? NULL : $_POST['mode']) : $_GET['mode'];

    if ($resp == NULL)
    {
      //default if none provided
      $this->mode = 'page';
      return true;
    }
    else
    {
      $resp = strtolower($resp);
      $this->mode = $resp;

      // Ensure the mode is valid
      if ($resp == 'ajax' || $resp == 'page' || $resp == 'submit')
      {
        return true;
      }
      else
      {
        log_err("Incorrect mode recieved");

        return false;
      }
    }
  }


  /**
   * Determines if the current request has a valid output (response) format.
   * @return Boolean True if valid, otherwise false
   */
  private function has_response_format()
  {
    $format = empty($_GET['format']) ? (empty($_POST['format']) ? NULL : $_POST['format']) : $_GET['format'];

    if ($format == NULL)
    {
      //default if none provided
      $this->format = 'html';
      return true;
    }
    else
    {
      $format = strtolower($format);
      $this->format = $format;

      // Ensure the format is valid
      if ($format == 'html' || $format == 'json' || $format == 'xml')
      {
        return true;
      }
      else
      {
        log_err("Incorrect output (response) format recieved");

        return false;
      }
    }
  }

  /**
   * Process the current page mode.
   * @return Boolean True if the page is to keep processing, false if processing
   * should stop.
   */
  public function process_mode()
  {
    if ($this->has_mode())
    {
      if ($this->mode == 'ajax')
      {
        return $this->process_ajax();
      }
      else if ($this->mode == 'submit')
      {
        return $this->process_submit();
      }
      else if ($this->mode == 'page')
      {
        //normal page display
        return true;
      }
    }

    return false;
  }

  /**
   * Gets the title for the current page.
   * @return String Title for the site and the page combined in a single string
   */
  public function get_title()
  {
    $mytitle = get_config()->site->title;

    if ($this->page->has_title())
    {
      if (empty($mytitle))
      {
        return $this->page->get_title();
      }
      else
      {
        return $mytitle . ' - ' . $this->page->get_title();
      }
    }

    return $mytitle;
  }

  /**
   * Processes the submit request if one was recieved.
   * @return True if the page is to continue after processing, otherwise false
   * ends the current processing
   */
  public function process_submit()
  {
    log_debug("{$this->page->name} page does not accept submit requests",
      !$this->page->has_submit());

    $submit = empty($_GET['submit']) ? (empty($_POST['submit']) ? NULL : $_POST['submit']) : $_GET['submit'];

    if ($submit != NULL && $this->page->has_submit())
    {
      log_debug("Submit request: {$submit}");

      $this->submit_response = $this->page->submit($submit);

      if (!empty($this->submit_response))
      {
        log_debug("Submit response: ". print_r($this->submit_response, true));

        //report in the correct format
        if ($this->has_response_format())
        {
          echo export_format($this->page->get_data(), $this->format);
        }

        calc_gen_time();

        return false;
      }
    }
    
    return true;
  }

  /**
   * Processes the ajax request if one was recieved.
   * @return True if the page is to continue after processing, otherwise false
   * ends the current processing
   */
  public function process_ajax()
  {
    log_debug("{$this->page->name} page does not accept ajax requests",
      !$this->page->has_ajax());

    $ajax = empty($_GET['request']) ? (empty($_POST['request']) ? NULL : $_POST['request']) : $_GET['request'];

    if ($ajax != NULL && $this->page->has_ajax())
    {
      log_debug("Ajax request: {$ajax}");

      $this->ajax_response = $this->page->ajax($ajax);

      if (!empty($this->ajax_response))
      {
        log_debug("Ajax response: ". print_r($this->ajax_response, true));

        //report in the correct format
        if ($this->has_response_format())
        {
          echo export_format($this->page->get_data(), $this->format);
        }

        calc_gen_time();
        
        return false;
      }
    }
    
    return true;
  }

  /**
   * Determines the page that is to be displayed, based on the URI.
   * @return <type>
   */
  private function determine_page()
  {
    // Determine the page that we are loading
    $p = empty($_GET['page']) ? (empty($_POST['page']) ? 'home' : $_POST['page']) : $_GET['page'];
    $page = NULL;

    $pages = get_config()->site->pages;
    $pageclasses = get_config()->site->pageclasses;

    //ensure that we load a class that can handle the page request
    try
    {
      for($i = 0; $i < count($pages); $i++)
      {
        if ($p == $pages[$i])
        {
          //dynamically instantiate the page class either by using default name
          //or the configured class name
          if (empty($pageclasses[$i]))
          {
            $pname = "page_{$pages[$i]}";
          }
          else
          {
            $pname = $pageclasses[$i];
          }

          if (class_exists($pname))
          {
            $page = new $pname();
          }
          else
          {
            throw new Exception("Could not load class $pname");
          }

          break;
        }
      }

      if ($page == NULL)
      {
        throw new Exception ("No page with link '$p' has been defined in ".
          "configuration file");
      }
    }
    catch (Exception $e)
    {
      log_warn("{$e->getMessage()}");
      $page = new page_notfound();
    }

    //use the name as give on the URL, for reference when creating links, etc.
    $page->name = $p;
    $page->set_defaults();
    
    return $page;
  }

  /**
   * Sets a message for display to the user. Message is removed after a
   * determined period of time. With no arguments, message is reset to NULL.
   * @param String $msg HTML/Text to display
   */
  public function set_user_message($msg=NULL)
  {
    $_SESSION['user_message'] = $msg;
  }

  /**
   * Gets the message for display to the user.
   * @return HTML/Text to display if any, otherwise NULL
   */
  public function get_user_message()
  {
    if (isset ($_SESSION['user_message']))
    {
      return $_SESSION['user_message'];
    }
    else
    {
      return NULL;
    }
  }

  /**
   * Determines if the authenticated flag is set.
   * @return Boolean True if set, otherwise false
   */
  public function is_authenticated()
  {
    if (key_exists('authenticated', $_SESSION))
    {
      return $_SESSION['authenticated'];
    }

    log_debug("SESSION[authenticated] did not exist");
    return false;
  }

  /**
   * Gets the username of the user who is currently authenticated.
   * @return Boolean/String False if the user is not currently authenticated,
   * otherwise the name of the user
   */
  public function user_authenticated()
  {
    if (key_exists('authenticated_username', $_SESSION))
    {
      return $_SESSION['authenticated_username'];
    }

    log_debug("SESSION[authenticated_username] did not exist");
    return false;
  }

  /**
   * Login with a user defined in the configuration file. Sets the authenticated
   * flag in the current session.
   * @param String $user Name of the user
   * @param String $password Authentication
   * @return Boolean True if successful, false otherwise
   */
  public function login($user, $password)
  {
    $users = get_config()->users->users;
    $passwords = get_config()->users->passwords;

    for ($i = 0; $i < count($users); $i++)
    {
      if ($user == $users[$i])
      {
        if (md5($password) == $passwords[$i])
        {
          $_SESSION['authenticated'] = TRUE;
          $_SESSION['authenticated_username'] = $user;
          return TRUE;
        }
        else
        {
          log_warn("Incorrect password for user $user");
          return FALSE;
        }
      }
    }
    
    return FALSE;
  }

  /**
   * Remove authenticated flag from the current session.
   */
  public function logout()
  {
    $_SESSION['authenticated'] = FALSE;
    $_SESSION['authenticated_username'] = FALSE;
  }
}
?>