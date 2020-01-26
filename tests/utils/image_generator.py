import os

from PIL import Image, ImageDraw


def generate_test_images(target_dir, count, start_date):
    """
    Generates dummy images in a given target directory where the name starts with given start_date for filename.

    :param Path target_dir: The directory in which the images should be generated.
    :param int count: The amount of test images to generate.
    :param datetime.datetime start_date: The date as unix timestamp to use for filename.
    """
    start_date_unix = int(start_date.timestamp())
    for count in range(count):
        print("Writing image {}".format(start_date_unix + count))
        preview = Image.new('RGB', (128, 50), color=(75, 100, 130))
        drawer = ImageDraw.Draw(preview)
        drawer.text((30, 10), 'Test image {}'.format(count), fill=(255, 255, 0))
        preview.save(os.path.join(target_dir, 'previews', '{}.jpg'.format(start_date_unix + count)))

        raw = Image.new('RGB', (200, 200), color=(75, 100, 130))
        drawer = ImageDraw.Draw(raw)
        drawer.text((30, 10), 'Test image {}'.format(count), fill=(255, 255, 0))
        extension = 'jpg' if count % 2 else 'png'
        raw.save(os.path.join(target_dir, 'raw', '{}.{}'.format(start_date_unix + count, extension)))
