<?php
/**
 * A page represents some content that can be displayed to the user.
 *
 * @author daniel
 */
abstract class page {

  /**
   * @var String A reference for the current page
   */
  public $name;
  
  /**
   * @var Site Global values for this website 
   */
  public $site;

  /**
   * @var String Optional title
   */
  public $title;

  /**
   * @var Array Data that can be sent in a response from submit or ajax requests
   */
  public $data;

  /**
   * @var Array List of scripts for use on the page.
   */
  public $scripts;

  /**
   * @var Array List of style sheets for use on the page.
   */
  public $styles;

  /**
   * Determines if the current page is a user defined page.
   */
  public $is_usr_page;

  /**
   * Creates a new page.
   */
  public function __construct()
  {
    $this->data = array();
    $this->scripts = array();
    $this->styles = array();
    $this->is_usr_page = false;
  }

  public function has_style()
  {
    return count($this->styles) > 0;
  }

  public function custom_init()
  {
    return true;
  }

  public function set_defaults()
  {
    $this->custom_init();

    if ($this->has_script())
    {
      if (!$this->is_usr_page)
      {
        array_push($this->scripts, "script/page/page.{$this->name}.js");
      }
      else
      {
        array_push($this->scripts, "usr/script/page/page.{$this->name}.js");
      }
    }
  }

  /**
   * Generates the main content to be displayed on the current page.
   * @return String Text/HTML representation
   */
  public function get_main()
  {
    return "";
  }

  /**
   * Generates the minor content to be displayed on the current page.
   * @return String Text/HTML representation
   */
  public function get_submain()
  {
    return "";
  }

  /**
   * Generates the title for the current page.
   * @return String Text for the title
   */
  public function get_title()
  {
    return "";
  }

  /**
   * Determines if this page has a defined title.
   * @return Boolean True if defined, otherwise false
   */
  public function has_title()
  {
    return false;
  }

  /**
   * Determines if this page supports ajax requests.
   * @return Boolean True or false
   */
  public function has_ajax()
  {
    return false;
  }

  /**
   * Processes an ajax request and generates a result. Ajax requests are
   * typically via HTTP GET.
   * Method should print the Text/Json/HTML representation internally unless
   * returning content to be displayed on the page.
   * @param String $query The type of ajax request being fulfilled
   * @return Empty if page is to continue once ajax request has been
   * fulfilled.
   */
  public function ajax($query)
  {
    return "";
  }

  /**
   * Determines if this page supports submit requests.
   * @return Boolean True or false
   */
  public function has_submit()
  {
    return false;
  }

  /**
   * Processes a submit request and generates a result. Submit requests are
   * typically via HTTP POST.
   * Method should print the Text/Json/HTML representation internally unless
   * returning content to be displayed on the page.
   * @param String $query The type of submit request being fulfilled
   * @return Empty if page is to continue once submit request has been
   * fulfilled.
   */
  public function submit($query)
  {
    return "";
  }

  /**
   * Determines if this page has some custom javscript. The script file is
   * located at /script/page/page.<pagename>.js
   * @return Boolean True or false
   */
  public function has_script()
  {
    return false;
  }

  /**
   * Add a data value for the page. Data is exported after ajax or submit modes.
   * @param Any $key Key value
   * @param Any $val Value
   */
  public function add_data($key, $val)
  {
    log_debug("{$this->name} page data: {$key} => {$val}");
    $this->data = array_push_assoc($this->data, $key, $val);
  }

  /**
   * Gets the data associated with this page.
   * @return Array Data to be exported from the page
   */
  public function get_data()
  {
    return $this->data;
  }
}
?>
