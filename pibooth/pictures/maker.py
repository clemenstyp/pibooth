# -*- coding: utf-8 -*-

import os
import os.path as osp
from pibooth import fonts
from pibooth.utils import timeit
from pibooth.pictures import sizing
from PIL import Image, ImageDraw, ImageFont

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None


class PictureMaker(object):

    """
    Concatenate up to 4 PIL images in portrait orientation...

         +---------+           +---------+           +---+-+---+           +---------+
         |         |           |   +-+   |           |   |1|   |           | +-+ +-+ |
         |         |           |   |1|   |           |   +-+   |           | |1| |2| |
         |   +-+   |           |   +-+   |           |   +-+   |           | +-+ +-+ |
         |   |1|   |           |         |           |   |2|   |           |         |
         |   +-+   |           |   +-+   |           |   +-+   |           | +-+ +-+ |
         |         |           |   |2|   |           |   +-+   |           | |3| |4| |
         |         |           |   +-+   |           |   |3|   |           | +-+ +-+ |
         +---------+           +---------+           +---+-+---+           +---------+

    ...or landscape orientation

      +---------------+     +---------------+     +---------------+     +----+-+-+-+----+
      |      +-+      |     |    +-+  +-+   |     |  +-+ +-+ +-+  |     |    |1| |2|    |
      |      |1|      |     |    |1|  |2|   |     |  |1| |2| |3|  |     |    +-+ +-+    |
      |      +-+      |     |    +-+  +-+   |     |  +-+ +-+ +-+  |     |    +-+ +-+    |
      |               |     |               |     |               |     |    |3| |4|    |
      +---------------+     +---------------+     +---------------+     +----+-+-+-+----+
    """

    CENTER = 'center'
    RIGHT = 'right'
    LEFT = 'left'

    def __init__(self, width, height, *images):
        assert len(images) in range(1, 5), "1 to 4 images can be concatenated"
        self._texts = []
        self._texts_height = 0
        self._final = None
        self._margin = 50
        self._crop = False
        self._outline = False  # For debug purpose
        self._images = images
        self._background_color = (255, 255, 255)
        self._background_image = None

        self.width = width
        self.height = height
        self.is_portrait = self.width < self.height

    def _get_font(self, text, font_name, max_width, max_height):
        """Create the font object which fit the given rectangle.

        :param text: text to draw
        :type text: str
        :param font_name: name or path to font definition file
        :type font_name: str
        :param max_width: width of the rect to fit
        :type max_width: int
        :param max_height: height of the rect to fit
        :type max_height: int

        :return: PIL.Font instance
        :rtype: object
        """
        start, end = 0, self._texts_height
        while start < end:
            k = (start + end) // 2
            font = ImageFont.truetype(font_name, k)
            font_size = font.getsize(text)
            if font_size[0] > max_width or font_size[1] > max_height:
                end = k
            else:
                start = k + 1
        return ImageFont.truetype(font_name, start)

    def _image_resize_keep_ratio(self, image, max_w, max_h, crop=False):
        """Resize an image to fixed dimensions while keeping its aspect ratio.
        If crop = True, the image will be cropped to fit in the target dimensions.

        :return: image object, new width, new height
        :rtype: tuple
        """
        raise NotImplementedError

    def _image_paste(self, image, dest_image, pos_x, pos_y):
        """Paste the given image on the destination one.
        """
        raise NotImplementedError

    def _build_background(self):
        """Create an image with the given background.

        :return: image object which depends on the child class implementation.
        :rtype: object
        """
        raise NotImplementedError

    def _build_matrix(self, image):
        """Draw the images matrix on the given image.

        :param image: image object which depends on the child class implementation.
        :type image: object

        :return: image object which depends on the child class implementation.
        :rtype: object
        """
        offset_generator = self._iter_images_rect()
        count = 1
        for src_image in self._iter_src_image():
            pos_x, pos_y, max_w, max_h = next(offset_generator)
            src_image, width, height = self._image_resize_keep_ratio(src_image, max_w, max_h, self._crop)

            # Adjuste position to have identical margin between borders and images
            if len(self._images) < 4:
                pos_x, pos_y = pos_x + (max_w - width) // 2, pos_y + (max_h - height) // 2
            elif count == 1:
                pos_x, pos_y = pos_x + (max_w - width) * 2 // 3, pos_y + (max_h - height) * 2 // 3
            elif count == 2:
                pos_x, pos_y = pos_x + (max_w - width) // 3, pos_y + (max_h - height) * 2 // 3
            elif count == 3:
                pos_x, pos_y = pos_x + (max_w - width) * 2 // 3, pos_y + (max_h - height) // 3
            else:
                pos_x, pos_y = pos_x + (max_w - width) // 3, pos_y + (max_h - height) // 3

            self._image_paste(src_image, image, pos_x, pos_y)
            count += 1
        return image

    def _build_final_image(self, image):
        """Create the final PIL image and set it to the _final attribute.

        :param image: image object which depends on the child class implementation.
        :type image: object

        :return: PIL.Image instance
        :rtype: object
        """
        raise NotImplementedError

    def _build_texts(self, image):
        """Draw texts on a PIL image (PIL is used instead of OpenCV
        because it is able to draw any fonts without ext).

        :param image: PIL.Image instance
        :type image: object
        """
        offset_generator = self._iter_texts_rect()
        draw = ImageDraw.Draw(image)
        for text, font_name, color, align in self._texts:
            text_x, text_y, max_width, max_height = next(offset_generator)
            if not text:  # Empty string: go to next text position
                continue
            font = self._get_font(text, font_name, max_width, max_height)
            (text_width, _baseline), (offset_x, offset_y) = font.font.getsize(text)
            if align == self.CENTER:
                text_x += (max_width - text_width) // 2
            elif align == self.RIGHT:
                text_x += (max_width - text_width)
            draw.text((text_x - offset_x // 2, text_y - offset_y // 2), text, color, font=font)

    def _build_borders(self, image):
        """Build rectangle around each elements. This method is only for
        debuging purpose.

        :param image: PIL.Image instance
        :type image: object
        """
        draw = ImageDraw.Draw(image)
        for x, y, w, h in self._iter_images_rect():
            draw.rectangle(((x, y), (x + w, y + h)), outline='black')
        for x, y, w, h in self._iter_texts_rect():
            draw.rectangle(((x, y), (x + w, y + h)), outline='black')

    def _iter_src_image(self):
        """Yield source images to concatenate.
        """
        raise NotImplementedError

    def _iter_images_rect(self):
        """Yield top-left coordinates and max size rectangle for each image.

        :return: (image_x, image_y, image_width, image_height)
        :rtype: tuple
        """
        image_x = self._margin
        image_y = self._margin
        total_width = self.width - 2 * self._margin
        total_height = self.height - self._texts_height - 2 * self._margin

        if len(self._images) == 1:
            image_width = total_width
            image_height = total_height
        elif 2 <= len(self._images) < 4:
            if self.is_portrait:
                image_width = total_width
                image_height = (total_height - (len(self._images) - 1) * self._margin) // len(self._images)
            else:
                image_width = (total_width - (len(self._images) - 1) * self._margin) // len(self._images)
                image_height = total_height
        else:
            image_width = (total_width - self._margin) // 2
            image_height = (total_height - self._margin) // 2

        yield image_x, image_y, image_width, image_height

        if 2 <= len(self._images) < 4:
            if self.is_portrait:
                image_y += image_height + self._margin
            else:
                image_x += image_width + self._margin
            yield image_x, image_y, image_width, image_height

        if 3 <= len(self._images) < 4:
            if self.is_portrait:
                image_y += image_height + self._margin
            else:
                image_x += image_width + self._margin
            yield image_x, image_y, image_width, image_height

        if len(self._images) == 4:
            image_x += image_width + self._margin
            yield image_x, image_y, image_width, image_height
            image_y += image_height + self._margin
            image_x = self._margin
            yield image_x, image_y, image_width, image_height
            image_x += image_width + self._margin
            yield image_x, image_y, image_width, image_height

    def _iter_texts_rect(self, interline=None):
        """Yield top-left coordinates and max size rectangle for each text.

        :param interline: margin between each text line
        :type interline: int

        :return: (text_x, text_y, text_width, text_height)
        :rtype: tuple
        """
        if not interline:
            interline = 20

        text_x = self._margin
        text_y = self.height - self._texts_height
        total_width = self.width - 2 * self._margin
        total_height = self._texts_height - self._margin

        if self.is_portrait:
            text_height = (total_height - interline * (len(self._texts) - 1)) // (len(self._texts) + 1)
            for i in range(len(self._texts)):
                if i == 0:
                    yield text_x, text_y, total_width, 2 * text_height
                elif i == 1:
                    text_y += interline + 2 * text_height
                    yield text_x, text_y, total_width, text_height
                else:
                    text_y += interline + text_height
                    yield text_x, text_y, total_width, text_height
        else:
            text_width = (total_width - interline * (len(self._texts) - 1)) // len(self._texts)
            text_height = total_height // 2
            for i in range(len(self._texts)):
                if i == 0:
                    yield text_x, text_y, text_width, 2 * text_height
                else:
                    text_x += interline + text_width
                    yield text_x, text_y + (total_height - text_height) // 2, text_width, text_height

    def add_text(self, text, font_name, color, align=CENTER):
        """Add a new text.

        :param text: text to draw
        :type text: str
        :param font_name: name or path to font file
        :type font_name: str
        :param color: RGB tuple
        :type color: tuple
        :param align: text alignment: left, right or center
        :type align: str
        """
        assert align in [self.CENTER, self.RIGHT, self.LEFT], "Unknown aligment '{}'".format(align)
        self._texts.append((text, fonts.get_filename(font_name), color, align))
        if self.is_portrait:
            self._texts_height = 600
        else:
            self._texts_height = 300
        self._final = None  # Force rebuild

    def set_background(self, color_or_path):
        """Set background color (RGB tuple) or path to an image that used to
        fill the background.

        :param color_or_path: RGB color tuple or image path
        :type color_or_path: tuple or str
        """
        if isinstance(color_or_path, (tuple, list)):
            assert len(color_or_path) == 3, "Length of 3 is required for RGB tuple"
            self._background_color = color_or_path
        else:
            color_or_path = osp.abspath(color_or_path)
            if not osp.isfile(color_or_path):
                raise ValueError("Invalid background image '{}'".format(color_or_path))
            self._background_image = color_or_path
        self._final = None  # Force rebuild

    def set_margin(self, margin):
        """Set margin between concatenated images.

        :param margin: margin in pixels
        :type margin: int
        """
        self._margin = margin

    def set_cropping(self, crop=True):
        """Enable the cropping of source images it order to fit to the final
        size. However some parts of the images will be lost.

        :param crop: enable / disable cropping
        :type crop: bool
        """
        self._crop = crop

    def build(self, rebuild=False):
        """Build the final image or doas nothing if the final image
        has already been built previously.

        :param rebuild: force re-build image
        :type rebuild: bool

        :return: PIL.Image instance
        :rtype: object
        """
        if not self._final or rebuild:

            with timeit("{}: create background".format(self.__class__.__name__)):
                image = self._build_background()

            with timeit("{}: concatenate images".format(self.__class__.__name__)):
                image = self._build_matrix(image)

            with timeit("{}: assemble final image".format(self.__class__.__name__)):
                self._final = self._build_final_image(image)

            with timeit("{}: draw texts".format(self.__class__.__name__)):
                self._build_texts(self._final)

            if self._outline:
                with timeit("{}: draw rectangle borders".format(self.__class__.__name__)):
                    self._build_borders(self._final)

        return self._final

    def save(self, path):
        """Build if not already done and save final image in a file.

        :param path: path to save
        :type path: str

        :return: PIL.Image instance
        :rtype: object
        """
        dirname = osp.dirname(osp.abspath(path))
        if not osp.isdir(dirname):
            os.mkdir(dirname)
        image = self.build()
        with timeit("Save image '{}'".format(path)):
            image.save(path)
        return image


class PilPictureMaker(PictureMaker):

    def _image_resize_keep_ratio(self, image, max_w, max_h, crop=False):
        """See upper class description.
        """
        if crop:
            width, height = sizing.new_size_keep_aspect_ratio(image.size, (max_w, max_h), 'outer')
            image = image.resize((width, height), Image.ANTIALIAS)
            image = image.crop(sizing.new_size_by_croping(image.size, (max_w, max_h)))
        else:
            width, height = sizing.new_size_keep_aspect_ratio(image.size, (max_w, max_h), 'inner')
            image = image.resize((width, height), Image.ANTIALIAS)
        return image, image.size[0], image.size[1]

    def _image_paste(self, image, dest_image, pos_x, pos_y):
        """See upper class description.
        """
        dest_image.paste(image, (pos_x, pos_y))

    def _iter_src_image(self):
        """See upper class description.
        """
        for image in self._images:
            yield image

    def _build_final_image(self, image):
        """See upper class description.
        """
        return image

    def _build_background(self):
        """See upper class description.
        """
        if self._background_image:
            bg = Image.open(self._background_image)
            image, _, _ = self._image_resize_keep_ratio(bg, self.width, self.height, True)
        else:
            image = Image.new('RGB', (self.width, self.height), color=self._background_color)
        return image


class OpenCvPictureMaker(PictureMaker):

    def _image_resize_keep_ratio(self, image, max_w, max_h, crop=False):
        """See upper class description.
        """
        inter = cv2.INTER_AREA
        height, width = image.shape[:2]

        source_aspect_ratio = float(width) / height
        target_aspect_ratio = float(max_w) / max_h

        if crop:
            if source_aspect_ratio <= target_aspect_ratio:
                h_cropped = int(width / target_aspect_ratio)
                x_offset = 0
                y_offset = int((float(height) - h_cropped) / 2)
                cropped = image[y_offset:(y_offset + h_cropped), x_offset:width]
            else:
                w_cropped = int(height * target_aspect_ratio)
                x_offset = int((float(width) - w_cropped) / 2)
                y_offset = 0
                cropped = image[y_offset:height, x_offset:(x_offset + w_cropped)]
            image = cv2.resize(cropped, (max_w, max_h), interpolation=inter)
        else:
            width, height = sizing.new_size_keep_aspect_ratio((width, height), (max_w, max_h), 'inner')
            image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        return image, image.shape[1], image.shape[0]

    def _image_paste(self, image, dest_image, pos_x, pos_y):
        """See upper class description.
        """
        height, width = image.shape[:2]
        dest_image[pos_y:(pos_y + height), pos_x:(pos_x + width)] = image

    def _iter_src_image(self):
        """See upper class description.
        """
        for image in self._images:
            yield np.array(image.convert('RGB'))

    def _build_final_image(self, image):
        """See upper class description.
        """
        return Image.fromarray(image)

    def _build_background(self):
        """See upper class description.
        """
        if self._background_image:
            bg = cv2.cvtColor(cv2.imread(self._background_image), cv2.COLOR_BGR2RGB)
            image, _, _ = self._image_resize_keep_ratio(bg, self.width, self.height, True)
        else:
            # Small optimization for all white or all black (or all grey...) background
            if self._background_color[0] == self._background_color[1] and self._background_color[1] == self._background_color[2]:
                image = np.full((self.height, self.width, 3), self._background_color[0], np.uint8)
            else:
                image = np.zeros((self.height, self.width, 3), np.uint8)
                image[:] = (self._background_color[0], self._background_color[1], self._background_color[2])

        return image
