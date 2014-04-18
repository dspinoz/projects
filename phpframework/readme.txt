My PHP Framework - Readme
================================================================================
This is a lightweight php framework for use in dynamic web page design with PHP.


==========
LAYOUT
==========
The following directory structure is created:

  config/        Configuration files
  php/db/        Classes for database communications
  php/g/         Global functions and classes
  php/page/      Specific web pages available on the site
  index.php  		 Single point of entry for all pages

User-created classes and pages should be defined in a "usr" directory structure:

  usr/config/     Configuration files
  usr/php/         PHP classes
  usr/script/      User script files
  usr/images/     User image files

NOTE: By default, php classes are automatically included.
NOTE: This directory structure is designed so that changes to the myphpframework
      can be updated, if necessary.


==========
SITE
==========
Role of the "site":
 * Provide single point of entry for all page requests, including ajax and submit
 * Provide access to the current session
 * Provide global functions for the current page


==========
PAGE
==========
To create a new page:
 * Modify the "site" class
   * navigation variable holds a mapping of site names to page names
   * modify the determine_page() function to ensure that a new "page" instance is
     created when the desired name is requested
 * create a new class that extends the default "page"
   * override functions depending on the functionality desired
     * get_main()        Return the page's main content (without overriding this the page will appear blank)
     * get_submain()     Return the page's sub content (eg. multiple areas with dynamic content)
     * has_script()      Enable a javascript file located in the /script directory structure with name "page.*.js"
     * has/get_ajax()    Enable "ajax" mode for simple requests of data
     * has/get_submit()  Enable "submit" mode for accepting data from forms
     * has/get_title()   Custom title for the page


==========
REQUESTS
==========
Each request requires a mode. The following modes are supported:
 * page     Default mode
 * ajax     Ajax request for data
 * submit   Submit data from form

Requests for data are typically with GET HTTP mode. Submits are typically with POST mode
However, any combination is supported, however not recommended

Each page request has the URL page=<name>, where <name> is the name of the page. Each request must be for a specific page

Ajax pages are submitted with URL mode=ajax and request=<func>, where <func> is some data to retrieve
  eg. http://localhost/index.php?mode=ajax&page=home&request=load

Submit pages are sent with URL mode=submit and submit=<func>, where <func> defines the action that should be performed. Submit data should be sent via POST
  eg. GET    http://localhost/index.php?mode=submit&page=home&submit=search
  eg. POST   query=Help

Submit and Ajax requests can respond in a specified format; one of html, json or xml.
Include a format=<type> value on the URL.
  eg. GET http://localhost/index.php?mode=submit&page=home&submit=login&format=xml
NOTE: The ajax/submit mode must support returning data values
