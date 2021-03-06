<?php
$uploadDirName = "uploads";
$uploadDirectory = realpath(getcwd()."/".$uploadDirName);
$warning = "";
if (isset($_GET['c']))  {
   $code = $_GET['c'];
?>

    <!-- LOGGED IN CONTENT HERE -->
    <html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Foto Box</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    <link href="https://fonts.googleapis.com/css?family=Droid+Sans:400,700" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/baguettebox.js/1.8.1/baguetteBox.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Amatic+SC:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="gallery-grid.css">
</head>
<body>
    <div class="container gallery-container">
    <h1>Foto Box</h1>
    <!--<p class="page-description text-center">Susanne &amp; Clemens</p>-->

    <div class="tz-gallery">

            <div class="row justify-content-md-center justify-content-sm-center">

            <?php
    $files = glob("$uploadDirectory/$code.jpg");
    if (count($files) == 0){
        $newCode = substr($code,0,5).'-'.substr($code,5,10);
        $files = glob("$uploadDirectory/$newCode.jpg");
    }
    if (count($files) == 1){
        printf('<div class="col-sm-6 col-md-4">
                <a class="lightbox" href="%1$s/%2$s"><img src="%1$s/%2$s" class="lazy"></a>

              </div>',$uploadDirName, basename($files[0]));

    }else{
        printf('<div class="col-sm-6 col-md-4">
                <div class="text-box">
                <p class="element-description text-center">
                Das Bild wurde leider nicht gefunden. Aber die Fotobox läd es sicherlich gleich hoch. Probie es später einfach nocheinmal.</p>
                </div>
              </div>');

    }
    ?>
        </div>
    </div>

</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/baguettebox.js/1.8.1/baguetteBox.min.js"></script>
<script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
<script>
    //baguetteBox.run('.tz-gallery');
</script>
</body>
</html>
<?php
      exit;
}
?>

<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Foto Box</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    <link href="https://fonts.googleapis.com/css?family=Droid+Sans:400,700" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/baguettebox.js/1.8.1/baguetteBox.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Amatic+SC:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="gallery-grid.css">
</head>
<body>
    <div class="container gallery-container">
    <h1>Foto Box</h1>
    <?php
    if (strlen($warning) != 0) {
    ?>
        <div class="alert alert-danger" role="alert">
        <?php
        echo $warning;
         ?>
        </div>
    <?php
    }
    ?>

    <div class="row justify-content-md-center justify-content-sm-center">
    <div class="col-sm-4">
    <div class="card-deck mb-3 text-center">

        <div class="card mb-4 shadow-sm">
          <div class="card-header">
            Bitte den Code eingeben:
          </div>
          <div class="card-body">
             <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="get">
                  <div class="form-group">
                    <label for="keypass">Code</label>
                    <input type="text" class="form-control" name="c" id="c">
                  </div>
                  <button type="submit" class="btn btn-primary">Öffnen</button>
            </form>
          </div>
        </div>
        </div>
    </div>
    </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/baguettebox.js/1.8.1/baguetteBox.min.js"></script>
<script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
<script>
    baguetteBox.run('.tz-gallery');
</script>
</body>
</html>








