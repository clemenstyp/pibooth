from PIL import Image
import piexif

from pibooth.utils import LOGGER


def write_exif(filename, capture_nbr, pic_id, config):
	"""Adding Exif data to image files
	"""
	try:
		im = Image.open(filename)
		exif_dict = piexif.load(filename)
		# process im and exif_dict...
		w, h = im.size
		exif_dict["0th"][piexif.ImageIFD.XResolution] = (w, 1)
		exif_dict["0th"][piexif.ImageIFD.YResolution] = (h, 1)
		exif_dict["Exif"][piexif.ExifIFD.ImageUniqueID] = str(pic_id)
		exif_dict["0th"][piexif.ImageIFD.ImageNumber] = capture_nbr
		exif_dict["0th"][piexif.ImageIFD.Model] = config.get('PICTURE', 'exif_model').strip('"')
		exif_dict["0th"][piexif.ImageIFD.Make] = config.get('PICTURE', 'exif_make').strip('"')
		exif_dict["0th"][piexif.ImageIFD.Software] = config.get('PICTURE', 'exif_software').strip('"')
		exif_dict["0th"][piexif.ImageIFD.ImageDescription] = config.get('PICTURE', 'exif_description').strip('"')
		exif_dict["0th"][piexif.ImageIFD.DocumentName] = config.get('PICTURE', 'exif_document_name').strip('"')
		exif_dict["0th"][piexif.ImageIFD.Artist] = config.get('PICTURE', 'exif_artist').strip('"')
		exif_dict["0th"][piexif.ImageIFD.HostComputer] = config.get('PICTURE', 'exif_host_computer').strip('"')
		exif_dict["0th"][piexif.ImageIFD.Copyright] = config.get('PICTURE', 'exif_copyright').strip('"')
		exif_dict["Exif"][piexif.ExifIFD.CameraOwnerName] = config.get('PICTURE', 'exif_camera_owner').strip('"')
		# exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = "N"
		# exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = "O"
		# exif_dict["GPS"][piexif.ImageIFD.GPSLatitude] = (50.757200)
		# exif_dict["GPS"][piexif.ImageIFD.GPSLongitude] = (7.128560)
		exif_bytes = piexif.dump(exif_dict)
		LOGGER.info("EXIF: adding metadata to image file")
		im.save(filename, "jpeg", exif=exif_bytes)
	except Exception as e:
		LOGGER.warning(f"EXIF: couldn't add exif informations to picture [{e}]")
