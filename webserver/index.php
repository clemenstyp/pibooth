<?php
$uploadDirName = "uploads";
$uploadDirectory = realpath(getcwd()."/".$uploadDirName);
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html><head><meta http-equiv="Content-Type" content="text/html; charset=windows-1256" /></head><body>


<?php

    // open this directory 
    $myDirectory = opendir($uploadDirectory);
    // get each entry
    while($entryName = readdir($myDirectory)) {$dirArray[] = $entryName;} closedir($myDirectory);
    $indexCount = count($dirArray);
        //echo "$indexCount files<br/>";
    sort($dirArray);

    echo "<TABLE border=1 cellpadding=5 cellspacing=0 class=whitelinks><TR><TH>Filename</TH></TR>\n";

        for($index=0; $index < $indexCount; $index++) 
        {
            if (substr("$dirArray[$index]", 0, 1) != ".")
            {
            echo "<TR>
            <td><a href=\"$uploadDirName/$dirArray[$index]\">$dirArray[$index]</a></td>
                </TR>";
            }
        }
    echo "</TABLE>";
    ?>
