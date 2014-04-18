<?php

/* Simple php page to calculate an MD5 checksum */

if (!empty($_GET['password']))
{
  $password = $_GET['password'];
  $md5 = md5($password);
}

?>

<h2>Calculate MD5 Hash</h2>
<form method="GET" action="md5.php">
  <table>
    <tr><th><label for="password">Password</label></th><td><input type="text" name="password" value="<?php echo (isset($password) ? $password : ''); ?>" /></td></tr>
    <tr><th><label for="md5">MD5 Hash</label></th><td><span><?php echo (isset($md5) ? $md5 : ''); ?></span></td></tr>
    <tr><td colspan="2"><input type="submit" value="MD5 hash" /></td></tr>
  </table>
</form>

