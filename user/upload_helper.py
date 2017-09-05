import os
import logging
import boto3
from api.settings import BASE_DIR
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import string
import random
import math
#
# logger = logging.getLogger('clienthub')

class Upload_Helper(object):

    BUCKET_REGION_URL = 'https://s3.us-east-2.amazonaws.com'
    BUCKET_NAME = 'cloudclienthub-test'

    @classmethod
    def upload_s3(cls, file, file_type, thumb=True):
        if (file):
            s3 = boto3.resource('s3')
            destination = os.path.join(BASE_DIR, 'uploads')
            if not os.path.isdir(destination):
                os.mkdir(destination)

            content = ContentFile(file.read())
            filename = file.name
            file_name = filename[0:filename.rfind('.')]
            file_ext = filename[filename.rfind('.')+1:len(filename)]
            path = default_storage.save('{0}'.format(filename), content)

            try:

                # Resize image if needed
                if int(file_type == 4):
                    im = Image.open('uploads/{0}'.format(path))
                    if thumb:
                        width = im.width
                        height = im.height
                        max_height = 90
                        divisor = height / max_height
                        newwidth = math.floor( width / divisor )
                        im.thumbnail((newwidth, 90))
                        im.save('uploads/thumb_{0}'.format(file.name), im.format)
                        filename = 'thumb_{0}'.format(file.name)
                    else:
                        im.save('uploads/{0}'.format(file.name), im.format)
                        filename = '{0}'.format(file.name)
                else:
                    filename = '{0}'.format(file.name)

                # Generate a random filename before saving to the bucket
                filename_rand = '{0}_{1}.{2}'.format(
                    file_name,
                    ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)),
                    file_ext
                )

                # Open the local file
                file_data = open('uploads/{0}'.format(filename), 'rb')
                # Upload to amazon
                upload_result = s3.Bucket(cls.BUCKET_NAME).put_object(
                    Key='{0}'.format(filename_rand), Body=file_data)

                # Generate the file URL
                url = '{}/{}/{}'.format(cls.BUCKET_REGION_URL, cls.BUCKET_NAME,
                                             '{0}'.format(filename_rand))

                # Change permission to public
                object_acl = s3.ObjectAcl(cls.BUCKET_NAME, '{0}'.format(filename_rand))
                response = object_acl.put(ACL='public-read')

                # Close file in python
                file_data.close()

                # Delete from django storage
                default_storage.delete(file.name)
                default_storage.delete('thumb_{0}'.format(file.name))

                return url

            except IOError as error:
                print("cannot create thumbnail for {0}".format(file.name))
            except Exception as e:
                print e