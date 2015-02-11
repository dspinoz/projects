<?php
if (count($_FILES) > 0)
{
  if ($_FILES["file"]["error"] > 0)
  {
    if ($_FILES["file"]["error"] == 1)
    {
      die("File too big!");
    }
    die("Upload error: ".$_FILES["file"]["error"]);
  }
  else
  {
    if (!file_exists("uploads") && !mkdir("uploads"))
    {
      die("Could not make uploads directory");
    }
    
    $newname = $_FILES["file"]["name"];
    
    if (file_exists("uploads/${newname}"))
    {
      $md5_orig = md5_file("uploads/${newname}");
      $md5_new = md5_file($_FILES["file"]["tmp_name"]);
      
      if ($md5_orig == $md5_new)  
      {
        die("File already exists. <a href='uploads/".$newname."'>${newname}</a>");
      }
    }
    
    $count = 0;
    while (file_exists("uploads/${newname}"))
    {
      $count++;
      $newname = $_FILES["file"]["name"].".".$count;
    }
    
    if (!move_uploaded_file($_FILES["file"]["tmp_name"], "uploads/".$newname))
    {
      die("ERROR Did not upload");
    }
    
    die("Upload <a href='uploads/".$newname."'>${newname}</a> successful");
  }
  die("");
}
?>
<html>
  <body>
    <form action="remote-upload.php" method="post" enctype="multipart/form-data">
      <label for="file">Filename</label>
      <input type="file" name="file" id="file"/>
      <input type="submit" name="submit" value="Submit"/>
    </form>
  </body>
</html>