<?php
$pass = "FOTO-BOX";
$target_dir = "uploads/";
$json = file_get_contents('php://input');
$data = json_decode($json, true);
$post_pass = $data['pass'];

if ($post_pass == $pass) {

    $file = base64_decode($data['image']);
    $filename = $data['filename'];
    if ($file) {
        $target_file = $target_dir.$filename;
        $uploadOk = 1;
        $imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));
        // Check if file already exists
        if (file_exists($target_file)) {
            echo "Sorry, file already exists.";
            $uploadOk = 0;
        }
        // Allow certain file formats
        if (
            $imageFileType != "jpg" && $imageFileType != "png" && $imageFileType != "jpeg"
            && $imageFileType != "gif"
        ) {
            echo "Sorry, only JPG, JPEG, PNG & GIF files are allowed.";
            $uploadOk = 0;
        }
        // Check if $uploadOk is set to 0 by an error
        if ($uploadOk == 0) {
            echo "Sorry, your file was not uploaded.";
            // if everything is ok, try to upload file
        } else {
            if (file_put_contents($target_file, $file)) {
                echo "OK";
            } else {
                echo "Sorry, there was an error uploading your file.";
            }
        }
    } else {
        echo "No File avaliable.";
    }
} else {
    echo "Wrong Password.";
}
